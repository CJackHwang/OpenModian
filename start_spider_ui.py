#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩点爬虫管理系统启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动摩点爬虫管理系统"""
    print("🚀 摩点爬虫管理系统启动中...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        sys.exit(1)
    
    # 检查依赖
    try:
        import flask
        import flask_socketio
        import requests
        import bs4  # beautifulsoup4的实际导入名
        import pandas
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 确保必要目录存在
    directories = ['output', 'logs', 'cache', 'database', 'data/raw', 'data/processed', 'data/cache']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构检查完成")
    
    # 启动Web UI
    web_ui_path = Path("web_ui/app.py")
    if not web_ui_path.exists():
        print("❌ 找不到Web UI文件")
        sys.exit(1)
    
    print("🌐 启动Web UI...")
    print("📱 访问地址: http://localhost:8080")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 启动Web UI
        subprocess.run([sys.executable, str(web_ui_path)], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
