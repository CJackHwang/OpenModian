# -*- coding: utf-8 -*-
"""
智能错误处理和恢复机制
提供自动重试、错误分类、恢复策略等功能
"""

import time
import threading
import traceback
import json
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import functools
import random
from pathlib import Path


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"           # 轻微错误，可忽略
    MEDIUM = "medium"     # 中等错误，需要重试
    HIGH = "high"         # 严重错误，需要人工干预
    CRITICAL = "critical" # 致命错误，停止系统


class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"           # 网络相关错误
    PARSING = "parsing"           # 解析错误
    DATABASE = "database"         # 数据库错误
    FILE_IO = "file_io"          # 文件I/O错误
    VALIDATION = "validation"     # 数据验证错误
    RATE_LIMIT = "rate_limit"    # 频率限制错误
    AUTHENTICATION = "auth"       # 认证错误
    UNKNOWN = "unknown"          # 未知错误


@dataclass
class ErrorInfo:
    """错误信息"""
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: float
    traceback_info: str
    context: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    resolved: bool = False


class ErrorClassifier:
    """错误分类器"""
    
    def __init__(self):
        # 错误模式匹配规则
        self.error_patterns = {
            ErrorCategory.NETWORK: [
                'ConnectionError', 'Timeout', 'HTTPError', 'URLError',
                'ConnectTimeout', 'ReadTimeout', 'SSLError', 'ProxyError'
            ],
            ErrorCategory.PARSING: [
                'JSONDecodeError', 'XMLSyntaxError', 'ParserError',
                'UnicodeDecodeError', 'ValueError'
            ],
            ErrorCategory.DATABASE: [
                'DatabaseError', 'IntegrityError', 'OperationalError',
                'SQLITE_BUSY', 'SQLITE_LOCKED'
            ],
            ErrorCategory.FILE_IO: [
                'FileNotFoundError', 'PermissionError', 'IOError',
                'OSError', 'DiskSpaceError'
            ],
            ErrorCategory.RATE_LIMIT: [
                '429', 'Too Many Requests', 'Rate limit exceeded',
                'Quota exceeded'
            ],
            ErrorCategory.AUTHENTICATION: [
                '401', '403', 'Unauthorized', 'Forbidden',
                'Authentication failed'
            ]
        }
        
        # 严重程度规则
        self.severity_rules = {
            ErrorCategory.NETWORK: ErrorSeverity.MEDIUM,
            ErrorCategory.PARSING: ErrorSeverity.LOW,
            ErrorCategory.DATABASE: ErrorSeverity.HIGH,
            ErrorCategory.FILE_IO: ErrorSeverity.MEDIUM,
            ErrorCategory.RATE_LIMIT: ErrorSeverity.MEDIUM,
            ErrorCategory.AUTHENTICATION: ErrorSeverity.HIGH,
            ErrorCategory.VALIDATION: ErrorSeverity.LOW,
            ErrorCategory.UNKNOWN: ErrorSeverity.MEDIUM
        }
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """分类错误"""
        error_type = type(error).__name__
        error_message = str(error)
        traceback_info = traceback.format_exc()
        
        # 确定错误分类
        category = self._determine_category(error_type, error_message)
        
        # 确定严重程度
        severity = self._determine_severity(category, error_message)
        
        return ErrorInfo(
            error_type=error_type,
            error_message=error_message,
            category=category,
            severity=severity,
            timestamp=time.time(),
            traceback_info=traceback_info,
            context=context or {}
        )
    
    def _determine_category(self, error_type: str, error_message: str) -> ErrorCategory:
        """确定错误分类"""
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern in error_type or pattern in error_message:
                    return category
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, category: ErrorCategory, error_message: str) -> ErrorSeverity:
        """确定错误严重程度"""
        # 特殊情况处理
        if 'CRITICAL' in error_message.upper():
            return ErrorSeverity.CRITICAL
        
        if 'FATAL' in error_message.upper():
            return ErrorSeverity.CRITICAL
        
        # 根据分类确定严重程度
        return self.severity_rules.get(category, ErrorSeverity.MEDIUM)


