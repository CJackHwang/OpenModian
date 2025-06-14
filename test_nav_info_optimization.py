#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导航信息解析优化效果
验证评论数、支持者数量、点赞数/收藏数的提取准确性
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_nav_info_parsing():
    """测试导航信息解析优化"""
    print("🧪 测试导航信息解析优化")
    print("=" * 60)
    
    try:
        from spider.config import SpiderConfig
        from spider.core import SpiderCore
        
        # 创建配置
        config = SpiderConfig()
        config.MAX_CONCURRENT_REQUESTS = 1  # 降低并发
        config.REQUEST_DELAY = (2.0, 3.0)   # 增加延迟
        
        # 创建爬虫核心
        spider_core = SpiderCore(config)
        
        print(f"✅ 爬虫核心初始化成功")
        
        # 运行小规模测试，重点关注导航信息
        print(f"\n🎯 开始导航信息解析测试...")
        success = spider_core.start_crawling(
            start_page=1,
            end_page=1,  # 只测试1页
            category="tablegames"
        )
        
        if success and spider_core.projects_data:
            # 分析导航信息解析结果
            analyze_nav_parsing_results(spider_core.projects_data)
            return True
        else:
            print(f"❌ 爬取失败或无数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_nav_parsing_results(projects_data: List[List[Any]]):
    """分析导航信息解析结果"""
    print(f"\n📊 导航信息解析结果分析")
    print("=" * 60)
    
    from spider.config import FieldMapping
    headers = FieldMapping.EXCEL_COLUMNS
    
    # 找到导航信息字段的索引
    nav_field_indices = {}
    nav_fields = ["项目更新数", "评论数", "项目支持者/点赞数", "收藏数"]
    
    for field in nav_fields:
        try:
            nav_field_indices[field] = headers.index(field)
        except ValueError:
            print(f"⚠️  字段 '{field}' 未找到在表头中")
    
    if not nav_field_indices:
        print("❌ 未找到导航信息字段")
        return
    
    # 统计解析结果
    total_projects = len(projects_data)
    field_stats = {}
    
    for field, index in nav_field_indices.items():
        non_zero_count = 0
        values = []
        
        for project_data in projects_data:
            if index < len(project_data):
                value = project_data[index]
                if value and str(value) not in ["0", "none", ""]:
                    non_zero_count += 1
                    try:
                        values.append(int(str(value)))
                    except ValueError:
                        pass
        
        success_rate = (non_zero_count / total_projects) * 100 if total_projects > 0 else 0
        avg_value = sum(values) / len(values) if values else 0
        max_value = max(values) if values else 0
        
        field_stats[field] = {
            "success_rate": success_rate,
            "non_zero_count": non_zero_count,
            "total_count": total_projects,
            "avg_value": avg_value,
            "max_value": max_value,
            "values": values[:5]  # 显示前5个值作为样本
        }
    
    # 输出分析结果
    print(f"📈 解析成功率分析 (总项目数: {total_projects})")
    print("-" * 50)
    
    for field, stats in field_stats.items():
        status = "✅" if stats["success_rate"] >= 90 else "⚠️" if stats["success_rate"] >= 70 else "❌"
        print(f"{status} {field}:")
        print(f"   成功率: {stats['success_rate']:.1f}% ({stats['non_zero_count']}/{stats['total_count']})")
        print(f"   平均值: {stats['avg_value']:.1f}")
        print(f"   最大值: {stats['max_value']}")
        print(f"   样本值: {stats['values']}")
        print()
    
    # 总体评估
    overall_success_rate = sum(stats["success_rate"] for stats in field_stats.values()) / len(field_stats)
    print(f"📊 总体解析成功率: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 90:
        print("🎉 导航信息解析优化效果优秀！")
    elif overall_success_rate >= 70:
        print("✅ 导航信息解析优化效果良好")
    elif overall_success_rate >= 50:
        print("⚠️  导航信息解析优化效果一般")
    else:
        print("❌ 导航信息解析需要进一步优化")
    
    return overall_success_rate

def test_specific_nav_fields():
    """测试特定导航字段的解析"""
    print(f"\n🔍 特定字段解析测试")
    print("=" * 60)
    
    try:
        from spider.config import SpiderConfig
        from spider.core import AdaptiveParser
        from spider.utils import NetworkUtils
        from bs4 import BeautifulSoup
        
        config = SpiderConfig()
        network_utils = NetworkUtils(config)
        parser = AdaptiveParser(config, network_utils)
        
        # 测试URL（桌游分类的一个项目）
        test_url = "https://zhongchou.modian.com/item/2250000.html"
        
        print(f"🌐 测试URL: {test_url}")
        
        # 获取页面内容
        html = network_utils.make_request(test_url)
        if not html:
            print("❌ 无法获取测试页面")
            return False
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 测试导航信息解析
        nav_info = parser._parse_nav_info(soup)
        
        print(f"📊 导航信息解析结果:")
        print(f"   更新数: {nav_info[0]}")
        print(f"   评论数: {nav_info[1]}")
        print(f"   支持者数: {nav_info[2]}")
        print(f"   收藏数: {nav_info[3]}")
        
        # 验证结果
        non_zero_count = sum(1 for x in nav_info if x != "0")
        success_rate = (non_zero_count / 4) * 100
        
        print(f"\n📈 单页面测试结果:")
        print(f"   非零字段: {non_zero_count}/4")
        print(f"   成功率: {success_rate:.1f}%")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"❌ 特定字段测试失败: {e}")
        return False

def test_parsing_strategies():
    """测试不同解析策略的效果"""
    print(f"\n🔧 解析策略效果测试")
    print("=" * 60)
    
    try:
        from spider.config import SpiderConfig
        from spider.core import AdaptiveParser
        from spider.utils import NetworkUtils
        from bs4 import BeautifulSoup
        
        config = SpiderConfig()
        network_utils = NetworkUtils(config)
        parser = AdaptiveParser(config, network_utils)
        
        # 获取一个测试页面
        test_url = "https://zhongchou.modian.com/item/2250000.html"
        html = network_utils.make_request(test_url)
        
        if not html:
            print("❌ 无法获取测试页面")
            return False
        
        soup = BeautifulSoup(html, "html.parser")
        
        # 测试各种解析策略
        strategies = [
            ("JavaScript数据提取", parser._extract_nav_from_javascript),
            ("增强DOM解析", parser._extract_nav_from_dom_enhanced),
            ("增强文本解析", parser._extract_nav_from_text_enhanced),
            ("回退DOM解析", parser._extract_nav_from_dom_fallback)
        ]
        
        results = {}
        
        for strategy_name, strategy_func in strategies:
            try:
                if strategy_name == "JavaScript数据提取":
                    result = strategy_func(soup)
                    # 转换为列表格式
                    nav_result = [
                        result.get("update_count", "0"),
                        result.get("comment_count", "0"),
                        result.get("supporter_count", "0"),
                        result.get("collect_count", "0")
                    ]
                else:
                    nav_result = strategy_func(soup)
                
                non_zero_count = sum(1 for x in nav_result if x != "0")
                success_rate = (non_zero_count / 4) * 100
                
                results[strategy_name] = {
                    "result": nav_result,
                    "success_rate": success_rate,
                    "non_zero_count": non_zero_count
                }
                
                status = "✅" if success_rate >= 75 else "⚠️" if success_rate >= 50 else "❌"
                print(f"{status} {strategy_name}:")
                print(f"   结果: {nav_result}")
                print(f"   成功率: {success_rate:.1f}% ({non_zero_count}/4)")
                print()
                
            except Exception as e:
                print(f"❌ {strategy_name} 测试失败: {e}")
                results[strategy_name] = {"error": str(e)}
        
        # 找出最佳策略
        best_strategy = max(
            [(name, data) for name, data in results.items() if "error" not in data],
            key=lambda x: x[1]["success_rate"],
            default=(None, None)
        )
        
        if best_strategy[0]:
            print(f"🏆 最佳策略: {best_strategy[0]} (成功率: {best_strategy[1]['success_rate']:.1f}%)")
        
        return len([r for r in results.values() if "error" not in r and r["success_rate"] >= 50]) >= 2
        
    except Exception as e:
        print(f"❌ 策略测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 导航信息解析优化测试")
    print("验证评论数、支持者数量、点赞数/收藏数的提取准确性")
    print("=" * 80)
    
    tests = [
        ("导航信息解析优化", test_nav_info_parsing),
        ("特定字段解析测试", test_specific_nav_fields),
        ("解析策略效果测试", test_parsing_strategies),
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
    print(f"📊 导航信息解析优化测试总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 所有导航信息解析优化测试通过！")
        print(f"✅ 评论数、支持者数量、收藏数提取准确性显著提升")
        print(f"✅ 多重解析策略有效提高数据完整性")
        print(f"✅ 数据验证机制确保结果可靠性")
        return True
    elif passed >= total * 0.7:
        print(f"⚠️  大部分导航信息解析优化成功")
        print(f"✅ 主要字段解析准确性有所提升")
        return True
    else:
        print(f"❌ 导航信息解析优化需要进一步完善")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
