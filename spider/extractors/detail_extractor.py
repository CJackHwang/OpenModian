# -*- coding: utf-8 -*-
"""
详情页面数据提取器
负责从项目详情页面提取完整的项目信息
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup

from ..config import SpiderConfig, StatusMapping
from ..utils import DataUtils, ParserUtils


class DetailExtractor:
    """项目详情页面数据提取器"""

    def __init__(self, config: SpiderConfig, web_monitor=None):
        self.config = config
        self.data_utils = DataUtils()
        self.web_monitor = web_monitor

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

    def extract_project_status(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """解析项目状态"""
        status_info = {
            "item_class": "未知情况",
            "is_idea": False,
            "is_preheat": False,
            "is_going": False,
            "is_success": False,
            "is_fail": False
        }

        # 基于状态按钮提取方法
        button_div = ParserUtils.safe_find(soup, 'div', {'class': 'buttons clearfloat'})
        if button_div:
            button_a = ParserUtils.safe_find(button_div, 'a')
            if button_a:
                button_text = ParserUtils.safe_get_text(button_a).strip()
                self._log("info", f"✅ 找到状态按钮文本: {button_text}")

                # 使用状态映射
                mapped_status = StatusMapping.get_status_info(button_text)
                status_info.update(mapped_status)
                status_info["raw_status_text"] = button_text

                # 根据按钮文本进行状态判断
                if "众筹成功" in button_text:
                    status_info["item_class"] = "众筹成功"
                    status_info["is_success"] = True
                elif "众筹结束" in button_text or "众筹失败" in button_text:
                    status_info["item_class"] = "众筹失败"
                    status_info["is_fail"] = True
                elif "看好创意" in button_text or "看好" in button_text:
                    status_info["item_class"] = "创意"
                    status_info["is_idea"] = True
                elif "立即购买支持" in button_text or "立即支持" in button_text:
                    status_info["item_class"] = "众筹中"
                    status_info["is_going"] = True
                elif "看好项目" in button_text:
                    status_info["item_class"] = "预热"
                    status_info["is_preheat"] = True

                self._log("info", f"✅ 项目状态: {status_info['item_class']}")

        return status_info

    def extract_basic_info(self, soup: BeautifulSoup, project_status: Dict) -> List[Any]:
        """解析基础信息"""
        data = []

        # 时间信息
        start_time, end_time = self._parse_time_info(soup, project_status)
        data.extend([start_time, end_time, project_status["item_class"]])

        return data

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
            # 从时间div中提取
            time_div = ParserUtils.safe_find(soup, 'div', {'class': 'col2 remain-time'})
            if time_div:
                h3_tags = ParserUtils.safe_find_all(time_div, 'h3')
                for h3 in h3_tags:
                    start_attr = ParserUtils.safe_get_attr(h3, 'start_time')
                    end_attr = ParserUtils.safe_get_attr(h3, 'end_time')
                    if start_attr:
                        start_time = start_attr
                        self._log("info", f"✅ 找到开始时间: {start_time}")
                    if end_attr:
                        end_time = end_attr
                        self._log("info", f"✅ 找到结束时间: {end_time}")

            # 如果HTML属性提取失败，尝试从JavaScript数据中提取时间
            if start_time == "none" or end_time == "none":
                js_data = self._extract_js_data(soup)
                if js_data["start_time"] != "none":
                    start_time = js_data["start_time"]
                    self._log("info", f"✅ JS提取开始时间: {start_time}")
                if js_data["end_time"] != "none":
                    end_time = js_data["end_time"]
                    self._log("info", f"✅ JS提取结束时间: {end_time}")

        return self.data_utils.parse_time(start_time), self.data_utils.parse_time(end_time)

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
            self._log("warning", f"解析JavaScript数据失败: {e}")

        return js_data

    def extract_project_content(self, soup: BeautifulSoup) -> List[Any]:
        """解析项目内容"""
        data = []
        
        # 回报信息
        rewards_info = self._parse_rewards(soup)
        data.extend(rewards_info)
        
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
