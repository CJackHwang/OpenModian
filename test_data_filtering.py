#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据管理的分类筛选和状态筛选功能
"""

import sys
import os
import requests

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data.database.db_manager import DatabaseManager


def test_category_filtering():
    """测试分类筛选功能"""
    print("🔍 测试分类筛选功能")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    # 测试不同分类的筛选
    test_categories = [
        'games', 'tablegames', 'publishing', 'toys', 'cards',
        'technology', 'film-video', 'music', 'activities'
    ]
    
    print("📊 分类筛选测试:")
    for category in test_categories:
        conditions = {'category': category}
        projects = db_manager.search_projects(conditions, limit=10)
        count = db_manager.count_projects(conditions)
        
        print(f"  {category:12} -> {count:4} 个项目 (显示前{len(projects)}个)")
        
        # 显示前几个项目的分类信息
        for i, project in enumerate(projects[:3]):
            actual_category = project.get('category', '未知')
            project_name = project.get('project_name', '未知项目')[:20]
            print(f"    {i+1}. {project_name:20} | 分类: {actual_category}")
    
    print("\n✅ 分类筛选测试完成")


def test_api_category_filtering():
    """测试API分类筛选功能"""
    print("\n🌐 测试API分类筛选功能")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试不同分类的API调用
    test_categories = ['all', 'games', 'tablegames', 'publishing']
    
    print("📡 API分类筛选测试:")
    for category in test_categories:
        try:
            url = f"{base_url}/api/database/projects"
            params = {'category': category, 'limit': 5}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    projects = data.get('projects', [])
                    count = data.get('count', 0)
                    
                    print(f"  {category:12} -> {count:4} 个项目")
                    
                    # 显示前几个项目
                    for i, project in enumerate(projects[:2]):
                        actual_category = project.get('category', '未知')
                        project_name = project.get('project_name', '未知项目')[:20]
                        print(f"    {i+1}. {project_name:20} | 分类: {actual_category}")
                else:
                    print(f"  {category:12} -> API错误: {data.get('message', '未知错误')}")
            else:
                print(f"  {category:12} -> HTTP错误: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  {category:12} -> 连接错误: {e}")
        except Exception as e:
            print(f"  {category:12} -> 其他错误: {e}")
    
    print("\n✅ API分类筛选测试完成")


def test_status_filtering():
    """测试状态筛选功能"""
    print("\n📋 测试状态筛选功能")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    # 检查数据库中的实际状态值
    print("🔍 检查数据库中的实际状态值:")
    try:
        import sqlite3
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT project_status FROM projects WHERE project_status IS NOT NULL AND project_status != '' ORDER BY project_status")
            statuses = cursor.fetchall()
            
            print(f"  数据库中的状态数量: {len(statuses)}")
            for status in statuses:
                cursor.execute("SELECT COUNT(*) FROM projects WHERE project_status = ?", (status[0],))
                count = cursor.fetchone()[0]
                print(f"  {status[0]:12} -> {count:4} 个项目")
    
    except Exception as e:
        print(f"  检查状态失败: {e}")
    
    print("\n✅ 状态筛选测试完成")


def test_combined_filtering():
    """测试组合筛选功能"""
    print("\n🔧 测试组合筛选功能")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    # 测试分类+状态组合筛选
    test_combinations = [
        {'category': 'games', 'status': '众筹中'},
        {'category': 'tablegames', 'status': '众筹成功'},
        {'category': 'publishing', 'min_amount': 1000}
    ]
    
    print("🔍 组合筛选测试:")
    for i, conditions in enumerate(test_combinations):
        projects = db_manager.search_projects(conditions, limit=5)
        count = db_manager.count_projects(conditions)
        
        condition_str = ", ".join([f"{k}={v}" for k, v in conditions.items()])
        print(f"  条件{i+1}: {condition_str}")
        print(f"    结果: {count} 个项目")
        
        for j, project in enumerate(projects[:2]):
            project_name = project.get('project_name', '未知项目')[:25]
            category = project.get('category', '未知')
            status = project.get('project_status', '未知')
            amount = project.get('raised_amount', '0')
            print(f"      {j+1}. {project_name:25} | {category:8} | {status:8} | ¥{amount}")
    
    print("\n✅ 组合筛选测试完成")


if __name__ == "__main__":
    print("🚀 开始测试数据筛选功能")
    print("=" * 60)
    
    try:
        # 测试数据库分类筛选
        test_category_filtering()
        
        # 测试API分类筛选
        test_api_category_filtering()
        
        # 测试状态筛选
        test_status_filtering()
        
        # 测试组合筛选
        test_combined_filtering()
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n💥 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
