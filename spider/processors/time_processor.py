# -*- coding: utf-8 -*-
"""
时间处理器
负责时间数据解析和格式化
"""

import re
import time
from datetime import datetime, timezone
from typing import Tuple
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import DataUtils, ParserUtils


class TimeProcessor:
    """时间处理器 - 负责时间解析和格式化"""

    def __init__(self, config: SpiderConfig, data_utils: DataUtils, web_monitor=None):
        self.config = config
        self.data_utils = data_utils
        self.web_monitor = web_monitor

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def parse_time_info(self, soup: BeautifulSoup, project_status: dict, js_data: dict = None) -> Tuple[str, str]:
        """解析项目时间信息"""
        start_time = "none"
        end_time = "none"

        # 根据项目状态确定时间解析策略
        if project_status["is_idea"]:
            # 创意阶段没有具体时间
            return "创意中", "创意中"
        elif project_status["is_preheat"]:
            # 预热阶段
            start_time = "预热中"
            end_time = self._extract_preheat_end_time(soup)
        else:
            # 众筹阶段 - 尝试多种方法提取时间
            start_time, end_time = self._extract_crowdfunding_time(soup)

            # 如果HTML属性提取失败，尝试从JavaScript数据中提取时间
            if (start_time == "none" or end_time == "none") and js_data:
                if js_data.get("start_time", "none") != "none":
                    start_time = js_data["start_time"]
                    self._log("info", f"✅ JS提取开始时间: {start_time}")
                if js_data.get("end_time", "none") != "none":
                    end_time = js_data["end_time"]
                    self._log("info", f"✅ JS提取结束时间: {end_time}")

        return self.parse_time_string(start_time), self.parse_time_string(end_time)

    def _extract_preheat_end_time(self, soup: BeautifulSoup) -> str:
        """提取预热结束时间"""
        try:
            # 查找预热结束时间的多种可能位置
            time_selectors = [
                'span[data-end-time]',
                '.preheat-time',
                '.countdown-time',
                'span[class*="time"]'
            ]

            for selector in time_selectors:
                elements = soup.select(selector)
                for element in elements:
                    # 尝试从data属性获取
                    end_time = ParserUtils.safe_get_attr(element, 'data-end-time')
                    if end_time:
                        return self._format_timestamp(end_time)
                    
                    # 尝试从文本内容获取
                    text = ParserUtils.safe_get_text(element)
                    if text and self._is_valid_time_text(text):
                        return self._parse_time_text(text)

        except Exception as e:
            self._log("debug", f"预热时间提取失败: {e}")

        return "预热中"

    def _extract_crowdfunding_time(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """提取众筹时间信息"""
        start_time = "none"
        end_time = "none"

        try:
            # 方法1: 从data属性提取
            start_element = ParserUtils.safe_find(soup, 'span', {'data-start-time': True})
            if start_element:
                start_timestamp = ParserUtils.safe_get_attr(start_element, 'data-start-time')
                if start_timestamp:
                    start_time = self._format_timestamp(start_timestamp)

            end_element = ParserUtils.safe_find(soup, 'span', {'data-end-time': True})
            if end_element:
                end_timestamp = ParserUtils.safe_get_attr(end_element, 'data-end-time')
                if end_timestamp:
                    end_time = self._format_timestamp(end_timestamp)

            # 方法2: 从文本内容提取
            if start_time == "none" or end_time == "none":
                time_info = self._extract_time_from_text(soup)
                if time_info[0] != "none":
                    start_time = time_info[0]
                if time_info[1] != "none":
                    end_time = time_info[1]

            # 方法3: 从特定的时间显示区域提取
            if start_time == "none" or end_time == "none":
                time_display = ParserUtils.safe_find(soup, 'div', {'class': 'time-display'})
                if time_display:
                    time_texts = ParserUtils.safe_find_all(time_display, 'span')
                    for span in time_texts:
                        text = ParserUtils.safe_get_text(span)
                        if self._is_valid_time_text(text):
                            parsed_time = self._parse_time_text(text)
                            if start_time == "none":
                                start_time = parsed_time
                            elif end_time == "none":
                                end_time = parsed_time

        except Exception as e:
            self._log("debug", f"众筹时间提取失败: {e}")

        return start_time, end_time

    def _extract_time_from_text(self, soup: BeautifulSoup) -> Tuple[str, str]:
        """从页面文本中提取时间信息"""
        start_time = "none"
        end_time = "none"

        try:
            # 获取页面文本
            page_text = soup.get_text()

            # 时间模式匹配
            time_patterns = [
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',  # 2024-01-01 12:00:00
                r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})',        # 2024/01/01 12:00
                r'(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})', # 2024年1月1日 12:00
                r'(\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})',     # 1月1日 12:00
            ]

            found_times = []
            for pattern in time_patterns:
                matches = re.findall(pattern, page_text)
                found_times.extend(matches)

            # 如果找到时间，假设第一个是开始时间，最后一个是结束时间
            if len(found_times) >= 2:
                start_time = self._normalize_time_format(found_times[0])
                end_time = self._normalize_time_format(found_times[-1])
            elif len(found_times) == 1:
                # 只有一个时间，可能是结束时间
                end_time = self._normalize_time_format(found_times[0])

        except Exception as e:
            self._log("debug", f"文本时间提取失败: {e}")

        return start_time, end_time

    def _format_timestamp(self, timestamp_str: str) -> str:
        """格式化时间戳"""
        try:
            timestamp = int(timestamp_str)
            
            # 处理毫秒时间戳
            if timestamp > 10000000000:
                timestamp = timestamp // 1000
            
            # 转换为datetime对象
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            
            # 转换为本地时间并格式化
            local_dt = dt.astimezone()
            return local_dt.strftime('%Y-%m-%d %H:%M:%S')
            
        except (ValueError, OSError) as e:
            self._log("debug", f"时间戳格式化失败: {timestamp_str}, {e}")
            return "none"

    def _is_valid_time_text(self, text: str) -> bool:
        """检查文本是否包含有效的时间信息"""
        if not text:
            return False
        
        time_indicators = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}',  # 日期格式
            r'\d{1,2}:\d{2}',                    # 时间格式
            r'(开始|结束|截止)',                   # 时间关键词
        ]
        
        for pattern in time_indicators:
            if re.search(pattern, text):
                return True
        
        return False

    def _parse_time_text(self, text: str) -> str:
        """解析时间文本"""
        if not text:
            return "none"
        
        try:
            # 尝试多种时间格式解析
            time_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y年%m月%d日 %H:%M',
                '%m月%d日 %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y年%m月%d日'
            ]
            
            for fmt in time_formats:
                try:
                    # 提取时间部分
                    time_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?\s*\d{0,2}:?\d{0,2}:?\d{0,2})', text)
                    if time_match:
                        time_str = time_match.group(1)
                        # 标准化格式
                        time_str = time_str.replace('年', '-').replace('月', '-').replace('日', '')
                        dt = datetime.strptime(time_str, fmt)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            return self._normalize_time_format(text)
            
        except Exception as e:
            self._log("debug", f"时间文本解析失败: {text}, {e}")
            return "none"

    def _normalize_time_format(self, time_str: str) -> str:
        """标准化时间格式"""
        if not time_str:
            return "none"
        
        try:
            # 移除多余的空白字符
            time_str = re.sub(r'\s+', ' ', time_str.strip())
            
            # 替换中文字符
            time_str = time_str.replace('年', '-').replace('月', '-').replace('日', ' ')
            
            # 确保时间格式完整
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', time_str):
                time_str += ' 00:00:00'
            elif re.match(r'^\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}$', time_str):
                time_str += ':00'
            
            return time_str
            
        except Exception as e:
            self._log("debug", f"时间格式标准化失败: {time_str}, {e}")
            return time_str

    def parse_time_string(self, time_str: str) -> str:
        """解析时间字符串（从DataUtils移植）"""
        if not time_str or time_str in ["none", "创意中", "预热中", "众筹中"]:
            return time_str
            
        # 时间模式
        time_patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
            r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}',
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{2}-\d{2}\s+\d{2}:\d{2}'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, str(time_str))
            if match:
                return match.group(0)
        
        return time_str

    def get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def calculate_duration(self, start_time: str, end_time: str) -> int:
        """计算时间间隔（天数）"""
        try:
            if start_time in ["none", "创意中", "预热中"] or end_time in ["none", "创意中", "预热中"]:
                return 0
            
            start_dt = datetime.strptime(start_time[:19], '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_time[:19], '%Y-%m-%d %H:%M:%S')
            
            duration = (end_dt - start_dt).days
            return max(0, duration)
            
        except Exception as e:
            self._log("debug", f"时间间隔计算失败: {e}")
            return 0
