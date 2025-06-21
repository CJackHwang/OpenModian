# -*- coding: utf-8 -*-
"""
异常定义模块
提供统一的异常处理
"""

from .spider_exceptions import SpiderException, TaskException, ConfigException

__all__ = [
    'SpiderException',
    'TaskException', 
    'ConfigException'
]
