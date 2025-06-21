# -*- coding: utf-8 -*-
"""
API层模块
提供RESTful API接口和WebSocket处理
"""

from .routes import spider_routes, data_routes, task_routes, system_routes
from .middleware import error_handler, response_formatter
from .websocket import handlers as websocket_handlers

__all__ = [
    'spider_routes',
    'data_routes', 
    'task_routes',
    'system_routes',
    'error_handler',
    'response_formatter',
    'websocket_handlers'
]
