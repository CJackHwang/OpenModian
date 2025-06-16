# -*- coding: utf-8 -*-
"""
爬虫监控模块
提供实时监控、统计分析和性能追踪功能
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json


@dataclass
class SpiderStats:
    """爬虫统计数据"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # 请求统计
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    
    # 页面统计
    pages_processed: int = 0
    pages_failed: int = 0
    
    # 项目统计
    projects_found: int = 0
    projects_processed: int = 0
    projects_failed: int = 0
    projects_skipped: int = 0
    
    # 性能统计
    avg_request_time: float = 0.0
    avg_parse_time: float = 0.0
    requests_per_minute: float = 0.0
    
    # 错误统计
    error_counts: Dict[str, int] = field(default_factory=dict)
    consecutive_errors: int = 0
    
    # 数据质量统计
    data_validation_passed: int = 0
    data_validation_failed: int = 0
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_error_rate(self) -> float:
        """获取错误率"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    def get_runtime(self) -> timedelta:
        """获取运行时间"""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "runtime_seconds": self.get_runtime().total_seconds(),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "cached_requests": self.cached_requests,
            "success_rate": round(self.get_success_rate(), 2),
            "error_rate": round(self.get_error_rate(), 2),
            "pages_processed": self.pages_processed,
            "pages_failed": self.pages_failed,
            "projects_found": self.projects_found,
            "projects_processed": self.projects_processed,
            "projects_failed": self.projects_failed,
            "projects_skipped": self.projects_skipped,
            "avg_request_time": round(self.avg_request_time, 3),
            "avg_parse_time": round(self.avg_parse_time, 3),
            "requests_per_minute": round(self.requests_per_minute, 2),
            "error_counts": self.error_counts,
            "consecutive_errors": self.consecutive_errors,
            "data_validation_passed": self.data_validation_passed,
            "data_validation_failed": self.data_validation_failed
        }


class SpiderMonitor:
    """爬虫监控器"""
    
    def __init__(self, config):
        self.config = config
        self.stats = SpiderStats()
        self.request_times = deque(maxlen=100)  # 保存最近100次请求时间
        self.parse_times = deque(maxlen=100)    # 保存最近100次解析时间
        self.error_history = deque(maxlen=50)   # 保存最近50个错误
        
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self):
        """开始监控"""
        if self.config.ENABLE_MONITORING and not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            print("爬虫监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self._monitoring = False
        self.stats.end_time = datetime.now()

        # 不等待线程结束，避免eventlet超时问题
        if self._monitor_thread:
            try:
                # 只检查线程状态，不等待
                if self._monitor_thread.is_alive():
                    print("⚠️ 监控线程仍在运行，但已设置停止标志")
                else:
                    print("✅ 监控线程已自然结束")
            except Exception as e:
                print(f"⚠️ 检查监控线程状态时出现异常: {e}")

        print("爬虫监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                self._update_performance_stats()
                self._check_error_threshold()
                time.sleep(self.config.STATS_UPDATE_INTERVAL)
            except Exception as e:
                print(f"监控循环错误: {e}")
    
    def _update_performance_stats(self):
        """更新性能统计"""
        with self._lock:
            # 计算平均请求时间
            if self.request_times:
                self.stats.avg_request_time = sum(self.request_times) / len(self.request_times)
            
            # 计算平均解析时间
            if self.parse_times:
                self.stats.avg_parse_time = sum(self.parse_times) / len(self.parse_times)
            
            # 计算每分钟请求数
            runtime_minutes = self.stats.get_runtime().total_seconds() / 60
            if runtime_minutes > 0:
                self.stats.requests_per_minute = self.stats.total_requests / runtime_minutes
    
    def _check_error_threshold(self):
        """检查错误阈值"""
        error_rate = self.stats.get_error_rate()
        
        if error_rate > self.config.ERROR_THRESHOLD_PERCENTAGE:
            print(f"⚠️ 警告: 错误率过高 ({error_rate:.1f}%)")
        
        if self.stats.consecutive_errors > self.config.MAX_CONSECUTIVE_ERRORS:
            print(f"⚠️ 警告: 连续错误次数过多 ({self.stats.consecutive_errors})")
    
    def record_request(self, success: bool, request_time: float, cached: bool = False):
        """记录请求"""
        with self._lock:
            self.stats.total_requests += 1
            
            if success:
                self.stats.successful_requests += 1
                self.stats.consecutive_errors = 0
            else:
                self.stats.failed_requests += 1
                self.stats.consecutive_errors += 1
            
            if cached:
                self.stats.cached_requests += 1
            
            self.request_times.append(request_time)
    
    def record_parse(self, parse_time: float):
        """记录解析时间"""
        with self._lock:
            self.parse_times.append(parse_time)
    
    def record_page(self, success: bool):
        """记录页面处理"""
        with self._lock:
            if success:
                self.stats.pages_processed += 1
            else:
                self.stats.pages_failed += 1
    
    def record_project(self, status: str):
        """记录项目处理状态"""
        with self._lock:
            if status == "found":
                self.stats.projects_found += 1
            elif status == "processed":
                self.stats.projects_processed += 1
            elif status == "failed":
                self.stats.projects_failed += 1
            elif status == "skipped":
                self.stats.projects_skipped += 1
    
    def record_error(self, error_type: str, error_msg: str):
        """记录错误"""
        with self._lock:
            self.stats.error_counts[error_type] = self.stats.error_counts.get(error_type, 0) + 1
            
            error_info = {
                "type": error_type,
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            self.error_history.append(error_info)
    
    def record_validation(self, passed: bool):
        """记录数据验证结果"""
        with self._lock:
            if passed:
                self.stats.data_validation_passed += 1
            else:
                self.stats.data_validation_failed += 1
    
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        with self._lock:
            return self.stats.to_dict()
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        with self._lock:
            return {
                "error_counts": dict(self.stats.error_counts),
                "recent_errors": list(self.error_history)[-10:],  # 最近10个错误
                "consecutive_errors": self.stats.consecutive_errors,
                "error_rate": round(self.stats.get_error_rate(), 2)
            }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_current_stats()
        runtime = timedelta(seconds=stats["runtime_seconds"])
        
        print("\n" + "="*60)
        print("📊 爬虫运行统计")
        print("="*60)
        print(f"运行时间: {runtime}")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"失败请求: {stats['failed_requests']}")
        print(f"缓存命中: {stats['cached_requests']}")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print(f"错误率: {stats['error_rate']:.1f}%")
        print(f"")
        print(f"页面处理: {stats['pages_processed']} 成功, {stats['pages_failed']} 失败")
        print(f"项目发现: {stats['projects_found']}")
        print(f"项目处理: {stats['projects_processed']} 成功, {stats['projects_failed']} 失败")
        print(f"项目跳过: {stats['projects_skipped']}")
        print(f"")
        print(f"平均请求时间: {stats['avg_request_time']:.3f}s")
        print(f"平均解析时间: {stats['avg_parse_time']:.3f}s")
        print(f"请求频率: {stats['requests_per_minute']:.1f}/分钟")
        print(f"")
        print(f"数据验证: {stats['data_validation_passed']} 通过, {stats['data_validation_failed']} 失败")
        
        if stats['error_counts']:
            print(f"\n错误类型统计:")
            for error_type, count in stats['error_counts'].items():
                print(f"  {error_type}: {count}")
        
        print("="*60)
    
    def save_stats(self, file_path: str):
        """保存统计信息到文件"""
        try:
            stats = self.get_current_stats()
            error_summary = self.get_error_summary()
            
            report = {
                "stats": stats,
                "errors": error_summary,
                "generated_at": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"统计报告已保存到: {file_path}")
            
        except Exception as e:
            print(f"保存统计报告失败: {e}")


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.timers = {}
        self.counters = defaultdict(int)
    
    def start_timer(self, name: str):
        """开始计时"""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """结束计时并返回耗时"""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]
            del self.timers[name]
            return elapsed
        return 0.0
    
    def increment_counter(self, name: str, value: int = 1):
        """增加计数器"""
        self.counters[name] += value
    
    def get_profile_data(self) -> Dict[str, Any]:
        """获取性能分析数据"""
        return {
            "active_timers": list(self.timers.keys()),
            "counters": dict(self.counters)
        }
