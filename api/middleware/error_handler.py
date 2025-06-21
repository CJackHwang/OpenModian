# -*- coding: utf-8 -*-
"""
统一错误处理中间件
提供标准化的错误响应格式
"""

from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from core.exceptions import SpiderException, TaskException, ConfigException
import traceback


def setup_error_handlers(app):
    """设置全局错误处理器"""
    
    @app.errorhandler(SpiderException)
    def handle_spider_exception(error):
        """处理爬虫系统异常"""
        return jsonify({
            'success': False,
            'error_code': error.error_code,
            'message': error.message,
            'details': error.details
        }), 400
    
    @app.errorhandler(TaskException)
    def handle_task_exception(error):
        """处理任务异常"""
        return jsonify({
            'success': False,
            'error_code': error.error_code,
            'message': error.message,
            'task_id': error.task_id,
            'details': error.details
        }), 400
    
    @app.errorhandler(ConfigException)
    def handle_config_exception(error):
        """处理配置异常"""
        return jsonify({
            'success': False,
            'error_code': error.error_code,
            'message': error.message,
            'config_key': error.config_key,
            'details': error.details
        }), 400
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理HTTP异常"""
        return jsonify({
            'success': False,
            'error_code': 'HTTP_ERROR',
            'message': error.description,
            'status_code': error.code
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """处理通用异常"""
        # 在开发环境下显示详细错误信息
        if current_app.debug:
            error_details = {
                'type': type(error).__name__,
                'traceback': traceback.format_exc()
            }
        else:
            error_details = {}
        
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': '服务器内部错误',
            'details': error_details
        }), 500


def handle_spider_exception(func):
    """装饰器：处理爬虫异常"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SpiderException as e:
            return jsonify({
                'success': False,
                'error_code': e.error_code,
                'message': e.message,
                'details': e.details
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error_code': 'INTERNAL_ERROR',
                'message': f'内部错误: {str(e)}'
            }), 500
    
    wrapper.__name__ = func.__name__
    return wrapper
