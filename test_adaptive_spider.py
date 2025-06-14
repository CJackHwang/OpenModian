#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能适配爬虫功能
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spider.config import SpiderConfig
from spider.core import SpiderCore

def test_adaptive_parsing():
    """测试智能适配解析功能"""
    print("🧪 测试智能适配爬虫功能")
    print("=" * 60)
    
    # 创建爬虫配置
    config = SpiderConfig()
    config.MAX_PAGES = 2  # 只测试2页
    config.MAX_CONCURRENT_REQUESTS = 2  # 降低并发数
    
    # 创建爬虫实例
    spider = SpiderCore(config)
    
    # 测试不同分类的爬取
    test_categories = [
        ("tablegames", "桌游"),
        ("games", "游戏"),
        ("publishing", "出版"),
        ("cards", "卡牌"),
        ("toys", "潮玩模型")
    ]
    
    results = {}
    
    for category, category_name in test_categories:
        print(f"\n🎯 测试分类: {category_name} ({category})")
        print("-" * 40)
        
        try:
            # 重置爬虫状态
            spider.projects_data.clear()
            spider.failed_urls.clear()
            
            # 开始爬取
            start_time = time.time()
            success = spider.start_crawling(
                start_page=1, 
                end_page=1,  # 只爬取第一页进行测试
                category=category
            )
            
            elapsed_time = time.time() - start_time
            
            # 收集结果
            stats = spider.get_crawl_stats()
            results[category] = {
                "success": success,
                "projects_count": len(spider.projects_data),
                "failed_count": len(spider.failed_urls),
                "elapsed_time": elapsed_time,
                "stats": stats
            }
            
            print(f"✅ 爬取完成:")
            print(f"   成功: {success}")
            print(f"   项目数量: {len(spider.projects_data)}")
            print(f"   失败数量: {len(spider.failed_urls)}")
            print(f"   耗时: {elapsed_time:.2f}秒")
            
            # 显示部分项目信息
            if spider.projects_data:
                print(f"   示例项目:")
                for i, project in enumerate(spider.projects_data[:3]):
                    if len(project) >= 5:
                        print(f"     {i+1}. {project[3][:50]}...")  # 项目名称
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results[category] = {
                "success": False,
                "error": str(e),
                "projects_count": 0,
                "failed_count": 0,
                "elapsed_time": 0
            }
        
        # 短暂休息避免请求过快
        time.sleep(2)
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    total_projects = 0
    successful_categories = 0
    
    for category, category_name in test_categories:
        result = results.get(category, {})
        success = result.get("success", False)
        projects_count = result.get("projects_count", 0)
        elapsed_time = result.get("elapsed_time", 0)
        
        status = "✅" if success else "❌"
        print(f"{status} {category_name:12} | 项目: {projects_count:3} | 耗时: {elapsed_time:6.2f}s")
        
        if success:
            successful_categories += 1
            total_projects += projects_count
    
    print("-" * 60)
    print(f"成功分类: {successful_categories}/{len(test_categories)}")
    print(f"总项目数: {total_projects}")
    
    # 测试数据完整性
    print(f"\n🔍 数据完整性测试")
    print("-" * 40)
    
    if spider.projects_data:
        sample_project = spider.projects_data[0]
        expected_fields = 34  # 预期的字段数量
        actual_fields = len(sample_project)
        
        print(f"预期字段数: {expected_fields}")
        print(f"实际字段数: {actual_fields}")
        print(f"完整性: {actual_fields/expected_fields*100:.1f}%")
        
        # 检查关键字段
        key_fields = {
            "项目URL": sample_project[1] if len(sample_project) > 1 else "缺失",
            "项目ID": sample_project[2] if len(sample_project) > 2 else "缺失", 
            "项目名称": sample_project[3] if len(sample_project) > 3 else "缺失",
            "项目状态": sample_project[7] if len(sample_project) > 7 else "缺失",
            "作者名称": sample_project[11] if len(sample_project) > 11 else "缺失"
        }
        
        for field_name, field_value in key_fields.items():
            status = "✅" if field_value and field_value != "缺失" and field_value != "none" else "❌"
            print(f"{status} {field_name}: {str(field_value)[:30]}...")
    
    # 性能评估
    print(f"\n⚡ 性能评估")
    print("-" * 40)
    
    if results:
        avg_time_per_category = sum(r.get("elapsed_time", 0) for r in results.values()) / len(results)
        avg_projects_per_category = sum(r.get("projects_count", 0) for r in results.values()) / len(results)
        
        print(f"平均每分类耗时: {avg_time_per_category:.2f}秒")
        print(f"平均每分类项目数: {avg_projects_per_category:.1f}个")
        
        if avg_projects_per_category > 0:
            avg_time_per_project = avg_time_per_category / avg_projects_per_category
            print(f"平均每项目耗时: {avg_time_per_project:.2f}秒")
    
    return results

def test_specific_category(category: str = "tablegames", pages: int = 3):
    """测试特定分类的详细爬取"""
    print(f"\n🎯 详细测试分类: {category}")
    print("=" * 60)
    
    config = SpiderConfig()
    config.MAX_PAGES = pages
    
    spider = SpiderCore(config)
    
    try:
        success = spider.start_crawling(
            start_page=1,
            end_page=pages,
            category=category
        )
        
        print(f"\n📊 详细测试结果:")
        print(f"成功: {success}")
        print(f"项目总数: {len(spider.projects_data)}")
        print(f"失败URL数: {len(spider.failed_urls)}")
        
        # 显示统计信息
        stats = spider.get_crawl_stats()
        print(f"\n📈 统计信息:")
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value}")
        
        return success
        
    except Exception as e:
        print(f"❌ 详细测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 摩点智能适配爬虫测试")
    print("=" * 60)
    
    # 基础适配测试
    results = test_adaptive_parsing()
    
    # 如果基础测试成功，进行详细测试
    successful_count = sum(1 for r in results.values() if r.get("success", False))
    
    if successful_count > 0:
        print(f"\n✅ 基础测试通过 ({successful_count}/{len(results)} 个分类成功)")
        
        # 选择一个成功的分类进行详细测试
        for category, result in results.items():
            if result.get("success", False):
                test_specific_category(category, 2)
                break
    else:
        print(f"\n❌ 基础测试失败，所有分类都无法正常爬取")
        return False
    
    print(f"\n🎉 智能适配爬虫测试完成！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
