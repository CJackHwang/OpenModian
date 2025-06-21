# -*- coding: utf-8 -*-
"""
监控器模块
提供Web界面和定时任务的监控功能
"""

from .web_monitor import WebSpiderMonitor
from .scheduled_monitor import ScheduledTaskMonitor

__all__ = [
    'WebSpiderMonitor',
    'ScheduledTaskMonitor'
]
