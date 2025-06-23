# -*- coding: utf-8 -*-
"""
智能端口管理工具
提供端口检测、进程管理、端口清理等功能
支持跨平台操作（macOS、Linux、Windows）
"""

import socket
import subprocess
import platform
import time
import os
from typing import Optional, List, Tuple


class PortManager:
    """端口管理器"""
    
    def __init__(self, verbose: bool = True):
        """
        初始化端口管理器
        
        Args:
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        self.system = platform.system().lower()
        
    def log(self, message: str, level: str = 'info'):
        """输出日志"""
        if self.verbose:
            icons = {
                'info': '📍',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
                'search': '🔍',
                'stop': '⏹️',
                'idea': '💡'
            }
            icon = icons.get(level, '📍')
            print(f"{icon} {message}")
    
    def is_port_available(self, port: int, host: str = 'localhost') -> bool:
        """
        检查端口是否可用
        
        Args:
            port: 端口号
            host: 主机地址
            
        Returns:
            bool: 端口是否可用
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return True
        except OSError:
            return False
    
    def get_process_using_port(self, port: int) -> List[str]:
        """
        获取占用指定端口的进程ID列表
        
        Args:
            port: 端口号
            
        Returns:
            List[str]: 进程ID列表
        """
        pids = []
        
        try:
            if self.system in ['darwin', 'linux']:
                # macOS 和 Linux 使用 lsof
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    pids = [pid.strip() for pid in result.stdout.strip().split('\n') if pid.strip()]
                    
            elif self.system == 'windows':
                # Windows 使用 netstat
                result = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    
                    for line in lines:
                        if f':{port}' in line and 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                if pid.isdigit():
                                    pids.append(pid)
                                    
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.log(f"获取端口{port}进程信息失败: {e}", 'error')
            
        return pids
    
    def kill_process(self, pid: str, force: bool = False) -> bool:
        """
        停止指定进程
        
        Args:
            pid: 进程ID
            force: 是否强制停止
            
        Returns:
            bool: 是否成功停止
        """
        try:
            if self.system in ['darwin', 'linux']:
                if force:
                    subprocess.run(['kill', '-9', pid], timeout=5, check=True)
                else:
                    subprocess.run(['kill', pid], timeout=5, check=True)
                    
            elif self.system == 'windows':
                subprocess.run(['taskkill', '/PID', pid, '/F'], timeout=5, check=True)
                
            return True
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            self.log(f"停止进程 {pid} 失败: {e}", 'error')
            return False
    
    def kill_processes_on_port(self, port: int, force_after_timeout: bool = True) -> bool:
        """
        停止占用指定端口的所有进程
        
        Args:
            port: 端口号
            force_after_timeout: 优雅停止失败后是否强制停止
            
        Returns:
            bool: 是否成功释放端口
        """
        pids = self.get_process_using_port(port)
        
        if not pids:
            self.log(f"端口{port}未被占用", 'info')
            return True
        
        self.log(f"发现占用端口{port}的进程: {', '.join(pids)}", 'search')
        
        # 尝试优雅停止
        success_count = 0
        for pid in pids:
            self.log(f"尝试优雅停止进程 {pid}", 'stop')
            if self.kill_process(pid, force=False):
                success_count += 1
        
        # 等待进程停止
        time.sleep(2)
        
        # 检查是否还有进程占用端口
        remaining_pids = self.get_process_using_port(port)
        
        if not remaining_pids:
            self.log(f"端口{port}已成功释放", 'success')
            return True
        
        # 如果还有进程，尝试强制停止
        if force_after_timeout:
            self.log(f"优雅停止失败，强制停止剩余进程: {', '.join(remaining_pids)}", 'warning')
            
            for pid in remaining_pids:
                self.log(f"强制停止进程 {pid}", 'stop')
                self.kill_process(pid, force=True)
            
            # 再次等待
            time.sleep(2)
            
            # 最终检查
            final_pids = self.get_process_using_port(port)
            if not final_pids:
                self.log(f"端口{port}已强制释放", 'success')
                return True
            else:
                self.log(f"端口{port}仍被占用，剩余进程: {', '.join(final_pids)}", 'error')
                return False
        else:
            self.log(f"端口{port}仍被占用", 'warning')
            return False
    
    def find_available_port(self, start_port: int = 8080, max_port: int = 8090, host: str = 'localhost') -> Optional[int]:
        """
        查找可用端口
        
        Args:
            start_port: 起始端口
            max_port: 最大端口
            host: 主机地址
            
        Returns:
            Optional[int]: 可用端口号，如果没有则返回None
        """
        for port in range(start_port, max_port + 1):
            if self.is_port_available(port, host):
                return port
        return None
    
    def smart_port_management(self, preferred_port: int = 8080, port_range: Tuple[int, int] = (8080, 8090), 
                            try_kill_processes: bool = True) -> Optional[int]:
        """
        智能端口管理
        
        Args:
            preferred_port: 首选端口
            port_range: 端口范围 (start, end)
            try_kill_processes: 是否尝试停止占用进程
            
        Returns:
            Optional[int]: 可用端口号，如果没有则返回None
        """
        start_port, max_port = port_range
        
        self.log(f"检查首选端口 {preferred_port}...", 'search')
        
        # 首先检查首选端口
        if self.is_port_available(preferred_port):
            self.log(f"端口{preferred_port}可用", 'success')
            return preferred_port
        
        # 尝试释放首选端口
        if try_kill_processes:
            self.log(f"端口{preferred_port}被占用，尝试释放...", 'warning')
            
            if self.kill_processes_on_port(preferred_port):
                if self.is_port_available(preferred_port):
                    self.log(f"成功释放并使用端口{preferred_port}", 'success')
                    return preferred_port
        
        # 寻找备用端口
        self.log(f"无法释放端口{preferred_port}，寻找备用端口...", 'warning')
        
        backup_port = self.find_available_port(start_port, max_port)
        if backup_port and backup_port != preferred_port:
            self.log(f"找到可用端口{backup_port}", 'success')
            return backup_port
        
        self.log(f"在范围 {start_port}-{max_port} 内未找到可用端口", 'error')
        return None


# 便捷函数
def smart_port_management(preferred_port: int = 8080, port_range: Tuple[int, int] = (8080, 8090), 
                         verbose: bool = True) -> Optional[int]:
    """
    智能端口管理便捷函数
    
    Args:
        preferred_port: 首选端口
        port_range: 端口范围
        verbose: 是否输出详细日志
        
    Returns:
        Optional[int]: 可用端口号
    """
    manager = PortManager(verbose=verbose)
    return manager.smart_port_management(preferred_port, port_range)


def is_port_available(port: int, host: str = 'localhost') -> bool:
    """
    检查端口是否可用的便捷函数
    
    Args:
        port: 端口号
        host: 主机地址
        
    Returns:
        bool: 端口是否可用
    """
    manager = PortManager(verbose=False)
    return manager.is_port_available(port, host)


def kill_processes_on_port(port: int, verbose: bool = True) -> bool:
    """
    停止占用端口进程的便捷函数
    
    Args:
        port: 端口号
        verbose: 是否输出详细日志
        
    Returns:
        bool: 是否成功释放端口
    """
    manager = PortManager(verbose=verbose)
    return manager.kill_processes_on_port(port)
