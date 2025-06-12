# -*- coding: utf-8 -*-
"""
优化版摩点众筹爬虫系统

主要特性:
- 模块化设计
- 自动化测试
- 性能监控
- 错误处理
- 数据验证
- 缓存机制
- 并发控制
"""

__version__ = "2.0.0"
__author__ = "Spider Team"

from .config import SpiderConfig, EnvConfig, RegexPatterns, CSSSelectors
from .core import SpiderCore
from .utils import NetworkUtils, DataUtils, CacheUtils
from .monitor import SpiderMonitor
from .validator import DataValidator
from .exporter import DataExporter

__all__ = [
    'SpiderConfig',
    'EnvConfig', 
    'RegexPatterns',
    'CSSSelectors',
    'SpiderCore',
    'NetworkUtils',
    'DataUtils',
    'CacheUtils',
    'SpiderMonitor',
    'DataValidator',
    'DataExporter'
]
