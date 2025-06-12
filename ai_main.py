# -*- coding: utf-8 -*-
"""
桌游市场调研AI分析系统主程序
整合爬虫数据处理、AI分析和报告生成功能
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# 添加模块路径
sys.path.append(str(Path(__file__).parent))

from modules import ConfigManager, DataProcessor, AIAnalyzer, ReportGenerator


class AIAnalysisSystem:
    """AI分析系统主控制器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化AI分析系统
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.logger = self._setup_logger()
        
        try:
            # 初始化各模块
            self.config_manager = ConfigManager(config_dir)
            self.data_processor = DataProcessor(self.config_manager)
            self.ai_analyzer = AIAnalyzer(self.config_manager)
            self.report_generator = ReportGenerator(self.config_manager)
            
            self.logger.info("AI分析系统初始化成功")
            
        except Exception as e:
            self.logger.error(f"AI分析系统初始化失败: {e}")
            raise
    
    def _setup_logger(self) -> logging.Logger:
        """设置主程序日志记录器"""
        logger = logging.getLogger("AIAnalysisSystem")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件输出
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_dir / f"ai_analysis_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def run_full_analysis(self, input_file: str, output_dir: str = "reports/latest") -> bool:
        """
        运行完整的分析流程
        
        Args:
            input_file: 输入Excel文件路径
            output_dir: 输出目录
            
        Returns:
            是否成功完成分析
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("开始桌游市场调研AI分析")
            self.logger.info("=" * 80)
            
            # 步骤1: 数据处理
            self.logger.info("步骤1: 处理Excel数据...")
            processed_data_file = "data/processed/projects_data.json"
            projects_data = self.data_processor.process_excel_file(input_file, processed_data_file)
            
            if not projects_data:
                self.logger.error("数据处理失败，无法继续分析")
                return False
            
            self.logger.info(f"数据处理完成，共处理 {len(projects_data)} 个项目")
            
            # 步骤2: AI分析
            self.logger.info("步骤2: 执行AI智能分析...")
            
            # 加载缓存
            cache_file = "data/cache/analysis_cache.json"
            if os.path.exists(cache_file):
                self.ai_analyzer.load_cache(cache_file)
            
            # 批量分析项目
            analysis_results = self.ai_analyzer.batch_analyze_projects(projects_data)
            
            if not analysis_results:
                self.logger.error("AI分析失败，无法继续生成报告")
                return False
            
            self.logger.info(f"AI分析完成，共分析 {len(analysis_results)} 个项目")
            
            # 保存缓存
            self.ai_analyzer.save_cache(cache_file)
            
            # 步骤3: 趋势分析（可选）
            self.logger.info("步骤3: 执行趋势分析...")
            trend_analysis = None
            
            try:
                trend_analysis = self.ai_analyzer.analyze_trends(projects_data, "整体市场")
                if trend_analysis:
                    self.logger.info("趋势分析完成")
                else:
                    self.logger.warning("趋势分析失败，将跳过此部分")
            except Exception as e:
                self.logger.warning(f"趋势分析出错: {e}")
            
            # 步骤4: 生成报告
            self.logger.info("步骤4: 生成市场调研报告...")
            
            report_file = self.report_generator.generate_and_save_report(
                projects_data, analysis_results, output_dir, trend_analysis
            )
            
            if report_file:
                self.logger.info(f"报告生成成功: {report_file}")
            else:
                self.logger.error("报告生成失败")
                return False
            
            # 步骤5: 输出统计信息
            self._print_analysis_summary(projects_data, analysis_results, report_file)
            
            self.logger.info("=" * 80)
            self.logger.info("桌游市场调研AI分析完成")
            self.logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            self.logger.error(f"分析过程中出现错误: {e}")
            return False
    
    def _print_analysis_summary(self, projects_data: list, analysis_results: list, report_file: str):
        """打印分析摘要"""
        total_projects = len(projects_data)
        total_funding = sum(p.get('raised_amount', 0) for p in projects_data)
        avg_score = sum(r.get('overall_score', 0) for r in analysis_results) / len(analysis_results) if analysis_results else 0
        
        # 威胁等级统计
        threat_stats = {'高': 0, '中': 0, '低': 0}
        for result in analysis_results:
            threat_level = result.get('threat_level', '低')
            if threat_level in threat_stats:
                threat_stats[threat_level] += 1
        
        # AI请求统计
        ai_stats = self.ai_analyzer.get_analysis_statistics()
        
        print("\n" + "=" * 60)
        print("                    分析结果摘要")
        print("=" * 60)
        print(f"分析项目总数: {total_projects}")
        print(f"总筹款金额: {total_funding:,.0f} 元")
        print(f"平均AI评分: {avg_score:.1f} 分")
        print(f"")
        print(f"威胁等级分布:")
        print(f"  高威胁: {threat_stats['高']} 个")
        print(f"  中威胁: {threat_stats['中']} 个") 
        print(f"  低威胁: {threat_stats['低']} 个")
        print(f"")
        print(f"AI分析统计:")
        print(f"  总请求次数: {ai_stats['total_requests']}")
        print(f"  缓存命中数: {ai_stats['cache_size']}")
        print(f"  使用模型: {ai_stats['ai_model']}")
        print(f"")
        print(f"报告文件: {report_file}")
        print("=" * 60)
    
    def run_data_processing_only(self, input_file: str, output_file: str = None) -> bool:
        """
        仅运行数据处理
        
        Args:
            input_file: 输入Excel文件路径
            output_file: 输出JSON文件路径
            
        Returns:
            是否成功完成处理
        """
        try:
            self.logger.info("开始数据处理...")
            
            if not output_file:
                output_file = "data/processed/projects_data.json"
            
            projects_data = self.data_processor.process_excel_file(input_file, output_file)
            
            if projects_data:
                self.logger.info(f"数据处理完成，共处理 {len(projects_data)} 个项目")
                self.logger.info(f"处理后的数据已保存到: {output_file}")
                return True
            else:
                self.logger.error("数据处理失败")
                return False
                
        except Exception as e:
            self.logger.error(f"数据处理过程中出现错误: {e}")
            return False
    
    def run_ai_analysis_only(self, data_file: str, output_dir: str = "reports/latest") -> bool:
        """
        仅运行AI分析（基于已处理的数据）
        
        Args:
            data_file: 处理后的JSON数据文件路径
            output_dir: 输出目录
            
        Returns:
            是否成功完成分析
        """
        try:
            self.logger.info("开始AI分析...")
            
            # 加载处理后的数据
            import json
            with open(data_file, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
            
            self.logger.info(f"加载数据完成，共 {len(projects_data)} 个项目")
            
            # 加载缓存
            cache_file = "data/cache/analysis_cache.json"
            if os.path.exists(cache_file):
                self.ai_analyzer.load_cache(cache_file)
            
            # 执行AI分析
            analysis_results = self.ai_analyzer.batch_analyze_projects(projects_data)
            
            if not analysis_results:
                self.logger.error("AI分析失败")
                return False
            
            # 保存缓存
            self.ai_analyzer.save_cache(cache_file)
            
            # 生成报告
            report_file = self.report_generator.generate_and_save_report(
                projects_data, analysis_results, output_dir
            )
            
            if report_file:
                self.logger.info(f"分析完成，报告已保存到: {report_file}")
                self._print_analysis_summary(projects_data, analysis_results, report_file)
                return True
            else:
                self.logger.error("报告生成失败")
                return False
                
        except Exception as e:
            self.logger.error(f"AI分析过程中出现错误: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """
        验证系统配置
        
        Returns:
            配置是否有效
        """
        try:
            self.logger.info("验证系统配置...")
            
            # 验证配置文件
            if not self.config_manager.validate_config():
                self.logger.error("配置文件验证失败")
                return False
            
            # 检查必要的目录
            required_dirs = ["data/raw", "data/processed", "data/cache", "reports/latest", "logs"]
            for dir_path in required_dirs:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            
            # 检查AI服务连接（可选）
            try:
                # 这里可以添加AI服务连接测试
                pass
            except Exception as e:
                self.logger.warning(f"AI服务连接测试失败: {e}")
            
            self.logger.info("系统配置验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证过程中出现错误: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="桌游市场调研AI分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 完整分析流程
  python ai_main.py --input "摩点众筹-主要信息.xls" --output "reports/latest"

  # 仅数据处理
  python ai_main.py --data-only --input "摩点众筹-主要信息.xls" --output "data/processed/projects.json"

  # 仅AI分析
  python ai_main.py --ai-only --input "data/processed/projects.json" --output "reports/latest"

  # 验证配置
  python ai_main.py --validate
        """
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="输入文件路径（Excel文件或JSON文件）"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="reports/latest",
        help="输出目录或文件路径（默认: reports/latest）"
    )

    parser.add_argument(
        "--config-dir", "-c",
        type=str,
        default="config",
        help="配置文件目录（默认: config）"
    )

    parser.add_argument(
        "--data-only",
        action="store_true",
        help="仅执行数据处理，不进行AI分析"
    )

    parser.add_argument(
        "--ai-only",
        action="store_true",
        help="仅执行AI分析，输入应为处理后的JSON文件"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="验证系统配置"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出模式"
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 初始化系统
        print("正在初始化AI分析系统...")
        system = AIAnalysisSystem(args.config_dir)

        # 验证配置
        if args.validate or not args.input:
            print("验证系统配置...")
            if system.validate_configuration():
                print("✓ 系统配置验证通过")
                if args.validate:
                    return 0
            else:
                print("✗ 系统配置验证失败")
                return 1

        # 检查输入文件
        if not args.input:
            print("错误: 请指定输入文件路径")
            parser.print_help()
            return 1

        if not os.path.exists(args.input):
            print(f"错误: 输入文件不存在: {args.input}")
            return 1

        # 执行相应的操作
        success = False

        if args.data_only:
            print("执行数据处理...")
            success = system.run_data_processing_only(args.input, args.output)

        elif args.ai_only:
            print("执行AI分析...")
            success = system.run_ai_analysis_only(args.input, args.output)

        else:
            print("执行完整分析流程...")
            success = system.run_full_analysis(args.input, args.output)

        if success:
            print("✓ 操作完成成功")
            return 0
        else:
            print("✗ 操作执行失败")
            return 1

    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 1

    except Exception as e:
        print(f"程序执行出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
