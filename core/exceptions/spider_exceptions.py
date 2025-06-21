# -*- coding: utf-8 -*-
"""
爬虫系统异常定义
提供统一的异常处理机制
"""


class SpiderException(Exception):
    """爬虫系统基础异常"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'SPIDER_ERROR'
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }


class TaskException(SpiderException):
    """任务相关异常"""
    
    def __init__(self, message: str, task_id: str = None, **kwargs):
        super().__init__(message, error_code='TASK_ERROR', **kwargs)
        self.task_id = task_id
        if task_id:
            self.details['task_id'] = task_id


class ConfigException(SpiderException):
    """配置相关异常"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, error_code='CONFIG_ERROR', **kwargs)
        self.config_key = config_key
        if config_key:
            self.details['config_key'] = config_key


class ValidationException(SpiderException):
    """数据验证异常"""
    
    def __init__(self, message: str, field_name: str = None, **kwargs):
        super().__init__(message, error_code='VALIDATION_ERROR', **kwargs)
        self.field_name = field_name
        if field_name:
            self.details['field_name'] = field_name


class NetworkException(SpiderException):
    """网络请求异常"""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, **kwargs):
        super().__init__(message, error_code='NETWORK_ERROR', **kwargs)
        self.url = url
        self.status_code = status_code
        if url:
            self.details['url'] = url
        if status_code:
            self.details['status_code'] = status_code
