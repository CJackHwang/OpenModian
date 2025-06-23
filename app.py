# -*- coding: utf-8 -*-
"""
摩点爬虫Web UI主应用 - 重构版
基于Flask的可视化工作流管理界面
采用工程化标准架构，保持与原版本功能完全一致
"""

import os
import sys

# 导入eventlet并进行monkey patching以支持WebSocket
# 注释掉monkey_patch避免导入时阻塞
# try:
#     import eventlet
#     eventlet.monkey_patch()
#     print("✅ Eventlet已加载，WebSocket支持已启用")
# except ImportError:
#     print("⚠️  Eventlet未安装，将使用threading模式（无WebSocket支持）")

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

# 导入重构后的模块
from core.monitors import ScheduledTaskMonitor
from core.logging import init_system_logger, log_system
from services import SpiderService
from services.log_service import RealTimeLogService
from api.middleware import setup_error_handlers
from api.routes import (
    register_spider_routes,
    register_data_routes,
    register_task_routes,
    register_system_routes,
    register_settings_routes
)
from api.routes.watch_routes import register_watch_routes
from api.websocket import register_websocket_handlers
from data.database.db_manager import DatabaseManager
from spider.scheduler import TaskScheduler
from spider.core import SpiderCore
from spider.config import SpiderConfig


class RefactoredSpiderApp:
    """重构版爬虫应用 - 工程化架构"""
    
    def __init__(self):
        self.app = None
        self.socketio = None
        self.db_manager = None
        self.task_scheduler = None
        self.spider_service = None
        self.log_service = None

        self._setup_application()
    
    def _setup_application(self):
        """设置应用"""
        # 创建Flask应用
        vue_dist_path = os.path.join(project_root, "web_ui_vue", "dist")
        self.app = Flask(__name__, static_folder=vue_dist_path, static_url_path='')
        self.app.config['SECRET_KEY'] = 'modian_spider_secret_key_2024'
        
        # 设置CORS
        CORS(self.app)
        
        # 设置SocketIO
        self._setup_socketio()
        
        # 设置数据库
        self._setup_database()
        
        # 设置任务调度器
        self._setup_task_scheduler()
        
        # 设置服务层
        self._setup_services()

        # 设置日志服务
        self._setup_log_service()

        # 设置错误处理
        setup_error_handlers(self.app)

        # 注册路由
        self._register_routes()

        # 注册WebSocket事件
        register_websocket_handlers(self.socketio)
    
    def _setup_socketio(self):
        """设置SocketIO"""
        try:
            import eventlet
            async_mode = 'eventlet'
            print("🔌 使用eventlet模式，完整WebSocket支持")
        except ImportError:
            async_mode = 'threading'
            print("🔌 使用threading模式，仅polling传输")
        
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode=async_mode,
            logger=False,
            engineio_logger=False,
            ping_timeout=60,
            ping_interval=25,
            max_http_buffer_size=1000000,
            allow_upgrades=True,
            transports=['websocket', 'polling'] if async_mode == 'eventlet' else ['polling']
        )
    
    def _setup_database(self):
        """设置数据库"""
        db_path = os.path.join(project_root, "data", "database", "modian_data.db")
        self.db_manager = DatabaseManager(db_path)
    
    def _setup_task_scheduler(self):
        """设置任务调度器"""
        def create_spider_instance():
            """爬虫实例工厂函数"""
            config = SpiderConfig.load_from_yaml()
            monitor = ScheduledTaskMonitor()
            return SpiderCore(config, web_monitor=monitor, db_manager=self.db_manager)
        
        self.task_scheduler = TaskScheduler(
            db_manager=self.db_manager,
            spider_factory=create_spider_instance
        )
        # 延迟启动调度器，避免导入时阻塞
        # self.task_scheduler.start_scheduler()
    
    def _setup_services(self):
        """设置服务层"""
        self.spider_service = SpiderService(
            db_manager=self.db_manager,
            task_scheduler=self.task_scheduler,
            socketio=self.socketio
        )

    def _setup_log_service(self):
        """设置日志服务"""
        try:
            self.log_service = RealTimeLogService(socketio=self.socketio)

            # 将日志服务绑定到socketio实例，供WebSocket处理器使用
            self.socketio.log_service = self.log_service

            # 初始化系统日志记录器
            init_system_logger(self.log_service)

            print("✅ 实时日志服务已启动")
            log_system('info', '实时日志服务已启动', 'app')
        except Exception as e:
            print(f"❌ 启动日志服务失败: {e}")
            self.log_service = None
    
    def _register_routes(self):
        """注册路由"""
        # Vue前端路由
        @self.app.route('/')
        def index():
            return self._serve_vue_file('index.html')
        
        @self.app.route('/<path:path>')
        def vue_routes(path):
            if '.' in path:
                try:
                    return self._serve_vue_file(path)
                except:
                    pass
            return self._serve_vue_file('index.html')
        
        # 注册API路由
        register_spider_routes(self.app, self.spider_service)
        register_data_routes(self.app, self.db_manager)
        register_task_routes(self.app, self.spider_service, self.task_scheduler, self.db_manager)
        register_system_routes(self.app, self.db_manager)
        register_settings_routes(self.app, self.db_manager)
        register_watch_routes(self.app, self.db_manager)
    
    def _serve_vue_file(self, filename):
        """服务Vue文件"""
        vue_dist_path = os.path.join(project_root, "web_ui_vue", "dist")
        if os.path.exists(vue_dist_path):
            return send_from_directory(vue_dist_path, filename)
        else:
            return jsonify({
                'error': 'Vue前端未构建',
                'message': '请运行 python3 start_vue_ui.py build 构建前端'
            }), 404
    
    def start_scheduler(self):
        """启动任务调度器"""
        if self.task_scheduler and not hasattr(self.task_scheduler, '_scheduler_started'):
            self.task_scheduler.start_scheduler()
            self.task_scheduler._scheduler_started = True

    def run(self, host='0.0.0.0', port=8080, debug=True):
        """运行应用"""
        try:
            # 启动任务调度器
            self.start_scheduler()

            print("🚀 摩点爬虫Web UI启动中... (重构版)")
            print(f"📱 访问地址: http://localhost:{port}")
            print("⏹️  按 Ctrl+C 停止服务")
            print("-" * 50)

            # 记录启动日志
            log_system('info', f'摩点爬虫Web UI启动完成，监听端口: {port}', 'app')
            log_system('info', f'访问地址: http://localhost:{port}', 'app')
            log_system('info', f'调试模式: {"开启" if debug else "关闭"}', 'app')
            log_system('info', f'监听地址: {host}', 'app')

            self.socketio.run(self.app, debug=debug, host=host, port=port)
        except KeyboardInterrupt:
            print("\n👋 服务已停止")
            log_system('warning', '服务被用户手动停止', 'app')
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            log_system('error', f'应用启动失败: {str(e)}', 'app')


