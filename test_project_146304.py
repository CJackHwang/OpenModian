#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试项目ID 146304的数据获取
"""

import time
import json
from spider.core import SpiderCore
from spider.config import SpiderConfig
from spider.utils import NetworkUtils

def test_project_146304():
    """测试项目ID 146304的完整数据获取"""
    print("🔧 测试项目ID 146304的数据获取")
    print("=" * 60)
    
    project_id = "146304"
    project_url = f"https://zhongchou.modian.com/item/{project_id}.html"
    
    print(f"📡 项目URL: {project_url}")
    print(f"🎯 目标: 获取完整的项目数据，包括看好数和评论数")
    print()
    
    # 创建配置和工具
    config = SpiderConfig()
    config.ENABLE_DYNAMIC_DATA = True
    
    network_utils = NetworkUtils(config)
    
    try:
        # 1. 获取页面HTML
        print("📥 获取页面HTML...")
        html = network_utils.make_request(project_url)
        
        if not html:
            print("❌ 页面获取失败")
            return
        
        print(f"✅ 页面获取成功，HTML长度: {len(html)}")
        
        # 2. 解析项目数据
        print("\n🔍 解析项目数据...")
        # 使用SpiderCore的内部方法
        spider = SpiderCore(config)
        project_data_list = spider._parse_project_detail(html, 1, project_url, project_id, "测试项目", "")

        if not project_data_list:
            print("❌ 项目数据解析失败")
            return

        # 转换为字典格式
        from spider.config import FieldMapping
        headers = FieldMapping.EXCEL_COLUMNS
        project_data = dict(zip(headers, project_data_list))
        
        # 3. 输出关键数据
        print("\n📊 项目数据解析结果:")
        print("-" * 40)
        
        key_fields = [
            "项目名称", "项目结果", "开始时间", "结束时间",
            "已筹金额", "百分比", "目标金额", "支持者(数量)",
            "看好数", "评论数", "项目更新数", "分类", "用户名"
        ]
        
        for field in key_fields:
            value = project_data.get(field, "未获取")
            print(f"{field}: {value}")
        
        # 4. 重点检查看好数和评论数
        print("\n🎯 重点数据检查:")
        print("-" * 40)
        
        like_count = project_data.get("看好数", "")
        comment_count = project_data.get("评论数", "")
        update_count = project_data.get("项目更新数", "")
        
        print(f"看好数: '{like_count}' (类型: {type(like_count)})")
        print(f"评论数: '{comment_count}' (类型: {type(comment_count)})")
        print(f"更新数: '{update_count}' (类型: {type(update_count)})")
        
        # 5. 数据质量评估
        print("\n📈 数据质量评估:")
        print("-" * 40)
        
        quality_score = 0
        total_fields = len(key_fields)
        
        for field in key_fields:
            value = project_data.get(field, "")
            if value and value != "未获取" and value != "none" and value != "":
                quality_score += 1
        
        quality_percentage = (quality_score / total_fields) * 100
        print(f"数据完整性: {quality_score}/{total_fields} ({quality_percentage:.1f}%)")
        
        # 特别关注看好数和评论数
        if like_count and like_count != "" and like_count != "0":
            print("✅ 看好数获取成功")
        else:
            print("❌ 看好数获取失败")
            
        if comment_count and comment_count != "" and comment_count != "0":
            print("✅ 评论数获取成功")
        else:
            print("❌ 评论数获取失败")
        
        # 6. 保存测试结果
        test_result = {
            "project_id": project_id,
            "project_url": project_url,
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data_quality": f"{quality_percentage:.1f}%",
            "project_data": project_data
        }
        
        with open(f"test_result_{project_id}.json", "w", encoding="utf-8") as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存到: test_result_{project_id}.json")
        
        return project_data
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_project_146304()
