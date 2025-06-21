# -*- coding: utf-8 -*-
"""
WebSocket事件处理器
处理客户端连接、断开、心跳等事件
"""

from flask_socketio import emit
from flask import request
from datetime import datetime
import traceback


def register_websocket_handlers(socketio):
    """注册WebSocket事件处理器"""
    
    @socketio.event
    def connect():
        """WebSocket连接"""
        try:
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
            user_agent = request.environ.get('HTTP_USER_AGENT', 'unknown')

            print(f'✅ 客户端已连接: {request.sid}')
            print(f'📍 客户端IP: {client_ip}')

            # 记录详细的连接日志
            from core.logging import log_webui, log_system
            log_webui('info', f'新客户端连接: {request.sid}', 'websocket')
            log_webui('info', f'客户端IP地址: {client_ip}', 'websocket')
            log_webui('debug', f'用户代理: {user_agent[:100]}...', 'websocket')
            log_system('info', f'WebSocket连接建立，当前活跃连接数: {len(socketio.server.manager.rooms.get("/", {}))}', 'websocket')

            emit('connected', {
                'message': '连接成功',
                'sid': request.sid,
                'timestamp': datetime.now().isoformat(),
                'server_info': {
                    'version': '2.0.0',
                    'features': ['real_time_logs', 'task_monitoring', 'data_management']
                }
            })
        except Exception as e:
            print(f"❌ 连接处理错误: {e}")
            from core.logging import log_system
            log_system('error', f'WebSocket连接处理错误: {str(e)}', 'websocket')
    
    @socketio.event
    def disconnect(reason=None):
        """WebSocket断开连接"""
        try:
            print(f'🔌 客户端已断开: {request.sid}, 原因: {reason}')

            # 记录断开连接日志
            from core.logging import log_webui, log_system
            log_webui('info', f'客户端断开连接: {request.sid}', 'websocket')
            log_webui('info', f'断开原因: {reason or "未知"}', 'websocket')

            remaining_connections = len(socketio.server.manager.rooms.get("/", {})) - 1
            log_system('info', f'WebSocket连接断开，剩余活跃连接数: {remaining_connections}', 'websocket')

        except Exception as e:
            print(f'🔌 客户端已断开 (获取SID失败: {e})')
            from core.logging import log_system
            log_system('warning', f'断开连接处理异常: {str(e)}', 'websocket')
    
    @socketio.on_error_default
    def default_error_handler(e):
        """默认错误处理器"""
        try:
            print(f"⚠️  SocketIO错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            traceback.print_exc()
        except Exception as handler_error:
            print(f"❌ 错误处理器本身出错: {handler_error}")
        return False
    
    @socketio.on('ping')
    def handle_ping():
        """心跳检测"""
        try:
            emit('pong', {'timestamp': datetime.now().isoformat()})
        except Exception as e:
            print(f"❌ 心跳检测错误: {e}")
    
    @socketio.on('connect_error')
    def handle_connect_error(data):
        """连接错误处理"""
        try:
            print(f"🔥 连接错误: {data}")
        except Exception as e:
            print(f"❌ 连接错误处理失败: {e}")
    
    @socketio.on('task_subscribe')
    def handle_task_subscribe(data):
        """订阅任务更新"""
        try:
            task_id = data.get('task_id')
            if task_id:
                # 将客户端加入任务房间
                from flask_socketio import join_room
                join_room(f"task_{task_id}")
                emit('task_subscribed', {'task_id': task_id, 'status': 'subscribed'})
                print(f"📡 客户端 {request.sid} 订阅任务 {task_id}")
        except Exception as e:
            print(f"❌ 任务订阅错误: {e}")
    
    @socketio.on('task_unsubscribe')
    def handle_task_unsubscribe(data):
        """取消订阅任务更新"""
        try:
            task_id = data.get('task_id')
            if task_id:
                # 将客户端移出任务房间
                from flask_socketio import leave_room
                leave_room(f"task_{task_id}")
                emit('task_unsubscribed', {'task_id': task_id, 'status': 'unsubscribed'})
                print(f"📡 客户端 {request.sid} 取消订阅任务 {task_id}")
        except Exception as e:
            print(f"❌ 取消任务订阅错误: {e}")
    
    @socketio.on('system_status_request')
    def handle_system_status_request():
        """系统状态请求"""
        try:
            # 这里可以发送系统状态信息
            status = {
                'timestamp': datetime.now().isoformat(),
                'server_status': 'running',
                'connected_clients': len(socketio.server.manager.rooms.get('/', {}))
            }
            emit('system_status', status)
        except Exception as e:
            print(f"❌ 系统状态请求错误: {e}")

    @socketio.on('log_subscribe')
    def handle_log_subscribe(data):
        """订阅日志更新"""
        try:
            log_type = data.get('log_type', 'all')  # all, system, spider, webui
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')

            # 将客户端加入日志房间
            from flask_socketio import join_room
            room_name = f"logs_{log_type}"
            join_room(room_name)

            emit('log_subscribed', {
                'log_type': log_type,
                'room': room_name,
                'status': 'subscribed',
                'timestamp': datetime.now().isoformat()
            })

            print(f"📡 客户端 {request.sid} 订阅日志 {log_type}")

            # 记录订阅日志
            from core.logging import log_webui, log_system
            log_webui('info', f'客户端订阅日志: {log_type}', 'websocket')
            log_webui('debug', f'订阅客户端: {request.sid} (IP: {client_ip})', 'websocket')
            log_system('info', f'日志订阅请求: 类型={log_type}, 房间={room_name}', 'websocket')

            # 发送最近的日志历史
            if hasattr(socketio, 'log_service') and socketio.log_service:
                recent_logs = socketio.log_service.get_logs(
                    log_type=log_type,
                    limit=50  # 发送最近50条日志
                )

                emit('log_history', {
                    'log_type': log_type,
                    'logs': recent_logs,
                    'count': len(recent_logs),
                    'timestamp': datetime.now().isoformat()
                })

                log_system('info', f'发送历史日志: {len(recent_logs)}条 (类型: {log_type})', 'websocket')

        except Exception as e:
            print(f"❌ 日志订阅错误: {e}")
            from core.logging import log_system
            log_system('error', f'日志订阅处理错误: {str(e)}', 'websocket')

    @socketio.on('log_unsubscribe')
    def handle_log_unsubscribe(data):
        """取消订阅日志更新"""
        try:
            log_type = data.get('log_type', 'all')

            # 将客户端移出日志房间
            from flask_socketio import leave_room
            room_name = f"logs_{log_type}"
            leave_room(room_name)

            emit('log_unsubscribed', {
                'log_type': log_type,
                'room': room_name,
                'status': 'unsubscribed'
            })

            print(f"📡 客户端 {request.sid} 取消订阅日志 {log_type}")

        except Exception as e:
            print(f"❌ 取消日志订阅错误: {e}")

    @socketio.on('log_request')
    def handle_log_request(data):
        """请求日志数据"""
        try:
            log_type = data.get('log_type', 'all')
            limit = data.get('limit', 100)
            level_filter = data.get('level', 'all')
            search_term = data.get('search', '')

            # 从日志服务获取数据
            if hasattr(socketio, 'log_service') and socketio.log_service:
                logs = socketio.log_service.get_logs(
                    log_type=log_type,
                    limit=limit,
                    level_filter=level_filter,
                    search_term=search_term
                )

                emit('log_response', {
                    'log_type': log_type,
                    'logs': logs,
                    'count': len(logs),
                    'filters': {
                        'level': level_filter,
                        'search': search_term
                    }
                })
            else:
                emit('log_response', {
                    'log_type': log_type,
                    'logs': [],
                    'count': 0,
                    'error': '日志服务未初始化'
                })

        except Exception as e:
            print(f"❌ 日志请求错误: {e}")
            emit('log_response', {
                'log_type': log_type,
                'logs': [],
                'count': 0,
                'error': str(e)
            })

    @socketio.on('log_clear')
    def handle_log_clear(data):
        """清空日志缓存"""
        try:
            log_type = data.get('log_type', 'all')

            # 清空日志服务缓存
            if hasattr(socketio, 'log_service') and socketio.log_service:
                socketio.log_service.clear_cache(log_type)

                # 通知所有订阅者
                room_name = f"logs_{log_type}"
                socketio.emit('log_cleared', {
                    'log_type': log_type,
                    'timestamp': datetime.now().isoformat()
                }, room=room_name)

                print(f"🗑️ 清空日志缓存: {log_type}")

        except Exception as e:
            print(f"❌ 清空日志错误: {e}")

    @socketio.on('log_manual')
    def handle_log_manual(data):
        """手动发送日志"""
        try:
            log_type = data.get('log_type', 'system')
            level = data.get('level', 'info')
            message = data.get('message', '')
            source = data.get('source', 'manual')

            # 添加到日志服务
            if hasattr(socketio, 'log_service') and socketio.log_service:
                socketio.log_service.add_manual_log(log_type, level, message, source)
                print(f"📝 手动日志: [{level.upper()}] {message}")

        except Exception as e:
            print(f"❌ 手动日志错误: {e}")


def emit_task_update(socketio, task_id, stats):
    """发送任务更新到订阅的客户端"""
    try:
        socketio.emit('task_update', {
            'task_id': task_id,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }, room=f"task_{task_id}")
    except Exception as e:
        print(f"❌ 发送任务更新失败: {e}")


def emit_system_notification(socketio, message, level='info'):
    """发送系统通知到所有客户端"""
    try:
        socketio.emit('system_notification', {
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"❌ 发送系统通知失败: {e}")
