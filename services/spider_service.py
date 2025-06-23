# -*- coding: utf-8 -*-
"""
爬虫服务层
封装爬虫相关的业务逻辑
"""

import uuid
import threading
from typing import Dict, Any, Optional
from spider.core import SpiderCore
from spider.config import SpiderConfig
from core.monitors import WebSpiderMonitor, ScheduledTaskMonitor
from core.managers import TaskManager, InstanceManager
from core.exceptions import TaskException, ConfigException


class SpiderService:
    """爬虫服务 - 封装爬虫业务逻辑"""
    
    def __init__(self, db_manager, task_scheduler=None, socketio=None):
        self.db_manager = db_manager
        self.task_scheduler = task_scheduler
        self.socketio = socketio
        
        # 初始化管理器
        self.task_manager = TaskManager()
        self.instance_manager = InstanceManager()
    
    def create_crawl_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建爬虫任务"""
        from core.logging import log_spider, log_system

        # 记录任务创建请求
        log_system('info', '收到爬虫任务创建请求', 'spider-service')
        log_spider('info', f'任务配置: 页面范围={config.get("start_page", 1)}-{config.get("end_page", 10)}, 分类={config.get("category", "all")}', 'spider-service')
        log_spider('info', f'并发设置: {config.get("max_concurrent", 3)}, 延迟范围={config.get("delay_min", 1)}-{config.get("delay_max", 3)}秒', 'spider-service')

        # 清理旧任务
        cleaned_count = self.cleanup_old_tasks()
        if cleaned_count > 0:
            log_system('info', f'清理了 {cleaned_count} 个已完成的旧任务', 'spider-service')

        # 检查是否为定时任务
        if config.get('is_scheduled', False):
            log_spider('info', f'创建定时任务，执行间隔: {config.get("schedule_interval", 3600)}秒', 'spider-service')
            return self._create_scheduled_task(config)
        else:
            log_spider('info', '创建即时执行任务', 'spider-service')
            return self._create_regular_task(config)
    
    def _create_scheduled_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建定时任务"""
        if not self.task_scheduler:
            raise TaskException("定时任务调度器未初始化")
        
        schedule_interval = max(5, config.get('schedule_interval', 3600))
        task_name = f"定时爬取_{config.get('category', 'all')}_{config.get('start_page', 1)}-{config.get('end_page', 10)}"
        
        try:
            task_id = self.task_scheduler.add_scheduled_task(
                name=task_name,
                config=config,
                interval_seconds=schedule_interval
            )
            
            return {
                'task_id': task_id,
                'message': f'定时任务已创建，执行间隔: {schedule_interval}秒',
                'is_scheduled': True
            }
        except Exception as e:
            raise TaskException(f"创建定时任务失败: {str(e)}")
    
    def _create_regular_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建普通任务"""
        from core.logging import log_spider, log_system

        task_id = str(uuid.uuid4())
        log_spider('info', f'生成任务ID: {task_id}', 'spider-service')

        # 创建爬虫配置
        spider_config = self._build_spider_config(config)
        log_spider('debug', f'爬虫配置构建完成: 并发={spider_config.MAX_CONCURRENT_REQUESTS}, 延迟={spider_config.REQUEST_DELAY}', 'spider-service')

        # 创建监控器 - 与原版本调用方式完全一致
        monitor = WebSpiderMonitor(task_id)
        log_system('debug', f'创建任务监控器: {task_id}', 'spider-service')

        # 设置socketio实例以支持WebSocket通信
        if self.socketio:
            monitor.set_socketio(self.socketio)
            log_system('debug', 'WebSocket通信已配置', 'spider-service')

        # 创建爬虫实例
        spider = SpiderCore(spider_config, web_monitor=monitor, db_manager=self.db_manager)
        log_spider('info', '爬虫核心实例创建完成', 'spider-service')

        # 保存实例和任务
        self.instance_manager.add_instance(task_id, spider)
        self.task_manager.add_task(task_id, monitor, config)
        log_system('debug', f'任务实例已注册到管理器: {task_id}', 'spider-service')

        # 保存任务到数据库
        self.db_manager.save_crawl_task(task_id, config)
        log_system('info', f'任务信息已保存到数据库: {task_id}', 'spider-service')

        # 启动爬虫线程
        thread = threading.Thread(
            target=self._run_spider_task,
            args=(task_id, spider, monitor, config)
        )
        thread.daemon = True
        thread.start()
        log_spider('info', f'爬虫任务线程已启动: {task_id}', 'spider-service')

        self.task_manager.update_task_thread(task_id, thread)

        log_system('info', f'爬虫任务创建完成并开始执行: {task_id}', 'spider-service')

        return {
            'task_id': task_id,
            'message': '爬虫任务已启动',
            'is_scheduled': False
        }
    
    def _build_spider_config(self, config: Dict[str, Any]) -> SpiderConfig:
        """构建爬虫配置"""
        spider_config = SpiderConfig()
        
        # 更新配置参数
        if 'max_concurrent' in config:
            spider_config.MAX_CONCURRENT_REQUESTS = int(config['max_concurrent'])
        if 'delay_min' in config and 'delay_max' in config:
            spider_config.REQUEST_DELAY = (float(config['delay_min']), float(config['delay_max']))
        
        return spider_config
    
    def _run_spider_task(self, task_id: str, spider: SpiderCore,
                        monitor: WebSpiderMonitor, config: Dict[str, Any]) -> None:
        """运行爬虫任务"""
        from core.logging import log_spider, log_system

        try:
            log_spider('info', f'开始执行爬虫任务: {task_id}', 'spider-task')
            log_spider('info', f'任务参数: 页面{config.get("start_page", 1)}-{config.get("end_page", 10)}, 分类={config.get("category", "all")}', 'spider-task')

            monitor.add_log('info', f'开始爬取任务 {task_id}')
            monitor.update_stats(status='running')

            # 设置进度回调
            def progress_callback(current_page=0, total_pages=0, total_projects=0,
                                completed_projects=0, project_progress=0):
                # 记录详细的进度信息
                log_spider('debug', f'任务进度更新: 页面{current_page}/{total_pages}, 项目{completed_projects}/{total_projects} ({project_progress:.1f}%)', 'spider-task')
                monitor.update_progress(current_page, total_pages, total_projects,
                                      completed_projects, project_progress)

            spider.set_progress_callback(progress_callback)
            log_system('debug', f'进度回调已设置: {task_id}', 'spider-task')

            # 启动爬虫
            log_spider('info', f'启动爬虫核心引擎: {task_id}', 'spider-task')

            # 检查是否包含关注列表
            watched_project_ids = config.get('watched_project_ids', [])
            if config.get('include_watch_list', False) and watched_project_ids:
                log_spider('info', f'包含关注列表项目: {len(watched_project_ids)}个', 'spider-task')

            success = spider.start_crawling(
                start_page=int(config.get('start_page', 1)),
                end_page=int(config.get('end_page', 10)),
                category=config.get('category', 'all'),
                task_id=task_id,
                watched_project_ids=watched_project_ids if config.get('include_watch_list', False) else None
            )

            log_spider('info', f'爬虫引擎执行完成: {task_id}, 成功={success}', 'spider-task')
            self._handle_task_completion(task_id, spider, monitor, success)

        except Exception as e:
            log_spider('error', f'爬虫任务执行异常: {task_id}, 错误={str(e)}', 'spider-task')
            self._handle_task_error(task_id, monitor, str(e))
    
    def _handle_task_completion(self, task_id: str, spider: SpiderCore, 
                               monitor: WebSpiderMonitor, success: bool) -> None:
        """处理任务完成"""
        total_saved = getattr(spider, 'saved_count', 0)
        total_found = len(spider.projects_data) if hasattr(spider, 'projects_data') else 0
        
        if success and not spider.is_stopped():
            monitor.add_log('success', f'🎉 爬取任务完成！发现 {total_found} 个项目，成功保存 {total_saved} 条数据到数据库')
            status = 'completed'
        elif spider.is_stopped():
            monitor.add_log('warning', f'⏹️ 任务被用户停止，已保存 {total_saved} 条数据到数据库（共发现 {total_found} 个项目）')
            status = 'stopped'
        else:
            monitor.add_log('error', '❌ 爬取任务失败')
            status = 'failed'
        
        # 更新统计和状态
        stats = {
            'projects_found': total_found,
            'projects_processed': total_saved
        }
        monitor.update_stats(projects_found=total_found, projects_processed=total_saved, status=status)
        self.db_manager.update_task_status(task_id, status, stats)
        
        # 延迟清理
        self._schedule_task_cleanup(task_id)
    
    def _handle_task_error(self, task_id: str, monitor: WebSpiderMonitor, error_msg: str) -> None:
        """处理任务错误"""
        monitor.add_log('error', f'爬取过程中出现错误: {error_msg}')
        monitor.update_stats(status='error')
        self.db_manager.update_task_status(task_id, 'error')
        self._schedule_task_cleanup(task_id)
    
    def _schedule_task_cleanup(self, task_id: str) -> None:
        """安排任务清理"""
        def delayed_cleanup():
            import time
            time.sleep(5)  # 等待5秒让前端显示完成状态
            self.cleanup_task(task_id)
        
        cleanup_thread = threading.Thread(target=delayed_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        # 获取任务信息
        task_info = self.task_manager.get_task(task_id)
        if not task_info:
            return False

        # 停止爬虫实例
        success = self.instance_manager.stop_instance(task_id)

        if success:
            # 更新监控器状态（与原版本保持一致）
            monitor = task_info['monitor']
            monitor.add_log('warning', '用户请求停止任务')
            monitor.update_stats(status='stopped')

            # 更新数据库任务状态
            self.db_manager.update_task_status(task_id, 'stopped')

            # 安排延迟清理
            self._schedule_task_cleanup(task_id)

        return success
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task_info = self.task_manager.get_task(task_id)
        if task_info:
            return task_info['monitor'].get_stats()
        return None
    
    def cleanup_task(self, task_id: str) -> None:
        """清理单个任务"""
        self.instance_manager.remove_instance(task_id)
        self.task_manager.remove_task(task_id)
    
    def cleanup_old_tasks(self) -> int:
        """清理旧任务"""
        # 先清理实例管理器中对应的实例
        completed_tasks = self.task_manager.get_tasks_by_status('completed')
        failed_tasks = self.task_manager.get_tasks_by_status('failed')
        stopped_tasks = self.task_manager.get_tasks_by_status('stopped')
        error_tasks = self.task_manager.get_tasks_by_status('error')
        
        all_cleanup_tasks = {**completed_tasks, **failed_tasks, **stopped_tasks, **error_tasks}
        
        for task_id in all_cleanup_tasks.keys():
            self.instance_manager.remove_instance(task_id)
        
        # 然后清理任务管理器
        return self.task_manager.cleanup_completed_tasks()
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务"""
        return self.task_manager.get_all_tasks()
