# -*- coding: utf-8 -*-
"""
数据处理器 - 简化版
专注于API数据的基础清理和格式化
"""

import re
from typing import Dict, Any

from ..config import SpiderConfig


class DataProcessor:
    """数据处理器 - 简化版，专注于API数据处理"""

    def __init__(self, config: SpiderConfig, data_utils=None, web_monitor=None):
        self.config = config
        self.web_monitor = web_monitor

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    # ========== 已弃用的方法 ==========
    # 以下方法在API时代已不需要，API数据准确可靠

    def extract_js_data(self, soup) -> Dict[str, Any]:
        """已弃用：JS数据提取，现在使用API获取"""
        return {}

    def validate_extracted_data(self, money: str, percent: str, goal_money: str, sponsor_num: str):
        """已弃用：数据验证，API数据无需验证"""
        pass

    def format_money(self, money_text: str) -> str:
        """已弃用：金额格式化，API数据已格式化"""
        return money_text

    def extract_number(self, text: str) -> str:
        """已弃用：数字提取，API数据已是数字"""
        return text

    def extract_percentage(self, text: str) -> str:
        """已弃用：百分比提取，API数据已是百分比"""
        return text

    # ========== 保留的有用方法 ==========
    # 这些方法在API时代仍然有用

    def clean_reward_text(self, text: str) -> str:
        """清理回报文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,，。！？:：；;()（）\[\]【】-]', '', text)
        
        return text.strip()

    def fix_encoding(self, text: str) -> str:
        """修复编码问题"""
        if not text:
            return ""
        
        try:
            # 处理常见的编码问题
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # 移除控制字符
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
            
            return text.strip()
            
        except Exception as e:
            self._log("debug", f"编码修复失败: {e}")
            return str(text)

    def normalize_text(self, text: str) -> str:
        """标准化文本格式"""
        if not text:
            return ""
        
        # 修复编码
        text = self.fix_encoding(text)
        
        # 清理文本
        text = self.clean_reward_text(text)
        
        # 限制长度
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text

    def format_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化API数据"""
        if not api_data:
            return {}
        
        formatted_data = {}
        
        for key, value in api_data.items():
            if isinstance(value, str):
                # 清理字符串值
                formatted_data[key] = self.normalize_text(value)
            elif isinstance(value, (int, float)):
                # 保持数字值
                formatted_data[key] = value
            elif isinstance(value, list):
                # 处理列表值（如回报列表）
                if key == "rewards_data":
                    formatted_data[key] = self._format_rewards_list(value)
                else:
                    formatted_data[key] = value
            else:
                # 其他类型直接保留
                formatted_data[key] = value
        
        return formatted_data

    def _format_rewards_list(self, rewards: list) -> list:
        """格式化回报列表"""
        if not rewards:
            return []
        
        formatted_rewards = []
        
        for reward in rewards:
            if isinstance(reward, dict):
                formatted_reward = {}
                for key, value in reward.items():
                    if isinstance(value, str):
                        formatted_reward[key] = self.normalize_text(value)
                    else:
                        formatted_reward[key] = value
                formatted_rewards.append(formatted_reward)
            else:
                formatted_rewards.append(reward)
        
        return formatted_rewards
