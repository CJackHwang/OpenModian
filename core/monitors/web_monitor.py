# -*- coding: utf-8 -*-
"""
Web界面专用的爬虫监控器
提供实时进度更新和日志记录功能
"""

from datetime import datetime


class WebSpiderMonitor:
    """Web界面专用的爬虫监控器"""

    def __init__(self, task_id, socketio=None):
        """
        初始化监控器
        保持向后兼容：支持原始的单参数调用方式
        """
        self.task_id = task_id
        # 支持全局socketio访问，保持与原版本一致
        self.socketio = socketio
        if socketio is None:
            # 尝试从全局作用域获取socketio（与原版本行为一致）
            try:
                import sys
                if hasattr(sys.modules.get('__main__'), 'socketio'):
                    self.socketio = sys.modules['__main__'].socketio
                elif 'app_refactored' in sys.modules:
                    self.socketio = getattr(sys.modules['app_refactored'], 'socketio', None)
            except:
                pass

        self.stats = {
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'pages_crawled': 0,
            'projects_found': 0,
            'projects_processed': 0,
            'errors': 0,
            'current_page': 0,
            'total_pages': 0,
            'progress': 0,
            'logs': []
        }
    
    def update_progress(self, current_page=0, total_pages=0, total_projects=0, completed_projects=0, project_progress=0):
        """更新进度（增强版本）- 与原版本完全一致"""
        self.stats['current_page'] = current_page
        self.stats['total_pages'] = total_pages
        self.stats['total_projects'] = total_projects
        self.stats['projects_processed'] = completed_projects

        # 计算总体进度：页面爬取占30%，项目详情爬取占70%
        if total_pages > 0 and total_projects > 0:
            page_progress = (current_page / total_pages) * 30
            detail_progress = (completed_projects / total_projects) * 70
            self.stats['progress'] = page_progress + detail_progress
        elif total_pages > 0:
            self.stats['progress'] = (current_page / total_pages) * 100
        elif project_progress > 0:
            self.stats['progress'] = project_progress
        else:
            self.stats['progress'] = 0

        self.emit_update()

    def add_log(self, level, message):
        """添加日志 - 与原版本完全一致"""
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message
        }
        self.stats['logs'].append(log_entry)
        # 只保留最近100条日志
        if len(self.stats['logs']) > 100:
            self.stats['logs'] = self.stats['logs'][-100:]
        self.emit_update()

    def update_stats(self, **kwargs):
        """更新统计信息 - 与原版本完全一致"""
        self.stats.update(kwargs)
        self.emit_update()

    def emit_update(self):
        """发送更新到前端 - 与原版本完全一致"""
        try:
            if self.socketio:
                self.socketio.emit('task_update', {
                    'task_id': self.task_id,
                    'stats': self.stats
                })
        except Exception as e:
            print(f"Socket.IO发送更新失败: {e}")
            # 不抛出异常，避免影响爬虫主流程

    def get_stats(self):
        """获取当前统计信息"""
        return self.stats.copy()

    def set_socketio(self, socketio):
        """设置SocketIO实例"""
        self.socketio = socketio
