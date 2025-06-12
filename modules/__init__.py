# AI分析系统核心模块包
"""
桌游市场调研AI分析系统核心模块

包含以下模块：
- config_manager: 配置管理
- data_processor: 数据处理
- ai_analyzer: AI分析
- report_generator: 报告生成
"""

__version__ = "1.0.0"
__author__ = "AI分析系统"

from .config_manager import ConfigManager
from .data_processor import DataProcessor
from .ai_analyzer import AIAnalyzer
from .report_generator import ReportGenerator

__all__ = [
    'ConfigManager',
    'DataProcessor', 
    'AIAnalyzer',
    'ReportGenerator'
]
