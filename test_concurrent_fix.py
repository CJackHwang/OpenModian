#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试并发处理修复效果
验证每个项目获取到独有的动态数据
"""

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from spider.config import SpiderConfig
from spider.lightning_fast_dynamic import LightningDataManager
from spider.utils import NetworkUtils


def test_single_project(project_id, manager_id):
    """测试单个项目的数据获取"""
    print(f"🧪 管理器 {manager_id} 开始测试项目 {project_id}")
    
    config = SpiderConfig()
    network_utils = NetworkUtils(config)
    manager = LightningDataManager(config, network_utils)
    
    try:
        start_time = time.time()
        result = manager.get_lightning_data(project_id)
        elapsed_time = time.time() - start_time
        
        print(f"✅ 管理器 {manager_id} 项目 {project_id} 完成: 看好数={result.get('like_count', '0')}, 评论数={result.get('comment_count', '0')}, 耗时: {elapsed_time:.2f}秒")
        
        # 清理资源
        manager.cleanup()
        
        return {
            'manager_id': manager_id,
            'project_id': project_id,
            'result': result,
            'elapsed_time': elapsed_time
        }
        
    except Exception as e:
        print(f"❌ 管理器 {manager_id} 项目 {project_id} 失败: {e}")
        manager.cleanup()
        return {
            'manager_id': manager_id,
            'project_id': project_id,
            'result': {'like_count': '0', 'comment_count': '0'},
            'elapsed_time': 0,
            'error': str(e)
        }


def test_concurrent_data_independence():
    """测试并发数据独立性"""
    print("🔧 测试并发数据独立性")
    print("=" * 60)
    
    # 测试项目ID列表（使用不同的项目确保数据不同）
    test_projects = [
        "147446",  # 项目1
        "147445",  # 项目2  
        "147444",  # 项目3
        "147443",  # 项目4
        "147442",  # 项目5
        "147441",  # 项目6
    ]
    
    print(f"📋 测试项目: {test_projects}")
    print(f"🔄 并发数: 3")
    print()
    
    # 使用3个并发任务测试
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务
        future_to_info = {
            executor.submit(test_single_project, project_id, f"M{i+1}"): (project_id, f"M{i+1}")
            for i, project_id in enumerate(test_projects)
        }
        
        # 收集结果
        results = []
        for future in as_completed(future_to_info):
            project_id, manager_id = future_to_info[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ 任务执行失败 {manager_id}-{project_id}: {e}")
    
    # 分析结果
    print("\n📊 结果分析:")
    print("=" * 60)
    
    # 按项目分组
    project_results = {}
    for result in results:
        project_id = result['project_id']
        if project_id not in project_results:
            project_results[project_id] = []
        project_results[project_id].append(result)
    
    # 检查数据独立性
    data_independence_ok = True
    for project_id, project_data in project_results.items():
        print(f"\n项目 {project_id}:")
        for data in project_data:
            like_count = data['result'].get('like_count', '0')
            comment_count = data['result'].get('comment_count', '0')
            manager_id = data['manager_id']
            elapsed = data.get('elapsed_time', 0)
            
            if 'error' in data:
                print(f"  {manager_id}: ❌ 错误 - {data['error']}")
            else:
                print(f"  {manager_id}: 看好数={like_count}, 评论数={comment_count}, 耗时={elapsed:.2f}s")
    
    # 检查是否有重复数据
    print("\n🔍 重复数据检查:")
    all_data_combinations = []
    for result in results:
        if 'error' not in result:
            like_count = result['result'].get('like_count', '0')
            comment_count = result['result'].get('comment_count', '0')
            combination = f"{like_count}-{comment_count}"
            all_data_combinations.append((result['project_id'], combination, result['manager_id']))
    
    # 查找重复的数据组合
    seen_combinations = {}
    duplicates = []
    for project_id, combination, manager_id in all_data_combinations:
        if combination in seen_combinations and combination != "0-0":
            duplicates.append({
                'combination': combination,
                'projects': [seen_combinations[combination], (project_id, manager_id)]
            })
        else:
            seen_combinations[combination] = (project_id, manager_id)
    
    if duplicates:
        print("❌ 发现重复数据:")
        for dup in duplicates:
            print(f"  数据组合 {dup['combination']} 出现在:")
            for proj_id, mgr_id in dup['projects']:
                print(f"    项目 {proj_id} (管理器 {mgr_id})")
        data_independence_ok = False
    else:
        print("✅ 未发现重复数据，数据独立性良好")
    
    # 总结
    print("\n📋 测试总结:")
    print("=" * 60)
    successful_tests = len([r for r in results if 'error' not in r])
    total_tests = len(results)
    
    print(f"总测试数: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {total_tests - successful_tests}")
    print(f"数据独立性: {'✅ 通过' if data_independence_ok else '❌ 失败'}")
    
    if successful_tests > 0:
        avg_time = sum(r.get('elapsed_time', 0) for r in results if 'error' not in r) / successful_tests
        print(f"平均耗时: {avg_time:.2f}秒")
    
    return data_independence_ok


if __name__ == "__main__":
    print("🚀 开始测试并发处理修复效果")
    print("=" * 60)
    
    try:
        success = test_concurrent_data_independence()
        
        if success:
            print("\n🎉 测试通过！并发处理问题已修复")
        else:
            print("\n⚠️ 测试失败！仍存在并发处理问题")
            
    except Exception as e:
        print(f"\n💥 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
