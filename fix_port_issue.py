#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口问题诊断和解决脚本
"""

import socket
import subprocess
import sys
import os

def check_port_usage(port):
    """检查端口是否被占用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return False  # 端口可用
    except OSError:
        return True  # 端口被占用

def find_process_using_port(port):
    """查找占用端口的进程"""
    try:
        # 在macOS上使用lsof命令
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except FileNotFoundError:
        # 如果lsof不可用，尝试netstat
        try:
            result = subprocess.run(['netstat', '-an'], 
                                  capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTEN' in line:
                    return line
        except:
            pass
    return None

def find_available_ports(start_port=8080, count=10):
    """查找可用端口"""
    available_ports = []
    
    for port in range(start_port, start_port + 100):
        if not check_port_usage(port):
            available_ports.append(port)
            if len(available_ports) >= count:
                break
    
    return available_ports

def kill_process_on_port(port):
    """尝试终止占用端口的进程"""
    try:
        # 获取占用端口的进程ID
        result = subprocess.run(['lsof', '-t', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"尝试终止进程 {pid}...")
                    subprocess.run(['kill', pid])
            return True
    except:
        pass
    return False

def show_airplay_solution():
    """显示AirPlay解决方案"""
    print("\n🍎 macOS AirPlay接收器解决方案:")
    print("1. 打开 系统偏好设置 (System Preferences)")
    print("2. 点击 通用 (General)")
    print("3. 点击 隔空投送与接力 (AirDrop & Handoff)")
    print("4. 关闭 AirPlay接收器 (AirPlay Receiver)")
    print("\n或者使用命令行:")
    print("sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.AirPlayXPCHelper.plist")

def main():
    """主函数"""
    print("🔍 摩点爬虫端口问题诊断工具")
    print("=" * 50)
    
    # 检查常用端口
    ports_to_check = [5000, 8080, 8000, 3000, 8888]
    
    print("检查端口占用情况:")
    for port in ports_to_check:
        is_used = check_port_usage(port)
        status = "❌ 被占用" if is_used else "✅ 可用"
        print(f"  端口 {port}: {status}")
        
        if is_used:
            process_info = find_process_using_port(port)
            if process_info:
                print(f"    占用进程: {process_info.strip()}")
    
    # 检查5000端口的特殊情况
    if check_port_usage(5000):
        print(f"\n⚠️  端口5000被占用，这通常是macOS的AirPlay接收器")
        show_airplay_solution()
    
    # 查找可用端口
    print(f"\n🔍 查找可用端口:")
    available_ports = find_available_ports()
    if available_ports:
        print(f"  可用端口: {', '.join(map(str, available_ports[:5]))}")
        recommended_port = available_ports[0]
        print(f"  推荐使用: {recommended_port}")
        
        # 询问是否要更新配置
        print(f"\n是否要将Web UI端口更改为 {recommended_port}? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes', '是']:
            update_port_config(recommended_port)
    else:
        print("  ❌ 未找到可用端口")
    
    print(f"\n💡 解决方案总结:")
    print(f"1. 使用可用端口 (推荐)")
    print(f"2. 关闭AirPlay接收器 (如果占用5000端口)")
    print(f"3. 终止占用端口的进程")
    print(f"4. 重启系统")

def update_port_config(new_port):
    """更新端口配置"""
    try:
        app_file = "web_ui/app.py"
        
        if not os.path.exists(app_file):
            print(f"❌ 找不到文件: {app_file}")
            return
        
        # 读取文件
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换端口
        import re
        
        # 替换socketio.run中的端口
        content = re.sub(
            r'socketio\.run\(app,.*?port=\d+\)',
            f'socketio.run(app, debug=True, host=\'0.0.0.0\', port={new_port})',
            content
        )
        
        # 替换访问地址提示
        content = re.sub(
            r'http://localhost:\d+',
            f'http://localhost:{new_port}',
            content
        )
        
        # 写回文件
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新端口配置为: {new_port}")
        print(f"📱 新的访问地址: http://localhost:{new_port}")
        
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")

if __name__ == "__main__":
    main()
