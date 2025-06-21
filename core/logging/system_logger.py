# -*- coding: utf-8 -*-
"""
系统日志记录器
提供统一的日志记录功能，支持文件写入和实时推送
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class SystemLogger:
    """系统日志记录器"""
    
    def __init__(self, log_service=None):
        self.log_service = log_service
        self.loggers = {}
        self._setup_loggers()
    
    def _setup_loggers(self):
        """设置日志记录器"""
        # 确保日志目录存在
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # 为每种日志类型创建记录器
        log_types = ['system', 'spider', 'webui']
        
        for log_type in log_types:
            # 创建日志目录
            log_type_dir = logs_dir / log_type
            log_type_dir.mkdir(exist_ok=True)
            
            # 创建记录器
            logger = logging.getLogger(f'modian_{log_type}')
            logger.setLevel(logging.DEBUG)
            
            # 避免重复添加处理器
            if not logger.handlers:
                # 文件处理器
                log_file = log_type_dir / f"{log_type}_{datetime.now().strftime('%Y%m%d')}.log"
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                
                # 格式化器
                formatter = logging.Formatter(
                    '[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                
                logger.addHandler(file_handler)
            
            self.loggers[log_type] = logger
    
    def log(self, log_type: str, level: str, message: str, source: str = "system"):
        """记录日志"""
        if log_type not in self.loggers:
            log_type = 'system'  # 默认使用系统日志
        
        logger = self.loggers[log_type]
        
        # 写入文件
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, message)
        
        # 实时推送
        if self.log_service:
            self.log_service.add_manual_log(log_type, level, message, source)
    
    def debug(self, message: str, log_type: str = 'system', source: str = "system"):
        """记录调试日志"""
        self.log(log_type, 'debug', message, source)
    
    def info(self, message: str, log_type: str = 'system', source: str = "system"):
        """记录信息日志"""
        self.log(log_type, 'info', message, source)
    
    def warning(self, message: str, log_type: str = 'system', source: str = "system"):
        """记录警告日志"""
        self.log(log_type, 'warning', message, source)
    
    def error(self, message: str, log_type: str = 'system', source: str = "system"):
        """记录错误日志"""
        self.log(log_type, 'error', message, source)
    
    def spider_log(self, level: str, message: str, source: str = "spider"):
        """记录爬虫日志"""
        self.log('spider', level, message, source)
    
    def webui_log(self, level: str, message: str, source: str = "webui"):
        """记录Web界面日志"""
        self.log('webui', level, message, source)
    
    def system_log(self, level: str, message: str, source: str = "system"):
        """记录系统日志"""
        self.log('system', level, message, source)


# 全局日志记录器实例
_system_logger: Optional[SystemLogger] = None


def get_system_logger() -> SystemLogger:
    """获取系统日志记录器实例"""
    global _system_logger
    if _system_logger is None:
        _system_logger = SystemLogger()
    return _system_logger


def init_system_logger(log_service=None):
    """初始化系统日志记录器"""
    global _system_logger
    _system_logger = SystemLogger(log_service)
    return _system_logger


# 便捷函数
def log_info(message: str, log_type: str = 'system', source: str = "system"):
    """记录信息日志"""
    get_system_logger().info(message, log_type, source)


def log_warning(message: str, log_type: str = 'system', source: str = "system"):
    """记录警告日志"""
    get_system_logger().warning(message, log_type, source)


def log_error(message: str, log_type: str = 'system', source: str = "system"):
    """记录错误日志"""
    get_system_logger().error(message, log_type, source)


def log_debug(message: str, log_type: str = 'system', source: str = "system"):
    """记录调试日志"""
    get_system_logger().debug(message, log_type, source)


def log_spider(level: str, message: str, source: str = "spider"):
    """记录爬虫日志"""
    get_system_logger().spider_log(level, message, source)


def log_webui(level: str, message: str, source: str = "webui"):
    """记录Web界面日志"""
    get_system_logger().webui_log(level, message, source)


def log_system(level: str, message: str, source: str = "system"):
    """记录系统日志"""
    get_system_logger().system_log(level, message, source)
