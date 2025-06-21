# -*- coding: utf-8 -*-
"""
任务管理器
统一管理爬虫任务的生命周期
"""

import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime


class TaskManager:
    """任务管理器 - 统一管理爬虫任务"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
    
    def add_task(self, task_id: str, monitor, config: Dict[str, Any], 
                 thread: Optional[threading.Thread] = None) -> None:
        """添加任务"""
        with self._lock:
            self.active_tasks[task_id] = {
                'monitor': monitor,
                'config': config,
                'thread': thread,
                'status': 'starting',
                'created_at': datetime.now().isoformat()
            }
    
    def update_task_thread(self, task_id: str, thread: threading.Thread) -> None:
        """更新任务线程"""
        with self._lock:
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['thread'] = thread
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        with self._lock:
            return self.active_tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务"""
        with self._lock:
            return self.active_tasks.copy()
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        with self._lock:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
                print(f"🧹 任务已移除: {task_id}")
                return True
            return False
    
    def cleanup_completed_tasks(self) -> int:
        """清理已完成的任务"""
        with self._lock:
            tasks_to_remove = []
            for task_id, task_info in self.active_tasks.items():
                status = task_info['monitor'].stats.get('status', 'unknown')
                if status in ['completed', 'failed', 'stopped', 'error']:
                    tasks_to_remove.append(task_id)
            
            removed_count = 0
            for task_id in tasks_to_remove:
                if self.remove_task(task_id):
                    removed_count += 1
            
            if removed_count > 0:
                print(f"🧹 批量清理了 {removed_count} 个已完成任务")
            
            return removed_count
    
    def get_task_count(self) -> int:
        """获取活跃任务数量"""
        with self._lock:
            return len(self.active_tasks)
    
    def get_tasks_by_status(self, status: str) -> Dict[str, Dict[str, Any]]:
        """根据状态获取任务"""
        with self._lock:
            result = {}
            for task_id, task_info in self.active_tasks.items():
                task_status = task_info['monitor'].stats.get('status', 'unknown')
                if task_status == status:
                    result[task_id] = task_info
            return result
