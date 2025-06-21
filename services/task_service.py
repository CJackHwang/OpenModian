# -*- coding: utf-8 -*-
"""
任务服务层
封装任务管理相关的业务逻辑
"""

from typing import Dict, Any, List, Optional
from core.managers import TaskManager, InstanceManager
from core.exceptions import TaskException


class TaskService:
    """任务服务 - 封装任务管理业务逻辑"""
    
    def __init__(self, db_manager, task_scheduler=None):
        self.db_manager = db_manager
        self.task_scheduler = task_scheduler
        
        # 初始化管理器
        self.task_manager = TaskManager()
        self.instance_manager = InstanceManager()
    
    def get_all_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有活跃任务"""
        return self.task_manager.get_all_tasks()
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取任务"""
        return self.task_manager.get_task(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task_info = self.task_manager.get_task(task_id)
        if task_info:
            return task_info['monitor'].get_stats()
        return None
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        return self.instance_manager.stop_instance(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        # 先停止任务
        self.instance_manager.stop_instance(task_id)
        
        # 移除实例和任务记录
        self.instance_manager.remove_instance(task_id)
        return self.task_manager.remove_task(task_id)
    
    def cleanup_completed_tasks(self) -> int:
        """清理已完成的任务"""
        # 获取已完成的任务
        completed_tasks = self.task_manager.get_tasks_by_status('completed')
        failed_tasks = self.task_manager.get_tasks_by_status('failed')
        stopped_tasks = self.task_manager.get_tasks_by_status('stopped')
        error_tasks = self.task_manager.get_tasks_by_status('error')
        
        all_cleanup_tasks = {**completed_tasks, **failed_tasks, **stopped_tasks, **error_tasks}
        
        # 清理对应的实例
        for task_id in all_cleanup_tasks.keys():
            self.instance_manager.remove_instance(task_id)
        
        # 清理任务管理器中的记录
        return self.task_manager.cleanup_completed_tasks()
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        all_tasks = self.task_manager.get_all_tasks()
        
        stats = {
            'total_active_tasks': len(all_tasks),
            'running_tasks': len(self.task_manager.get_tasks_by_status('running')),
            'completed_tasks': len(self.task_manager.get_tasks_by_status('completed')),
            'failed_tasks': len(self.task_manager.get_tasks_by_status('failed')),
            'stopped_tasks': len(self.task_manager.get_tasks_by_status('stopped'))
        }
        
        return stats
    
    def get_historical_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取历史任务"""
        try:
            return self.db_manager.get_all_tasks(limit)
        except Exception as e:
            raise TaskException(f"获取历史任务失败: {str(e)}")
    
    def delete_historical_task(self, task_id: str) -> bool:
        """删除历史任务记录"""
        try:
            return self.db_manager.delete_task(task_id)
        except Exception as e:
            raise TaskException(f"删除历史任务失败: {str(e)}")
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """获取定时任务列表"""
        if not self.task_scheduler:
            return []
        
        try:
            return self.task_scheduler.get_scheduled_tasks()
        except Exception as e:
            raise TaskException(f"获取定时任务失败: {str(e)}")
    
    def stop_scheduled_task(self, task_id: str) -> bool:
        """停止定时任务"""
        if not self.task_scheduler:
            return False
        
        try:
            return self.task_scheduler.stop_scheduled_task(task_id)
        except Exception as e:
            raise TaskException(f"停止定时任务失败: {str(e)}")
    
    def start_scheduled_task(self, task_id: str) -> bool:
        """启动定时任务"""
        if not self.task_scheduler:
            return False
        
        try:
            return self.task_scheduler.start_scheduled_task(task_id)
        except Exception as e:
            raise TaskException(f"启动定时任务失败: {str(e)}")
    
    def delete_scheduled_task(self, task_id: str) -> bool:
        """删除定时任务"""
        if not self.task_scheduler:
            return False
        
        try:
            return self.task_scheduler.remove_scheduled_task(task_id)
        except Exception as e:
            raise TaskException(f"删除定时任务失败: {str(e)}")
