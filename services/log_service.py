# -*- coding: utf-8 -*-
"""
实时日志服务
提供日志文件监控、实时推送和缓存管理功能
"""

import os
import time
import threading
from pathlib import Path
from datetime import datetime
from collections import deque
import re
import glob
from typing import Dict, List, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LogEntry:
    """日志条目"""
    
    def __init__(self, timestamp: str, level: str, message: str, source: str = ""):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.source = source
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'level': self.level,
            'message': self.message,
            'source': self.source,
            'created_at': self.created_at.isoformat()
        }
    
    def matches_filter(self, level_filter: str = 'all', search_term: str = '') -> bool:
        """检查是否匹配过滤条件"""
        # 级别过滤
        if level_filter != 'all' and self.level.lower() != level_filter.lower():
            return False
        
        # 搜索过滤
        if search_term and search_term.lower() not in self.message.lower():
            return False
        
        return True


class LogFileHandler(FileSystemEventHandler):
    """日志文件监控处理器"""
    
    def __init__(self, log_service):
        self.log_service = log_service
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory and event.src_path.endswith('.log'):
            self.log_service._handle_file_change(event.src_path)
    
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory and event.src_path.endswith('.log'):
            self.log_service._handle_file_change(event.src_path)


class RealTimeLogService:
    """实时日志服务"""
    
    def __init__(self, socketio=None, max_cache_size: int = 1000):
        self.socketio = socketio
        self.max_cache_size = max_cache_size

        # 日志缓存 - 按类型分类
        self.log_cache: Dict[str, deque] = {
            'system': deque(maxlen=max_cache_size),
            'spider': deque(maxlen=max_cache_size),
            'webui': deque(maxlen=max_cache_size),
            'all': deque(maxlen=max_cache_size * 3)
        }

        # 文件监控
        self.observer = Observer()
        self.handler = LogFileHandler(self)
        self.is_monitoring = False

        # 订阅管理
        self.subscribers: Dict[str, List[Callable]] = {
            'system': [],
            'spider': [],
            'webui': [],
            'all': []
        }

        # 文件位置记录（用于增量读取）
        self.file_positions: Dict[str, int] = {}

        # 定时刷新线程
        self.refresh_thread = None
        self.refresh_stop_flag = threading.Event()

        # 启动监控
        self.start_monitoring()

        # 启动定时刷新
        self.start_refresh_timer()
    
    def start_monitoring(self):
        """启动日志文件监控"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                logs_dir.mkdir(parents=True, exist_ok=True)
                
            # 为每个日志类型创建目录
            for log_type in ['system', 'spider', 'webui']:
                log_type_dir = logs_dir / log_type
                log_type_dir.mkdir(exist_ok=True)
                
                # 监控目录
                self.observer.schedule(self.handler, str(log_type_dir), recursive=False)
            
            self.observer.start()
            self.is_monitoring = True
            
            # 初始加载现有日志
            self._load_existing_logs()
            
            print("✅ 实时日志监控已启动")
            
        except Exception as e:
            print(f"❌ 启动日志监控失败: {e}")
    
    def stop_monitoring(self):
        """停止日志文件监控"""
        if self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            print("🛑 实时日志监控已停止")

        # 停止定时刷新
        if self.refresh_thread:
            self.refresh_stop_flag.set()
            self.refresh_thread.join()
            print("🛑 定时日志刷新已停止")
    
    def _load_existing_logs(self):
        """加载现有日志文件"""
        for log_type in ['system', 'spider', 'webui']:
            log_dir = Path("logs") / log_type
            if not log_dir.exists():
                continue
                
            # 获取最新的日志文件
            log_files = sorted(
                glob.glob(str(log_dir / "*.log")),
                key=os.path.getmtime,
                reverse=True
            )
            
            # 只读取最新的几个文件，避免启动时加载过多数据
            for log_file in log_files[:3]:
                self._read_log_file(log_file, log_type, initial_load=True)
    
    def _handle_file_change(self, file_path: str):
        """处理文件变化"""
        try:
            # 确定日志类型
            log_type = self._get_log_type_from_path(file_path)
            if not log_type:
                print(f"⚠️ 无法确定日志类型: {file_path}")
                return

            print(f"📝 检测到日志文件变化: {file_path} (类型: {log_type})")

            # 增量读取新内容
            self._read_log_file(file_path, log_type, initial_load=False)

        except Exception as e:
            print(f"❌ 处理日志文件变化失败 {file_path}: {e}")
    
    def _get_log_type_from_path(self, file_path: str) -> Optional[str]:
        """从文件路径确定日志类型"""
        path = Path(file_path)
        if 'system' in str(path):
            return 'system'
        elif 'spider' in str(path):
            return 'spider'
        elif 'webui' in str(path):
            return 'webui'
        return None
    
    def _read_log_file(self, file_path: str, log_type: str, initial_load: bool = False):
        """读取日志文件"""
        try:
            # 获取文件当前位置
            current_pos = self.file_positions.get(file_path, 0)

            with open(file_path, 'r', encoding='utf-8') as f:
                # 如果是增量读取，跳到上次位置
                if not initial_load and current_pos > 0:
                    f.seek(current_pos)

                lines = f.readlines()
                new_pos = f.tell()

                # 更新文件位置
                self.file_positions[file_path] = new_pos

                # 处理新行
                new_entries_count = 0
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    log_entry = self._parse_log_line(line, file_path)
                    if log_entry:
                        self._add_log_entry(log_entry, log_type)
                        new_entries_count += 1

                        # 如果不是初始加载，实时推送
                        if not initial_load:
                            self._broadcast_log_entry(log_entry, log_type)
                            print(f"📡 实时推送日志: [{log_entry.level}] {log_entry.message[:50]}...")

                if not initial_load and new_entries_count > 0:
                    print(f"📝 处理了 {new_entries_count} 条新日志 (类型: {log_type})")

        except Exception as e:
            print(f"❌ 读取日志文件失败 {file_path}: {e}")
    
    def _parse_log_line(self, line: str, file_path: str) -> Optional[LogEntry]:
        """解析日志行"""
        try:
            # 尝试解析标准格式: [TIMESTAMP] [LEVEL] MESSAGE
            pattern = r'\[([^\]]+)\]\s*\[([^\]]+)\]\s*(.*)'
            match = re.match(pattern, line)
            
            if match:
                timestamp_str, level, message = match.groups()
                return LogEntry(
                    timestamp=timestamp_str,
                    level=level.strip(),
                    message=message.strip(),
                    source=os.path.basename(file_path)
                )
            else:
                # 如果不匹配标准格式，作为普通消息处理
                return LogEntry(
                    timestamp=datetime.now().strftime('%H:%M:%S'),
                    level='info',
                    message=line,
                    source=os.path.basename(file_path)
                )
        except Exception:
            return None
    
    def _add_log_entry(self, log_entry: LogEntry, log_type: str):
        """添加日志条目到缓存"""
        self.log_cache[log_type].append(log_entry)
        self.log_cache['all'].append(log_entry)
    
    def _broadcast_log_entry(self, log_entry: LogEntry, log_type: str):
        """广播日志条目"""
        if self.socketio:
            try:
                # 发送到特定类型的房间
                self.socketio.emit('log_update', {
                    'log_type': log_type,
                    'entry': log_entry.to_dict()
                }, room=f'logs_{log_type}')
                
                # 发送到全部日志房间
                self.socketio.emit('log_update', {
                    'log_type': 'all',
                    'entry': log_entry.to_dict()
                }, room='logs_all')
                
            except Exception as e:
                print(f"广播日志条目失败: {e}")
    
    def get_logs(self, log_type: str = 'all', limit: int = 100, 
                 level_filter: str = 'all', search_term: str = '') -> List[Dict]:
        """获取日志"""
        if log_type not in self.log_cache:
            return []
        
        logs = []
        cache = self.log_cache[log_type]
        
        # 从最新开始遍历
        for log_entry in reversed(cache):
            if log_entry.matches_filter(level_filter, search_term):
                logs.append(log_entry.to_dict())
                
                if len(logs) >= limit:
                    break
        
        return logs
    
    def add_manual_log(self, log_type: str, level: str, message: str, source: str = "manual"):
        """手动添加日志条目"""
        log_entry = LogEntry(
            timestamp=datetime.now().strftime('%H:%M:%S'),
            level=level,
            message=message,
            source=source
        )
        
        self._add_log_entry(log_entry, log_type)
        self._broadcast_log_entry(log_entry, log_type)
    
    def clear_cache(self, log_type: str = 'all'):
        """清空日志缓存"""
        if log_type == 'all':
            for cache in self.log_cache.values():
                cache.clear()
        elif log_type in self.log_cache:
            self.log_cache[log_type].clear()
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            log_type: len(cache)
            for log_type, cache in self.log_cache.items()
        }

    def start_refresh_timer(self):
        """启动定时刷新线程"""
        def refresh_worker():
            while not self.refresh_stop_flag.is_set():
                try:
                    # 每2秒强制检查一次所有日志文件
                    self._force_refresh_all_logs()
                    self.refresh_stop_flag.wait(2)  # 等待2秒或停止信号
                except Exception as e:
                    print(f"❌ 定时刷新错误: {e}")
                    self.refresh_stop_flag.wait(5)  # 出错时等待5秒

        self.refresh_thread = threading.Thread(target=refresh_worker, daemon=True)
        self.refresh_thread.start()
        print("⏰ 定时日志刷新已启动 (间隔: 2秒)")

    def _force_refresh_all_logs(self):
        """强制刷新所有日志文件"""
        try:
            for log_type in ['system', 'spider', 'webui']:
                log_dir = Path("logs") / log_type
                if not log_dir.exists():
                    continue

                # 获取最新的日志文件
                log_files = sorted(
                    glob.glob(str(log_dir / "*.log")),
                    key=os.path.getmtime,
                    reverse=True
                )

                # 只检查最新的文件
                if log_files:
                    latest_file = log_files[0]
                    self._read_log_file(latest_file, log_type, initial_load=False)

        except Exception as e:
            print(f"❌ 强制刷新日志失败: {e}")
