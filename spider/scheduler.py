# -*- coding: utf-8 -*-
"""
后台定时任务调度器
实现爬虫任务的定时执行和管理功能
"""

import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import uuid

@dataclass
class TaskExecutionRecord:
    """任务执行记录"""
    execution_id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, error
    result_summary: str = ""
    projects_processed: int = 0
    errors_count: int = 0
    duration_seconds: float = 0.0

@dataclass
class ScheduledTask:
    """定时任务数据结构"""
    task_id: str
    name: str
    config: Dict
    interval_seconds: int
    next_run_time: datetime
    is_active: bool = True
    last_run_time: Optional[datetime] = None
    run_count: int = 0
    last_status: str = "pending"
    created_time: datetime = None
    execution_history: List[TaskExecutionRecord] = None

    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()
        if self.execution_history is None:
            self.execution_history = []

class TaskScheduler:
    """后台定时任务调度器"""
    
    def __init__(self, db_manager=None, spider_factory: Callable = None):
        self.db_manager = db_manager
        self.spider_factory = spider_factory  # 用于创建爬虫实例的工厂函数
        
        # 任务存储
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, threading.Thread] = {}
        
        # 调度器控制
        self._scheduler_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        
        # 配置
        self.max_concurrent_tasks = 3
        self.check_interval = 5  # 每5秒检查一次
        
        # 🔧 修复：添加健康检查机制
        self._last_heartbeat = datetime.now()
        self._is_healthy = True

        print("📅 定时任务调度器初始化完成")
    
    def start_scheduler(self):
        """启动调度器"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            print("⚠️ 调度器已经在运行")
            return
        
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        print("🚀 定时任务调度器已启动")
    
    def stop_scheduler(self):
        """停止调度器"""
        self._stop_event.set()
        
        # 停止所有运行中的任务
        with self._lock:
            for task_id, thread in list(self.running_tasks.items()):
                print(f"🛑 停止运行中的任务: {task_id}")
                # 这里需要实现任务停止逻辑
        
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=10)
        
        print("⏹️ 定时任务调度器已停止")
    
    def add_scheduled_task(self, name: str, config: Dict, interval_seconds: int) -> str:
        """添加定时任务"""
        if interval_seconds < 5:
            raise ValueError("定时间隔不能小于5秒")
        
        task_id = f"scheduled_{uuid.uuid4().hex[:8]}"
        next_run_time = datetime.now() + timedelta(seconds=interval_seconds)
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            config=config,
            interval_seconds=interval_seconds,
            next_run_time=next_run_time
        )
        
        with self._lock:
            self.scheduled_tasks[task_id] = task
        
        # 保存到数据库
        if self.db_manager:
            self._save_scheduled_task_to_db(task)
        
        print(f"📅 已添加定时任务: {name} (ID: {task_id})")
        print(f"   - 执行间隔: {interval_seconds}秒")
        print(f"   - 下次执行: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return task_id
    
    def remove_scheduled_task(self, task_id: str) -> bool:
        """删除定时任务"""
        with self._lock:
            if task_id in self.scheduled_tasks:
                # 如果任务正在运行，先停止
                if task_id in self.running_tasks:
                    print(f"⚠️ 任务 {task_id} 正在运行，请先停止")
                    return False
                
                del self.scheduled_tasks[task_id]
                
                # 从数据库删除
                if self.db_manager:
                    self._remove_scheduled_task_from_db(task_id)
                
                print(f"🗑️ 已删除定时任务: {task_id}")
                return True
            else:
                print(f"❌ 定时任务不存在: {task_id}")
                return False
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """获取所有定时任务"""
        with self._lock:
            tasks = []
            for task in self.scheduled_tasks.values():
                task_dict = asdict(task)
                # 转换datetime为字符串
                for key, value in task_dict.items():
                    if isinstance(value, datetime):
                        task_dict[key] = value.isoformat() if value else None
                
                # 添加运行状态
                task_dict['is_running'] = task.task_id in self.running_tasks
                tasks.append(task_dict)
            
            return tasks
    
    def toggle_task_status(self, task_id: str) -> bool:
        """切换任务激活状态"""
        with self._lock:
            if task_id in self.scheduled_tasks:
                task = self.scheduled_tasks[task_id]
                task.is_active = not task.is_active

                # 更新数据库
                if self.db_manager:
                    self._save_scheduled_task_to_db(task)

                status = "激活" if task.is_active else "暂停"
                print(f"🔄 任务 {task_id} 已{status}")
                return True
            return False

    def run_task_immediately(self, task_id: str) -> bool:
        """立即执行定时任务"""
        with self._lock:
            if task_id not in self.scheduled_tasks:
                print(f"❌ 定时任务不存在: {task_id}")
                return False

            task = self.scheduled_tasks[task_id]

            if task_id in self.running_tasks:
                print(f"⚠️ 任务 {task_id} 正在运行中")
                return False

            if not task.is_active:
                print(f"⚠️ 任务 {task_id} 已暂停，无法执行")
                return False

            # 立即执行任务
            print(f"🚀 立即执行定时任务: {task.name} (ID: {task_id})")
            self._run_task(task)
            return True

    def get_task_execution_history(self, task_id: str, limit: int = 20) -> List[Dict]:
        """获取任务执行历史"""
        with self._lock:
            if task_id not in self.scheduled_tasks:
                return []

            task = self.scheduled_tasks[task_id]
            history = task.execution_history[-limit:] if task.execution_history else []

            # 转换为字典格式
            result = []
            for record in history:
                record_dict = asdict(record)
                # 转换datetime为字符串
                for key, value in record_dict.items():
                    if isinstance(value, datetime):
                        record_dict[key] = value.isoformat() if value else None
                result.append(record_dict)

            return result

    def is_scheduler_healthy(self) -> bool:
        """检查调度器是否健康运行 - 🔧 修复：添加健康检查"""
        if not self._scheduler_thread or not self._scheduler_thread.is_alive():
            return False

        # 检查心跳时间（如果超过30秒没有心跳，认为不健康）
        time_since_heartbeat = (datetime.now() - self._last_heartbeat).total_seconds()
        if time_since_heartbeat > 30:
            print(f"⚠️ 调度器心跳超时: {time_since_heartbeat:.1f}秒")
            return False

        return self._is_healthy

    def get_scheduler_status(self) -> Dict:
        """获取调度器状态信息 - 🔧 修复：添加状态监控"""
        with self._lock:
            return {
                'is_running': self._scheduler_thread and self._scheduler_thread.is_alive(),
                'is_healthy': self.is_scheduler_healthy(),
                'last_heartbeat': self._last_heartbeat.isoformat(),
                'total_tasks': len(self.scheduled_tasks),
                'active_tasks': sum(1 for task in self.scheduled_tasks.values() if task.is_active),
                'running_tasks': len(self.running_tasks),
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'check_interval': self.check_interval
            }

    def _scheduler_loop(self):
        """调度器主循环 - 🔧 修复：增强异常处理和日志"""
        print("🔄 定时任务调度器开始运行")
        loop_count = 0

        while not self._stop_event.wait(self.check_interval):
            try:
                loop_count += 1

                # 🔧 修复：更新心跳时间
                self._last_heartbeat = datetime.now()
                self._is_healthy = True

                # 每10次循环打印一次状态（避免日志过多）
                if loop_count % 10 == 1:
                    with self._lock:
                        active_tasks = sum(1 for task in self.scheduled_tasks.values() if task.is_active)
                        running_tasks = len(self.running_tasks)
                    print(f"🔄 调度器循环 #{loop_count}: 活跃任务{active_tasks}个，运行中{running_tasks}个")

                self._check_and_run_tasks()
                self._cleanup_finished_tasks()

            except Exception as e:
                print(f"❌ 调度器运行错误 (循环#{loop_count}): {e}")
                import traceback
                print(f"   详细错误: {traceback.format_exc()}")

                # 发生错误时等待更长时间再继续
                if not self._stop_event.wait(5):
                    print("🔄 调度器错误恢复，继续运行...")

        print("⏹️ 定时任务调度器循环结束")
    
    def _check_and_run_tasks(self):
        """检查并运行到期的任务 - 🔧 修复：优化锁使用，避免阻塞"""
        current_time = datetime.now()
        tasks_to_run = []

        # 🔧 缩短锁持有时间，只用于读取任务列表
        with self._lock:
            # 检查并发任务数限制
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                return

            # 快速收集需要运行的任务，避免长时间持有锁
            for task in list(self.scheduled_tasks.values()):
                if not task.is_active:
                    continue

                if task.task_id in self.running_tasks:
                    continue

                if current_time >= task.next_run_time:
                    tasks_to_run.append(task)

        # 🔧 在锁外运行任务，避免阻塞调度器
        for task in tasks_to_run:
            try:
                print(f"⏰ 定时任务到期: {task.name} (下次执行时间: {task.next_run_time})")
                self._run_task(task)
            except Exception as e:
                print(f"❌ 启动定时任务失败: {task.name} - {e}")
    
    def _run_task(self, task: ScheduledTask):
        """运行单个任务"""
        print(f"🚀 开始执行定时任务: {task.name} (ID: {task.task_id})")

        # 创建执行记录
        execution_id = f"{task.task_id}_exec_{int(datetime.now().timestamp())}"
        execution_record = TaskExecutionRecord(
            execution_id=execution_id,
            task_id=task.task_id,
            start_time=datetime.now()
        )

        def task_runner():
            try:
                # 更新任务状态
                task.last_run_time = execution_record.start_time
                task.run_count += 1
                task.last_status = "running"
                execution_record.status = "running"

                # 添加执行记录到历史
                task.execution_history.append(execution_record)

                # 创建并运行爬虫
                if self.spider_factory:
                    spider = self.spider_factory()

                    # 运行爬虫任务
                    config = task.config
                    success = spider.start_crawling(
                        start_page=config.get('start_page', 1),
                        end_page=config.get('end_page', 10),
                        category=config.get('category', 'all'),
                        task_id=f"{task.task_id}_{task.run_count}"
                    )

                    # 更新执行记录
                    execution_record.end_time = datetime.now()
                    execution_record.duration_seconds = (execution_record.end_time - execution_record.start_time).total_seconds()

                    if success:
                        execution_record.status = "completed"
                        execution_record.result_summary = f"任务执行成功"
                        task.last_status = "completed"
                    else:
                        execution_record.status = "failed"
                        execution_record.result_summary = f"任务执行失败"
                        task.last_status = "failed"

                    # 🔧 修复：获取爬虫统计信息（优先级顺序修复）
                    projects_processed = 0
                    errors_count = 0

                    # 🔧 修复：按优先级顺序获取统计信息
                    # 1. 优先从爬虫实例的saved_count获取（最准确）
                    if hasattr(spider, 'saved_count'):
                        projects_processed = getattr(spider, 'saved_count', 0)
                        errors_count = len(getattr(spider, 'failed_urls', []))
                        print(f"📊 从spider.saved_count获取统计: 保存{projects_processed}个项目，错误{errors_count}个")

                    # 2. 从web监控器获取统计信息（作为补充）
                    elif hasattr(spider, 'web_monitor') and spider.web_monitor:
                        monitor_stats = spider.web_monitor.stats
                        projects_processed = monitor_stats.get('projects_processed', 0)
                        errors_count = monitor_stats.get('errors_count', 0) or monitor_stats.get('failed_count', 0)
                        print(f"📊 从web_monitor获取统计: 处理{projects_processed}个项目，错误{errors_count}个")

                        # 🔧 修复：如果监控器有saved_count属性，优先使用
                        if hasattr(spider.web_monitor, 'saved_count'):
                            projects_processed = spider.web_monitor.saved_count
                            print(f"📊 从web_monitor.saved_count获取统计: 保存{projects_processed}个项目")

                    # 3. 从项目数据列表获取（最后选择）
                    elif hasattr(spider, 'projects_data'):
                        projects_processed = len(getattr(spider, 'projects_data', []))
                        errors_count = len(getattr(spider, 'failed_urls', []))
                        print(f"📊 从projects_data获取统计: 发现{projects_processed}个项目，错误{errors_count}个")

                    else:
                        print(f"⚠️ 无法获取爬虫统计信息，spider属性: {[attr for attr in dir(spider) if not attr.startswith('_')]}")

                    execution_record.projects_processed = projects_processed
                    execution_record.errors_count = errors_count
                    execution_record.result_summary += f"，处理项目{projects_processed}个"

                    if errors_count > 0:
                        execution_record.result_summary += f"，失败{errors_count}个"

                else:
                    print(f"❌ 爬虫工厂函数未设置，无法执行任务: {task.task_id}")
                    execution_record.end_time = datetime.now()
                    execution_record.duration_seconds = (execution_record.end_time - execution_record.start_time).total_seconds()
                    execution_record.status = "error"
                    execution_record.result_summary = "爬虫工厂函数未设置"
                    task.last_status = "error"

                # 计算下次执行时间
                task.next_run_time = datetime.now() + timedelta(seconds=task.interval_seconds)

                print(f"✅ 定时任务执行完成: {task.name}")
                print(f"   - 状态: {task.last_status}")
                print(f"   - 执行时长: {execution_record.duration_seconds:.1f}秒")
                print(f"   - 处理项目: {execution_record.projects_processed}个")
                print(f"   - 下次执行: {task.next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")

                # 限制执行历史记录数量（保留最近50条）
                if len(task.execution_history) > 50:
                    task.execution_history = task.execution_history[-50:]

                # 🔧 修复：异步更新数据库，避免阻塞调度器
                if self.db_manager:
                    try:
                        # 使用单独线程保存数据库，避免阻塞主调度循环
                        def save_to_db():
                            try:
                                self._save_scheduled_task_to_db(task)
                            except Exception as e:
                                print(f"⚠️ 异步保存定时任务到数据库失败: {e}")

                        db_thread = threading.Thread(target=save_to_db, daemon=True)
                        db_thread.start()
                    except Exception as e:
                        print(f"⚠️ 启动数据库保存线程失败: {e}")

            except Exception as e:
                print(f"❌ 定时任务执行失败: {task.name} - {e}")
                execution_record.end_time = datetime.now()
                execution_record.duration_seconds = (execution_record.end_time - execution_record.start_time).total_seconds()
                execution_record.status = "error"
                execution_record.result_summary = f"执行异常: {str(e)}"
                task.last_status = "error"
                task.next_run_time = datetime.now() + timedelta(seconds=task.interval_seconds)

            finally:
                # 🔧 修复：确保任务状态正确清理
                with self._lock:
                    if task.task_id in self.running_tasks:
                        del self.running_tasks[task.task_id]
                        print(f"🧹 定时任务 {task.task_id} 已从运行列表中清理")

                # 🔧 修复：确保爬虫监控正确停止
                try:
                    if 'spider' in locals():
                        # 检查不同类型的监控器
                        if hasattr(spider, 'monitor') and spider.monitor:
                            if hasattr(spider.monitor, 'stop'):
                                spider.monitor.stop()
                                print(f"🛑 爬虫监控已停止")
                            else:
                                print(f"🛑 爬虫监控无需手动停止")

                        # 检查web监控器
                        if hasattr(spider, 'web_monitor') and spider.web_monitor:
                            if hasattr(spider.web_monitor, 'stop'):
                                spider.web_monitor.stop()
                                print(f"🛑 Web监控器已停止")
                            else:
                                print(f"🛑 Web监控器无需手动停止")
                except Exception as e:
                    print(f"⚠️ 停止爬虫监控时出错: {e}")

        # 启动任务线程
        thread = threading.Thread(target=task_runner, daemon=True)
        thread.start()

        with self._lock:
            self.running_tasks[task.task_id] = thread
    
    def _cleanup_finished_tasks(self):
        """清理已完成的任务线程 - 🔧 修复：增强线程清理逻辑"""
        finished_tasks = []

        with self._lock:
            for task_id, thread in list(self.running_tasks.items()):
                if not thread.is_alive():
                    finished_tasks.append(task_id)

        # 清理完成的任务
        if finished_tasks:
            with self._lock:
                for task_id in finished_tasks:
                    if task_id in self.running_tasks:
                        thread = self.running_tasks[task_id]
                        del self.running_tasks[task_id]

                        # 确保线程完全结束
                        try:
                            if thread.is_alive():
                                thread.join(timeout=1.0)  # 最多等待1秒
                        except Exception as e:
                            print(f"⚠️ 清理任务线程时出错 {task_id}: {e}")

            print(f"🧹 清理了 {len(finished_tasks)} 个已完成的任务线程")
    
    def _save_scheduled_task_to_db(self, task: ScheduledTask):
        """保存定时任务到数据库"""
        try:
            # 这里需要实现数据库保存逻辑
            # 暂时使用JSON文件保存
            pass
        except Exception as e:
            print(f"保存定时任务到数据库失败: {e}")
    
    def _remove_scheduled_task_from_db(self, task_id: str):
        """从数据库删除定时任务"""
        try:
            # 这里需要实现数据库删除逻辑
            pass
        except Exception as e:
            print(f"从数据库删除定时任务失败: {e}")
