# -*- coding: utf-8 -*-
"""
API路由模块
提供各种API路由的注册和管理
"""

from .spider_routes import register_spider_routes
from .data_routes import register_data_routes
from .task_routes import register_task_routes
from .system_routes import register_system_routes
from .settings_routes import register_settings_routes

__all__ = [
    'register_spider_routes',
    'register_data_routes',
    'register_task_routes',
    'register_system_routes',
    'register_settings_routes'
]
