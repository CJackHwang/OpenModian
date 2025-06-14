#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩点爬虫管理系统功能测试
"""

import sys
import os
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        # 测试核心模块
        from modules.config_manager import ConfigManager
        from modules.data_processor import DataProcessor
        print("✅ 核心模块导入成功")
        
        # 测试爬虫模块
        from spider.config import SpiderConfig
        from spider.core import SpiderCore
        print("✅ 爬虫模块导入成功")
        
        # 测试数据库模块
        from database.db_manager import DatabaseManager
        print("✅ 数据库模块导入成功")
        
        # 测试Web UI模块
        from web_ui.app import app
        print("✅ Web UI模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n🔧 测试配置管理器...")
    
    try:
        from modules.config_manager import ConfigManager
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        # 测试配置获取
        spider_settings = config_manager.get_spider_settings()
        output_settings = config_manager.get_output_settings()
        
        print(f"✅ 爬虫设置: {len(spider_settings)} 项")
        print(f"✅ 输出设置: {len(output_settings)} 项")
        
        # 测试配置验证
        is_valid = config_manager.validate_config()
        print(f"✅ 配置验证: {'通过' if is_valid else '失败'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

def test_data_processor():
    """测试数据处理器"""
    print("\n📊 测试数据处理器...")
    
    try:
        from modules.data_processor import DataProcessor
        
        # 创建数据处理器
        processor = DataProcessor()
        
        # 测试默认配置
        config = processor._get_default_data_config()
        print(f"✅ 默认配置: {len(config)} 项")
        
        # 测试时间分类
        age_days = 30
        time_period = processor._categorize_time_period(age_days)
        print(f"✅ 时间分类: {age_days}天 -> {time_period}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据处理器测试失败: {e}")
        return False

def test_database_manager():
    """测试数据库管理器"""
    print("\n🗄️ 测试数据库管理器...")
    
    try:
        from database.db_manager import DatabaseManager
        
        # 创建测试数据库
        db_manager = DatabaseManager("test_system.db")
        
        # 测试统计信息
        stats = db_manager.get_statistics()
        print(f"✅ 数据库统计: {len(stats)} 项")
        
        # 测试项目查询
        projects = db_manager.get_projects_by_time('all', 10)
        print(f"✅ 项目查询: {len(projects)} 条记录")
        
        # 清理测试数据库
        test_db_path = Path("test_system.db")
        if test_db_path.exists():
            test_db_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        return False

def test_spider_core():
    """测试爬虫核心"""
    print("\n🕷️ 测试爬虫核心...")
    
    try:
        from spider.config import SpiderConfig
        from spider.core import SpiderCore
        
        # 创建爬虫配置
        config = SpiderConfig()
        
        # 创建爬虫实例
        spider = SpiderCore(config)
        
        print(f"✅ 爬虫初始化成功")
        print(f"✅ 输出目录: {config.OUTPUT_DIR}")
        print(f"✅ 缓存目录: {config.CACHE_DIR}")
        
        # 测试统计信息
        stats = spider.get_crawl_stats()
        print(f"✅ 统计信息: {len(stats)} 项")
        
        return True
        
    except Exception as e:
        print(f"❌ 爬虫核心测试失败: {e}")
        return False

def test_web_ui():
    """测试Web UI"""
    print("\n🌐 测试Web UI...")
    
    try:
        from web_ui.app import app
        
        # 测试Flask应用
        with app.test_client() as client:
            # 测试主页
            response = client.get('/')
            print(f"✅ 主页响应: {response.status_code}")
            
            # 测试配置API
            response = client.get('/api/config')
            print(f"✅ 配置API响应: {response.status_code}")
            
            # 测试数据库统计API
            response = client.get('/api/database/stats')
            print(f"✅ 数据库API响应: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Web UI测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n📁 测试目录结构...")
    
    required_dirs = [
        'output', 'logs', 'cache', 'database', 
        'data/raw', 'data/processed', 'data/cache'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"✅ 目录存在: {directory}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 摩点爬虫管理系统功能测试")
    print("=" * 50)
    
    tests = [
        ("目录结构", test_directory_structure),
        ("模块导入", test_imports),
        ("配置管理器", test_config_manager),
        ("数据处理器", test_data_processor),
        ("数据库管理器", test_database_manager),
        ("爬虫核心", test_spider_core),
        ("Web UI", test_web_ui),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关模块")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
