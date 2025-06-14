#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摩点爬虫增强版 - 融合main.py和spider/模块版本的优点
集成最佳的数据提取、网络请求、错误处理和输出功能
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spider.config import SpiderConfig
from spider.core import SpiderCore
from spider.utils import NetworkUtils, DataUtils
from spider.monitor import SpiderMonitor
from spider.validator import DataValidator
from spider.exporter import DataExporter

class EnhancedModianSpider:
    """增强版摩点爬虫 - 融合两个版本的优点"""
    
    def __init__(self, config: SpiderConfig = None):
        self.config = config or SpiderConfig()
        self.config.create_directories()
        
        # 初始化组件
        self.network_utils = NetworkUtils(self.config)
        self.monitor = SpiderMonitor(self.config)
        self.validator = DataValidator(self.config)
        self.exporter = DataExporter(self.config)
        
        # 核心爬虫
        self.spider_core = SpiderCore(self.config)
        
        print(f"🚀 增强版摩点爬虫初始化完成")
        print(f"📂 输出目录: {self.config.OUTPUT_DIR}")
        print(f"🔧 配置: 缓存={self.config.ENABLE_CACHE}, 监控={self.config.ENABLE_MONITORING}")
    
    def run_enhanced_crawling(self, start_page: int = 1, end_page: int = 3, 
                            category: str = "all") -> bool:
        """运行增强版爬取 - 融合两个版本的优点"""
        print(f"\n🎯 开始增强版爬取")
        print(f"📄 页面范围: {start_page}-{end_page}")
        print(f"🏷️  分类: {category}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # 使用spider/模块版本的核心爬取逻辑
            success = self.spider_core.start_crawling(
                start_page=start_page,
                end_page=end_page,
                category=category
            )
            
            if success and self.spider_core.projects_data:
                # 🔧 融合main.py的多格式输出和质量报告
                self._enhanced_data_export()
                
                # 数据质量分析
                self._analyze_data_quality()
                
                print(f"\n✅ 增强版爬取完成")
                return True
            else:
                print(f"\n❌ 爬取失败或无数据")
                return False
                
        except Exception as e:
            print(f"\n💥 爬取过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            end_time = time.time()
            runtime = end_time - start_time
            print(f"\n⏱️  总运行时间: {runtime:.1f}秒")
    
    def _enhanced_data_export(self):
        """增强版数据导出 - 融合main.py的多格式输出"""
        print(f"\n📊 开始增强版数据导出...")
        
        projects_data = self.spider_core.projects_data
        stats = self.spider_core.monitor.get_current_stats()
        
        # 生成时间戳
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        try:
            # 🔧 融合main.py的多格式同步输出
            exported_files = {}
            
            # Excel格式
            excel_file = self.exporter.export_to_excel(
                projects_data, 
                f"modian_projects_{timestamp}_enhanced.xls"
            )
            exported_files["excel"] = excel_file
            
            # JSON格式（带统计信息）
            json_file = self.exporter.export_to_json(
                projects_data,
                f"modian_projects_{timestamp}_enhanced.json"
            )
            exported_files["json"] = json_file
            
            # CSV格式 - 使用简单的CSV导出
            csv_file = self._export_csv_simple(projects_data, timestamp)
            exported_files["csv"] = csv_file
            
            # 🔧 融合main.py的质量报告生成
            quality_report = self._generate_enhanced_quality_report(
                projects_data, timestamp, stats
            )
            exported_files["quality_report"] = quality_report
            
            print(f"\n📁 导出文件列表:")
            for format_type, file_path in exported_files.items():
                print(f"   {format_type.upper()}: {Path(file_path).name}")
            
            return exported_files
            
        except Exception as e:
            print(f"❌ 数据导出失败: {e}")
            return {}

    def _export_csv_simple(self, projects_data: List[List[Any]], timestamp: str) -> str:
        """简单的CSV导出"""
        import csv
        from spider.config import FieldMapping

        filename = f"modian_projects_{timestamp}_enhanced.csv"
        file_path = Path(self.config.OUTPUT_DIR) / filename

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 写入表头
                headers = FieldMapping.EXCEL_COLUMNS
                writer.writerow(headers)

                # 写入数据
                for project_data in projects_data:
                    # 确保数据长度与表头一致
                    row = project_data[:len(headers)]
                    while len(row) < len(headers):
                        row.append("")
                    writer.writerow(row)

            print(f"📄 CSV文件已生成: {filename}")
            return str(file_path)

        except Exception as e:
            print(f"❌ CSV导出失败: {e}")
            return ""

    def _generate_enhanced_quality_report(self, projects_data: List[List[Any]],
                                        timestamp: str, stats: Dict) -> str:
        """生成增强版质量报告 - 融合main.py的质量分析"""
        filename = f"modian_projects_{timestamp}_enhanced_quality_report.txt"
        file_path = Path(self.config.OUTPUT_DIR) / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("摩点众筹爬虫增强版数据质量报告\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"爬虫版本: 增强版 (融合main.py + spider/模块)\n")
                f.write(f"数据项目数: {len(projects_data)}\n\n")
                
                # 🔧 融合main.py的详细质量分析
                self._write_detailed_quality_analysis(f, projects_data)
                
                # 运行统计
                if stats:
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("爬虫运行统计:\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"运行时间: {stats.get('runtime_seconds', 0):.1f}秒\n")
                    f.write(f"总请求数: {stats.get('total_requests', 0)}\n")
                    f.write(f"成功请求: {stats.get('successful_requests', 0)}\n")
                    f.write(f"失败请求: {stats.get('failed_requests', 0)}\n")
                    f.write(f"成功率: {stats.get('success_rate', 0):.1f}%\n")
                    f.write(f"页面处理: {stats.get('pages_processed', 0)}\n")
                    f.write(f"项目发现: {stats.get('projects_found', 0)}\n")
                    f.write(f"项目处理: {stats.get('projects_processed', 0)}\n")
                
                f.write(f"\n报告结束\n")
            
            print(f"📋 质量报告已生成: {filename}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 质量报告生成失败: {e}")
            return ""
    
    def _write_detailed_quality_analysis(self, f, projects_data: List[List[Any]]):
        """写入详细的质量分析 - 融合main.py的分析逻辑"""
        from spider.config import FieldMapping
        
        headers = FieldMapping.EXCEL_COLUMNS
        total_fields = len(headers)
        total_projects = len(projects_data)
        
        f.write("=" * 50 + "\n")
        f.write("数据完整性分析:\n")
        f.write("=" * 50 + "\n")
        
        # 字段完整性统计
        field_stats = {}
        for i, header in enumerate(headers):
            non_empty_count = 0
            for project_data in projects_data:
                if i < len(project_data):
                    value = project_data[i]
                    if value and str(value).strip() not in ["", "none", "0", "缺失", "{}", "[]"]:
                        non_empty_count += 1
            
            completeness = (non_empty_count / total_projects) * 100 if total_projects > 0 else 0
            field_stats[header] = {
                "filled": non_empty_count,
                "total": total_projects,
                "completeness": completeness
            }
        
        # 总体完整性
        total_filled = sum(stats["filled"] for stats in field_stats.values())
        total_possible = total_fields * total_projects
        overall_completeness = (total_filled / total_possible) * 100 if total_possible > 0 else 0
        
        f.write(f"总体数据完整性: {overall_completeness:.2f}%\n")
        f.write(f"总字段数: {total_fields}\n")
        f.write(f"总项目数: {total_projects}\n")
        f.write(f"已填充字段: {total_filled}/{total_possible}\n\n")
        
        # 关键字段分析
        key_fields = ["项目名称", "分类", "已筹金额", "目标金额", "支持者(数量)", "作者名称"]
        f.write("关键字段完整性:\n")
        f.write("-" * 30 + "\n")
        
        for field in key_fields:
            if field in field_stats:
                stats = field_stats[field]
                f.write(f"  {field}: {stats['completeness']:.1f}% ({stats['filled']}/{stats['total']})\n")
        
        # 问题字段识别
        f.write(f"\n数据质量问题字段 (完整性 < 80%):\n")
        f.write("-" * 40 + "\n")
        
        problem_fields = [(field, stats) for field, stats in field_stats.items() 
                         if stats["completeness"] < 80]
        problem_fields.sort(key=lambda x: x[1]["completeness"])
        
        for field, stats in problem_fields[:10]:  # 显示前10个问题字段
            missing_count = stats["total"] - stats["filled"]
            f.write(f"  {field}: 缺失数量: {missing_count}, 完整性: {stats['completeness']:.1f}%\n")
    
    def _analyze_data_quality(self):
        """分析数据质量"""
        projects_data = self.spider_core.projects_data
        
        if not projects_data:
            print("❌ 无数据可分析")
            return
        
        print(f"\n📈 数据质量分析:")
        print(f"   项目总数: {len(projects_data)}")
        
        # 简单的完整性检查
        if projects_data:
            sample_project = projects_data[0]
            field_count = len(sample_project)
            non_empty_count = sum(1 for field in sample_project 
                                if field and str(field) not in ["0", "none", "缺失", ""])
            completeness = (non_empty_count / field_count) * 100
            
            print(f"   字段总数: {field_count}")
            print(f"   非空字段: {non_empty_count}")
            print(f"   数据完整性: {completeness:.1f}%")
            
            if completeness >= 80:
                print("   ✅ 数据质量良好")
            elif completeness >= 60:
                print("   ⚠️  数据质量一般")
            else:
                print("   ❌ 数据质量需要改进")

def main():
    """主函数"""
    print("🚀 摩点爬虫增强版启动")
    print("融合main.py和spider/模块版本的优点")
    print("=" * 60)
    
    # 创建配置
    config = SpiderConfig()
    config.MAX_CONCURRENT_REQUESTS = 3  # 适中的并发数
    config.REQUEST_DELAY = (1.0, 2.0)   # 适中的延迟
    
    # 创建增强版爬虫
    spider = EnhancedModianSpider(config)
    
    # 运行爬取
    success = spider.run_enhanced_crawling(
        start_page=1,
        end_page=2,  # 测试用小范围
        category="tablegames"  # 桌游分类
    )
    
    if success:
        print("\n🎉 增强版爬虫运行成功！")
        print("✅ 已融合两个版本的优点")
        print("✅ 数据提取完整性优化")
        print("✅ 网络请求稳定性增强")
        print("✅ 多格式输出支持")
        print("✅ 质量报告生成")
    else:
        print("\n❌ 增强版爬虫运行失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
