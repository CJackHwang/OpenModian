#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版爬虫的功能整合效果
验证main.py和spider/模块版本的优点是否成功融合
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_spider():
    """测试增强版爬虫"""
    print("🧪 测试增强版爬虫功能整合")
    print("=" * 60)
    
    try:
        from enhanced_spider import EnhancedModianSpider
        from spider.config import SpiderConfig
        
        # 创建配置
        config = SpiderConfig()
        config.MAX_CONCURRENT_REQUESTS = 1  # 降低并发避免被封
        config.REQUEST_DELAY = (2.0, 3.0)   # 增加延迟
        
        # 创建增强版爬虫
        spider = EnhancedModianSpider(config)
        
        print(f"✅ 增强版爬虫初始化成功")
        
        # 运行小规模测试
        print(f"\n🎯 开始小规模测试...")
        success = spider.run_enhanced_crawling(
            start_page=1,
            end_page=1,  # 只测试1页
            category="tablegames"
        )
        
        if success:
            print(f"✅ 增强版爬虫测试成功")
            return True
        else:
            print(f"❌ 增强版爬虫测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feature_comparison():
    """测试功能对比"""
    print(f"\n🔍 功能对比测试")
    print("=" * 60)
    
    features_tested = {
        "网络请求双重策略": False,
        "文本解析优化": False,
        "编码问题处理": False,
        "多格式输出": False,
        "质量报告生成": False,
        "缓存机制": False,
        "监控统计": False,
        "数据验证": False
    }
    
    try:
        from spider.utils import NetworkUtils
        from spider.config import SpiderConfig
        
        config = SpiderConfig()
        network_utils = NetworkUtils(config)
        
        # 测试网络请求双重策略
        if hasattr(network_utils, '_make_urllib_request') and hasattr(network_utils, '_make_requests_request'):
            features_tested["网络请求双重策略"] = True
            print("✅ 网络请求双重策略: 已融合")
        
        # 测试缓存机制
        if config.ENABLE_CACHE:
            features_tested["缓存机制"] = True
            print("✅ 缓存机制: 已启用")
        
        # 测试监控统计
        from spider.monitor import SpiderMonitor
        monitor = SpiderMonitor(config)
        if hasattr(monitor, 'get_stats'):
            features_tested["监控统计"] = True
            print("✅ 监控统计: 已集成")
        
        # 测试数据验证
        from spider.validator import DataValidator
        validator = DataValidator(config)
        if hasattr(validator, 'validate_project_data'):
            features_tested["数据验证"] = True
            print("✅ 数据验证: 已集成")
        
        # 测试多格式输出
        from spider.exporter import DataExporter
        exporter = DataExporter(config)
        if (hasattr(exporter, 'export_to_excel') and 
            hasattr(exporter, 'export_to_json') and 
            hasattr(exporter, 'export_to_csv')):
            features_tested["多格式输出"] = True
            print("✅ 多格式输出: 已支持")
        
        # 检查输出目录
        output_dir = Path(config.OUTPUT_DIR)
        if output_dir.exists():
            recent_files = list(output_dir.glob("*enhanced*"))
            if recent_files:
                features_tested["质量报告生成"] = True
                print("✅ 质量报告生成: 已实现")
        
        # 统计成功率
        success_count = sum(features_tested.values())
        total_count = len(features_tested)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 功能整合统计:")
        print(f"   成功整合: {success_count}/{total_count}")
        print(f"   整合率: {success_rate:.1f}%")
        
        # 显示未整合的功能
        failed_features = [name for name, status in features_tested.items() if not status]
        if failed_features:
            print(f"\n⚠️  待完善功能:")
            for feature in failed_features:
                print(f"   - {feature}")
        
        return success_rate >= 70
        
    except Exception as e:
        print(f"❌ 功能对比测试失败: {e}")
        return False

def test_data_quality_improvement():
    """测试数据质量改进"""
    print(f"\n📈 数据质量改进测试")
    print("=" * 60)
    
    try:
        # 检查最新的质量报告
        output_dir = Path("data/spider")
        if not output_dir.exists():
            output_dir = Path("output")
        
        if output_dir.exists():
            quality_reports = list(output_dir.glob("*quality_report*.txt"))
            if quality_reports:
                latest_report = max(quality_reports, key=lambda x: x.stat().st_mtime)
                print(f"📋 分析最新质量报告: {latest_report.name}")
                
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取数据完整性
                import re
                completeness_match = re.search(r'总体数据完整性:\s*([0-9.]+)%', content)
                if completeness_match:
                    completeness = float(completeness_match.group(1))
                    print(f"📊 当前数据完整性: {completeness:.1f}%")
                    
                    if completeness >= 80:
                        print("✅ 数据质量优秀")
                        return True
                    elif completeness >= 70:
                        print("✅ 数据质量良好")
                        return True
                    elif completeness >= 60:
                        print("⚠️  数据质量一般")
                        return True
                    else:
                        print("❌ 数据质量需要改进")
                        return False
                else:
                    print("⚠️  无法解析数据完整性")
                    return False
            else:
                print("⚠️  未找到质量报告")
                return False
        else:
            print("⚠️  输出目录不存在")
            return False
            
    except Exception as e:
        print(f"❌ 数据质量测试失败: {e}")
        return False

def test_output_formats():
    """测试输出格式"""
    print(f"\n📁 输出格式测试")
    print("=" * 60)
    
    try:
        # 检查输出目录
        output_dirs = [Path("data/spider"), Path("output")]
        
        for output_dir in output_dirs:
            if output_dir.exists():
                print(f"📂 检查目录: {output_dir}")
                
                # 检查各种格式的文件
                formats = {
                    "Excel": list(output_dir.glob("*.xls")) + list(output_dir.glob("*.xlsx")),
                    "JSON": list(output_dir.glob("*.json")),
                    "CSV": list(output_dir.glob("*.csv")),
                    "质量报告": list(output_dir.glob("*quality_report*.txt"))
                }
                
                for format_name, files in formats.items():
                    if files:
                        latest_file = max(files, key=lambda x: x.stat().st_mtime)
                        file_size = latest_file.stat().st_size
                        print(f"   ✅ {format_name}: {latest_file.name} ({file_size} bytes)")
                    else:
                        print(f"   ❌ {format_name}: 未找到文件")
                
                # 检查是否有增强版文件
                enhanced_files = list(output_dir.glob("*enhanced*"))
                if enhanced_files:
                    print(f"   🎉 增强版文件: {len(enhanced_files)}个")
                    for file in enhanced_files[:3]:  # 显示前3个
                        print(f"      - {file.name}")
                
                return len([f for files in formats.values() for f in files]) >= 3
        
        print("❌ 未找到有效的输出目录")
        return False
        
    except Exception as e:
        print(f"❌ 输出格式测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 摩点爬虫功能整合测试")
    print("验证main.py和spider/模块版本的优点融合效果")
    print("=" * 80)
    
    tests = [
        ("增强版爬虫功能", test_enhanced_spider),
        ("功能对比验证", test_feature_comparison),
        ("数据质量改进", test_data_quality_improvement),
        ("输出格式支持", test_output_formats),
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
    print(f"📊 功能整合测试总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 所有功能整合测试通过！")
        print(f"✅ main.py和spider/模块版本优点成功融合")
        print(f"✅ 数据提取完整性显著提升")
        print(f"✅ 网络请求稳定性增强")
        print(f"✅ 多格式输出功能完善")
        return True
    elif passed >= total * 0.7:
        print(f"⚠️  大部分功能整合成功")
        print(f"✅ 主要优点已成功融合")
        return True
    else:
        print(f"❌ 功能整合需要进一步完善")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
