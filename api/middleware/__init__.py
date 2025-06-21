# -*- coding: utf-8 -*-
"""
中间件模块
提供统一的错误处理和响应格式化
"""

from .error_handler import setup_error_handlers, handle_spider_exception
from .response_formatter import success_response, error_response, paginated_response

__all__ = [
    'setup_error_handlers',
    'handle_spider_exception',
    'success_response',
    'error_response', 
    'paginated_response'
]
