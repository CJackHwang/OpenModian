# -*- coding: utf-8 -*-
"""
作者信息提取器
负责从项目页面和作者页面提取作者相关信息
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import DataUtils, ParserUtils, NetworkUtils


class AuthorExtractor:
    """作者信息提取器"""

    def __init__(self, config: SpiderConfig, network_utils: NetworkUtils, web_monitor=None):
        self.config = config
        self.data_utils = DataUtils()
        self.network_utils = network_utils
        self.web_monitor = web_monitor

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def extract_author_info(self, soup: BeautifulSoup) -> List[str]:
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
            return self._parse_author_info_fallback(soup)

        # 按照字段映射的顺序返回：用户主页(链接), 用户头像(图片链接), 分类, 用户名, 用户UID(data-username)
        return [sponsor_href, author_image, category, author_name, author_uid]

    def _parse_author_info_fallback(self, soup: BeautifulSoup) -> List[str]:
        """传统作者信息解析方法"""
        sponsor_info = ParserUtils.safe_find(soup, 'div', {'class': 'sponsor-info clearfix'})
        if not sponsor_info:
            sponsor_info = ParserUtils.safe_find(soup, 'div', {'class': 'sponsor-info'})

        sponsor_href = "none"
        author_image = "none"
        category = "none"
        author_name = "none"
        author_uid = "0"

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
            if js_data.get("category") != "none":
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

        return [sponsor_href, author_image, category, author_name, author_uid]

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
                            import json
                            project_data = json.loads(json_str)
                            js_data["project_info"] = project_data
                            js_data["category"] = project_data.get("category", "none")
                        except json.JSONDecodeError:
                            pass

        except Exception as e:
            self._log("warning", f"解析JavaScript数据失败: {e}")

        return js_data

    def fetch_author_details(self, author_url: str, user_id: str) -> List[str]:
        """获取作者详细信息 - 禁用API调用，直接解析页面"""
        try:
            # 直接解析页面，不使用API（避免418错误）
            html = self.network_utils.make_request(author_url, header_type="mobile")
            if html:
                return self._parse_author_page(html, user_id, author_url)

        except Exception as e:
            self._log("warning", f"获取作者信息失败: {e}")

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

    def get_author_details(self, soup: BeautifulSoup, author_url: str, author_uid: str) -> List[str]:
        """获取作者详细信息"""
        if author_url != "none" and author_uid != "0":
            try:
                return self.fetch_author_details(author_url, author_uid)
            except Exception as e:
                self._log("warning", f"获取作者详细信息失败: {e}")

        # 返回默认值
        return ["0", "0", "0", "{}", "{}", author_url if author_url != "none" else "none"]
