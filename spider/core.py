# -*- coding: utf-8 -*-
"""
爬虫核心模块
优化版的摩点众筹爬虫，集成监控、验证、缓存等功能
"""

import time
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .config import SpiderConfig, StatusMapping
from .utils import NetworkUtils, DataUtils, CacheUtils, ParserUtils
from .monitor import SpiderMonitor
from .validator import DataValidator
from .exporter import DataExporter


class AdaptiveParser:
    """智能适配解析器 - 能够自动适配摩点网站的各种页面结构"""

    def __init__(self, config: SpiderConfig, network_utils: NetworkUtils, web_monitor=None):
        self.config = config
        self.network_utils = network_utils
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

        # 详情页多套选择器策略
        self.detail_selectors = {
            'status_button': [
                'div.buttons.clearfloat a',
                '.buttons a',
                '[class*="button"] a',
                'a[class*="support"], a[class*="back"]'
            ],
            'raised_money': [
                'span[backer_money]',
                '.raised-money',
                '[class*="raised"] [class*="money"]',
                'span:contains("¥"), .money'
            ],
            'completion_rate': [
                'span[rate]',
                '.completion-rate',
                '[class*="rate"]',
                'span:contains("%")'
            ],
            'target_money': [
                'span.goal-money',
                '.target-money',
                '.goal-money',
                '[class*="target"] [class*="money"]'
            ],
            'backer_count': [
                'span[backer_count]',
                '.backer-count',
                '[class*="supporter"]',
                'span:contains("人"), span:contains("支持")'
            ],
            'author_name': [
                'span.name',
                '.author-name',
                '.creator-name',
                '[class*="author"] .name'
            ],
            'author_link': [
                'a.sponsor-link',
                '.author-link',
                'a[href*="/u/detail"]',
                'a[href*="uid="]'
            ]
        }

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def try_multiple_selectors(self, soup: BeautifulSoup, selectors: list, element_type: str = "element") -> any:
        """尝试多个选择器，返回第一个成功的结果"""
        for selector in selectors:
            try:
                if element_type == "text":
                    element = soup.select_one(selector)
                    if element:
                        return ParserUtils.safe_get_text(element)
                elif element_type == "attr":
                    element = soup.select_one(selector)
                    if element:
                        return element
                else:
                    result = soup.select(selector) if element_type == "all" else soup.select_one(selector)
                    if result:
                        return result
            except Exception:
                continue
        return None

    def adaptive_parse_project_list(self, html: str) -> List[Tuple[str, str, str, str]]:
        """智能适配解析项目列表"""
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

                print(f"✅ 使用选择器策略: {selector_set['container']} -> 找到 {len(items)} 个项目")

                for item in items:
                    try:
                        # 项目链接
                        link_element = item.select_one(selector_set['link'])
                        if not link_element:
                            continue

                        project_url = ParserUtils.safe_get_attr(link_element, 'href')
                        if not project_url:
                            continue

                        project_url = self.data_utils.validate_url(project_url)
                        project_id = self.data_utils.extract_project_id(project_url)

                        if not project_id:
                            continue

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

                        projects.append((project_url, project_id, project_name, project_image))

                    except Exception as e:
                        print(f"解析单个项目失败: {e}")
                        continue

                # 如果找到项目，返回结果
                if projects:
                    return projects

            except Exception as e:
                print(f"选择器策略失败 {selector_set['container']}: {e}")
                continue

        print("⚠️ 所有选择器策略都失败了，尝试通用解析")
        return self._fallback_parse_project_list(soup)

    def _fallback_parse_project_list(self, soup: BeautifulSoup) -> List[Tuple[str, str, str, str]]:
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

                projects.append((project_url, project_id, project_name, project_image))

            except Exception as e:
                print(f"通用解析失败: {e}")
                continue

        return projects

    def _extract_js_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """从JavaScript代码中提取项目数据"""
        js_data = {
            "category": "none",
            "start_time": "none",
            "end_time": "none",
            "project_info": {}
        }

        try:
            # 查找包含PROJECT_INFO的script标签
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text()

                # 提取PROJECT_INFO数据
                if 'PROJECT_INFO.push(JSON.parse(' in script_text:
                    # 使用正则表达式提取JSON字符串
                    pattern = r'PROJECT_INFO\.push\(JSON\.parse\(\'([^\']+)\'\)\);'
                    match = re.search(pattern, script_text)
                    if match:
                        json_str = match.group(1)
                        # 解码Unicode字符
                        json_str = json_str.encode().decode('unicode_escape')
                        try:
                            project_data = json.loads(json_str)
                            js_data["project_info"] = project_data
                            js_data["category"] = project_data.get("category", "none")
                        except json.JSONDecodeError:
                            pass

                # 提取时间信息
                if 'realtime_sync.pro_time(' in script_text:
                    # 提取开始和结束时间
                    time_pattern = r'realtime_sync\.pro_time\([\'"]([^\'\"]+)[\'"],\s*[\'"]([^\'\"]+)[\'"]'
                    time_match = re.search(time_pattern, script_text)
                    if time_match:
                        js_data["start_time"] = time_match.group(1)
                        js_data["end_time"] = time_match.group(2)

        except Exception as e:
            print(f"解析JavaScript数据失败: {e}")

        return js_data
    
    def parse_project_status(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """解析项目状态"""
        status_info = {
            "item_class": "未知情况",
            "is_idea": False,
            "is_preheat": False,
            "is_going": False,
            "is_success": False,
            "is_fail": False
        }
        
        button = ParserUtils.safe_find(soup, 'div', {'class': 'buttons clearfloat'})
        if button:
            button_a = ParserUtils.safe_find(button, 'a')
            if button_a:
                button_text = ParserUtils.safe_get_text(button_a).strip()
                status_info.update(StatusMapping.get_status_info(button_text))
                status_info["raw_status_text"] = button_text
        
        return status_info
    
    def parse_basic_info(self, soup: BeautifulSoup, project_status: Dict) -> List[Any]:
        """解析基础信息"""
        data = []

        # 时间信息
        start_time, end_time = self._parse_time_info(soup, project_status)
        data.extend([start_time, end_time, project_status["item_class"]])

        # 作者基础信息 - 使用智能适配解析 (5个字段)
        author_info = self.adaptive_parse_author_info(soup)
        data.extend(author_info)

        # 众筹数据 - 使用智能适配解析 (4个字段)
        funding_info = self.adaptive_parse_funding_info(soup, project_status)
        data.extend(funding_info)

        # 作者详细信息 (6个字段)
        author_details = self._get_author_details(soup, author_info[0], author_info[4])
        data.extend(author_details)

        return data

    def _get_author_details(self, soup: BeautifulSoup, author_url: str, author_uid: str) -> List[str]:
        """获取作者详细信息"""
        if author_url != "none" and author_uid != "0":
            try:
                return self._fetch_author_details(author_url, author_uid)
            except Exception as e:
                self._log("warning", f"获取作者详细信息失败: {e}")

        # 返回默认值
        return ["0", "0", "0", "{}", "{}", author_url if author_url != "none" else "none"]
    
    def _parse_time_info(self, soup: BeautifulSoup, project_status: Dict) -> Tuple[str, str]:
        """解析时间信息"""
        start_time = "none"
        end_time = "none"
        
        if project_status["is_preheat"]:
            time_div = ParserUtils.safe_find(soup, 'div', {'class': 'col2 start-time'})
            if time_div:
                h3_tags = ParserUtils.safe_find_all(time_div, 'h3')
                if h3_tags:
                    start_text = ParserUtils.safe_get_text(h3_tags[0])
                    if "开始" in start_text:
                        start_time = start_text.replace("开始", "").strip()
                    
                    if len(h3_tags) > 1:
                        end_text = ParserUtils.safe_get_text(h3_tags[1])
                        if "结束" in end_text:
                            end_time = end_text.replace("结束", "").strip()
                        else:
                            end_time = "预热中"
                    else:
                        end_time = "预热中"
        
        elif project_status["is_idea"]:
            start_time = "创意中"
            end_time = "创意中"
        
        else:
            # 首先尝试从JavaScript数据中提取时间
            js_data = self._extract_js_data(soup)
            if js_data["start_time"] != "none" and js_data["end_time"] != "none":
                start_time = js_data["start_time"]
                end_time = js_data["end_time"]
            else:
                # 回退到原有的解析逻辑
                time_div = ParserUtils.safe_find(soup, 'div', {'class': 'col2 remain-time'})
                if time_div:
                    h3_tags = ParserUtils.safe_find_all(time_div, 'h3')
                    for h3 in h3_tags:
                        start_attr = ParserUtils.safe_get_attr(h3, 'start_time')
                        end_attr = ParserUtils.safe_get_attr(h3, 'end_time')
                        if start_attr:
                            start_time = start_attr
                        if end_attr:
                            end_time = end_attr

        return self.data_utils.parse_time(start_time), self.data_utils.parse_time(end_time)
    
    def adaptive_parse_author_info(self, soup: BeautifulSoup) -> List[str]:
        """智能适配解析作者信息 - 基于实际HTML结构"""
        sponsor_href = "none"
        author_image = "none"
        category = "none"
        author_name = "none"
        author_uid = "0"
        try:
            # 从页面文本中提取作者名称 - 查找"发起了这个项目"前的文本
            page_text = soup.get_text()

            # 解析作者名称
            author_match = re.search(r'([^\n]+)\s*发起了这个项目', page_text)
            if author_match:
                author_name = author_match.group(1).strip()
                self._log("info", f"找到作者名称: {author_name}")

            # 解析项目分类 - "项目类别：桌游"
            category_match = re.search(r'项目类别[：:]\s*([^\n\r]+)', page_text)
            if category_match:
                category = category_match.group(1).strip()
                self._log("info", f"找到项目分类: {category}")

            # 查找作者链接 - 查找包含uid的链接
            author_links = soup.find_all('a', href=re.compile(r'uid=\d+'))
            if author_links:
                sponsor_href = ParserUtils.safe_get_attr(author_links[0], 'href')
                sponsor_href = self.data_utils.validate_url(sponsor_href)

                # 提取用户ID
                uid_match = re.search(r'uid=(\d+)', sponsor_href)
                if uid_match:
                    author_uid = uid_match.group(1)
                    self._log("info", f"找到作者UID: {author_uid}")

            # 查找作者头像
            author_imgs = soup.find_all('img')
            for img in author_imgs:
                src = ParserUtils.safe_get_attr(img, 'src')
                if src and ('avatar' in src or 'dst_avatar' in src):
                    author_image = self.data_utils.validate_url(src)
                    self._log("info", f"找到作者头像: {author_image[:50]}...")
                    break

        except Exception as e:
            self._log("warning", f"作者信息解析失败: {e}")
            # 回退到传统解析
            return self._parse_author_info(soup)

        # 按照字段映射的顺序返回：用户主页(链接), 用户头像(图片链接), 分类, 用户名, 用户UID(data-username)
        return [sponsor_href, author_image, category, author_name, author_uid]

    def _parse_author_info(self, soup: BeautifulSoup) -> List[str]:
        """解析作者信息"""
        sponsor_info = ParserUtils.safe_find(soup, 'div', {'class': 'sponsor-info clearfix'})
        if not sponsor_info:
            sponsor_info = ParserUtils.safe_find(soup, 'div', {'class': 'sponsor-info'})

        sponsor_href = "none"
        author_image = "none"
        category = "none"
        author_name = "none"
        author_uid = "0"
        author_details = ["0", "0", "0", "{}", "{}", "none"]

        if sponsor_info:
            # 作者链接 - 优化选择器
            sponsor_link = ParserUtils.safe_find(sponsor_info, 'a', {'class': 'sponsor-link'})
            if not sponsor_link:
                # 尝试其他可能的链接选择器
                sponsor_link = ParserUtils.safe_find(sponsor_info, 'a', {'class': 'avater'})
            if not sponsor_link:
                # 查找包含modian.com的链接
                links = ParserUtils.safe_find_all(sponsor_info, 'a')
                for link in links:
                    href = ParserUtils.safe_get_attr(link, 'href')
                    if href and 'modian.com/u/detail' in href:
                        sponsor_link = link
                        break

            if sponsor_link:
                sponsor_href = ParserUtils.safe_get_attr(sponsor_link, 'href')
                sponsor_href = self.data_utils.validate_url(sponsor_href)

                # 获取作者详细信息
                if sponsor_href != "none":
                    user_id = self.data_utils.extract_user_id(sponsor_href)
                    if user_id:
                        author_details = self._fetch_author_details(sponsor_href, user_id)

            # 作者头像 - 优化选择器
            img_tag = ParserUtils.safe_find(sponsor_info, 'img', {'class': 'sponsor-image'})
            if not img_tag:
                # 尝试其他可能的图片选择器
                img_tag = ParserUtils.safe_find(sponsor_info, 'img')
            if img_tag:
                author_image = ParserUtils.safe_get_attr(img_tag, 'src')
                author_image = self.data_utils.validate_url(author_image)

            # 项目分类 - 优化解析逻辑
            # 首先尝试从JavaScript数据中提取
            js_data = self._extract_js_data(soup)
            if js_data["category"] != "none":
                category = js_data["category"]
            else:
                # 回退到HTML解析
                category_span = ParserUtils.safe_find(sponsor_info, 'span', string=lambda text: text and '项目类别：' in text)
                if category_span:
                    category = ParserUtils.safe_get_text(category_span).replace('项目类别：', '').strip()
                else:
                    # 尝试从tags区域获取分类
                    tags_p = ParserUtils.safe_find(sponsor_info, 'p', {'class': 'tags'})
                    if tags_p:
                        category_text = ParserUtils.safe_get_text(tags_p)
                        if '项目类别：' in category_text:
                            category = category_text.replace('项目类别：', '').strip()

            # 作者名称 - 优化选择器
            name_span = ParserUtils.safe_find(sponsor_info, 'span', {'data-nickname': True})
            if name_span:
                raw_name = ParserUtils.safe_get_attr(name_span, 'data-nickname') or ParserUtils.safe_get_text(name_span)
                author_name = self.data_utils.fix_encoding(raw_name)
                author_uid = ParserUtils.safe_get_attr(name_span, 'data-username', "0")
            else:
                # 尝试其他可能的名称选择器
                name_span = ParserUtils.safe_find(sponsor_info, 'span', {'class': 'name'})
                if name_span:
                    raw_name = ParserUtils.safe_get_text(name_span)
                    author_name = self.data_utils.fix_encoding(raw_name)

        result = [sponsor_href, author_image, category, author_name, author_uid]
        result.extend(author_details)
        return result
    
    def _fetch_author_details(self, author_url: str, user_id: str) -> List[str]:
        """获取作者详细信息 - 禁用API调用，直接解析页面"""
        try:
            # 直接解析页面，不使用API（避免418错误）
            html = self.network_utils.make_request(author_url, header_type="mobile")
            if html:
                return self._parse_author_page(html, user_id, author_url)

        except Exception as e:
            print(f"获取作者信息失败: {e}")

        # 返回默认值，避免验证失败
        return ["0", "0", "0", "{}", "{}", author_url]
    
    def _parse_author_page(self, html: str, user_id: str, author_url: str) -> List[str]:
        """解析作者页面"""
        soup = BeautifulSoup(html, "html.parser")
        
        fans_num = "0"
        following_num = "0"
        likes_num = "0"
        
        # 解析粉丝、关注、获赞数
        banner_div = ParserUtils.safe_find(soup, 'div', {'class': 'banner'})
        if banner_div:
            cont_div = ParserUtils.safe_find(banner_div, 'div', {'class': 'cont'})
            if cont_div:
                # 粉丝数
                fans_span = ParserUtils.safe_find(cont_div, 'span', {'class': 'go_span fans'})
                if fans_span:
                    fans_i = ParserUtils.safe_find(fans_span, 'i')
                    if fans_i:
                        fans_text = ParserUtils.safe_get_text(fans_i)
                        fans_num = self.data_utils.extract_number(fans_text)
                
                # 关注数和获赞数
                spans = ParserUtils.safe_find_all(cont_div, 'span')
                for span in spans:
                    text = ParserUtils.safe_get_text(span)
                    if '关注' in text:
                        following_num = self.data_utils.extract_number(text)
                    elif '获赞' in text or 'ALL' in ParserUtils.safe_get_attr(span, 'id'):
                        likes_num = self.data_utils.extract_number(text)
        
        # 解析详细信息
        detail_result = {}
        detail_div = ParserUtils.safe_find(soup, 'div', {'class': 'detail'})
        if detail_div:
            items = ParserUtils.safe_find_all(detail_div, 'div', class_='item')
            for item in items:
                label = ParserUtils.safe_find(item, 'label')
                p = ParserUtils.safe_find(item, 'p')
                if label and p:
                    detail_result[ParserUtils.safe_get_text(label)] = ParserUtils.safe_get_text(p)
        
        # 解析其他信息
        other_result = {}
        other_div = ParserUtils.safe_find(soup, 'div', {'class': 'other_info'})
        if other_div:
            items = ParserUtils.safe_find_all(other_div, 'div', class_='item')
            for item in items:
                p_tags = ParserUtils.safe_find_all(item, 'p')
                if len(p_tags) >= 2:
                    key = ParserUtils.safe_get_text(p_tags[1])
                    value = ParserUtils.safe_get_text(p_tags[0])
                    if value.isdigit():
                        other_result[key] = int(value)
        
        return [
            fans_num,
            following_num, 
            likes_num,
            str(detail_result),
            str(other_result),
            author_url
        ]
    
    def adaptive_parse_funding_info(self, soup: BeautifulSoup, project_status: Dict) -> List[str]:
        """智能适配解析众筹信息 - 基于实际HTML结构"""
        money = "0"
        percent = "0"
        goal_money = "0"
        sponsor_num = "0"

        try:
            # 从页面文本中提取已筹金额 - "已筹¥1,608"
            page_text = soup.get_text()

            # 解析已筹金额 - 处理编码问题 "å·²ç­¹Â¥1,608"
            money_patterns = [
                r'已筹[¥￥Â¥]([0-9,]+)',  # 正常编码
                r'å·²ç­¹[¥￥Â¥]([0-9,]+)',  # 编码后的中文
                r'已筹.*?[¥￥Â¥]\s*([0-9,]+)',  # 宽松匹配
                r'å·²ç­¹.*?[¥￥Â¥]\s*([0-9,]+)'   # 编码后宽松匹配
            ]

            for pattern in money_patterns:
                money_match = re.search(pattern, page_text)
                if money_match:
                    money = self.data_utils.format_money(money_match.group(1).replace(',', ''))
                    self._log("info", f"找到已筹金额: ¥{money}")
                    break

            # 解析目标金额 - 处理编码问题 "ç®æ éé¢ Â¥1,000"
            goal_patterns = [
                r'目标金额\s*[¥￥Â¥]([0-9,]+)',  # 正常编码
                r'ç®æ éé¢\s*[¥￥Â¥]([0-9,]+)',  # 编码后的中文
                r'目标金额.*?[¥￥Â¥]\s*([0-9,]+)',  # 宽松匹配
                r'ç®æ éé¢.*?[¥￥Â¥]\s*([0-9,]+)'   # 编码后宽松匹配
            ]

            for pattern in goal_patterns:
                goal_match = re.search(pattern, page_text)
                if goal_match:
                    goal_money = self.data_utils.format_money(goal_match.group(1).replace(',', ''))
                    self._log("info", f"找到目标金额: ¥{goal_money}")
                    break

            # 解析完成百分比 - "160.8%"
            percent_match = re.search(r'([0-9.]+)%', page_text)
            if percent_match:
                percent = percent_match.group(1)
                self._log("info", f"找到完成百分比: {percent}%")

            # 解析支持者数量 - 处理编码问题
            supporter_patterns = [
                r'(\d+)人\s*支持人数',  # 正常编码
                r'(\d+)äºº\s*æ¯æäººæ°',  # 编码后的中文
                r'支持人数\s*(\d+)',
                r'æ¯æäººæ°\s*(\d+)',
                r'(\d+)\s*人\s*支持',
                r'(\d+)\s*äºº\s*æ¯æ',
                r'支持者\s*(\d+)',
                r'æ¯æè\s*(\d+)',
                r'(\d+)\s*支持者',
                r'(\d+)\s*æ¯æè'
            ]

            for pattern in supporter_patterns:
                supporter_match = re.search(pattern, page_text)
                if supporter_match:
                    sponsor_num = supporter_match.group(1)
                    self._log("info", f"找到支持者数量: {sponsor_num}人")
                    break

            # 验证数据合理性
            if money != "0" and goal_money != "0":
                try:
                    calculated_percent = (float(money) / float(goal_money)) * 100
                    if percent == "0":
                        percent = f"{calculated_percent:.1f}"
                except:
                    pass

            self._log("info", f"解析众筹信息: 已筹¥{money}, 目标¥{goal_money}, 完成率{percent}%, 支持者{sponsor_num}人")

        except Exception as e:
            self._log("warning", f"众筹信息解析失败: {e}")
            # 回退到传统解析
            return self._parse_funding_info(soup, project_status)

        return [money, percent, goal_money, sponsor_num]

    def _parse_funding_info(self, soup: BeautifulSoup, project_status: Dict) -> List[str]:
        """解析众筹信息"""
        money = "0"
        percent = "0"
        goal_money = "0"
        sponsor_num = "0"
        
        center_div = ParserUtils.safe_find(soup, 'div', {'class': 'center'})
        if not center_div:
            return [money, percent, goal_money, sponsor_num]
        
        if project_status["is_preheat"]:
            # 预热阶段
            goal_div = ParserUtils.safe_find(center_div, 'div', {'class': 'col1 project-goal'})
            if goal_div:
                goal_span = ParserUtils.safe_find(goal_div, 'span')
                if goal_span:
                    goal_money = ParserUtils.safe_get_text(goal_span).replace('￥', '')
                    goal_money = self.data_utils.extract_number(goal_money)
            
            subscribe_span = ParserUtils.safe_find(center_div, 'span', {'subscribe_count': True})
            if subscribe_span:
                sponsor_num = ParserUtils.safe_get_attr(subscribe_span, 'subscribe_count')
                if not sponsor_num:
                    sponsor_num = ParserUtils.safe_get_text(subscribe_span).replace('人订阅', '')
                sponsor_num = self.data_utils.extract_number(sponsor_num)
        
        elif project_status["is_idea"]:
            # 创意阶段
            goal_money = 'none'
            sponsor_num = 'none'
        
        else:
            # 众筹中、成功、失败阶段
            money_span = ParserUtils.safe_find(center_div, 'span', {'backer_money': True})
            if money_span:
                money = ParserUtils.safe_get_text(money_span).replace('￥', '')
                money = self.data_utils.format_money(money)
            
            rate_span = ParserUtils.safe_find(center_div, 'span', {'rate': True})
            if rate_span:
                percent = ParserUtils.safe_get_text(rate_span).replace('%', '')
                percent = self.data_utils.extract_percentage(percent + '%')
            
            goal_span = ParserUtils.safe_find(center_div, 'span', {'class': 'goal-money'})
            if goal_span:
                goal_text = ParserUtils.safe_get_text(goal_span)
                # 处理编码问题和多种格式
                import re
                # 使用正则表达式提取金额数字
                amount_match = re.search(r'[¥￥]\s*([0-9,]+)', goal_text)
                if amount_match:
                    goal_money = amount_match.group(1).replace(',', '')
                    goal_money = self.data_utils.format_money(goal_money)
                else:
                    # 尝试直接提取数字
                    numbers = re.findall(r'[0-9,]+', goal_text)
                    if numbers:
                        goal_money = numbers[-1].replace(',', '')  # 取最后一个数字
                        goal_money = self.data_utils.format_money(goal_money)
            
            backer_span = ParserUtils.safe_find(center_div, 'span', {'backer_count': True})
            if backer_span:
                sponsor_num = ParserUtils.safe_get_attr(backer_span, 'backer_count')
                if not sponsor_num:
                    sponsor_num = ParserUtils.safe_get_text(backer_span).replace('人支持', '')
                sponsor_num = self.data_utils.extract_number(sponsor_num)
        
        return [money, percent, goal_money, sponsor_num]
    
    def parse_project_content(self, soup: BeautifulSoup) -> List[Any]:
        """解析项目内容"""
        data = []
        
        # 回报信息
        rewards_info = self._parse_rewards(soup)
        data.extend(rewards_info)
        
        # 导航信息
        nav_info = self._parse_nav_info(soup)
        data.extend(nav_info)
        
        # 项目详情
        content_info = self._parse_content_media(soup)
        data.extend(content_info)
        
        return data
    
    def _parse_rewards(self, soup: BeautifulSoup) -> List[Any]:
        """解析回报信息"""
        rewards_list = []
        
        main_right = ParserUtils.safe_find(soup, 'div', {'class': 'main-right'})
        if main_right:
            payback_div = ParserUtils.safe_find(main_right, 'div', {'class': 'payback-lists margin36'})
            if payback_div:
                reward_items = ParserUtils.safe_find_all(payback_div, 'div', class_=lambda x: x and 'back-list' in x)
                
                for item in reward_items:
                    reward_data = self._parse_single_reward(item)
                    rewards_list.append(str(reward_data))
        
        return [str(rewards_list), len(rewards_list)]
    
    def _parse_single_reward(self, item) -> List[str]:
        """解析单个回报项"""
        # 回报金额
        head_div = ParserUtils.safe_find(item, 'div', {'class': 'head'})
        back_money = "0"
        backers = "0"

        if head_div:
            money_span = ParserUtils.safe_find(head_div, 'span')
            if money_span:
                money_text = ParserUtils.safe_get_text(money_span).replace('￥', '')
                back_money = self.data_utils.extract_number(money_text)

            em_tag = ParserUtils.safe_find(head_div, 'em')
            if em_tag:
                em_text = ParserUtils.safe_get_text(em_tag)
                if "已满" in em_text:
                    backers = "已满"
                else:
                    backers = self.data_utils.extract_number(em_text)

        # 限量信息
        sign_logo = "0"
        subhead_div = ParserUtils.safe_find(item, 'div', {'class': 'zc-subhead'})
        if subhead_div:
            sign_span = ParserUtils.safe_find(subhead_div, 'span')
            if sign_span:
                sign_text = ParserUtils.safe_get_text(sign_span)
                if "限量" in sign_text:
                    num_part = sign_text.replace("限量", "").replace("份", "").strip()
                    sign_logo = f"限量 {num_part}" if num_part.isdigit() else "限量"

        # 回报内容
        content_div = ParserUtils.safe_find(item, 'div', {'class': 'back-content'})
        title = "none"
        detail = "none"
        time_info = "none"

        if content_div:
            title_div = ParserUtils.safe_find(content_div, 'div', {'class': 'back-sub-title'})
            if title_div:
                raw_title = ParserUtils.safe_get_text(title_div)
                title = self.data_utils.clean_reward_text(raw_title)

            detail_div = ParserUtils.safe_find(content_div, 'div', {'class': 'back-detail'})
            if detail_div:
                raw_detail = ParserUtils.safe_get_text(detail_div)
                detail = self.data_utils.clean_reward_text(raw_detail)

            time_div = ParserUtils.safe_find(content_div, 'div', {'class': 'back-time'})
            if time_div:
                raw_time = ParserUtils.safe_get_text(time_div)
                time_info = self.data_utils.clean_reward_text(raw_time)

        return [title, sign_logo, back_money, backers, time_info, detail]
    
    def _parse_nav_info(self, soup: BeautifulSoup) -> List[str]:
        """解析导航信息"""
        update_count = "0"
        comment_count = "0"
        supporter_count = "0"
        collect_count = "0"
        
        nav_wrap = ParserUtils.safe_find(soup, 'div', {'class': 'nav-wrap-inner'})
        if nav_wrap:
            nav_left = ParserUtils.safe_find(nav_wrap, 'ul', {'class': 'nav-left'})
            if nav_left:
                # 更新数
                update_li = ParserUtils.safe_find(nav_left, 'li', {'class': 'pro-gengxin'})
                if update_li:
                    update_span = ParserUtils.safe_find(update_li, 'span')
                    if update_span:
                        update_count = self.data_utils.extract_number(ParserUtils.safe_get_text(update_span))
                
                # 评论数
                comment_li = ParserUtils.safe_find(nav_left, 'li', {'class': 'nav-comment'})
                if comment_li:
                    comment_span = ParserUtils.safe_find(comment_li, 'span')
                    if comment_span:
                        comment_count = self.data_utils.extract_number(ParserUtils.safe_get_text(comment_span))
                
                # 支持者/点赞数
                userlist_li = ParserUtils.safe_find(nav_left, 'li', class_='dialog_user_list')
                if userlist_li:
                    user_span = ParserUtils.safe_find(userlist_li, 'span')
                    if user_span:
                        supporter_count = self.data_utils.extract_number(ParserUtils.safe_get_text(user_span))
            
            # 收藏数
            nav_right = ParserUtils.safe_find(nav_wrap, 'ul', {'class': 'nav-right'})
            if nav_right:
                atten_li = ParserUtils.safe_find(nav_right, 'li', {'class': 'atten'})
                if atten_li:
                    atten_span = ParserUtils.safe_find(atten_li, 'span')
                    if atten_span:
                        collect_count = self.data_utils.extract_number(ParserUtils.safe_get_text(atten_span))
        
        return [update_count, comment_count, supporter_count, collect_count]
    
    def _parse_content_media(self, soup: BeautifulSoup) -> List[Any]:
        """解析项目媒体内容"""
        img_list = []
        video_list = []
        
        main_left = ParserUtils.safe_find(soup, 'div', {'class': 'main-left'})
        if main_left:
            content_div = ParserUtils.safe_find(main_left, 'div', {'class': 'project-content'})
            if content_div:
                # 图片
                img_tags = ParserUtils.safe_find_all(content_div, 'img')
                for img in img_tags:
                    src = ParserUtils.safe_get_attr(img, 'src')
                    if src:
                        img_list.append(self.data_utils.validate_url(src))
                
                # 视频
                video_tags = ParserUtils.safe_find_all(content_div, 'video')
                for video in video_tags:
                    src = ParserUtils.safe_get_attr(video, 'src')
                    if src:
                        video_list.append(self.data_utils.validate_url(src))
                    else:
                        # 检查source标签
                        sources = ParserUtils.safe_find_all(video, 'source')
                        for source in sources:
                            src = ParserUtils.safe_get_attr(source, 'src')
                            if src:
                                video_list.append(self.data_utils.validate_url(src))
                                break
        
        return [len(img_list), str(img_list), len(video_list), str(video_list)]


class SpiderCore:
    """爬虫核心类"""

    def __init__(self, config: SpiderConfig = None, web_monitor=None):
        self.config = config or SpiderConfig()
        self.config.create_directories()

        # Web UI监控器
        self.web_monitor = web_monitor

        # 初始化组件
        self.network_utils = NetworkUtils(self.config)
        self.cache_utils = CacheUtils(self.config)
        self.monitor = SpiderMonitor(self.config)
        self.validator = DataValidator(self.config)
        self.exporter = DataExporter(self.config)
        self.parser = AdaptiveParser(self.config, self.network_utils, self.web_monitor)

        # 数据存储
        self.projects_data = []
        self.failed_urls = []

        # 线程锁和停止标志
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._is_running = False

        # 进度回调
        self._progress_callback = None

        self._log("info", f"爬虫初始化完成，输出目录: {self.config.OUTPUT_DIR}")

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self._progress_callback = callback

    def stop_crawling(self):
        """停止爬虫"""
        print("收到停止信号，正在停止爬虫...")
        self._stop_flag.set()
        self._is_running = False

    def is_stopped(self):
        """检查是否已停止"""
        return self._stop_flag.is_set()

    def is_running(self):
        """检查是否正在运行"""
        return self._is_running

    def start_crawling(self, start_page: int = 1, end_page: int = 50,
                      category: str = "all") -> bool:
        """开始爬取"""
        try:
            self._is_running = True
            self._stop_flag.clear()

            self._log("info", f"开始爬取摩点众筹数据...")
            self._log("info", f"页面范围: {start_page}-{end_page}")
            self._log("info", f"分类: {category}")

            # 启动监控
            self.monitor.start_monitoring()

            # 爬取项目列表
            project_urls = self._crawl_project_lists(start_page, end_page, category)

            if self.is_stopped():
                self._log("warning", "爬取已被用户停止")
                return False

            if not project_urls:
                self._log("warning", "未找到任何项目URL")
                return False

            self._log("info", f"发现 {len(project_urls)} 个项目，开始详细爬取...")

            # 更新进度
            if self._progress_callback:
                self._progress_callback(0, end_page - start_page + 1, len(project_urls), 0)

            # 爬取项目详情
            success = self._crawl_project_details(project_urls)

            # 停止监控
            self.monitor.stop_monitoring()

            # 数据验证和导出（如果有数据且未被停止）
            if self.projects_data and not self.is_stopped():
                self._validate_and_export_data()

            # 打印统计信息
            self.monitor.print_stats()

            return success

        except KeyboardInterrupt:
            print("\n用户中断爬取")
            self._is_running = False
            self.monitor.stop_monitoring()
            return False
        except Exception as e:
            print(f"爬取过程中出现错误: {e}")
            self.monitor.record_error("crawling_error", str(e))
            self._is_running = False
            self.monitor.stop_monitoring()
            return False
        finally:
            self._is_running = False

    def _crawl_project_lists(self, start_page: int, end_page: int,
                           category: str) -> List[Tuple[str, str, str, str]]:
        """爬取项目列表页面"""
        project_urls = []

        for page in range(start_page, end_page + 1):
            # 检查停止标志
            if self.is_stopped():
                print("收到停止信号，停止爬取页面列表")
                break

            try:
                self._log("info", f"正在爬取第 {page} 页...")

                url = self.config.get_full_url(category, page)
                page_projects = self._parse_project_list_page(url, page)

                if page_projects:
                    project_urls.extend(page_projects)
                    self.monitor.record_page(True)
                    self._log("success", f"第 {page} 页发现 {len(page_projects)} 个项目")

                    # 更新进度
                    if self._progress_callback:
                        current_progress = page - start_page + 1
                        total_pages = end_page - start_page + 1
                        self._progress_callback(current_progress, total_pages, len(project_urls), 0)
                else:
                    self.monitor.record_page(False)
                    self._log("warning", f"第 {page} 页未发现项目")

                # 检查是否需要停止
                if self.monitor.stats.consecutive_errors > self.config.MAX_CONSECUTIVE_ERRORS:
                    print("连续错误过多，停止爬取")
                    break

            except Exception as e:
                print(f"爬取第 {page} 页失败: {e}")
                self.monitor.record_error("page_crawl_error", str(e))
                self.monitor.record_page(False)

        return project_urls

    def _parse_project_list_page(self, url: str, page: int) -> List[Tuple[str, str, str, str]]:
        """解析项目列表页面"""
        start_time = time.time()

        # 检查缓存
        cached_content = self.cache_utils.get_cache(url)
        if cached_content:
            html = cached_content
            self.monitor.record_request(True, 0, cached=True)
        else:
            # 发送请求
            html = self.network_utils.make_request(url)
            request_time = time.time() - start_time

            if html:
                self.cache_utils.set_cache(url, html)
                self.monitor.record_request(True, request_time)
            else:
                self.monitor.record_request(False, request_time)
                return []

        # 解析页面
        parse_start = time.time()
        projects = self._extract_projects_from_list(html)
        parse_time = time.time() - parse_start
        self.monitor.record_parse(parse_time)

        return projects

    def _extract_projects_from_list(self, html: str) -> List[Tuple[str, str, str, str]]:
        """从列表页面提取项目信息 - 使用智能适配解析"""
        try:
            # 使用智能适配解析器
            projects = self.parser.adaptive_parse_project_list(html)

            # 过滤和验证项目
            filtered_projects = []
            for project_url, project_id, project_name, project_image in projects:
                try:
                    # 检查是否跳过
                    if self._should_skip_project(project_name):
                        self.monitor.record_project("skipped")
                        continue

                    filtered_projects.append((project_url, project_id, project_name, project_image))
                    self.monitor.record_project("found")

                except Exception as e:
                    print(f"验证项目失败: {e}")
                    self.monitor.record_error("project_validation_error", str(e))
                    continue

            print(f"✅ 智能解析完成: 发现 {len(projects)} 个项目，过滤后 {len(filtered_projects)} 个")
            return filtered_projects

        except Exception as e:
            print(f"智能解析失败，使用传统解析: {e}")
            self.monitor.record_error("adaptive_parse_error", str(e))
            return self._fallback_extract_projects(html)

    def _fallback_extract_projects(self, html: str) -> List[Tuple[str, str, str, str]]:
        """传统解析方法作为回退"""
        projects = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # 查找项目列表
            project_list = ParserUtils.safe_find(soup, 'div', {'class': 'pro_field'})
            if not project_list:
                return projects

            project_items = ParserUtils.safe_find_all(project_list, 'li')

            for item in project_items:
                try:
                    # 项目链接
                    link_tag = ParserUtils.safe_find(item, 'a', {'class': 'pro_name ga'})
                    if not link_tag:
                        continue

                    project_url = ParserUtils.safe_get_attr(link_tag, 'href')
                    if not project_url:
                        continue

                    project_url = self.data_utils.validate_url(project_url)

                    # 项目ID
                    project_id = self.data_utils.extract_project_id(project_url)
                    if not project_id:
                        continue

                    # 项目名称
                    title_tag = ParserUtils.safe_find(link_tag, 'h3', {'class': 'pro_title'})
                    project_name = ParserUtils.safe_get_text(title_tag) if title_tag else "未知项目"
                    project_name = self.data_utils.clean_text(project_name, self.config.MAX_TITLE_LENGTH)

                    # 检查是否跳过
                    if self._should_skip_project(project_name):
                        self.monitor.record_project("skipped")
                        continue

                    # 项目图片
                    img_tag = ParserUtils.safe_find(item, 'img')
                    project_image = ParserUtils.safe_get_attr(img_tag, 'src') if img_tag else "none"
                    project_image = self.data_utils.validate_url(project_image)

                    projects.append((project_url, project_id, project_name, project_image))
                    self.monitor.record_project("found")

                except Exception as e:
                    print(f"解析项目项失败: {e}")
                    continue

        except Exception as e:
            print(f"解析项目列表失败: {e}")
            self.monitor.record_error("parse_list_error", str(e))

        return projects

    def _should_skip_project(self, project_name: str) -> bool:
        """检查是否应该跳过项目"""
        if not project_name or len(project_name) < self.config.MIN_TITLE_LENGTH:
            return True

        for keyword in self.config.SKIP_KEYWORDS:
            if keyword in project_name:
                return True

        return False

    def _crawl_project_details(self, project_urls: List[Tuple[str, str, str, str]]) -> bool:
        """爬取项目详情"""
        if not project_urls:
            return False

        # 使用线程池并发爬取
        with ThreadPoolExecutor(max_workers=self.config.MAX_CONCURRENT_REQUESTS) as executor:
            # 提交任务
            future_to_project = {
                executor.submit(self._crawl_single_project, i, project_info): project_info
                for i, project_info in enumerate(project_urls)
            }

            # 处理结果
            completed = 0
            for future in as_completed(future_to_project):
                project_info = future_to_project[future]

                try:
                    result = future.result()
                    if result:
                        with self._lock:
                            self.projects_data.append(result)
                        self.monitor.record_project("processed")
                    else:
                        self.monitor.record_project("failed")
                        self.failed_urls.append(project_info[0])

                except Exception as e:
                    print(f"处理项目失败 {project_info[2]}: {e}")
                    self.monitor.record_error("project_process_error", str(e))
                    self.monitor.record_project("failed")
                    self.failed_urls.append(project_info[0])

                completed += 1
                if completed % 10 == 0:
                    print(f"已完成 {completed}/{len(project_urls)} 个项目")

        print(f"项目详情爬取完成，成功: {len(self.projects_data)}, 失败: {len(self.failed_urls)}")
        return len(self.projects_data) > 0

    def _crawl_single_project(self, index: int, project_info: Tuple[str, str, str, str]) -> Optional[List[Any]]:
        """爬取单个项目详情"""
        project_url, project_id, project_name, project_image = project_info

        try:
            start_time = time.time()

            # 检查缓存
            cached_content = self.cache_utils.get_cache(project_url)
            if cached_content:
                html = cached_content
                self.monitor.record_request(True, 0, cached=True)
            else:
                # 发送请求
                html = self.network_utils.make_request(project_url)
                request_time = time.time() - start_time

                if html:
                    self.cache_utils.set_cache(project_url, html)
                    self.monitor.record_request(True, request_time)
                else:
                    self.monitor.record_request(False, request_time)
                    return None

            # 解析项目详情
            parse_start = time.time()
            project_data = self._parse_project_detail(html, index + 1, project_url, project_id, project_name, project_image)
            parse_time = time.time() - parse_start
            self.monitor.record_parse(parse_time)

            return project_data

        except Exception as e:
            print(f"爬取项目详情失败 {project_name}: {e}")
            self.monitor.record_error("project_detail_error", str(e))
            return None

    def _parse_project_detail(self, html: str, index: int, project_url: str,
                            project_id: str, project_name: str, project_image: str) -> List[Any]:
        """解析项目详情页面"""
        soup = BeautifulSoup(html, "html.parser")

        # 基础信息
        project_data = [index, project_url, project_id, project_name, project_image]

        # 解析项目状态
        project_status = self.parser.parse_project_status(soup)

        # 解析基础信息
        basic_info = self.parser.parse_basic_info(soup, project_status)
        project_data.extend(basic_info)

        # 解析项目内容
        content_info = self.parser.parse_project_content(soup)
        project_data.extend(content_info)

        return project_data

    def _validate_and_export_data(self):
        """验证和导出数据"""
        print("开始数据验证...")

        # 批量验证
        validation_results = self.validator.validate_batch(self.projects_data)

        # 记录验证结果
        for result in validation_results['results']:
            self.monitor.record_validation(result['is_valid'])

        # 打印验证摘要
        print(self.validator.get_validation_summary(validation_results))

        # 导出数据
        print("开始导出数据...")

        try:
            # 导出Excel
            excel_file = self.exporter.export_to_excel(self.projects_data, self.config.EXCEL_FILENAME)

            # 导出JSON
            json_file = self.exporter.export_to_json(self.projects_data, self.config.JSON_FILENAME)

            # 导出摘要报告
            stats = self.monitor.get_current_stats()
            summary_file = self.exporter.export_summary_report(self.projects_data, stats)

            # 保存统计报告
            stats_file = f"{self.config.OUTPUT_DIR}/spider_stats_{time.strftime('%Y%m%d_%H%M%S')}.json"
            self.monitor.save_stats(stats_file)

            print(f"数据导出完成:")
            print(f"  Excel文件: {excel_file}")
            print(f"  JSON文件: {json_file}")
            print(f"  摘要报告: {summary_file}")
            print(f"  统计报告: {stats_file}")

        except Exception as e:
            print(f"数据导出失败: {e}")
            self.monitor.record_error("export_error", str(e))

    def get_crawl_stats(self) -> Dict[str, Any]:
        """获取爬取统计信息"""
        stats = self.monitor.get_current_stats()
        stats.update({
            "projects_data_count": len(self.projects_data),
            "failed_urls_count": len(self.failed_urls),
            "cache_stats": self.cache_utils.get_cache_stats(),
            "network_stats": self.network_utils.get_request_stats(),
            "export_stats": self.exporter.get_export_stats()
        })
        return stats

    def retry_failed_projects(self) -> bool:
        """重试失败的项目"""
        if not self.failed_urls:
            print("没有失败的项目需要重试")
            return True

        print(f"开始重试 {len(self.failed_urls)} 个失败的项目...")

        # 重新构造项目信息
        retry_projects = []
        for url in self.failed_urls:
            project_id = self.data_utils.extract_project_id(url)
            retry_projects.append((url, project_id, "重试项目", "none"))

        # 清空失败列表
        self.failed_urls.clear()

        # 重新爬取
        return self._crawl_project_details(retry_projects)

    def clear_cache(self):
        """清空缓存"""
        self.cache_utils.clear_cache()

    def save_progress(self):
        """保存进度"""
        if self.projects_data:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            progress_file = f"{self.config.OUTPUT_DIR}/progress_{timestamp}.json"

            progress_data = {
                "timestamp": timestamp,
                "projects_count": len(self.projects_data),
                "failed_urls": self.failed_urls,
                "stats": self.monitor.get_current_stats()
            }

            try:
                import json
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
                print(f"进度已保存到: {progress_file}")
            except Exception as e:
                print(f"保存进度失败: {e}")
