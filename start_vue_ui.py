#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩点爬虫Vue UI启动脚本
同时启动Flask后端和Vue前端开发服务器
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def check_node_installed():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Node.js已安装: {version}")
            return True
        else:
            print("✗ Node.js未安装")
            return False
    except FileNotFoundError:
        print("✗ Node.js未安装")
        return False

def check_npm_installed():
    """检查npm是否安装"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ npm已安装: {version}")
            return True
        else:
            print("✗ npm未安装")
            return False
    except FileNotFoundError:
        print("✗ npm未安装")
        return False

def install_frontend_dependencies():
    """安装前端依赖"""
    vue_dir = Path(__file__).parent / "web_ui_vue"
    
    if not vue_dir.exists():
        print("✗ Vue项目目录不存在")
        return False
    
    print("正在安装前端依赖...")
    try:
        result = subprocess.run(
            ['npm', 'install'],
            cwd=vue_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ 前端依赖安装完成")
            return True
        else:
            print(f"✗ 前端依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 前端依赖安装失败: {e}")
        return False

def check_backend_dependencies():
    """检查后端依赖"""
    try:
        import flask
        import flask_socketio
        print("✓ Flask后端依赖已安装")
        return True
    except ImportError:
        print("✗ Flask后端依赖未安装")
        return False

def install_backend_dependencies():
    """安装后端依赖"""
    print("正在安装后端依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ 后端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 后端依赖安装失败: {e}")
        return False

def build_frontend():
    """构建Vue前端"""
    print("🔨 构建Vue前端...")

    vue_dir = Path(__file__).parent / "web_ui_vue"

    if not vue_dir.exists():
        print("✗ Vue项目目录不存在")
        return False

    try:
        # 构建Vue应用
        result = subprocess.run([
            'npm', 'run', 'build'
        ], cwd=vue_dir, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Vue前端构建完成")
            return True
        else:
            print(f"✗ Vue前端构建失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Vue前端构建失败: {e}")
        return False

def start_integrated_server():
    """启动集成服务器（Flask + Vue）"""
    print("🚀 启动集成服务器...")

    project_root = Path(__file__).parent
    app_file = project_root / "app.py"

    if not app_file.exists():
        print("✗ Flask应用文件不存在")
        return False

    try:
        # 设置环境变量
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['FLASK_DEBUG'] = '1'

        # 启动Flask应用
        subprocess.run([
            sys.executable, str(app_file)
        ], cwd=project_root, env=env)

    except KeyboardInterrupt:
        print("\n集成服务器已停止")
    except Exception as e:
        print(f"✗ 集成服务器启动失败: {e}")
        return False

    return True



def start_backend_dev():
    """启动Flask后端开发服务器"""
    print("🚀 启动Flask后端开发服务器...")

    project_root = Path(__file__).parent
    app_file = project_root / "app.py"

    if not app_file.exists():
        print("✗ Flask应用文件不存在")
        return False

    try:
        # 设置环境变量
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        env['FLASK_DEBUG'] = '1'

        # 启动Flask应用（让Flask自己处理端口检测）
        subprocess.run([
            sys.executable, str(app_file)
        ], cwd=project_root, env=env)

    except KeyboardInterrupt:
        print("\n后端开发服务器已停止")
    except Exception as e:
        print(f"✗ 后端开发服务器启动失败: {e}")
        return False

    return True

def find_backend_port():
    """查找后端实际使用的端口"""
    import socket

    # 检查常用端口
    for port in [8080, 8081, 8082, 8083]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                # 端口被占用，可能是我们的后端
                return port
        except:
            continue

    return 8080  # 默认端口

def start_frontend_dev():
    """启动Vue前端开发服务器"""
    print("🚀 启动Vue前端开发服务器...")

    vue_dir = Path(__file__).parent / "web_ui_vue"

    if not vue_dir.exists():
        print("✗ Vue项目目录不存在")
        return False

    # 等待后端启动，然后检测端口
    print("⏳ 等待后端启动...")
    time.sleep(3)

    backend_port = find_backend_port()
    print(f"🔍 检测到后端端口: {backend_port}")

    try:
        # 设置环境变量
        env = os.environ.copy()
        env['BACKEND_URL'] = f'http://localhost:{backend_port}'

        # 启动Vue开发服务器
        subprocess.run([
            'npm', 'run', 'dev'
        ], cwd=vue_dir, env=env)

    except KeyboardInterrupt:
        print("\n前端开发服务器已停止")
    except Exception as e:
        print(f"✗ 前端开发服务器启动失败: {e}")
        return False

    return True

def open_browser():
    """打开浏览器（生产模式）"""
    import webbrowser
    time.sleep(3)  # 等待服务器启动
    try:
        webbrowser.open('http://localhost:8080')
        print("📱 浏览器已打开: http://localhost:8080")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:8080")

def open_browser_dev():
    """打开浏览器（开发模式）"""
    import webbrowser
    time.sleep(5)  # 等待开发服务器启动
    try:
        webbrowser.open('http://localhost:3001')
        print("📱 浏览器已打开: http://localhost:3001")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:3001")

def main():
    """主函数"""
    import sys

    # 检查命令行参数
    mode = 'prod'  # 默认生产模式（单端口）
    if len(sys.argv) > 1:
        if sys.argv[1] in ['dev', 'build', 'prod', 'single']:
            mode = sys.argv[1]
        else:
            print("用法: python3 start_vue_ui.py [dev|build|prod|single]")
            print("  dev    - 开发模式（前后端分离，热重载）")
            print("  build  - 仅构建前端")
            print("  prod   - 生产模式（单端口，默认）")
            print("  single - 单端口模式（同prod）")
            return

    # single模式等同于prod模式
    if mode == 'single':
        mode = 'prod'

    print("摩点爬虫Vue UI启动器")
    print("=" * 50)

    # 检查Node.js和npm
    if not check_node_installed() or not check_npm_installed():
        print("\n请先安装Node.js和npm:")
        print("1. 访问 https://nodejs.org/ 下载安装Node.js")
        print("2. Node.js安装包通常包含npm")
        return

    # 检查前端依赖
    vue_dir = Path(__file__).parent / "web_ui_vue"
    node_modules = vue_dir / "node_modules"

    if not node_modules.exists():
        print("\n需要安装前端依赖...")
        if not install_frontend_dependencies():
            return
    else:
        print("✓ 前端依赖已安装")

    # 检查后端依赖
    if not check_backend_dependencies():
        print("\n需要安装后端依赖...")
        if not install_backend_dependencies():
            return

    if mode == 'build':
        # 仅构建模式
        print("\n🔨 构建前端...")
        if build_frontend():
            print("✓ 前端构建完成")
        else:
            print("✗ 前端构建失败")
        return

    elif mode == 'dev':
        # 开发模式（前后端分离）
        print("\n" + "=" * 50)
        print("🚀 启动开发模式（前后端分离）...")
        print("📱 前端开发服务器: http://localhost:3001")
        print("🔧 后端API服务器: http://localhost:8080")
        print("⚠️  注意：此模式仅用于前端开发调试")
        print("⏹️  按 Ctrl+C 停止所有服务")
        print("=" * 50)

        # 启动后端
        backend_thread = threading.Thread(target=start_backend_dev, daemon=True)
        backend_thread.start()

        # 在后台打开浏览器（延迟启动）
        browser_thread = threading.Thread(target=lambda: open_browser_dev(), daemon=True)
        browser_thread.start()

        # 启动前端开发服务器（主线程）
        try:
            start_frontend_dev()
        except KeyboardInterrupt:
            print("\n👋 开发服务器已停止")

    elif mode == 'prod':
        # 生产模式（单端口）
        print("\n" + "=" * 50)
        print("🚀 启动单端口模式...")
        print("📱 访问地址: http://localhost:8080")
        print("✨ 前后端整合在同一端口")
        print("⏹️  按 Ctrl+C 停止服务")
        print("=" * 50)

        # 构建前端
        if not build_frontend():
            print("前端构建失败，请检查错误信息")
            return

        # 在后台打开浏览器
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # 启动集成服务器（主线程）
        try:
            start_integrated_server()
        except KeyboardInterrupt:
            print("\n👋 集成服务器已停止")

if __name__ == "__main__":
    main()
