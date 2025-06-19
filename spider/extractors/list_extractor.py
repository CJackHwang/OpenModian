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
            "list_backer_money": "api",    # 已筹金额 - 使用API数据
            "list_rate": "api",            # 完成率 - 使用API数据
            "list_backer_count": "0",      # 支持者数量 - 继续尝试列表解析
            "list_author_name": "none",    # 作者名称
            "list_author_avatar": "none"   # 作者头像
        }

        try:
            # 1. 已筹金额 - 使用API数据 (列表解析不可靠)
            # 注释：由于HTML结构变化，列表解析金额字段不可靠，改为完全依赖API数据
            pass  # list_data["list_backer_money"] 保持为 "api" 标记

            # 2. 完成率 - 使用API数据 (列表解析不可靠)
            # 注释：由于HTML结构变化，列表解析进度字段不可靠，改为完全依赖API数据
            pass  # list_data["list_rate"] 保持为 "api" 标记

            # 3. 提取支持者数量 - 多种策略
            # 策略1: 直接查找backer_count属性
            backer_count_spans = item_element.select('span[backer_count]')
            if not backer_count_spans:
                # 策略2: 在gray_ex区域查找span
                gray_ex = item_element.select_one('.gray_ex')
                if gray_ex:
                    backer_count_spans = gray_ex.select('span')

            for span in backer_count_spans:
                span_text = ParserUtils.safe_get_text(span).strip()
                if span_text:
                    try:
                        # 尝试转换为整数验证
                        int(span_text)  # 只验证，不存储
                        list_data["list_backer_count"] = span_text
                        break
                    except ValueError:
                        # 如果转换失败，继续尝试下一个
                        continue

            # 4. 提取作者名称 - 从作者区域
            author_elements = item_element.select('.author p, .author a')
            for elem in author_elements:
                author_text = ParserUtils.safe_get_text(elem).strip()
                if author_text and len(author_text) > 0 and len(author_text) < 50:
                    list_data["list_author_name"] = author_text
                    break

            # 5. 提取作者头像 - 从.author .au_logo的style属性
            author_avatar_elements = item_element.select('.author .au_logo')
            for elem in author_avatar_elements:
                style_attr = ParserUtils.safe_get_attr(elem, 'style')
                if style_attr:
                    # 从style属性中提取background url
                    import re
                    url_match = re.search(r'background:\s*url\(([^)]+)\)', style_attr)
                    if url_match:
                        avatar_url = url_match.group(1).strip('\'"')
                        if avatar_url and avatar_url.startswith('http'):
                            list_data["list_author_avatar"] = avatar_url
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

            # 显示详细的解析状态
            avatar_status = "有头像" if list_data.get("list_author_avatar", "none") != "none" else "无头像"
            money_status = "API" if list_data["list_backer_money"] == "api" else "✅" if list_data["list_backer_money"] != "0" else "❌"
            rate_status = "API" if list_data["list_rate"] == "api" else "✅" if list_data["list_rate"] != "0" else "❌"
            count_status = "✅" if list_data["list_backer_count"] != "0" else "❌"

            self._log("debug", f"列表数据提取: 项目{project_id} -> 已筹¥{list_data['list_backer_money']}{money_status}, 完成率{list_data['list_rate']}%{rate_status}, 支持者{list_data['list_backer_count']}人{count_status}, 作者:{list_data.get('list_author_name', 'none')}({avatar_status})")

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
                        "list_backer_money": "api",  # 使用API数据
                        "list_rate": "api",          # 使用API数据
                        "list_backer_count": "0",
                        "list_author_name": "none",
                        "list_author_avatar": "none"
                    }

                projects.append((project_url, project_id, project_name, project_image, list_data))

            except Exception as e:
                self._log("warning", f"通用解析失败: {e}")
                continue

        return projects
