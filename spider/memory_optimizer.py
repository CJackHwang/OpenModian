# -*- coding: utf-8 -*-
"""
内存优化模块
管理爬虫系统的内存使用，防止内存泄漏和OOM错误
"""

import gc
import psutil
import threading
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import weakref
import sys


@dataclass
class MemoryStats:
    """内存统计信息"""
    total_memory_mb: float = 0.0
    used_memory_mb: float = 0.0
    available_memory_mb: float = 0.0
    memory_percent: float = 0.0
    process_memory_mb: float = 0.0
    gc_collections: int = 0
    objects_count: int = 0


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self, memory_threshold_mb: int = 1024, gc_threshold: float = 80.0):
        self.memory_threshold_mb = memory_threshold_mb
        self.gc_threshold = gc_threshold  # 内存使用率阈值（%）
        
        # 监控状态
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock()
        
        # 统计信息
        self.stats = MemoryStats()
        self.memory_history = []
        
        # 对象引用跟踪
        self._tracked_objects = weakref.WeakSet()
        
        # 配置垃圾回收
        self._configure_gc()
    
    def _configure_gc(self):
        """配置垃圾回收器"""
        # 设置更激进的垃圾回收阈值
        gc.set_threshold(700, 10, 10)  # 默认是 (700, 10, 10)
        
        # 启用垃圾回收调试（开发环境）
        if __debug__:
            gc.set_debug(gc.DEBUG_STATS)
    
    def start_monitoring(self, interval: float = 30.0):
        """开始内存监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        print(f"🧠 内存监控已启动，检查间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止内存监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("🧠 内存监控已停止")
    
    def _monitor_loop(self, interval: float):
        """内存监控循环"""
        while self._monitoring:
            try:
                self._update_memory_stats()
                self._check_memory_pressure()
                self._cleanup_if_needed()
                time.sleep(interval)
            except Exception as e:
                print(f"❌ 内存监控错误: {e}")
                time.sleep(interval)
    
    def _update_memory_stats(self):
        """更新内存统计信息"""
        try:
            # 系统内存信息
            memory = psutil.virtual_memory()
            self.stats.total_memory_mb = memory.total / 1024 / 1024
            self.stats.used_memory_mb = memory.used / 1024 / 1024
            self.stats.available_memory_mb = memory.available / 1024 / 1024
            self.stats.memory_percent = memory.percent
            
            # 当前进程内存信息
            process = psutil.Process()
            process_memory = process.memory_info()
            self.stats.process_memory_mb = process_memory.rss / 1024 / 1024
            
            # 垃圾回收统计
            self.stats.gc_collections = sum(gc.get_count())
            self.stats.objects_count = len(gc.get_objects())
            
            # 记录历史数据（保留最近100个数据点）
            with self._lock:
                self.memory_history.append({
                    'timestamp': time.time(),
                    'memory_percent': self.stats.memory_percent,
                    'process_memory_mb': self.stats.process_memory_mb
                })
                
                if len(self.memory_history) > 100:
                    self.memory_history.pop(0)
                    
        except Exception as e:
            print(f"❌ 更新内存统计失败: {e}")
    
    def _check_memory_pressure(self):
        """检查内存压力"""
        if self.stats.memory_percent > self.gc_threshold:
            print(f"⚠️ 内存使用率过高: {self.stats.memory_percent:.1f}%")
            self._force_garbage_collection()
        
        if self.stats.process_memory_mb > self.memory_threshold_mb:
            print(f"⚠️ 进程内存使用过高: {self.stats.process_memory_mb:.1f}MB")
            self._aggressive_cleanup()
    
    def _cleanup_if_needed(self):
        """根据需要进行清理"""
        # 定期垃圾回收
        if self.stats.objects_count > 50000:  # 对象数量阈值
            self._force_garbage_collection()
    
    def _force_garbage_collection(self):
        """强制垃圾回收"""
        print("🗑️ 执行垃圾回收...")
        collected = gc.collect()
        print(f"🗑️ 垃圾回收完成，清理了 {collected} 个对象")
    
    def _aggressive_cleanup(self):
        """激进清理"""
        print("🧹 执行激进内存清理...")
        
        # 强制垃圾回收所有代
        for generation in range(3):
            collected = gc.collect(generation)
            print(f"🗑️ 第{generation}代垃圾回收: {collected} 个对象")
        
        # 清理缓存
        self._clear_caches()
        
        # 压缩内存（如果可能）
        try:
            import ctypes
            if sys.platform == 'win32':
                ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
        except:
            pass
    
    def _clear_caches(self):
        """清理各种缓存"""
        # 清理正则表达式缓存
        import re
        re.purge()
        
        # 清理导入缓存
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
    
    def track_object(self, obj):
        """跟踪对象（用于调试内存泄漏）"""
        self._tracked_objects.add(obj)
    
    def get_memory_report(self) -> Dict[str, Any]:
        """获取内存报告"""
        return {
            'current_stats': {
                'total_memory_mb': self.stats.total_memory_mb,
                'used_memory_mb': self.stats.used_memory_mb,
                'available_memory_mb': self.stats.available_memory_mb,
                'memory_percent': self.stats.memory_percent,
                'process_memory_mb': self.stats.process_memory_mb,
                'gc_collections': self.stats.gc_collections,
                'objects_count': self.stats.objects_count
            },
            'tracked_objects': len(self._tracked_objects),
            'memory_history_points': len(self.memory_history),
            'thresholds': {
                'memory_threshold_mb': self.memory_threshold_mb,
                'gc_threshold_percent': self.gc_threshold
            }
        }
    
    def optimize_data_structure(self, data_list: List[Any], max_size: int = 10000) -> List[Any]:
        """优化数据结构，防止内存过度使用"""
        if len(data_list) <= max_size:
            return data_list
        
        print(f"🔧 数据结构过大 ({len(data_list)} 项)，进行优化...")
        
        # 保留最新的数据
        optimized_data = data_list[-max_size:]
        
        # 强制垃圾回收被丢弃的数据
        del data_list[:-max_size]
        gc.collect()
        
        print(f"🔧 数据结构优化完成，保留 {len(optimized_data)} 项")
        return optimized_data
    
    def create_memory_efficient_batch(self, data: List[Any], batch_size: int = 1000):
        """创建内存高效的批处理迭代器"""
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            yield batch
            
            # 批处理完成后建议垃圾回收
            if i % (batch_size * 10) == 0:  # 每10个批次
                gc.collect()


class DataStreamProcessor:
    """流式数据处理器 - 减少内存占用"""
    
    def __init__(self, memory_optimizer: MemoryOptimizer):
        self.memory_optimizer = memory_optimizer
        self.buffer_size = 1000
        self.buffer = []
    
    def add_data(self, data: Any):
        """添加数据到缓冲区"""
        self.buffer.append(data)
        
        # 缓冲区满时处理数据
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()
    
    def flush_buffer(self):
        """刷新缓冲区"""
        if not self.buffer:
            return
        
        # 处理缓冲区数据
        processed_data = self._process_batch(self.buffer)
        
        # 清空缓冲区
        self.buffer.clear()
        
        # 建议垃圾回收
        gc.collect()
        
        return processed_data
    
    def _process_batch(self, batch: List[Any]) -> List[Any]:
        """处理批次数据"""
        # 这里可以实现具体的数据处理逻辑
        return batch


# 全局内存优化器实例
_global_memory_optimizer = None
_optimizer_lock = threading.Lock()


def get_memory_optimizer() -> MemoryOptimizer:
    """获取全局内存优化器实例（单例模式）"""
    global _global_memory_optimizer
    
    if _global_memory_optimizer is None:
        with _optimizer_lock:
            if _global_memory_optimizer is None:
                _global_memory_optimizer = MemoryOptimizer()
    
    return _global_memory_optimizer


def memory_efficient_decorator(func):
    """内存高效装饰器"""
    def wrapper(*args, **kwargs):
        optimizer = get_memory_optimizer()
        
        # 执行前检查内存
        optimizer._update_memory_stats()
        initial_memory = optimizer.stats.process_memory_mb
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 执行后检查内存并清理
            optimizer._update_memory_stats()
            final_memory = optimizer.stats.process_memory_mb
            
            memory_increase = final_memory - initial_memory
            if memory_increase > 100:  # 内存增长超过100MB
                print(f"⚠️ 函数 {func.__name__} 内存增长: {memory_increase:.1f}MB")
                optimizer._force_garbage_collection()
    
    return wrapper
