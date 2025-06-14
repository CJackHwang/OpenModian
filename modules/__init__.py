# 摩点爬虫管理系统核心模块包
"""
摩点爬虫管理系统核心模块

包含以下模块：
- config_manager: 配置管理
- data_processor: 数据处理
"""

__version__ = "2.0.0"
__author__ = "摩点爬虫管理系统"

from .config_manager import ConfigManager
from .data_processor import DataProcessor

__all__ = [
    'ConfigManager',
    'DataProcessor'
]
