# -*- coding: utf-8 -*-
"""
数据处理器
负责数据清洗、转换、编码处理等功能
"""

import re
import json
from typing import Dict, Any
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import DataUtils, ParserUtils


class DataProcessor:
    """数据处理器 - 负责数据清洗和转换"""

    def __init__(self, config: SpiderConfig, data_utils: DataUtils, web_monitor=None):
        self.config = config
        self.data_utils = data_utils
        self.web_monitor = web_monitor

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def extract_js_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """从JavaScript中提取项目数据"""
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
                if 'start_time' in script_text and 'end_time' in script_text:
                    # 查找时间戳模式
                    start_match = re.search(r'"start_time"\s*:\s*(\d+)', script_text)
                    end_match = re.search(r'"end_time"\s*:\s*(\d+)', script_text)
                    
                    if start_match:
                        timestamp = int(start_match.group(1))
                        if timestamp > 1000000000:  # 合理的时间戳范围
                            js_data["start_time"] = self.data_utils.format_timestamp(timestamp)
                    
                    if end_match:
                        timestamp = int(end_match.group(1))
                        if timestamp > 1000000000:
                            js_data["end_time"] = self.data_utils.format_timestamp(timestamp)

        except Exception as e:
            self._log("debug", f"JavaScript数据提取失败: {e}")

        return js_data

    def validate_extracted_data(self, money: str, percent: str, goal_money: str, sponsor_num: str):
        """验证提取的数据合理性（不进行反推计算）"""
        try:
            # 验证金额数据
            if money != "0":
                money_val = float(money)
                if money_val < 0:
                    self._log("warning", f"已筹金额异常: {money}")
                elif money_val > 10000000:  # 1000万
                    self._log("warning", f"已筹金额过大: {money}")

            if goal_money != "0":
                goal_val = float(goal_money)
                if goal_val < 0:
                    self._log("warning", f"目标金额异常: {goal_money}")
                elif goal_val > 50000000:  # 5000万
                    self._log("warning", f"目标金额过大: {goal_money}")

            # 验证百分比数据
            if percent != "0":
                percent_val = float(percent)
                if percent_val < 0:
                    self._log("warning", f"完成百分比异常: {percent}%")
                elif percent_val > 10000:  # 100倍
                    self._log("warning", f"完成百分比过大: {percent}%")
                else:
                    self._log("info", f"百分比数据正常: {percent}%")

            # 验证支持者数量
            if sponsor_num != "0":
                sponsor_val = int(sponsor_num)
                if sponsor_val < 0:
                    self._log("warning", f"支持者数量异常: {sponsor_num}")
                elif sponsor_val > 100000:  # 10万人
                    self._log("warning", f"支持者数量过大: {sponsor_num}")

        except ValueError as e:
            self._log("warning", f"数据验证时类型转换失败: {e}")
        except Exception as e:
            self._log("warning", f"数据验证失败: {e}")

    def clean_reward_text(self, text: str) -> str:
        """清理回报文本"""
        if not text:
            return "none"
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()
        
        # 移除特殊字符
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff.,，。！？]', '', cleaned)
        
        # 限制长度
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."
            
        return cleaned if cleaned else "none"

    def format_money(self, money_str: str) -> str:
        """格式化金额字符串"""
        if not money_str:
            return "0"
        
        # 移除非数字字符（保留小数点）
        cleaned = re.sub(r'[^\d.]', '', str(money_str))
        
        try:
            # 转换为浮点数再转回字符串，确保格式一致
            amount = float(cleaned) if cleaned else 0
            return str(int(amount)) if amount.is_integer() else str(amount)
        except ValueError:
            return "0"

    def extract_number(self, text: str) -> str:
        """从文本中提取数字"""
        if not text:
            return "0"
        
        # 查找数字模式
        numbers = re.findall(r'\d+', str(text))
        if numbers:
            # 返回最大的数字（通常是我们想要的）
            return str(max(int(num) for num in numbers))
        
        return "0"

    def extract_percentage(self, text: str) -> str:
        """从文本中提取百分比"""
        if not text:
            return "0"
        
        # 查找百分比模式
        match = re.search(r'(\d+(?:\.\d+)?)%', str(text))
        if match:
            return match.group(1)
        
        # 如果没有%符号，尝试提取数字
        numbers = re.findall(r'\d+(?:\.\d+)?', str(text))
        if numbers:
            return numbers[0]
        
        return "0"

    def fix_encoding(self, text: str) -> str:
        """修复编码问题"""
        if not text:
            return "none"
        
        try:
            # 处理常见的编码问题
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # 移除控制字符
            text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', str(text))
            
            # 标准化空白字符
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text if text else "none"
            
        except Exception as e:
            self._log("warning", f"编码修复失败: {e}")
            return "none"

    def normalize_category(self, category: str) -> str:
        """标准化分类名称"""
        if not category or category == "none":
            return "其他"
        
        # 分类映射表
        category_mapping = {
            "game": "游戏",
            "tech": "科技", 
            "design": "设计",
            "art": "艺术",
            "music": "音乐",
            "film": "影视",
            "book": "出版",
            "food": "美食",
            "fashion": "时尚",
            "sports": "体育",
            "travel": "旅行",
            "education": "教育",
            "charity": "公益"
        }
        
        # 尝试映射
        category_lower = category.lower()
        if category_lower in category_mapping:
            return category_mapping[category_lower]
        
        # 如果是中文分类，直接返回
        if re.search(r'[\u4e00-\u9fff]', category):
            return category
        
        return "其他"
