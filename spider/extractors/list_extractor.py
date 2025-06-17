# -*- coding: utf-8 -*-
"""
列表页面数据提取器
负责从项目列表页面提取项目基础信息
"""

import re
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import DataUtils, ParserUtils


class ListExtractor:
    """项目列表页面数据提取器"""

    def __init__(self, config: SpiderConfig, web_monitor=None):
        self.config = config
        self.data_utils = DataUtils()
        self.web_monitor = web_monitor

        # 多套CSS选择器策略，按优先级排序
        self.list_selectors = [
            # 主要选择器
            {'container': 'div.pro_field', 'items': 'li', 'link': 'a.pro_name.ga', 'title': 'h3.pro_title'},
            # 备用选择器
            {'container': '.pro_field', 'items': 'li', 'link': 'a[href*="/item/"]', 'title': 'h3'},
            {'container': 'ul.project-list', 'items': 'li', 'link': 'a.project-link', 'title': '.project-title'},
            # 通用选择器
            {'container': '[class*="project"]', 'items': 'li, .item', 'link': 'a[href*="/item/"]', 'title': 'h3, .title'}
        ]

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def extract_project_list(self, html: str) -> List[Tuple[str, str, str, str, Dict[str, str]]]:
        """智能适配解析项目列表 - 提取首页列表中的所有可用数据"""
        projects = []
        soup = BeautifulSoup(html, "html.parser")

        # 尝试多套选择器策略
        for selector_set in self.list_selectors:
            try:
                container = soup.select_one(selector_set['container'])
                if not container:
                    continue

                items = container.select(selector_set['items'])
                if not items:
                    continue

                self._log("info", f"✅ 使用选择器策略: {selector_set['container']} -> 找到 {len(items)} 个项目")

                for item in items:
                    try:
                        project_data = self._extract_single_project(item, selector_set)
                        if project_data:
                            projects.append(project_data)
                    except Exception as e:
                        self._log("warning", f"解析单个项目失败: {e}")
                        continue

                # 如果找到项目，返回结果
                if projects:
                    return projects

            except Exception as e:
                self._log("warning", f"选择器策略失败 {selector_set['container']}: {e}")
                continue

        self._log("warning", "⚠️ 所有选择器策略都失败了，尝试通用解析")
        return self._fallback_parse_project_list(soup)

    def _extract_single_project(self, item, selector_set) -> Tuple[str, str, str, str, Dict[str, str]]:
        """提取单个项目信息"""
        # 项目链接
        link_element = item.select_one(selector_set['link'])
        if not link_element:
            return None

        project_url = ParserUtils.safe_get_attr(link_element, 'href')
        if not project_url:
            return None

        project_url = self.data_utils.validate_url(project_url)
        project_id = self.data_utils.extract_project_id(project_url)

        if not project_id:
            return None

        # 项目标题
        title_element = item.select_one(selector_set['title'])
        if title_element:
            project_name = ParserUtils.safe_get_text(title_element)
        else:
            # 尝试从链接中获取标题
            project_name = ParserUtils.safe_get_text(link_element)

        project_name = self.data_utils.clean_text(project_name, self.config.MAX_TITLE_LENGTH)

        # 项目图片
        img_element = item.select_one('img')
        project_image = "none"
        if img_element:
            project_image = ParserUtils.safe_get_attr(img_element, 'src')
            project_image = self.data_utils.validate_url(project_image)

        # 提取首页列表中的额外数据
        list_data = self._extract_list_page_data(item, project_id)

        return (project_url, project_id, project_name, project_image, list_data)

    def _extract_list_page_data(self, item_element, project_id: str) -> Dict[str, str]:
        """从首页列表项中提取额外数据"""
        list_data = {
            "list_backer_money": "0",      # 已筹金额
            "list_rate": "0",              # 完成率
            "list_backer_count": "0",      # 支持者数量
            "list_author_name": "none"     # 作者名称
        }

        try:
            # 1. 提取已筹金额 - 从backer_money属性
            backer_money_spans = item_element.select('span[backer_money]')
            for span in backer_money_spans:
                span_text = ParserUtils.safe_get_text(span).strip()
                if span_text and span_text.replace(',', '').replace('.', '').isdigit():
                    list_data["list_backer_money"] = span_text.replace(',', '')
                    break

            # 2. 提取完成率 - 从rate属性
            rate_spans = item_element.select('span[rate]')
            for span in rate_spans:
                span_text = ParserUtils.safe_get_text(span).strip()
                if span_text and '%' in span_text:
                    list_data["list_rate"] = span_text.replace('%', '')
                    break
                elif span_text and span_text.replace('.', '').isdigit():
                    try:
                        rate_val = float(span_text)
                        if rate_val > 10:  # 如果大于10，可能是百分比形式
                            list_data["list_rate"] = str(rate_val)
                        else:  # 如果小于等于10，可能是小数形式，需要乘100
                            list_data["list_rate"] = str(rate_val * 100)
                        break
                    except ValueError:
                        continue

            # 3. 提取支持者数量 - 从backer_count属性
            backer_count_spans = item_element.select('span[backer_count]')
            for span in backer_count_spans:
                span_text = ParserUtils.safe_get_text(span).strip()
                if span_text and span_text.isdigit():
                    list_data["list_backer_count"] = span_text
                    break

            # 4. 提取作者名称 - 从作者区域
            author_elements = item_element.select('.author p, .author a')
            for elem in author_elements:
                author_text = ParserUtils.safe_get_text(elem).strip()
                if author_text and len(author_text) > 0 and len(author_text) < 50:
                    list_data["list_author_name"] = author_text
                    break

            # 回退到文本解析（如果HTML属性提取失败）
            if list_data["list_backer_count"] == "0":
                item_text = item_element.get_text()
                # 查找"支持者"模式
                supporter_matches = re.findall(r'(\d+)\s*支持者', item_text)
                if supporter_matches:
                    list_data["list_backer_count"] = supporter_matches[0]
                else:
                    # 查找其他支持者模式
                    supporter_patterns = [
                        r'(\d+)\s*人\s*支持',
                        r'支持者\s*(\d+)',
                        r'(\d+)\s*人',
                    ]
                    for pattern in supporter_patterns:
                        match = re.search(pattern, item_text)
                        if match:
                            list_data["list_backer_count"] = match.group(1)
                            break

            self._log("debug", f"列表数据提取: 项目{project_id} -> 已筹¥{list_data['list_backer_money']}, 完成率{list_data['list_rate']}%, 支持者{list_data['list_backer_count']}人")

        except Exception as e:
            self._log("warning", f"列表数据提取失败: {e}")

        return list_data

    def _fallback_parse_project_list(self, soup: BeautifulSoup) -> List[Tuple[str, str, str, str, Dict[str, str]]]:
        """通用回退解析策略"""
        projects = []

        # 查找所有包含项目链接的元素
        all_links = soup.find_all('a', href=re.compile(r'/item/\d+\.html'))

        for link in all_links:
            try:
                project_url = ParserUtils.safe_get_attr(link, 'href')
                project_url = self.data_utils.validate_url(project_url)
                project_id = self.data_utils.extract_project_id(project_url)

                if not project_id:
                    continue

                # 获取标题
                title_element = link.find(['h3', 'h2', 'h1']) or link
                project_name = ParserUtils.safe_get_text(title_element)
                project_name = self.data_utils.clean_text(project_name, self.config.MAX_TITLE_LENGTH)

                # 获取图片
                img_element = link.find('img')
                project_image = "none"
                if img_element:
                    project_image = ParserUtils.safe_get_attr(img_element, 'src')
                    project_image = self.data_utils.validate_url(project_image)

                # 尝试从父元素提取列表数据
                parent_li = link.find_parent('li')
                if parent_li:
                    list_data = self._extract_list_page_data(parent_li, project_id)
                else:
                    list_data = {
                        "list_backer_money": "0",
                        "list_rate": "0",
                        "list_backer_count": "0",
                        "list_author_name": "none"
                    }

                projects.append((project_url, project_id, project_name, project_image, list_data))

            except Exception as e:
                self._log("warning", f"通用解析失败: {e}")
                continue

        return projects