# 导入端口管理工具
try:
    from utils.port_manager import smart_port_management
except ImportError:
    # 如果导入失败，使用简化版本
    def smart_port_management(preferred_port=8080, port_range=(8080, 8090)):
        """简化版端口管理（备用）"""
        import socket

        start_port, max_port = port_range

        # 检查首选端口
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', preferred_port))
                return preferred_port
        except OSError:
            pass

        # 寻找备用端口
        for port in range(start_port, max_port + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue

        return None


# 创建应用实例
refactored_app = RefactoredSpiderApp()

# 导出Flask应用和SocketIO实例，用于外部访问
app = refactored_app.app
socketio = refactored_app.socketio

# 设置全局socketio实例，确保WebSpiderMonitor能够访问
import sys
sys.modules[__name__].socketio = socketio

if __name__ == '__main__':
    print("🚀 摩点爬虫Web UI启动中...")
    print("🔧 正在进行智能端口管理...")
    print("-" * 50)

    # 使用智能端口管理
    port = smart_port_management(preferred_port=8080, port_range=(8080, 8090))

    if port is None:
        print("❌ 无法找到可用端口 (8080-8090)")
        print("💡 建议操作:")
        print("   1. 手动停止占用端口的程序")
        print("   2. 重启系统释放端口")
        print("   3. 使用其他端口范围")
        exit(1)

    if port != 8080:
        print(f"📍 使用端口: {port} (首选端口8080不可用)")
    else:
        print(f"📍 使用首选端口: {port}")

    print("-" * 50)

    # 运行应用
    refactored_app.run(port=port)
