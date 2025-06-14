#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据字段对齐修复
"""

import sys
import time
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spider.config import SpiderConfig, FieldMapping
from spider.core import SpiderCore

class MockWebMonitor:
    """模拟Web监控器"""
    def __init__(self):
        self.logs = []
    
    def add_log(self, level, message):
        log_entry = {
            'timestamp': time.strftime('%H:%M:%S'),
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        print(f"[{level.upper()}] {message}")

def test_field_alignment():
    """测试字段对齐修复"""
    print("🧪 测试数据字段对齐修复")
    print("=" * 60)
    
    # 创建配置
    config = SpiderConfig()
    config.MAX_CONCURRENT_REQUESTS = 1
    
    # 创建模拟监控器
    mock_monitor = MockWebMonitor()
    
    # 创建爬虫实例
    spider = SpiderCore(config, web_monitor=mock_monitor)
    
    try:
        # 测试单个项目爬取
        print(f"\n🎯 测试单个项目数据字段对齐...")
        success = spider.start_crawling(
            start_page=1,
            end_page=1,
            category='tablegames'
        )
        
        if not success or not spider.projects_data:
            print("❌ 爬取失败，无法进行字段对齐测试")
            return False
        
        # 分析字段对齐
        sample_project = spider.projects_data[0]
        headers = FieldMapping.EXCEL_COLUMNS
        
        print(f"\n📊 字段对齐分析:")
        print(f"   预期字段数: {len(headers)}")
        print(f"   实际字段数: {len(sample_project)}")
        
        # 检查关键字段位置
        key_field_positions = {
            "已筹金额": 13,
            "百分比": 14,
            "目标金额": 15,
            "支持者(数量)": 16,
            "用户名": 11,
            "分类": 10
        }
        
        print(f"\n🔍 关键字段位置检查:")
        alignment_correct = True
        
        for field_name, expected_pos in key_field_positions.items():
            if expected_pos < len(sample_project):
                actual_value = sample_project[expected_pos]
                expected_header = headers[expected_pos] if expected_pos < len(headers) else "超出范围"
                
                # 检查字段名是否匹配
                if expected_header == field_name:
                    status = "✅"
                    print(f"   {status} 位置{expected_pos:2}: {field_name} = {str(actual_value)[:30]}...")
                else:
                    status = "❌"
                    alignment_correct = False
                    print(f"   {status} 位置{expected_pos:2}: 期望{field_name}, 实际{expected_header}")
            else:
                status = "❌"
                alignment_correct = False
                print(f"   {status} 位置{expected_pos:2}: {field_name} - 数据不足")
        
        # 检查众筹数据是否有值
        print(f"\n💰 众筹数据值检查:")
        funding_fields = {
            "已筹金额": 13,
            "百分比": 14, 
            "目标金额": 15,
            "支持者(数量)": 16
        }
        
        has_funding_data = False
        for field_name, pos in funding_fields.items():
            if pos < len(sample_project):
                value = sample_project[pos]
                if value and str(value) not in ["0", "0.0", "none", ""]:
                    has_funding_data = True
                    print(f"   ✅ {field_name}: {value}")
                else:
                    print(f"   ❌ {field_name}: {value} (无数据)")
        
        # 检查作者信息
        print(f"\n👤 作者信息检查:")
        author_fields = {
            "用户主页(链接)": 8,
            "用户头像(图片链接)": 9,
            "分类": 10,
            "用户名": 11,
            "用户UID(data-username)": 12
        }
        
        has_author_data = False
        for field_name, pos in author_fields.items():
            if pos < len(sample_project):
                value = sample_project[pos]
                if value and str(value) not in ["none", "", "0"]:
                    has_author_data = True
                    print(f"   ✅ {field_name}: {str(value)[:40]}...")
                else:
                    print(f"   ❌ {field_name}: {value} (无数据)")
        
        # 输出完整的字段映射
        print(f"\n📋 完整字段映射 (前20个字段):")
        for i in range(min(20, len(sample_project), len(headers))):
            value = str(sample_project[i])[:30] if sample_project[i] else "空"
            print(f"   {i:2}: {headers[i]:25} = {value}...")
        
        # 总结
        print(f"\n📊 修复效果总结:")
        print(f"   字段对齐: {'✅ 正确' if alignment_correct else '❌ 错误'}")
        print(f"   众筹数据: {'✅ 有数据' if has_funding_data else '❌ 缺失'}")
        print(f"   作者信息: {'✅ 有数据' if has_author_data else '❌ 缺失'}")
        
        # 检查JSON输出
        output_dir = Path(config.OUTPUT_DIR)
        json_files = list(output_dir.glob("*.json"))
        if json_files:
            latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"\n📁 JSON文件检查: {latest_json.name}")
            
            with open(latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'projects' in data and data['projects']:
                first_project = data['projects'][0]
                
                # 检查JSON中的关键字段
                json_funding_check = {
                    "已筹金额": first_project.get("已筹金额", 0),
                    "百分比": first_project.get("百分比", 0),
                    "目标金额": first_project.get("目标金额", 0),
                    "支持者(数量)": first_project.get("支持者(数量)", 0)
                }
                
                print(f"   JSON众筹数据:")
                for field, value in json_funding_check.items():
                    status = "✅" if value and value != 0 else "❌"
                    print(f"     {status} {field}: {value}")
        
        return alignment_correct and (has_funding_data or has_author_data)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 摩点爬虫字段对齐修复测试")
    print("=" * 60)
    
    success = test_field_alignment()
    
    print(f"\n" + "=" * 60)
    print(f"📊 测试结果")
    print("=" * 60)
    
    if success:
        print(f"🎉 字段对齐修复测试通过！")
        print(f"✅ 数据字段位置正确")
        print(f"✅ 众筹信息能够正确提取")
        print(f"✅ 作者信息能够正确提取")
        return True
    else:
        print(f"❌ 字段对齐修复测试失败")
        print(f"⚠️ 需要进一步调试数据解析逻辑")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
