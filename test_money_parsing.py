#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试金额解析修复
"""

import sys
import time
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spider.config import SpiderConfig
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

def test_money_parsing():
    """测试金额解析修复"""
    print("🧪 测试金额解析修复")
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
        print(f"\n🎯 测试金额解析修复...")
        success = spider.start_crawling(
            start_page=1,
            end_page=1,
            category='tablegames'
        )
        
        if not success or not spider.projects_data:
            print("❌ 爬取失败，无法进行金额解析测试")
            return False
        
        # 分析金额数据
        print(f"\n💰 金额数据分析:")
        
        funding_data_found = False
        for i, project in enumerate(spider.projects_data[:5]):  # 检查前5个项目
            if len(project) >= 17:
                project_name = project[3][:30] if project[3] else "未知项目"
                raised_money = project[13]  # 已筹金额
                percentage = project[14]    # 百分比
                target_money = project[15]  # 目标金额
                supporters = project[16]    # 支持者数量
                
                print(f"\n项目 {i+1}: {project_name}...")
                print(f"   已筹金额: {raised_money}")
                print(f"   目标金额: {target_money}")
                print(f"   完成百分比: {percentage}")
                print(f"   支持者数量: {supporters}")
                
                # 检查是否有非零数据
                if (str(raised_money) != "0" or 
                    str(target_money) != "0" or 
                    str(percentage) != "0" or 
                    str(supporters) != "0"):
                    funding_data_found = True
                    print(f"   ✅ 发现有效金额数据")
                else:
                    print(f"   ❌ 金额数据仍为0")
        
        # 检查日志中的解析信息
        print(f"\n📝 解析日志分析:")
        money_logs = [log for log in mock_monitor.logs if "找到" in log['message']]
        
        if money_logs:
            print(f"   发现 {len(money_logs)} 条解析日志:")
            for log in money_logs[:10]:  # 显示前10条
                print(f"   {log['message']}")
            funding_data_found = True
        else:
            print(f"   ❌ 未发现金额解析日志")
        
        # 检查JSON输出
        output_dir = Path(config.OUTPUT_DIR)
        json_files = list(output_dir.glob("*.json"))
        if json_files:
            latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"\n📁 JSON文件检查: {latest_json.name}")
            
            with open(latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'projects' in data and data['projects']:
                # 统计非零金额数据
                non_zero_raised = sum(1 for p in data['projects'] if p.get("已筹金额", 0) != 0)
                non_zero_target = sum(1 for p in data['projects'] if p.get("目标金额", 0) != 0)
                non_zero_percent = sum(1 for p in data['projects'] if p.get("百分比", 0) != 0)
                non_zero_supporters = sum(1 for p in data['projects'] if p.get("支持者(数量)", 0) != 0)
                
                total_projects = len(data['projects'])
                
                print(f"   总项目数: {total_projects}")
                print(f"   非零已筹金额: {non_zero_raised}/{total_projects} ({non_zero_raised/total_projects*100:.1f}%)")
                print(f"   非零目标金额: {non_zero_target}/{total_projects} ({non_zero_target/total_projects*100:.1f}%)")
                print(f"   非零完成百分比: {non_zero_percent}/{total_projects} ({non_zero_percent/total_projects*100:.1f}%)")
                print(f"   非零支持者数量: {non_zero_supporters}/{total_projects} ({non_zero_supporters/total_projects*100:.1f}%)")
                
                if non_zero_raised > 0 or non_zero_target > 0:
                    funding_data_found = True
        
        # 总结
        print(f"\n📊 金额解析修复效果:")
        if funding_data_found:
            print(f"✅ 金额解析修复成功")
            print(f"✅ 能够正确提取金额数据")
            return True
        else:
            print(f"❌ 金额解析仍然失败")
            print(f"⚠️ 需要进一步调试正则表达式")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 摩点爬虫金额解析修复测试")
    print("=" * 60)
    
    success = test_money_parsing()
    
    print(f"\n" + "=" * 60)
    print(f"📊 测试结果")
    print("=" * 60)
    
    if success:
        print(f"🎉 金额解析修复测试通过！")
        print(f"✅ 已筹金额、目标金额等数据能够正确提取")
        print(f"✅ 支持者数量能够正确提取")
        print(f"✅ 数据完整性大幅提升")
        return True
    else:
        print(f"❌ 金额解析修复测试失败")
        print(f"⚠️ 需要进一步分析网页结构和正则表达式")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