class RetryStrategy:
    """重试策略"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
    
    def should_retry(self, error_info: ErrorInfo) -> bool:
        """判断是否应该重试"""
        # 致命错误不重试
        if error_info.severity == ErrorSeverity.CRITICAL:
            return False
        
        # 超过最大重试次数
        if error_info.retry_count >= self.max_retries:
            return False
        
        # 根据错误类型决定是否重试
        retry_categories = {
            ErrorCategory.NETWORK,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.PARSING
        }
        
        return error_info.category in retry_categories
    
    def get_delay(self, retry_count: int) -> float:
        """获取重试延迟时间"""
        delay = self.base_delay * (self.backoff_factor ** retry_count)
        
        # 添加随机抖动，避免雷群效应
        jitter = random.uniform(0.1, 0.3) * delay
        delay += jitter
        
        return min(delay, self.max_delay)


class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self, config=None):
        self.config = config
        self.classifier = ErrorClassifier()
        self.retry_strategy = RetryStrategy()
        
        # 错误历史记录
        self.error_history: List[ErrorInfo] = []
        self.max_history_size = 1000
        
        # 恢复策略注册表
        self.recovery_strategies: Dict[ErrorCategory, List[Callable]] = {
            ErrorCategory.NETWORK: [self._recover_network_error],
            ErrorCategory.DATABASE: [self._recover_database_error],
            ErrorCategory.RATE_LIMIT: [self._recover_rate_limit_error],
            ErrorCategory.FILE_IO: [self._recover_file_io_error]
        }
        
        # 统计信息
        self.stats = {
            'total_errors': 0,
            'recovered_errors': 0,
            'failed_recoveries': 0,
            'by_category': {},
            'by_severity': {}
        }
        
        self._lock = threading.RLock()
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    operation: Callable = None) -> Any:
        """处理错误"""
        with self._lock:
            # 分类错误
            error_info = self.classifier.classify_error(error, context)
            
            # 记录错误
            self._record_error(error_info)
            
            # 尝试恢复
            if self.retry_strategy.should_retry(error_info):
                return self._attempt_recovery(error_info, operation)
            else:
                print(f"❌ 错误无法恢复: {error_info.error_message}")
                return None
    
    def _record_error(self, error_info: ErrorInfo):
        """记录错误信息"""
        self.error_history.append(error_info)
        
        # 限制历史记录大小
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
        
        # 更新统计信息
        self.stats['total_errors'] += 1
        
        category_key = error_info.category.value
        self.stats['by_category'][category_key] = self.stats['by_category'].get(category_key, 0) + 1
        
        severity_key = error_info.severity.value
        self.stats['by_severity'][severity_key] = self.stats['by_severity'].get(severity_key, 0) + 1
        
        print(f"🔍 错误分类: {error_info.category.value} | 严重程度: {error_info.severity.value}")
        print(f"🔍 错误信息: {error_info.error_message}")
    
    def _attempt_recovery(self, error_info: ErrorInfo, operation: Callable = None) -> Any:
        """尝试错误恢复"""
        error_info.retry_count += 1
        
        print(f"🔄 尝试恢复错误 (第{error_info.retry_count}次): {error_info.error_message}")
        
        # 执行恢复策略
        recovery_strategies = self.recovery_strategies.get(error_info.category, [])
        
        for strategy in recovery_strategies:
            try:
                strategy(error_info)
                print(f"✅ 恢复策略执行成功: {strategy.__name__}")
            except Exception as e:
                print(f"⚠️ 恢复策略执行失败: {strategy.__name__} - {e}")
        
        # 等待重试延迟
        delay = self.retry_strategy.get_delay(error_info.retry_count - 1)
        print(f"⏳ 等待 {delay:.1f} 秒后重试...")
        time.sleep(delay)
        
        # 重新执行操作
        if operation:
            try:
                result = operation()
                error_info.resolved = True
                self.stats['recovered_errors'] += 1
                print(f"✅ 错误恢复成功")
                return result
            except Exception as new_error:
                print(f"❌ 重试失败: {new_error}")
                return self.handle_error(new_error, error_info.context, operation)
        
        return None
    
    def _recover_network_error(self, error_info: ErrorInfo):
        """网络错误恢复策略"""
        print("🌐 执行网络错误恢复策略...")
        
        # 清理网络连接
        try:
            import requests
            # 关闭所有连接
            requests.Session().close()
        except:
            pass
        
        # 增加延迟
        time.sleep(2)
    
    def _recover_database_error(self, error_info: ErrorInfo):
        """数据库错误恢复策略"""
        print("🗄️ 执行数据库错误恢复策略...")
        
        # 等待数据库锁释放
        if 'SQLITE_BUSY' in error_info.error_message:
            time.sleep(5)
        
        # 强制垃圾回收
        import gc
        gc.collect()
    
    def _recover_rate_limit_error(self, error_info: ErrorInfo):
        """频率限制错误恢复策略"""
        print("⏱️ 执行频率限制错误恢复策略...")
        
        # 增加较长的等待时间
        wait_time = 30 + random.uniform(10, 30)  # 30-60秒
        print(f"⏱️ 频率限制，等待 {wait_time:.1f} 秒...")
        time.sleep(wait_time)
    
    def _recover_file_io_error(self, error_info: ErrorInfo):
        """文件I/O错误恢复策略"""
        print("📁 执行文件I/O错误恢复策略...")
        
        # 检查磁盘空间
        try:
            import shutil
            free_space = shutil.disk_usage('.').free / (1024**3)  # GB
            if free_space < 1:  # 小于1GB
                print(f"⚠️ 磁盘空间不足: {free_space:.1f}GB")
        except:
            pass
        
        # 创建目录（如果不存在）
        if 'FileNotFoundError' in error_info.error_type:
            context = error_info.context
            if 'file_path' in context:
                file_path = Path(context['file_path'])
                file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_error_report(self) -> Dict[str, Any]:
        """获取错误报告"""
        with self._lock:
            recent_errors = self.error_history[-50:]  # 最近50个错误
            
            return {
                'total_errors': self.stats['total_errors'],
                'recovered_errors': self.stats['recovered_errors'],
                'failed_recoveries': self.stats['failed_recoveries'],
                'recovery_rate': (
                    self.stats['recovered_errors'] / self.stats['total_errors'] * 100
                    if self.stats['total_errors'] > 0 else 0
                ),
                'by_category': self.stats['by_category'],
                'by_severity': self.stats['by_severity'],
                'recent_errors': [
                    {
                        'type': err.error_type,
                        'message': err.error_message,
                        'category': err.category.value,
                        'severity': err.severity.value,
                        'timestamp': err.timestamp,
                        'retry_count': err.retry_count,
                        'resolved': err.resolved
                    }
                    for err in recent_errors
                ]
            }
    
    def clear_error_history(self):
        """清空错误历史"""
        with self._lock:
            self.error_history.clear()
            self.stats = {
                'total_errors': 0,
                'recovered_errors': 0,
                'failed_recoveries': 0,
                'by_category': {},
                'by_severity': {}
            }
            print("🧹 错误历史已清空")


def error_handler(max_retries: int = 3, recovery_manager: ErrorRecoveryManager = None):
    """错误处理装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            manager = recovery_manager or ErrorRecoveryManager()
            
            def operation():
                return func(*args, **kwargs)
            
            try:
                return operation()
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],  # 限制长度
                    'kwargs': str(kwargs)[:200]
                }
                return manager.handle_error(e, context, operation)
        
        return wrapper
    return decorator


# 全局错误恢复管理器
_global_error_manager = None
_manager_lock = threading.Lock()


def get_error_recovery_manager() -> ErrorRecoveryManager:
    """获取全局错误恢复管理器实例（单例模式）"""
    global _global_error_manager
    
    if _global_error_manager is None:
        with _manager_lock:
            if _global_error_manager is None:
                _global_error_manager = ErrorRecoveryManager()
    
    return _global_error_manager
