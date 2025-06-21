# -*- coding: utf-8 -*-
"""
响应格式化中间件
提供统一的API响应格式
"""

from flask import jsonify
from datetime import datetime
from typing import Any, Dict, Optional, List


def success_response(data: Any = None, message: str = "操作成功", 
                    meta: Optional[Dict] = None) -> Dict:
    """成功响应格式"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if meta:
        response['meta'] = meta
    
    return jsonify(response)


def error_response(message: str, error_code: str = "ERROR", 
                  details: Optional[Dict] = None, status_code: int = 400) -> tuple:
    """错误响应格式"""
    response = {
        'success': False,
        'error_code': error_code,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


def paginated_response(items: List[Any], page: int, per_page: int, 
                      total: int, message: str = "获取成功") -> Dict:
    """分页响应格式"""
    total_pages = (total + per_page - 1) // per_page
    
    return success_response(
        data=items,
        message=message,
        meta={
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    )


def task_response(task_id: str, status: str = "created", 
                 message: str = "任务已创建", **kwargs) -> Dict:
    """任务响应格式"""
    data = {
        'task_id': task_id,
        'status': status,
        **kwargs
    }
    
    return success_response(data=data, message=message)


def validation_error_response(errors: Dict[str, List[str]]) -> tuple:
    """验证错误响应格式"""
    return error_response(
        message="数据验证失败",
        error_code="VALIDATION_ERROR",
        details={'validation_errors': errors},
        status_code=422
    )
