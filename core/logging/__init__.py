# -*- coding: utf-8 -*-
"""
日志记录模块
提供统一的日志记录功能
"""

from .system_logger import (
    SystemLogger,
    get_system_logger,
    init_system_logger,
    log_info,
    log_warning,
    log_error,
    log_debug,
    log_spider,
    log_webui,
    log_system
)

__all__ = [
    'SystemLogger',
    'get_system_logger',
    'init_system_logger',
    'log_info',
    'log_warning',
    'log_error',
    'log_debug',
    'log_spider',
    'log_webui',
    'log_system'
]
