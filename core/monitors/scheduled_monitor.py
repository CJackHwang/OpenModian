# -*- coding: utf-8 -*-
"""
定时任务专用监控器
提供定时任务的进度跟踪和统计功能
"""

from typing import Dict, Any


class ScheduledTaskMonitor:
    """定时任务专用监控器"""
    
    def __init__(self):
        self.stats = {
            'projects_processed': 0,
            'total_projects': 0,
            'errors_count': 0,
            'failed_count': 0,
            'status': 'running',
            'pages_crawled': 0,
            'projects_found': 0,
            'current_page': 0,
            'total_pages': 0,
            'progress': 0
        }
        self.saved_count = 0  # 保存计数器

    def update_progress(self, current_page: int = 0, total_pages: int = 0, 
                       total_projects: int = 0, completed_projects: int = 0, 
                       project_progress: float = 0, **kwargs) -> None:
        """更新进度信息"""
        self.stats.update({
            'current_page': current_page,
            'total_pages': total_pages,
            'total_projects': total_projects,
            'projects_processed': completed_projects,
            'projects_found': total_projects,
            'progress': project_progress
        })
        self.stats.update(kwargs)

        # 同步保存计数
        if completed_projects > 0:
            self.saved_count = completed_projects
            self.stats['projects_processed'] = completed_projects

        print(f"📊 定时任务进度更新: 页面{current_page}/{total_pages}, 项目{completed_projects}/{total_projects}")

    def add_log(self, level: str, message: str) -> None:
        """添加日志（定时任务使用简单的打印输出）"""
        print(f"[{level.upper()}] {message}")

    def update_stats(self, **kwargs) -> None:
        """更新统计信息"""
        self.stats.update(kwargs)

        # 确保保存计数同步
        if 'projects_processed' in kwargs:
            self.saved_count = kwargs['projects_processed']
        elif 'total_projects' in kwargs:
            self.stats['projects_found'] = kwargs['total_projects']

    def increment_saved_count(self, count: int = 1) -> None:
        """增加保存计数"""
        self.saved_count += count
        self.stats['projects_processed'] = self.saved_count
        print(f"📊 定时任务保存计数更新: {self.saved_count}")

    def set_final_stats(self, projects_found: int = 0, projects_saved: int = 0) -> None:
        """设置最终统计"""
        self.stats.update({
            'projects_found': projects_found,
            'projects_processed': projects_saved,
            'total_projects': projects_found
        })
        self.saved_count = projects_saved
        print(f"📊 定时任务最终统计: 发现{projects_found}个，保存{projects_saved}个")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        return self.stats.copy()
