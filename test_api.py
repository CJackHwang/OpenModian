#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API功能测试脚本
用于测试Web UI的各个API接口
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_api_endpoint(endpoint, method="GET", data=None):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{'='*50}")
        print(f"测试: {method} {endpoint}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            except:
                print(f"响应: {response.text}")
                return response.text
        else:
            print(f"错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def main():
    """主测试函数"""
    print("🧪 开始API功能测试")
    print(f"测试服务器: {BASE_URL}")
    
    # 1. 测试配置获取
    print("\n📋 测试配置获取...")
    config = test_api_endpoint("/api/config")
    
    # 2. 测试数据库统计
    print("\n📊 测试数据库统计...")
    stats = test_api_endpoint("/api/database/stats")
    
    # 3. 测试任务列表
    print("\n📝 测试任务列表...")
    tasks = test_api_endpoint("/api/tasks")
    
    # 4. 测试数据库项目
    print("\n🗃️ 测试数据库项目...")
    projects = test_api_endpoint("/api/database/projects?limit=5")
    
    # 5. 测试启动小规模爬虫任务
    print("\n🕷️ 测试启动爬虫任务...")
    crawl_data = {
        "start_page": 1,
        "end_page": 1,  # 只爬取1页进行测试
        "category": "games",
        "max_concurrent": 1,
        "delay_min": 2.0,
        "delay_max": 3.0,
        "enable_dynamic": False  # 关闭动态数据以加快测试
    }
    
    start_result = test_api_endpoint("/api/start_crawl", "POST", crawl_data)
    
    if start_result and start_result.get("success"):
        task_id = start_result.get("task_id")
        print(f"✅ 任务启动成功，任务ID: {task_id}")
        
        # 6. 监控任务状态
        print("\n⏱️ 监控任务状态...")
        for i in range(10):  # 最多监控10次
            time.sleep(3)  # 等待3秒
            task_status = test_api_endpoint(f"/api/task/{task_id}")
            
            if task_status and task_status.get("success"):
                status = task_status["task"]["stats"]["status"]
                progress = task_status["task"]["stats"]["progress"]
                print(f"第{i+1}次检查 - 状态: {status}, 进度: {progress}%")
                
                if status in ["completed", "failed", "stopped"]:
                    print(f"✅ 任务已结束，最终状态: {status}")
                    break
            else:
                print("❌ 获取任务状态失败")
                break
        
        # 7. 测试停止任务（如果还在运行）
        final_status = test_api_endpoint(f"/api/task/{task_id}")
        if final_status and final_status.get("success"):
            if final_status["task"]["stats"]["status"] == "running":
                print("\n⏹️ 测试停止任务...")
                stop_result = test_api_endpoint(f"/api/stop_crawl/{task_id}", "POST")
                if stop_result and stop_result.get("success"):
                    print("✅ 任务停止成功")
                else:
                    print("❌ 任务停止失败")
    
    # 8. 最终状态检查
    print("\n🔍 最终状态检查...")
    final_tasks = test_api_endpoint("/api/tasks")
    final_stats = test_api_endpoint("/api/database/stats")
    
    print("\n🎉 API测试完成！")
    print("请检查上述输出，确认各个功能是否正常工作。")

if __name__ == "__main__":
    main()
