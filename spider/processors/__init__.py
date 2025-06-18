# -*- coding: utf-8 -*-
"""
数据处理器模块 - 简化版
专注于API数据的基础处理和验证
"""

from .data_processor import DataProcessor
from .validation_processor import ValidationProcessor

__all__ = [
    'DataProcessor',      # 简化版数据处理器
    'ValidationProcessor' # 简化版验证处理器
]

# 已移除的处理器（API时代不再需要）：
# - StatusProcessor (API直接提供准确状态)
# - TimeProcessor (API直接提供准确时间)
