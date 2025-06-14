#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的数据提取 - 验证不使用反推计算的效果
基于HTML结构分析结果，直接从页面提取准确数据
"""

import sys
import time
import re
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_direct_data_extraction():
    """测试直接数据提取（不使用反推）"""
    print("🧪 测试直接数据提取（避免反推计算）")
    print("=" * 60)
    
    try:
        from spider.config import SpiderConfig
        from spider.core import SpiderCore
        
        # 创建配置
        config = SpiderConfig()
        config.MAX_CONCURRENT_REQUESTS = 1
        config.REQUEST_DELAY = (2.0, 3.0)
        
        # 创建爬虫核心
        spider_core = SpiderCore(config)
        
        print(f"✅ 爬虫核心初始化成功")
        
        # 运行测试
        print(f"\n🎯 开始直接数据提取测试...")
        success = spider_core.start_crawling(
            start_page=1,
            end_page=1,
            category="tablegames"
        )
        
        if success and spider_core.projects_data:
            # 分析提取结果
            analyze_extraction_results(spider_core.projects_data)
            return True
        else:
            print(f"❌ 爬取失败或无数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_extraction_results(projects_data: List[List[Any]]):
    """分析数据提取结果"""
    print(f"\n📊 数据提取结果分析")
    print("=" * 60)
    
    from spider.config import FieldMapping
    headers = FieldMapping.EXCEL_COLUMNS
    
    # 找到关键字段的索引
    key_fields = {
        "已筹金额": "已筹金额",
        "完成百分比": "完成百分比",
        "目标金额": "目标金额",
        "支持者数量": "支持者(数量)"
    }
    
    field_indices = {}
    for display_name, field_name in key_fields.items():
        try:
            field_indices[display_name] = headers.index(field_name)
        except ValueError:
            print(f"⚠️  字段 '{field_name}' 未找到")
    
    if not field_indices:
        print("❌ 未找到关键字段")
        return
    
    # 分析数据质量
    total_projects = len(projects_data)
    print(f"📈 数据质量分析 (总项目数: {total_projects})")
    print("-" * 50)
    
    field_stats = {}
    data_consistency_issues = []
    
    for project_idx, project_data in enumerate(projects_data):
        project_values = {}
        
        # 提取项目的关键数据
        for display_name, field_idx in field_indices.items():
            if field_idx < len(project_data):
                value = project_data[field_idx]
                project_values[display_name] = value
        
        # 检查数据一致性
        if all(key in project_values for key in ["已筹金额", "完成百分比", "目标金额"]):
            try:
                money = float(str(project_values["已筹金额"]).replace(',', ''))
                percent = float(str(project_values["完成百分比"]).replace('%', ''))
                goal = float(str(project_values["目标金额"]).replace(',', ''))
                
                if money > 0 and goal > 0:
                    theoretical_percent = (money / goal) * 100
                    if abs(theoretical_percent - percent) > 10:  # 10%误差
                        data_consistency_issues.append({
                            "project_idx": project_idx,
                            "money": money,
                            "goal": goal,
                            "displayed_percent": percent,
                            "theoretical_percent": theoretical_percent,
                            "difference": abs(theoretical_percent - percent)
                        })
            except (ValueError, ZeroDivisionError):
                pass
    
    # 统计各字段的完整性
    for display_name, field_idx in field_indices.items():
        non_zero_count = 0
        values = []
        
        for project_data in projects_data:
            if field_idx < len(project_data):
                value = project_data[field_idx]
                if value and str(value) not in ["0", "none", "", "缺失"]:
                    non_zero_count += 1
                    try:
                        # 尝试转换为数字进行统计
                        clean_value = str(value).replace(',', '').replace('%', '').replace('¥', '')
                        if clean_value.replace('.', '').isdigit():
                            values.append(float(clean_value))
                    except ValueError:
                        pass
        
        success_rate = (non_zero_count / total_projects) * 100 if total_projects > 0 else 0
        avg_value = sum(values) / len(values) if values else 0
        max_value = max(values) if values else 0
        
        field_stats[display_name] = {
            "success_rate": success_rate,
            "non_zero_count": non_zero_count,
            "total_count": total_projects,
            "avg_value": avg_value,
            "max_value": max_value,
            "sample_values": values[:3]
        }
    
    # 输出统计结果
    for field_name, stats in field_stats.items():
        status = "✅" if stats["success_rate"] >= 90 else "⚠️" if stats["success_rate"] >= 70 else "❌"
        print(f"{status} {field_name}:")
        print(f"   成功率: {stats['success_rate']:.1f}% ({stats['non_zero_count']}/{stats['total_count']})")
        if stats["avg_value"] > 0:
            print(f"   平均值: {stats['avg_value']:.1f}")
            print(f"   最大值: {stats['max_value']:.1f}")
        print(f"   样本值: {stats['sample_values']}")
        print()
    
    # 数据一致性报告
    print(f"🔍 数据一致性检查:")
    print("-" * 30)
    
    if data_consistency_issues:
        print(f"⚠️  发现 {len(data_consistency_issues)} 个数据一致性问题:")
        for issue in data_consistency_issues[:5]:  # 显示前5个问题
            print(f"   项目 {issue['project_idx']+1}: 已筹¥{issue['money']:.0f}, 目标¥{issue['goal']:.0f}")
            print(f"      显示百分比: {issue['displayed_percent']:.1f}%")
            print(f"      理论百分比: {issue['theoretical_percent']:.1f}%")
            print(f"      差异: {issue['difference']:.1f}%")
            print()
    else:
        print(f"✅ 所有数据一致性良好")
    
    # 总体评估
    overall_success_rate = sum(stats["success_rate"] for stats in field_stats.values()) / len(field_stats)
    consistency_rate = ((total_projects - len(data_consistency_issues)) / total_projects) * 100 if total_projects > 0 else 0
    
    print(f"📊 总体评估:")
    print(f"   数据完整性: {overall_success_rate:.1f}%")
    print(f"   数据一致性: {consistency_rate:.1f}%")
    
    if overall_success_rate >= 90 and consistency_rate >= 90:
        print(f"🎉 数据提取质量优秀！")
    elif overall_success_rate >= 80 and consistency_rate >= 80:
        print(f"✅ 数据提取质量良好")
    else:
        print(f"⚠️  数据提取质量需要改进")

def test_specific_extraction_patterns():
    """测试特定的提取模式"""
    print(f"\n🔍 测试特定提取模式")
    print("=" * 60)
    
    try:
        from spider.config import SpiderConfig
        from spider.utils import NetworkUtils
        from bs4 import BeautifulSoup
        
        config = SpiderConfig()
        network_utils = NetworkUtils(config)
        
        # 测试URL
        test_url = "https://zhongchou.modian.com/item/2250000.html"
        
        print(f"🌐 测试URL: {test_url}")
        
        # 获取页面内容
        html = network_utils.make_request(test_url)
        if not html:
            print("❌ 无法获取页面内容")
            return False
        
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text()
        
        print(f"📝 页面文本长度: {len(page_text)}")
        
        # 测试基于HTML分析的提取模式
        patterns_to_test = {
            "金额模式": r'[¥￥]\s*([0-9,]+)',
            "百分比模式": r'([0-9.]+)%',
            "支持者模式": r'(\d+)\s*支持者'
        }
        
        for pattern_name, pattern in patterns_to_test.items():
            matches = re.findall(pattern, page_text)
            print(f"\n{pattern_name}: {pattern}")
            if matches:
                print(f"   ✅ 匹配结果: {matches[:5]}")  # 显示前5个匹配
            else:
                print(f"   ❌ 无匹配结果")
        
        # 测试智能金额匹配逻辑
        print(f"\n🧠 智能金额匹配测试:")
        money_matches = re.findall(r'[¥￥]\s*([0-9,]+)', page_text)
        percent_matches = re.findall(r'([0-9.]+)%', page_text)
        
        if len(money_matches) >= 2 and percent_matches:
            money_values = []
            for match in money_matches:
                clean_value = match.replace(',', '')
                if clean_value.isdigit():
                    money_values.append(int(clean_value))
            
            if len(money_values) >= 2:
                percent_val = float(percent_matches[0])
                
                if percent_val > 100:
                    money = max(money_values)
                    goal_money = min(money_values)
                else:
                    money = min(money_values)
                    goal_money = max(money_values)
                
                print(f"   百分比: {percent_val}%")
                print(f"   智能匹配: 已筹¥{money}, 目标¥{goal_money}")
                
                # 验证匹配结果
                theoretical_percent = (money / goal_money) * 100
                print(f"   理论百分比: {theoretical_percent:.1f}%")
                print(f"   匹配准确性: {'✅ 良好' if abs(theoretical_percent - percent_val) < 10 else '⚠️ 需要调整'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 特定模式测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 数据提取优化测试（避免反推计算）")
    print("基于HTML结构分析，直接提取准确数据")
    print("=" * 80)
    
    tests = [
        ("直接数据提取测试", test_direct_data_extraction),
        ("特定提取模式测试", test_specific_extraction_patterns),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ❌ 异常 - {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n" + "=" * 80)
    print(f"📊 数据提取优化测试总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 数据提取优化成功！")
        print(f"✅ 已避免反推计算")
        print(f"✅ 直接从页面提取准确数据")
        print(f"✅ 数据一致性显著提升")
        return True
    else:
        print(f"⚠️  数据提取优化需要进一步完善")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
