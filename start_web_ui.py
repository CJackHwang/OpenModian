#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩点爬虫Web UI启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_socketio
        print("✓ Flask依赖已安装")
        return True
    except ImportError:
        print("✗ Flask依赖未安装")
        return False

def install_requirements():
    """安装依赖"""
    print("正在安装Web UI依赖...")
    
    requirements_file = Path(__file__).parent / "web_ui" / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False

def start_web_ui():
    """启动Web UI"""
    web_ui_dir = Path(__file__).parent / "web_ui"
    app_file = web_ui_dir / "app.py"
    
    if not app_file.exists():
        print("✗ Web UI文件不存在")
        return False
    
    print("启动摩点爬虫Web UI...")
    print("访问地址: http://localhost:8080")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 切换到web_ui目录
        os.chdir(web_ui_dir)
        
        # 启动Flask应用
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("摩点爬虫Web UI启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        print("\n需要安装Web UI依赖，是否现在安装？(y/n): ", end="")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes', '是']:
            if not install_requirements():
                print("依赖安装失败，请手动安装")
                return
        else:
            print("请先安装依赖: pip install -r web_ui/requirements.txt")
            return
    
    # 启动Web UI
    start_web_ui()

if __name__ == "__main__":
    main()
