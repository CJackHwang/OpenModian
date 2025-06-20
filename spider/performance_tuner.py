# -*- coding: utf-8 -*-
"""
性能监控和自动调优模块
实时监控系统性能并自动调整参数以优化性能
"""

import time
import threading
import psutil
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import statistics
import queue


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    network_io_bytes: int
    disk_io_bytes: int
    active_threads: int
    request_rate: float
    response_time: float
    error_rate: float
    success_rate: float


@dataclass
class TuningRule:
    """调优规则"""
    name: str
    condition: Callable[[PerformanceMetrics], bool]
    action: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str
    cooldown_seconds: int = 60
    last_applied: float = 0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, monitoring_interval: float = 10.0):
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        
        # 监控状态
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.RLock()
        
        # 性能基线
        self.baseline_metrics = None
        self.baseline_samples = 10
        
        # 告警阈值
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'error_rate': 10.0,
            'response_time': 5.0
        }
        
        # 告警历史
        self.alerts = []
        self.max_alerts = 100
    
    def start_monitoring(self):
        """开始性能监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()
        print(f"📊 性能监控已启动，监控间隔: {self.monitoring_interval}秒")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("📊 性能监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                metrics = self._collect_metrics()
                
                with self._lock:
                    self.metrics_history.append(metrics)
                    
                    # 限制历史记录大小
                    if len(self.metrics_history) > self.max_history_size:
                        self.metrics_history.pop(0)
                
                # 检查告警
                self._check_alerts(metrics)
                
                # 建立性能基线
                if not self.baseline_metrics and len(self.metrics_history) >= self.baseline_samples:
                    self._establish_baseline()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"❌ 性能监控错误: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        # CPU和内存信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # 网络和磁盘I/O
        try:
            net_io = psutil.net_io_counters()
            network_io_bytes = net_io.bytes_sent + net_io.bytes_recv
        except:
            network_io_bytes = 0
        
        try:
            disk_io = psutil.disk_io_counters()
            disk_io_bytes = disk_io.read_bytes + disk_io.write_bytes if disk_io else 0
        except:
            disk_io_bytes = 0
        
        # 线程数
        active_threads = threading.active_count()
        
        # 应用级指标（需要从其他组件获取）
        request_rate = self._get_request_rate()
        response_time = self._get_average_response_time()
        error_rate = self._get_error_rate()
        success_rate = 100.0 - error_rate
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=memory.used / 1024 / 1024,
            network_io_bytes=network_io_bytes,
            disk_io_bytes=disk_io_bytes,
            active_threads=active_threads,
            request_rate=request_rate,
            response_time=response_time,
            error_rate=error_rate,
            success_rate=success_rate
        )
    
    def _get_request_rate(self) -> float:
        """获取请求速率（每秒请求数）"""
        # 从网络优化器获取统计信息
        try:
            from .network_optimizer import get_network_optimizer
            optimizer = get_network_optimizer()
            stats = optimizer.get_network_stats()
            
            # 计算最近的请求速率
            if len(self.metrics_history) >= 2:
                recent_metrics = self.metrics_history[-2:]
                time_diff = recent_metrics[1].timestamp - recent_metrics[0].timestamp
                if time_diff > 0:
                    return stats['total_requests'] / time_diff
            
            return 0.0
        except:
            return 0.0
    
    def _get_average_response_time(self) -> float:
        """获取平均响应时间"""
        try:
            from .network_optimizer import get_network_optimizer
            optimizer = get_network_optimizer()
            stats = optimizer.get_network_stats()
            return stats.get('average_response_time', 0.0)
        except:
            return 0.0
    
    def _get_error_rate(self) -> float:
        """获取错误率"""
        try:
            from .error_recovery import get_error_recovery_manager
            manager = get_error_recovery_manager()
            report = manager.get_error_report()
            
            total_errors = report['total_errors']
            if total_errors > 0:
                # 计算最近的错误率
                recent_errors = len([
                    err for err in report['recent_errors']
                    if time.time() - err['timestamp'] < 300  # 最近5分钟
                ])
                return (recent_errors / total_errors) * 100
            
            return 0.0
        except:
            return 0.0
    
    def _establish_baseline(self):
        """建立性能基线"""
        recent_metrics = self.metrics_history[-self.baseline_samples:]
        
        self.baseline_metrics = {
            'cpu_percent': statistics.mean(m.cpu_percent for m in recent_metrics),
            'memory_percent': statistics.mean(m.memory_percent for m in recent_metrics),
            'response_time': statistics.mean(m.response_time for m in recent_metrics),
            'request_rate': statistics.mean(m.request_rate for m in recent_metrics)
        }
        
        print(f"📊 性能基线已建立: CPU {self.baseline_metrics['cpu_percent']:.1f}%, "
              f"内存 {self.baseline_metrics['memory_percent']:.1f}%, "
              f"响应时间 {self.baseline_metrics['response_time']:.2f}s")
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """检查告警条件"""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"CPU使用率过高: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"内存使用率过高: {metrics.memory_percent:.1f}%")
        
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append(f"错误率过高: {metrics.error_rate:.1f}%")
        
        if metrics.response_time > self.alert_thresholds['response_time']:
            alerts.append(f"响应时间过长: {metrics.response_time:.2f}s")
        
        # 记录告警
        for alert in alerts:
            alert_info = {
                'timestamp': metrics.timestamp,
                'message': alert,
                'metrics': metrics
            }
            
            with self._lock:
                self.alerts.append(alert_info)
                if len(self.alerts) > self.max_alerts:
                    self.alerts.pop(0)
            
            print(f"⚠️ 性能告警: {alert}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        with self._lock:
            if not self.metrics_history:
                return {'message': '暂无性能数据'}
            
            recent_metrics = self.metrics_history[-10:]  # 最近10个数据点
            
            return {
                'current_metrics': {
                    'cpu_percent': recent_metrics[-1].cpu_percent,
                    'memory_percent': recent_metrics[-1].memory_percent,
                    'memory_mb': recent_metrics[-1].memory_mb,
                    'active_threads': recent_metrics[-1].active_threads,
                    'request_rate': recent_metrics[-1].request_rate,
                    'response_time': recent_metrics[-1].response_time,
                    'error_rate': recent_metrics[-1].error_rate,
                    'success_rate': recent_metrics[-1].success_rate
                },
                'average_metrics': {
                    'cpu_percent': statistics.mean(m.cpu_percent for m in recent_metrics),
                    'memory_percent': statistics.mean(m.memory_percent for m in recent_metrics),
                    'response_time': statistics.mean(m.response_time for m in recent_metrics),
                    'request_rate': statistics.mean(m.request_rate for m in recent_metrics)
                },
                'baseline_metrics': self.baseline_metrics,
                'recent_alerts': self.alerts[-10:],
                'total_data_points': len(self.metrics_history)
            }


class AutoTuner:
    """自动调优器"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.tuning_rules: List[TuningRule] = []
        self.current_config = {}
        self.tuning_history = []
        
        # 注册默认调优规则
        self._register_default_rules()
        
        # 调优状态
        self._tuning_enabled = True
        self._lock = threading.RLock()
    
    def _register_default_rules(self):
        """注册默认调优规则"""
        # CPU使用率过高时减少并发数
        self.add_tuning_rule(
            name="reduce_concurrency_on_high_cpu",
            condition=lambda m: m.cpu_percent > 80,
            action=lambda c: {**c, 'max_concurrent_requests': max(1, c.get('max_concurrent_requests', 5) - 1)},
            description="CPU使用率过高时减少并发数",
            cooldown_seconds=120
        )
        
        # 内存使用率过高时触发垃圾回收
        self.add_tuning_rule(
            name="gc_on_high_memory",
            condition=lambda m: m.memory_percent > 85,
            action=self._trigger_garbage_collection,
            description="内存使用率过高时触发垃圾回收",
            cooldown_seconds=60
        )
        
        # 响应时间过长时增加请求延迟
        self.add_tuning_rule(
            name="increase_delay_on_slow_response",
            condition=lambda m: m.response_time > 5.0,
            action=lambda c: {**c, 'request_delay': (
                c.get('request_delay', (1.0, 3.0))[0] + 0.5,
                c.get('request_delay', (1.0, 3.0))[1] + 1.0
            )},
            description="响应时间过长时增加请求延迟",
            cooldown_seconds=180
        )
        
        # 错误率过高时减少请求频率
        self.add_tuning_rule(
            name="reduce_rate_on_high_errors",
            condition=lambda m: m.error_rate > 10,
            action=lambda c: {**c, 'request_delay': (
                max(2.0, c.get('request_delay', (1.0, 3.0))[0] * 1.5),
                max(5.0, c.get('request_delay', (1.0, 3.0))[1] * 1.5)
            )},
            description="错误率过高时减少请求频率",
            cooldown_seconds=300
        )
    
    def add_tuning_rule(self, name: str, condition: Callable, action: Callable, 
                       description: str, cooldown_seconds: int = 60):
        """添加调优规则"""
        rule = TuningRule(
            name=name,
            condition=condition,
            action=action,
            description=description,
            cooldown_seconds=cooldown_seconds
        )
        
        with self._lock:
            self.tuning_rules.append(rule)
        
        print(f"🔧 已添加调优规则: {name}")
    
    def apply_tuning(self, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """应用自动调优"""
        if not self._tuning_enabled:
            return current_config
        
        with self._lock:
            if not self.monitor.metrics_history:
                return current_config
            
            latest_metrics = self.monitor.metrics_history[-1]
            new_config = current_config.copy()
            applied_rules = []
            
            for rule in self.tuning_rules:
                # 检查冷却时间
                if time.time() - rule.last_applied < rule.cooldown_seconds:
                    continue
                
                # 检查条件
                if rule.condition(latest_metrics):
                    try:
                        new_config = rule.action(new_config)
                        rule.last_applied = time.time()
                        applied_rules.append(rule.name)
                        
                        print(f"🔧 应用调优规则: {rule.name} - {rule.description}")
                        
                    except Exception as e:
                        print(f"❌ 调优规则执行失败: {rule.name} - {e}")
            
            # 记录调优历史
            if applied_rules:
                self.tuning_history.append({
                    'timestamp': time.time(),
                    'applied_rules': applied_rules,
                    'old_config': current_config,
                    'new_config': new_config,
                    'metrics': latest_metrics
                })
                
                # 限制历史记录大小
                if len(self.tuning_history) > 100:
                    self.tuning_history.pop(0)
            
            return new_config
    
    def _trigger_garbage_collection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """触发垃圾回收"""
        try:
            from .memory_optimizer import get_memory_optimizer
            optimizer = get_memory_optimizer()
            optimizer._force_garbage_collection()
        except:
            import gc
            gc.collect()
        
        return config
    
    def enable_tuning(self):
        """启用自动调优"""
        self._tuning_enabled = True
        print("🔧 自动调优已启用")
    
    def disable_tuning(self):
        """禁用自动调优"""
        self._tuning_enabled = False
        print("🔧 自动调优已禁用")
    
    def get_tuning_report(self) -> Dict[str, Any]:
        """获取调优报告"""
        with self._lock:
            return {
                'tuning_enabled': self._tuning_enabled,
                'total_rules': len(self.tuning_rules),
                'rules': [
                    {
                        'name': rule.name,
                        'description': rule.description,
                        'last_applied': rule.last_applied,
                        'cooldown_seconds': rule.cooldown_seconds
                    }
                    for rule in self.tuning_rules
                ],
                'recent_tuning_history': self.tuning_history[-10:],
                'total_tuning_actions': len(self.tuning_history)
            }


# 全局性能调优器
_global_performance_tuner = None
_tuner_lock = threading.Lock()


def get_performance_tuner() -> AutoTuner:
    """获取全局性能调优器实例（单例模式）"""
    global _global_performance_tuner
    
    if _global_performance_tuner is None:
        with _tuner_lock:
            if _global_performance_tuner is None:
                monitor = PerformanceMonitor()
                _global_performance_tuner = AutoTuner(monitor)
                monitor.start_monitoring()
    
    return _global_performance_tuner
