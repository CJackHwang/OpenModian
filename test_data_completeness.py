#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩点爬虫数据完整性深度测试
专门测试修复后的数据提取完整性
"""

import sys
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import ModianSpider, ModianSpiderConfig

def test_single_project_completeness(project_url: str) -> Dict[str, Any]:
    """测试单个项目的数据完整性"""
    print(f"\n🔍 测试项目: {project_url}")
    
    config = ModianSpiderConfig()
    spider = ModianSpider(config)
    
    # 获取项目页面
    html = spider.askURL(project_url)
    if not html:
        return {"error": "无法获取页面内容"}
    
    # 解析项目详情
    project_data = spider.parse_project_detail_page(html)
    
    # 分析数据完整性
    field_names = [
        "开始时间", "结束时间", "项目结果",
        "用户主页(链接)", "用户头像(图片链接)", "分类", "用户名", "用户UID(data-username)",
        "已筹金额", "百分比", "目标金额", "支持者(数量)",
        "真实用户ID(链接提取)", "作者页-粉丝数", "作者页-关注数", "作者页-获赞数",
        "作者页-详情", "作者页-其他信息", "作者页-主页确认",
        "回报列表信息(字符串)", "回报列表项目数",
        "项目更新数", "评论数", "项目支持者/点赞数", "收藏数",
        "项目详情-图片数量", "项目详情-图片(列表字符串)",
        "项目详情-视频数量", "项目详情-视频(列表字符串)"
    ]
    
    completeness_report = {
        "project_url": project_url,
        "total_fields": len(field_names),
        "extracted_fields": len(project_data),
        "field_analysis": {},
        "critical_fields": {},
        "completeness_score": 0
    }
    
    # 分析每个字段
    non_empty_count = 0
    critical_fields_filled = 0
    critical_field_names = ["分类", "用户名", "已筹金额", "目标金额", "支持者(数量)"]
    
    for i, field_name in enumerate(field_names):
        if i < len(project_data):
            value = project_data[i]
            is_empty = value is None or str(value).strip() in ["", "none", "0", "缺失", "{}", "[]"]
            
            completeness_report["field_analysis"][field_name] = {
                "value": str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
                "is_empty": is_empty,
                "status": "❌ 空值" if is_empty else "✅ 有值"
            }
            
            if not is_empty:
                non_empty_count += 1
                
            # 检查关键字段
            if field_name in critical_field_names:
                completeness_report["critical_fields"][field_name] = {
                    "value": str(value),
                    "is_filled": not is_empty
                }
                if not is_empty:
                    critical_fields_filled += 1
        else:
            completeness_report["field_analysis"][field_name] = {
                "value": "字段缺失",
                "is_empty": True,
                "status": "❌ 缺失"
            }
    
    # 计算完整性分数
    completeness_report["completeness_score"] = (non_empty_count / len(field_names)) * 100
    completeness_report["critical_completeness"] = (critical_fields_filled / len(critical_field_names)) * 100
    
    return completeness_report

def test_multiple_projects():
    """测试多个不同类型的项目"""
    print("🚀 摩点爬虫数据完整性深度测试")
    print("=" * 80)
    
    # 测试项目列表（不同状态的项目）
    test_projects = [
        "https://zhongchou.modian.com/item/147901.html",  # 预热项目
        "https://zhongchou.modian.com/item/147828.html",  # 众筹中项目
        "https://zhongchou.modian.com/item/147457.html",  # 众筹中项目
    ]
    
    all_reports = []
    
    for project_url in test_projects:
        try:
            report = test_single_project_completeness(project_url)
            all_reports.append(report)
            
            print(f"\n📊 项目分析结果:")
            print(f"   数据完整性: {report['completeness_score']:.1f}%")
            print(f"   关键字段完整性: {report['critical_completeness']:.1f}%")
            
            # 显示关键字段状态
            print(f"\n🔑 关键字段检查:")
            for field_name, field_info in report["critical_fields"].items():
                status = "✅" if field_info["is_filled"] else "❌"
                value = field_info["value"][:30] + "..." if len(field_info["value"]) > 30 else field_info["value"]
                print(f"   {status} {field_name}: {value}")
            
            # 显示问题字段
            problem_fields = [name for name, info in report["field_analysis"].items() if info["is_empty"]]
            if problem_fields:
                print(f"\n⚠️  空值字段 ({len(problem_fields)}个):")
                for field in problem_fields[:5]:  # 只显示前5个
                    print(f"   - {field}")
                if len(problem_fields) > 5:
                    print(f"   ... 还有 {len(problem_fields) - 5} 个字段")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 生成总体报告
    if all_reports:
        print(f"\n" + "=" * 80)
        print(f"📈 总体数据完整性分析")
        print("=" * 80)
        
        avg_completeness = sum(r["completeness_score"] for r in all_reports) / len(all_reports)
        avg_critical = sum(r["critical_completeness"] for r in all_reports) / len(all_reports)
        
        print(f"测试项目数: {len(all_reports)}")
        print(f"平均数据完整性: {avg_completeness:.1f}%")
        print(f"平均关键字段完整性: {avg_critical:.1f}%")
        
        # 分析最常见的问题字段
        all_problem_fields = {}
        for report in all_reports:
            for field_name, field_info in report["field_analysis"].items():
                if field_info["is_empty"]:
                    all_problem_fields[field_name] = all_problem_fields.get(field_name, 0) + 1
        
        if all_problem_fields:
            print(f"\n🔧 最需要优化的字段:")
            sorted_problems = sorted(all_problem_fields.items(), key=lambda x: x[1], reverse=True)
            for field_name, count in sorted_problems[:10]:
                percentage = (count / len(all_reports)) * 100
                print(f"   {field_name}: {count}/{len(all_reports)} ({percentage:.1f}%)")
        
        # 评估修复效果
        print(f"\n💡 修复效果评估:")
        if avg_completeness >= 90:
            print("   ✅ 优秀 - 数据完整性超过90%")
        elif avg_completeness >= 80:
            print("   ✅ 良好 - 数据完整性超过80%")
        elif avg_completeness >= 70:
            print("   ⚠️  一般 - 数据完整性超过70%，仍需优化")
        else:
            print("   ❌ 较差 - 数据完整性低于70%，需要重点修复")
        
        if avg_critical >= 90:
            print("   ✅ 关键字段提取优秀")
        elif avg_critical >= 80:
            print("   ✅ 关键字段提取良好")
        else:
            print("   ⚠️  关键字段提取需要改进")
        
        return avg_completeness >= 80 and avg_critical >= 80
    
    return False

def test_specific_parsing_functions():
    """测试特定的解析函数"""
    print(f"\n🧪 测试特定解析函数")
    print("=" * 50)
    
    config = ModianSpiderConfig()
    spider = ModianSpider(config)
    
    # 测试项目
    test_url = "https://zhongchou.modian.com/item/147828.html"
    html = spider.askURL(test_url)
    
    if html:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # 测试项目状态解析
        print("🔍 测试项目状态解析:")
        status_info = spider.get_project_status_info(soup)
        print(f"   项目状态: {status_info}")
        
        # 测试作者信息解析
        print("\n🔍 测试作者信息解析:")
        author_info = spider.parse_upper_items(soup, status_info)
        print(f"   作者信息字段数: {len(author_info)}")
        print(f"   开始时间: {author_info[0] if len(author_info) > 0 else 'N/A'}")
        print(f"   结束时间: {author_info[1] if len(author_info) > 1 else 'N/A'}")
        print(f"   项目状态: {author_info[2] if len(author_info) > 2 else 'N/A'}")
        print(f"   作者名称: {author_info[6] if len(author_info) > 6 else 'N/A'}")
        print(f"   项目分类: {author_info[5] if len(author_info) > 5 else 'N/A'}")
        print(f"   已筹金额: {author_info[8] if len(author_info) > 8 else 'N/A'}")
        print(f"   目标金额: {author_info[10] if len(author_info) > 10 else 'N/A'}")
        
        # 测试导航信息解析
        print("\n🔍 测试导航信息解析:")
        nav_info = spider.parse_main_middle_nav_info(soup, status_info)
        print(f"   导航信息: {nav_info}")
        
        # 测试媒体内容解析
        print("\n🔍 测试媒体内容解析:")
        media_info = spider.parse_main_left_content(soup)
        print(f"   媒体信息: {media_info}")
        
        return True
    
    return False

def main():
    """主测试函数"""
    success1 = test_multiple_projects()
    success2 = test_specific_parsing_functions()
    
    print(f"\n" + "=" * 80)
    print(f"🎯 测试总结")
    print("=" * 80)
    
    if success1 and success2:
        print("✅ 所有测试通过！数据完整性修复成功")
        return True
    elif success1 or success2:
        print("⚠️  部分测试通过，仍需进一步优化")
        return True
    else:
        print("❌ 测试失败，需要继续修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
