# -*- coding: utf-8 -*-
"""
实例管理器
统一管理爬虫实例的生命周期
"""

import threading
from typing import Dict, Any, Optional


class InstanceManager:
    """爬虫实例管理器"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self.spider_instances: Dict[str, Any] = {}
    
    def add_instance(self, task_id: str, spider_instance) -> None:
        """添加爬虫实例"""
        with self._lock:
            self.spider_instances[task_id] = spider_instance
            print(f"📝 爬虫实例已添加: {task_id}")
    
    def get_instance(self, task_id: str) -> Optional[Any]:
        """获取爬虫实例"""
        with self._lock:
            return self.spider_instances.get(task_id)
    
    def remove_instance(self, task_id: str) -> bool:
        """移除爬虫实例"""
        with self._lock:
            if task_id in self.spider_instances:
                spider = self.spider_instances[task_id]
                
                # 尝试清理爬虫资源
                try:
                    if hasattr(spider, '_cleanup_lightning_managers'):
                        spider._cleanup_lightning_managers()
                except Exception as e:
                    print(f"清理爬虫资源时出错: {e}")
                
                del self.spider_instances[task_id]
                print(f"🧹 爬虫实例已移除: {task_id}")
                return True
            return False
    
    def get_all_instances(self) -> Dict[str, Any]:
        """获取所有实例"""
        with self._lock:
            return self.spider_instances.copy()
    
    def get_instance_count(self) -> int:
        """获取实例数量"""
        with self._lock:
            return len(self.spider_instances)
    
    def cleanup_all_instances(self) -> int:
        """清理所有实例"""
        with self._lock:
            count = len(self.spider_instances)
            
            # 逐个清理实例
            for task_id in list(self.spider_instances.keys()):
                self.remove_instance(task_id)
            
            if count > 0:
                print(f"🧹 已清理所有 {count} 个爬虫实例")
            
            return count
    
    def stop_instance(self, task_id: str) -> bool:
        """停止指定实例"""
        with self._lock:
            spider = self.spider_instances.get(task_id)
            if spider and hasattr(spider, 'stop_crawling'):
                try:
                    spider.stop_crawling()
                    print(f"⏹️ 爬虫实例已停止: {task_id}")
                    return True
                except Exception as e:
                    print(f"停止爬虫实例时出错: {e}")
                    return False
            return False
