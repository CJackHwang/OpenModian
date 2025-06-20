# -*- coding: utf-8 -*-
"""
并发控制配置模块
管理爬虫系统的并发参数和资源限制
"""

import threading
import time
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ConcurrencyConfig:
    """并发控制配置"""
    
    # 数据库并发配置
    max_db_connections: int = 10
    db_connection_timeout: float = 30.0
    db_lock_timeout: float = 10.0
    
    # 文件操作并发配置
    max_file_operations: int = 5
    file_operation_timeout: float = 30.0
    
    # 网络请求并发配置
    max_concurrent_requests: int = 5
    request_rate_limit: float = 1.0  # 每秒最大请求数
    global_request_delay: tuple = (1.0, 3.0)  # 全局请求延迟范围
    
    # 任务调度并发配置
    max_concurrent_tasks: int = 3
    task_check_interval: float = 5.0
    
    # 资源监控配置
    memory_threshold_mb: int = 1024  # 内存使用阈值（MB）
    cpu_threshold_percent: float = 80.0  # CPU使用阈值（%）
    
    # 错误处理配置
    max_consecutive_errors: int = 5
    error_backoff_factor: float = 2.0
    max_retry_delay: float = 60.0


class GlobalRateLimiter:
    """全局请求频率限制器"""
    
    def __init__(self, max_requests_per_second: float = 1.0):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
        self._lock = threading.Lock()
    
    def acquire(self):
        """获取请求许可"""
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()


class ResourceMonitor:
    """资源使用监控器"""
    
    def __init__(self, config: ConcurrencyConfig):
        self.config = config
        self._stats = {
            'active_connections': 0,
            'active_file_operations': 0,
            'active_requests': 0,
            'total_requests': 0,
            'error_count': 0
        }
        self._lock = threading.Lock()
    
    def increment_counter(self, counter_name: str):
        """增加计数器"""
        with self._lock:
            if counter_name in self._stats:
                self._stats[counter_name] += 1
    
    def decrement_counter(self, counter_name: str):
        """减少计数器"""
        with self._lock:
            if counter_name in self._stats and self._stats[counter_name] > 0:
                self._stats[counter_name] -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return self._stats.copy()
    
    def is_resource_available(self, resource_type: str) -> bool:
        """检查资源是否可用"""
        with self._lock:
            if resource_type == 'db_connection':
                return self._stats['active_connections'] < self.config.max_db_connections
            elif resource_type == 'file_operation':
                return self._stats['active_file_operations'] < self.config.max_file_operations
            elif resource_type == 'request':
                return self._stats['active_requests'] < self.config.max_concurrent_requests
            return True


class ConcurrencyManager:
    """并发控制管理器"""
    
    def __init__(self, config: ConcurrencyConfig = None):
        self.config = config or ConcurrencyConfig()
        self.rate_limiter = GlobalRateLimiter(self.config.request_rate_limit)
        self.resource_monitor = ResourceMonitor(self.config)
        
        # 全局锁
        self.db_lock = threading.RLock()
        self.file_lock = threading.RLock()
        self.task_lock = threading.RLock()
    
    def acquire_db_resource(self):
        """获取数据库资源"""
        if not self.resource_monitor.is_resource_available('db_connection'):
            raise RuntimeError("数据库连接数已达上限")
        
        self.resource_monitor.increment_counter('active_connections')
        return self.db_lock
    
    def release_db_resource(self):
        """释放数据库资源"""
        self.resource_monitor.decrement_counter('active_connections')
    
    def acquire_file_resource(self):
        """获取文件操作资源"""
        if not self.resource_monitor.is_resource_available('file_operation'):
            raise RuntimeError("文件操作数已达上限")
        
        self.resource_monitor.increment_counter('active_file_operations')
        return self.file_lock
    
    def release_file_resource(self):
        """释放文件操作资源"""
        self.resource_monitor.decrement_counter('active_file_operations')
    
    def acquire_request_resource(self):
        """获取网络请求资源"""
        if not self.resource_monitor.is_resource_available('request'):
            raise RuntimeError("网络请求数已达上限")
        
        self.rate_limiter.acquire()
        self.resource_monitor.increment_counter('active_requests')
        self.resource_monitor.increment_counter('total_requests')
    
    def release_request_resource(self):
        """释放网络请求资源"""
        self.resource_monitor.decrement_counter('active_requests')
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        stats = self.resource_monitor.get_stats()
        stats.update({
            'config': {
                'max_db_connections': self.config.max_db_connections,
                'max_file_operations': self.config.max_file_operations,
                'max_concurrent_requests': self.config.max_concurrent_requests,
                'request_rate_limit': self.config.request_rate_limit
            }
        })
        return stats


# 全局并发管理器实例
_global_concurrency_manager = None
_manager_lock = threading.Lock()


def get_concurrency_manager() -> ConcurrencyManager:
    """获取全局并发管理器实例（单例模式）"""
    global _global_concurrency_manager
    
    if _global_concurrency_manager is None:
        with _manager_lock:
            if _global_concurrency_manager is None:
                _global_concurrency_manager = ConcurrencyManager()
    
    return _global_concurrency_manager


def reset_concurrency_manager(config: ConcurrencyConfig = None):
    """重置并发管理器（主要用于测试）"""
    global _global_concurrency_manager
    
    with _manager_lock:
        _global_concurrency_manager = ConcurrencyManager(config)
