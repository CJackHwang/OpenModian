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
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import uuid

from spider.core import SpiderCore
from spider.config import SpiderConfig
# from spider.monitor import SpiderMonitor  # 暂时不使用
from database.db_manager import DatabaseManager

# 检查Vue构建文件是否存在
vue_dist_path = os.path.join(project_root, "web_ui_vue", "dist")
vue_build_exists = os.path.exists(vue_dist_path)

if vue_build_exists:
    # 如果Vue构建文件存在，使用Vue前端
    app = Flask(__name__, static_folder=vue_dist_path, static_url_path='')
else:
    # 否则使用传统模板
    app = Flask(__name__)

app.config['SECRET_KEY'] = 'modian_spider_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
CORS(app)  # 启用CORS支持

# 全局变量
spider_instances = {}
active_tasks = {}

# 创建数据库管理器，使用项目根目录下的数据库
db_path = os.path.join(project_root, "database", "modian_data.db")
db_manager = DatabaseManager(db_path)

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
    if vue_build_exists:
        return send_from_directory(vue_dist_path, 'index.html')
    else:
        return render_template('index.html')

@app.route('/<path:path>')
def vue_routes(path):
    """Vue路由处理"""
    if vue_build_exists:
        # 检查是否是静态文件
        if '.' in path:
            try:
                return send_from_directory(vue_dist_path, path)
            except:
                pass
        # 对于Vue路由，返回index.html
        return send_from_directory(vue_dist_path, 'index.html')
    else:
        # 传统路由处理
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
        
        # 获取配置参数
        start_page = int(data.get('start_page', 1))
        end_page = int(data.get('end_page', 10))
        category = data.get('category', 'all')

        if 'max_concurrent' in data:
            config.MAX_CONCURRENT_REQUESTS = int(data['max_concurrent'])
        if 'delay_min' in data and 'delay_max' in data:
            config.REQUEST_DELAY = (float(data['delay_min']), float(data['delay_max']))
        
        # 创建监控器
        monitor = WebSpiderMonitor(task_id)
        
        # 创建爬虫实例，传入Web监控器
        spider = SpiderCore(config, web_monitor=monitor)
        
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

                # 进度更新回调（预留接口）
                # def update_progress_callback(current, total):
                #     monitor.update_progress(current, total)
                # def log_callback(level, message):
                #     monitor.add_log(level, message)

                # 启动爬虫
                success = spider.start_crawling(
                    start_page=start_page,
                    end_page=end_page,
                    category=category
                )

                if success and not spider.is_stopped():
                    # 保存爬取的数据到数据库
                    if hasattr(spider, 'projects_data') and spider.projects_data:
                        saved_count = db_manager.save_projects(spider.projects_data, task_id)
                        monitor.add_log('success', f'爬取任务完成，保存了 {saved_count} 条数据到数据库')

                        # 更新任务统计
                        stats = {
                            'projects_found': len(spider.projects_data),
                            'projects_processed': saved_count
                        }
                        monitor.update_stats(
                            projects_found=len(spider.projects_data),
                            projects_processed=saved_count
                        )
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
    """获取所有任务状态（活跃任务）"""
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

@app.route('/api/tasks/history')
def get_task_history():
    """获取历史任务记录"""
    try:
        limit = int(request.args.get('limit', 100))
        tasks = db_manager.get_all_tasks(limit)

        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取任务历史失败: {str(e)}'
        }), 500

@app.route('/api/task/<task_id>')
def get_task(task_id):
    """获取特定任务状态（活跃任务或历史任务）"""
    # 首先检查活跃任务
    if task_id in active_tasks:
        return jsonify({
            'success': True,
            'task': {
                'task_id': task_id,
                'config': active_tasks[task_id]['config'],
                'stats': active_tasks[task_id]['monitor'].stats,
                'is_active': True
            }
        })

    # 检查历史任务
    try:
        task = db_manager.get_task_by_id(task_id)
        if task:
            return jsonify({
                'success': True,
                'task': {
                    'task_id': task['task_id'],
                    'config': task.get('config', {}),
                    'stats': {
                        'status': task['status'],
                        'start_time': task['start_time'],
                        'end_time': task['end_time'],
                        'projects_found': task['projects_found'],
                        'projects_processed': task['projects_processed'],
                        'errors_count': task['errors_count'],
                        'duration': task.get('duration')
                    },
                    'is_active': False
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取任务详情失败: {str(e)}'
        }), 500

@app.route('/api/task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除历史任务记录"""
    try:
        # 不能删除活跃任务
        if task_id in active_tasks:
            return jsonify({
                'success': False,
                'message': '不能删除正在运行的任务'
            }), 400

        success = db_manager.delete_task(task_id)
        if success:
            return jsonify({
                'success': True,
                'message': '任务删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务不存在或删除失败'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除任务失败: {str(e)}'
        }), 500

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
                {'value': 'all', 'label': '全部'},
                {'value': 'games', 'label': '游戏'},
                {'value': 'publishing', 'label': '出版'},
                {'value': 'tablegames', 'label': '桌游'},
                {'value': 'toys', 'label': '潮玩模型'},
                {'value': 'cards', 'label': '卡牌'},
                {'value': 'technology', 'label': '科技'},
                {'value': 'film-video', 'label': '影视'},
                {'value': 'music', 'label': '音乐'},
                {'value': 'activities', 'label': '活动'},
                {'value': 'design', 'label': '设计'},
                {'value': 'curio', 'label': '文玩'},
                {'value': 'home', 'label': '家居'},
                {'value': 'food', 'label': '食品'},
                {'value': 'comics', 'label': '动漫'},
                {'value': 'charity', 'label': '爱心通道'},
                {'value': 'animals', 'label': '动物救助'},
                {'value': 'wishes', 'label': '个人愿望'},
                {'value': 'others', 'label': '其他'}
            ]
        }
    })

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

def find_available_port(start_port=8080, max_port=8090):
    """查找可用端口"""
    import socket

    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue

    return None

if __name__ == '__main__':
    # 确保模板和静态文件目录存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

    # 只在主进程中执行端口检测和启动信息显示
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # 查找可用端口
        port = find_available_port()

        if port is None:
            print("❌ 无法找到可用端口 (8080-8090)")
            print("请手动停止占用端口的程序或使用其他端口")
            exit(1)

        if port != 8080:
            print(f"⚠️  端口8080被占用，使用端口{port}")

        print("🚀 摩点爬虫Web UI启动中...")
        print(f"📱 访问地址: http://localhost:{port}")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)

        # 将端口保存到环境变量，供重启后的进程使用
        os.environ['SPIDER_WEB_PORT'] = str(port)
    else:
        # 重启后的进程从环境变量获取端口
        port = int(os.environ.get('SPIDER_WEB_PORT', 8080))

    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

        if "Address already in use" in str(e):
            print("\n💡 解决方案:")
            print("1. 关闭占用端口的程序")
            print("2. 在macOS中关闭AirPlay接收器:")
            print("   系统偏好设置 -> 通用 -> 隔空投送与接力 -> 关闭AirPlay接收器")
            print("3. 或者修改web_ui/app.py中的端口号")
