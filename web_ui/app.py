# -*- coding: utf-8 -*-
"""
摩点爬虫Web UI主应用
基于Flask的可视化工作流管理界面
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit
import uuid

from spider.core import SpiderCore
from spider.config import SpiderConfig
from spider.monitor import SpiderMonitor
from database.db_manager import DatabaseManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'modian_spider_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量
spider_instances = {}
active_tasks = {}
db_manager = DatabaseManager()

class WebSpiderMonitor:
    """Web界面专用的爬虫监控器"""
    
    def __init__(self, task_id):
        self.task_id = task_id
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
    
    def update_progress(self, current, total):
        """更新进度"""
        self.stats['current_page'] = current
        self.stats['total_pages'] = total
        self.stats['progress'] = (current / total * 100) if total > 0 else 0
        self.emit_update()
    
    def add_log(self, level, message):
        """添加日志"""
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
        """更新统计信息"""
        self.stats.update(kwargs)
        self.emit_update()
    
    def emit_update(self):
        """发送更新到前端"""
        socketio.emit('task_update', {
            'task_id': self.task_id,
            'stats': self.stats
        })

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/start_crawl', methods=['POST'])
def start_crawl():
    """启动爬虫任务"""
    try:
        data = request.json
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建爬虫配置
        config = SpiderConfig()
        
        # 更新配置参数
        if 'start_page' in data:
            config.start_page = int(data['start_page'])
        if 'end_page' in data:
            config.end_page = int(data['end_page'])
        if 'category' in data:
            config.category = data['category']
        if 'max_concurrent' in data:
            config.MAX_CONCURRENT_REQUESTS = int(data['max_concurrent'])
        if 'delay_min' in data and 'delay_max' in data:
            config.REQUEST_DELAY = (float(data['delay_min']), float(data['delay_max']))
        
        # 创建监控器
        monitor = WebSpiderMonitor(task_id)
        
        # 创建爬虫实例
        spider = SpiderCore(config)
        
        # 保存实例
        spider_instances[task_id] = spider
        active_tasks[task_id] = {
            'monitor': monitor,
            'config': data,
            'thread': None,
            'status': 'starting'
        }
        
        # 保存任务到数据库
        db_manager.save_crawl_task(task_id, data)

        # 启动爬虫线程
        def run_spider():
            try:
                monitor.add_log('info', f'开始爬取任务 {task_id}')
                monitor.update_stats(status='running')

                # 启动爬虫
                success = spider.start_crawling(
                    start_page=config.start_page,
                    end_page=config.end_page,
                    category=config.category
                )

                if success and not spider.is_stopped():
                    # 保存爬取的数据到数据库
                    if spider.projects_data:
                        saved_count = db_manager.save_projects(spider.projects_data, task_id)
                        monitor.add_log('success', f'爬取任务完成，保存了 {saved_count} 条数据到数据库')

                        # 更新任务统计
                        stats = {
                            'projects_found': len(spider.projects_data),
                            'projects_processed': saved_count
                        }
                        db_manager.update_task_status(task_id, 'completed', stats)
                    else:
                        monitor.add_log('warning', '爬取任务完成，但没有获取到数据')
                        db_manager.update_task_status(task_id, 'completed')

                    monitor.update_stats(status='completed')
                elif spider.is_stopped():
                    monitor.add_log('warning', '任务被用户停止')
                    monitor.update_stats(status='stopped')
                    db_manager.update_task_status(task_id, 'stopped')
                else:
                    monitor.add_log('error', '爬取任务失败')
                    monitor.update_stats(status='failed')
                    db_manager.update_task_status(task_id, 'failed')

            except Exception as e:
                monitor.add_log('error', f'爬取过程中出现错误: {str(e)}')
                monitor.update_stats(status='error')
                db_manager.update_task_status(task_id, 'error')
        
        thread = threading.Thread(target=run_spider)
        thread.daemon = True
        thread.start()
        
        active_tasks[task_id]['thread'] = thread
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '爬虫任务已启动'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启动失败: {str(e)}'
        }), 500

@app.route('/api/stop_crawl/<task_id>', methods=['POST'])
def stop_crawl(task_id):
    """停止爬虫任务"""
    try:
        if task_id in active_tasks:
            # 停止爬虫实例
            if task_id in spider_instances:
                spider = spider_instances[task_id]
                spider.stop_crawling()
                active_tasks[task_id]['monitor'].add_log('warning', '用户请求停止任务')
                active_tasks[task_id]['monitor'].update_stats(status='stopped')

                # 更新数据库任务状态
                db_manager.update_task_status(task_id, 'stopped')

                return jsonify({
                    'success': True,
                    'message': '任务已停止'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '爬虫实例不存在'
                }), 404
        else:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'停止失败: {str(e)}'
        }), 500

@app.route('/api/tasks')
def get_tasks():
    """获取所有任务状态"""
    tasks = []
    for task_id, task_info in active_tasks.items():
        tasks.append({
            'task_id': task_id,
            'config': task_info['config'],
            'stats': task_info['monitor'].stats
        })
    
    return jsonify({
        'success': True,
        'tasks': tasks
    })

@app.route('/api/task/<task_id>')
def get_task(task_id):
    """获取特定任务状态"""
    if task_id in active_tasks:
        return jsonify({
            'success': True,
            'task': {
                'task_id': task_id,
                'config': active_tasks[task_id]['config'],
                'stats': active_tasks[task_id]['monitor'].stats
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404

@app.route('/api/download/<task_id>')
def download_results(task_id):
    """下载爬取结果"""
    try:
        if task_id in spider_instances:
            spider = spider_instances[task_id]
            
            # 查找最新的输出文件
            output_dir = Path(spider.config.OUTPUT_DIR)
            excel_files = list(output_dir.glob('*.xlsx'))
            
            if excel_files:
                # 返回最新的文件
                latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
                return send_file(latest_file, as_attachment=True)
            else:
                return jsonify({
                    'success': False,
                    'message': '没有找到输出文件'
                }), 404
        else:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        }), 500

@app.route('/api/config')
def get_config():
    """获取默认配置"""
    config = SpiderConfig()
    return jsonify({
        'success': True,
        'config': {
            'start_page': 1,
            'end_page': 10,
            'category': 'all',
            'max_concurrent': config.MAX_CONCURRENT_REQUESTS,
            'delay_min': config.REQUEST_DELAY[0],
            'delay_max': config.REQUEST_DELAY[1],
            'categories': [
                {'value': 'all', 'label': '全部分类'},
                {'value': 'game', 'label': '游戏'},
                {'value': 'publish', 'label': '出版'},
                {'value': 'design', 'label': '设计'},
                {'value': 'tech', 'label': '科技'},
                {'value': 'food', 'label': '美食'},
                {'value': 'fashion', 'label': '时尚'},
                {'value': 'art', 'label': '艺术'},
                {'value': 'film', 'label': '影视'},
                {'value': 'music', 'label': '音乐'},
                {'value': 'other', 'label': '其他'}
            ]
        }
    })

@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    print(f'客户端已连接: {request.sid}')
    emit('connected', {'message': '连接成功'})

@app.route('/api/database/stats')
def get_database_stats():
    """获取数据库统计信息"""
    try:
        stats = db_manager.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500

@app.route('/api/database/projects')
def get_database_projects():
    """获取数据库中的项目数据"""
    try:
        time_period = request.args.get('period', 'all')
        limit = int(request.args.get('limit', 100))

        projects = db_manager.get_projects_by_time(time_period, limit)

        return jsonify({
            'success': True,
            'projects': projects,
            'count': len(projects)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取项目数据失败: {str(e)}'
        }), 500

@app.route('/api/database/export')
def export_database():
    """导出数据库数据"""
    try:
        time_period = request.args.get('period', 'all')

        output_path = db_manager.export_to_excel(time_period)

        if output_path:
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({
                'success': False,
                'message': '导出失败或没有数据'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导出失败: {str(e)}'
        }), 500

@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    print(f'客户端已连接: {request.sid}')
    emit('connected', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开连接"""
    print(f'客户端已断开: {request.sid}')

if __name__ == '__main__':
    # 确保模板和静态文件目录存在
    os.makedirs('web_ui/templates', exist_ok=True)
    os.makedirs('web_ui/static/css', exist_ok=True)
    os.makedirs('web_ui/static/js', exist_ok=True)
    
    print("摩点爬虫Web UI启动中...")
    print("访问地址: http://localhost:5000")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
