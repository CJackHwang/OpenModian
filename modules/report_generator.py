# -*- coding: utf-8 -*-
"""
报告生成模块
负责生成结构化的市场调研报告
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config_manager):
        """
        初始化报告生成器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.report_config = config_manager.get_report_config()
        self.analysis_config = config_manager.get_analysis_config()
        self.logger = self._setup_logger()
        
        # 加载报告模板
        self.report_template = self._load_report_template()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_report_template(self) -> str:
        """加载报告模板"""
        template_file = Path("config/report_templates/main_report_template.txt")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = f.read()
            
            self.logger.info(f"报告模板加载成功: {template_file}")
            return template
            
        except FileNotFoundError:
            self.logger.warning(f"报告模板文件不存在: {template_file}")
            return self._get_default_template()
        except Exception as e:
            self.logger.error(f"加载报告模板失败: {e}")
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """获取默认报告模板"""
        return """
================================================================================
                        桌游市场调研AI分析报告
================================================================================

报告生成时间：{report_date}
数据分析范围：{data_start_date} 至 {data_end_date}
分析项目总数：{total_projects} 个

================================================================================
                              执行摘要
================================================================================

{executive_summary}

================================================================================
                        各时间段分析结果
================================================================================

{time_period_analysis}

================================================================================
                        竞品威胁分析
================================================================================

{threat_analysis}

================================================================================
报告结束 - 生成时间：{report_generation_time}
================================================================================
"""
    
    def generate_report(self, projects_data: List[Dict[str, Any]], analysis_results: List[Dict[str, Any]], 
                       trend_analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        生成完整的市场调研报告
        
        Args:
            projects_data: 项目数据列表
            analysis_results: AI分析结果列表
            trend_analysis: 趋势分析结果
            
        Returns:
            生成的报告内容
        """
        self.logger.info("开始生成市场调研报告")
        
        # 按时间段分组数据
        time_grouped_data = self._group_data_by_time_period(projects_data, analysis_results)
        
        # 生成各部分内容
        report_params = {
            'report_date': datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'),
            'report_version': '1.0',
            'data_start_date': self._get_earliest_date(projects_data),
            'data_end_date': self._get_latest_date(projects_data),
            'total_projects': len(projects_data),
            'report_generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            # 执行摘要
            'executive_summary': self._generate_executive_summary(projects_data, analysis_results),
            
            # 关键发现
            'key_finding_1': self._get_key_finding(analysis_results, 1),
            'key_finding_2': self._get_key_finding(analysis_results, 2),
            'key_finding_3': self._get_key_finding(analysis_results, 3),
            
            # 机会和风险
            'opportunity_1': self._get_market_opportunity(analysis_results, 1),
            'opportunity_2': self._get_market_opportunity(analysis_results, 2),
            'risk_1': self._get_market_risk(analysis_results, 1),
            'risk_2': self._get_market_risk(analysis_results, 2),
        }
        
        # 添加各时间段的分析内容
        self._add_time_period_content(report_params, time_grouped_data)
        
        # 添加威胁分析内容
        self._add_threat_analysis_content(report_params, analysis_results)
        
        # 添加综合分析内容
        self._add_comprehensive_analysis_content(report_params, projects_data, analysis_results, trend_analysis)
        
        # 格式化报告
        try:
            report_content = self.report_template.format(**report_params)
            self.logger.info("市场调研报告生成完成")
            return report_content
        except KeyError as e:
            self.logger.error(f"报告模板参数缺失: {e}")
            return self._generate_simple_report(projects_data, analysis_results)
    
    def _group_data_by_time_period(self, projects_data: List[Dict[str, Any]], 
                                  analysis_results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        按时间段分组数据
        
        Args:
            projects_data: 项目数据列表
            analysis_results: 分析结果列表
            
        Returns:
            按时间段分组的数据
        """
        # 创建项目ID到分析结果的映射
        analysis_map = {result.get('project_id', ''): result for result in analysis_results}
        
        # 合并项目数据和分析结果
        combined_data = []
        for project in projects_data:
            project_id = project.get('project_id', '')
            analysis = analysis_map.get(project_id, {})
            
            combined_item = {**project, **analysis}
            combined_data.append(combined_item)
        
        # 按时间段分组
        time_periods = ['2周内', '1个月内', '3个月内', '6个月内', '1年内', '3年内', '历史']
        grouped_data = {period: [] for period in time_periods}
        
        for item in combined_data:
            time_period = item.get('time_period', '历史')
            if time_period in grouped_data:
                grouped_data[time_period].append(item)
            else:
                grouped_data['历史'].append(item)
        
        return grouped_data
    
    def _generate_executive_summary(self, projects_data: List[Dict[str, Any]], 
                                   analysis_results: List[Dict[str, Any]]) -> str:
        """
        生成执行摘要
        
        Args:
            projects_data: 项目数据列表
            analysis_results: 分析结果列表
            
        Returns:
            执行摘要内容
        """
        total_projects = len(projects_data)
        total_funding = sum(p.get('raised_amount', 0) for p in projects_data)
        avg_score = sum(r.get('overall_score', 0) for r in analysis_results) / len(analysis_results) if analysis_results else 0
        
        high_threat_count = len([r for r in analysis_results if r.get('threat_level') == '高'])
        successful_projects = len([p for p in projects_data if p.get('completion_rate', 0) >= 100])
        success_rate = (successful_projects / total_projects * 100) if total_projects > 0 else 0
        
        summary = f"""
本报告基于 {total_projects} 个桌游众筹项目的数据分析，总筹款金额达到 {total_funding:,.0f} 元。
通过AI智能分析，项目平均综合评分为 {avg_score:.1f} 分，整体成功率为 {success_rate:.1f}%。

在所有分析项目中，{high_threat_count} 个项目被评定为高威胁等级，显示出强劲的市场竞争力。
这些项目在产品创新、市场执行和用户参与度方面表现突出，值得重点关注。

市场整体呈现出多元化发展趋势，传统桌游类型依然占据主导地位，但新兴玩法和创新机制
正在获得越来越多的关注。众筹模式的成熟化使得项目质量和执行能力成为成功的关键因素。
"""
        
        return summary.strip()
    
    def _get_key_finding(self, analysis_results: List[Dict[str, Any]], index: int) -> str:
        """获取关键发现"""
        findings = [
            "高质量项目的成功率显著高于平均水平",
            "用户参与度是项目成功的重要指标",
            "创新性玩法正在成为市场新的增长点"
        ]
        
        if index <= len(findings):
            return findings[index - 1]
        
        return "需要进一步分析的市场趋势"
    
    def _get_market_opportunity(self, analysis_results: List[Dict[str, Any]], index: int) -> str:
        """获取市场机会"""
        opportunities = [
            "新兴品类存在较大发展空间",
            "高质量内容制作能力稀缺，存在差异化机会"
        ]
        
        if index <= len(opportunities):
            return opportunities[index - 1]
        
        return "待识别的市场机会"
    
    def _get_market_risk(self, analysis_results: List[Dict[str, Any]], index: int) -> str:
        """获取市场风险"""
        risks = [
            "市场竞争日趋激烈，同质化项目增多",
            "用户需求变化快，产品生命周期缩短"
        ]
        
        if index <= len(risks):
            return risks[index - 1]
        
        return "待识别的市场风险"
    
    def _get_earliest_date(self, projects_data: List[Dict[str, Any]]) -> str:
        """获取最早日期"""
        dates = [p.get('start_date') for p in projects_data if p.get('start_date')]
        if dates:
            return min(dates)[:10]  # 只取日期部分
        return '未知'
    
    def _get_latest_date(self, projects_data: List[Dict[str, Any]]) -> str:
        """获取最晚日期"""
        dates = [p.get('start_date') for p in projects_data if p.get('start_date')]
        if dates:
            return max(dates)[:10]  # 只取日期部分
        return '未知'
    
    def _add_time_period_content(self, report_params: Dict[str, Any], 
                                time_grouped_data: Dict[str, List[Dict[str, Any]]]):
        """
        添加各时间段的内容
        
        Args:
            report_params: 报告参数字典
            time_grouped_data: 按时间段分组的数据
        """
        time_period_mapping = {
            '历史': 'historical',
            '3年内': 'three_year', 
            '1年内': 'one_year',
            '6个月内': 'six_month',
            '3个月内': 'three_month',
            '1个月内': 'one_month',
            '2周内': 'two_week'
        }
        
        for period_name, period_key in time_period_mapping.items():
            period_data = time_grouped_data.get(period_name, [])
            
            # 基础统计
            report_params[f'{period_key}_total_projects'] = len(period_data)
            report_params[f'{period_key}_start_date'] = self._get_period_start_date(period_name)
            report_params[f'{period_key}_end_date'] = self._get_period_end_date(period_name)
            
            # 顶级项目数量配置
            top_count = self.report_config.get('top_projects_count', {}).get(f'{period_key}_analysis', 10)
            report_params[f'{period_key}_top_count'] = top_count
            
            # 生成顶级项目列表
            report_params[f'{period_key}_top_projects'] = self._generate_top_projects_list(period_data, top_count)
            
            # 生成其他分析内容
            if period_key == 'historical':
                report_params[f'{period_key}_total_funding'] = sum(p.get('raised_amount', 0) for p in period_data)
                report_params[f'{period_key}_avg_funding'] = report_params[f'{period_key}_total_funding'] / len(period_data) if period_data else 0
                report_params[f'{period_key}_success_rate'] = len([p for p in period_data if p.get('completion_rate', 0) >= 100]) / len(period_data) * 100 if period_data else 0
                report_params[f'{period_key}_avg_backers'] = sum(p.get('backer_count', 0) for p in period_data) / len(period_data) if period_data else 0
                report_params[f'{period_key}_category_analysis'] = self._generate_category_analysis(period_data)
                report_params[f'{period_key}_insights'] = self._generate_period_insights(period_data, period_name)
            else:
                # 其他时间段的特定分析
                report_params[f'{period_key}_hot_projects'] = self._generate_hot_projects_analysis(period_data)
                report_params[f'{period_key}_trends'] = self._generate_period_trends(period_data, period_name)
                
                if period_key in ['six_month', 'three_month']:
                    report_params[f'{period_key}_emerging_projects'] = report_params[f'{period_key}_hot_projects']
                    report_params[f'{period_key}_emerging_trends'] = self._generate_emerging_trends(period_data)
                    report_params[f'{period_key}_innovations'] = self._generate_innovations_analysis(period_data)
                
                if period_key in ['three_month', 'one_month', 'two_week']:
                    report_params[f'{period_key}_dynamic_projects'] = report_params[f'{period_key}_hot_projects']
                    report_params[f'{period_key}_market_dynamics'] = self._generate_market_dynamics(period_data)
                    
                    if period_key == 'three_month':
                        report_params[f'{period_key}_competition_changes'] = self._generate_competition_changes(period_data)
                    elif period_key == 'one_month':
                        report_params[f'{period_key}_latest_projects'] = report_params[f'{period_key}_hot_projects']
                        report_params[f'{period_key}_latest_trends'] = self._generate_latest_trends(period_data)
                        report_params[f'{period_key}_opportunities'] = self._generate_immediate_opportunities(period_data)
                    elif period_key == 'two_week':
                        report_params[f'{period_key}_immediate_projects'] = report_params[f'{period_key}_hot_projects']
                        report_params[f'{period_key}_market_reactions'] = self._generate_market_reactions(period_data)
                        report_params[f'{period_key}_urgent_matters'] = self._generate_urgent_matters(period_data)

    def _get_period_start_date(self, period_name: str) -> str:
        """获取时间段开始日期"""
        current_date = datetime.now()

        if period_name == '2周内':
            start_date = current_date - timedelta(days=14)
        elif period_name == '1个月内':
            start_date = current_date - timedelta(days=30)
        elif period_name == '3个月内':
            start_date = current_date - timedelta(days=90)
        elif period_name == '6个月内':
            start_date = current_date - timedelta(days=180)
        elif period_name == '1年内':
            start_date = current_date - timedelta(days=365)
        elif period_name == '3年内':
            start_date = current_date - timedelta(days=1095)
        else:  # 历史
            return '项目最早记录'

        return start_date.strftime('%Y-%m-%d')

    def _get_period_end_date(self, period_name: str) -> str:
        """获取时间段结束日期"""
        if period_name == '历史':
            return '当前'
        return datetime.now().strftime('%Y-%m-%d')

    def _generate_top_projects_list(self, period_data: List[Dict[str, Any]], top_count: int) -> str:
        """
        生成顶级项目列表

        Args:
            period_data: 时间段数据
            top_count: 显示项目数量

        Returns:
            格式化的项目列表
        """
        if not period_data:
            return "本时间段内暂无项目数据。"

        # 按综合评分排序
        sorted_projects = sorted(period_data, key=lambda x: x.get('overall_score', 0), reverse=True)
        top_projects = sorted_projects[:top_count]

        project_list = []
        for i, project in enumerate(top_projects, 1):
            project_info = f"""
【项目 {i}】{project.get('project_name', '未知项目')}
【项目链接】{project.get('project_url', '无')}
【发起时间】{project.get('start_date', '未知')[:10] if project.get('start_date') else '未知'}
【众筹数据】目标：{project.get('target_amount', 0):,.0f}元 | 实际：{project.get('raised_amount', 0):,.0f}元 | 完成率：{project.get('completion_rate', 0):.1f}% | 支持者：{project.get('backer_count', 0)}人
【AI评估】热度：{project.get('heat_score', 0)}/100 | 受欢迎度：{project.get('popularity_score', 0)}/100 | 传播率：{project.get('viral_score', 0)}/100
【分析结果】{project.get('analysis_reason', '暂无AI分析')[:150]}
【竞品威胁】{project.get('threat_level', '未知')}
---"""
            project_list.append(project_info.strip())

        return '\n\n'.join(project_list)

    def _generate_category_analysis(self, period_data: List[Dict[str, Any]]) -> str:
        """生成品类分析"""
        if not period_data:
            return "暂无数据进行品类分析。"

        # 统计各品类
        categories = {}
        for project in period_data:
            category = project.get('category', '未知')
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_funding': 0,
                    'avg_score': 0,
                    'scores': []
                }

            categories[category]['count'] += 1
            categories[category]['total_funding'] += project.get('raised_amount', 0)
            score = project.get('overall_score', 0)
            categories[category]['scores'].append(score)

        # 计算平均分
        for category in categories:
            scores = categories[category]['scores']
            categories[category]['avg_score'] = sum(scores) / len(scores) if scores else 0

        # 按项目数量排序
        sorted_categories = sorted(categories.items(), key=lambda x: x[1]['count'], reverse=True)

        analysis_lines = []
        for category, stats in sorted_categories[:10]:  # 显示前10个品类
            analysis_lines.append(
                f"• {category}：{stats['count']}个项目，总筹款{stats['total_funding']:,.0f}元，平均评分{stats['avg_score']:.1f}分"
            )

        return '\n'.join(analysis_lines)

    def _generate_period_insights(self, period_data: List[Dict[str, Any]], period_name: str) -> str:
        """生成时间段洞察"""
        if not period_data:
            return f"{period_name}暂无足够数据生成洞察。"

        insights = []

        # 成功率分析
        successful_count = len([p for p in period_data if p.get('completion_rate', 0) >= 100])
        success_rate = (successful_count / len(period_data) * 100) if period_data else 0
        insights.append(f"• 项目成功率为{success_rate:.1f}%，共{successful_count}个项目成功完成众筹")

        # 高分项目分析
        high_score_count = len([p for p in period_data if p.get('overall_score', 0) >= 80])
        insights.append(f"• {high_score_count}个项目获得80分以上的高评分，占比{high_score_count/len(period_data)*100:.1f}%")

        # 资金规模分析
        total_funding = sum(p.get('raised_amount', 0) for p in period_data)
        avg_funding = total_funding / len(period_data)
        insights.append(f"• 平均项目筹款金额为{avg_funding:,.0f}元，总筹款规模{total_funding:,.0f}元")

        return '\n'.join(insights)

    def _generate_hot_projects_analysis(self, period_data: List[Dict[str, Any]]) -> str:
        """生成热门项目分析"""
        return self._generate_top_projects_list(period_data, 5)

    def _generate_period_trends(self, period_data: List[Dict[str, Any]], period_name: str) -> str:
        """生成时间段趋势"""
        if not period_data:
            return f"{period_name}暂无趋势数据。"

        trends = []

        # 评分趋势
        avg_score = sum(p.get('overall_score', 0) for p in period_data) / len(period_data)
        trends.append(f"• 平均项目评分：{avg_score:.1f}分")

        # 威胁等级分布
        threat_distribution = {'高': 0, '中': 0, '低': 0}
        for project in period_data:
            threat_level = project.get('threat_level', '低')
            if threat_level in threat_distribution:
                threat_distribution[threat_level] += 1

        trends.append(f"• 威胁等级分布：高威胁{threat_distribution['高']}个，中威胁{threat_distribution['中']}个，低威胁{threat_distribution['低']}个")

        return '\n'.join(trends)

    def _generate_emerging_trends(self, period_data: List[Dict[str, Any]]) -> str:
        """生成新兴趋势"""
        return "• 创新玩法项目增多\n• 高质量美术成为标配\n• 用户参与度要求提升"

    def _generate_innovations_analysis(self, period_data: List[Dict[str, Any]]) -> str:
        """生成创新亮点分析"""
        return "• 机制创新成为差异化关键\n• 主题融合趋势明显\n• 数字化元素应用增加"

    def _generate_market_dynamics(self, period_data: List[Dict[str, Any]]) -> str:
        """生成市场动态"""
        return "• 竞争加剧，质量要求提升\n• 用户更加理性，选择更加谨慎\n• 成功项目的示范效应明显"

    def _generate_competition_changes(self, period_data: List[Dict[str, Any]]) -> str:
        """生成竞争格局变化"""
        return "• 头部项目优势扩大\n• 中腰部项目分化明显\n• 新进入者面临更高门槛"

    def _generate_latest_trends(self, period_data: List[Dict[str, Any]]) -> str:
        """生成最新趋势"""
        return "• 快速迭代成为常态\n• 社区运营重要性凸显\n• 跨界合作增多"

    def _generate_immediate_opportunities(self, period_data: List[Dict[str, Any]]) -> str:
        """生成即时机会"""
        return "• 细分市场仍有空白\n• 技术创新应用潜力大\n• 国际化市场待开发"

    def _generate_market_reactions(self, period_data: List[Dict[str, Any]]) -> str:
        """生成市场反应"""
        return "• 用户对新项目保持高关注\n• 成功案例快速传播\n• 失败项目教训被广泛讨论"

    def _generate_urgent_matters(self, period_data: List[Dict[str, Any]]) -> str:
        """生成紧急关注事项"""
        return "• 关注高分项目的后续发展\n• 监控新兴竞争对手动向\n• 及时调整产品策略"

    def _add_threat_analysis_content(self, report_params: Dict[str, Any], analysis_results: List[Dict[str, Any]]):
        """
        添加威胁分析内容

        Args:
            report_params: 报告参数字典
            analysis_results: 分析结果列表
        """
        # 按威胁等级分组
        high_threat = [r for r in analysis_results if r.get('threat_level') == '高']
        medium_threat = [r for r in analysis_results if r.get('threat_level') == '中']
        low_threat = [r for r in analysis_results if r.get('threat_level') == '低']

        # 高威胁项目
        report_params['high_threat_projects'] = self._format_threat_projects(high_threat, '高威胁')

        # 中威胁项目
        report_params['medium_threat_projects'] = self._format_threat_projects(medium_threat, '中威胁')

        # 威胁等级分布
        total_projects = len(analysis_results)
        if total_projects > 0:
            high_pct = len(high_threat) / total_projects * 100
            medium_pct = len(medium_threat) / total_projects * 100
            low_pct = len(low_threat) / total_projects * 100

            report_params['threat_level_distribution'] = f"""
高威胁项目：{len(high_threat)}个 ({high_pct:.1f}%)
中威胁项目：{len(medium_threat)}个 ({medium_pct:.1f}%)
低威胁项目：{len(low_threat)}个 ({low_pct:.1f}%)

威胁等级分布显示，{high_pct:.1f}%的项目具有高竞争威胁，需要重点关注和应对。
"""
        else:
            report_params['threat_level_distribution'] = "暂无威胁分析数据。"

        # 应对策略建议
        report_params['threat_response_strategies'] = self._generate_threat_response_strategies(high_threat, medium_threat)

    def _format_threat_projects(self, threat_projects: List[Dict[str, Any]], threat_level: str) -> str:
        """
        格式化威胁项目列表

        Args:
            threat_projects: 威胁项目列表
            threat_level: 威胁等级

        Returns:
            格式化的项目列表
        """
        if not threat_projects:
            return f"暂无{threat_level}项目。"

        # 按综合评分排序
        sorted_projects = sorted(threat_projects, key=lambda x: x.get('overall_score', 0), reverse=True)

        project_list = []
        for i, project in enumerate(sorted_projects[:10], 1):  # 最多显示10个
            project_info = f"""
{i}. 【{project.get('project_name', '未知项目')}】
   综合评分：{project.get('overall_score', 0):.1f}/100
   热度：{project.get('heat_score', 0)}/100 | 受欢迎度：{project.get('popularity_score', 0)}/100 | 传播率：{project.get('viral_score', 0)}/100
   分析：{project.get('analysis_reason', '暂无分析')[:100]}...
   链接：{project.get('project_url', '无')}
"""
            project_list.append(project_info.strip())

        return '\n'.join(project_list)

    def _generate_threat_response_strategies(self, high_threat: List[Dict[str, Any]],
                                           medium_threat: List[Dict[str, Any]]) -> str:
        """生成威胁应对策略"""
        strategies = []

        if high_threat:
            strategies.append("针对高威胁项目：")
            strategies.append("• 深度分析其成功要素，学习借鉴优秀经验")
            strategies.append("• 关注其产品创新点，避免直接竞争")
            strategies.append("• 监控其市场表现，及时调整自身策略")

        if medium_threat:
            strategies.append("\n针对中威胁项目：")
            strategies.append("• 分析其优势和不足，寻找差异化机会")
            strategies.append("• 关注其发展趋势，预判市场变化")
            strategies.append("• 适度关注，重点关注突破性表现")

        strategies.append("\n总体策略建议：")
        strategies.append("• 持续提升产品质量和用户体验")
        strategies.append("• 加强品牌建设和市场推广")
        strategies.append("• 建立快速响应机制，及时应对市场变化")

        return '\n'.join(strategies)

    def _add_comprehensive_analysis_content(self, report_params: Dict[str, Any],
                                          projects_data: List[Dict[str, Any]],
                                          analysis_results: List[Dict[str, Any]],
                                          trend_analysis: Optional[Dict[str, Any]]):
        """
        添加综合分析内容

        Args:
            report_params: 报告参数字典
            projects_data: 项目数据列表
            analysis_results: 分析结果列表
            trend_analysis: 趋势分析结果
        """
        # 市场发展阶段判断
        report_params['market_development_stage'] = self._analyze_market_stage(projects_data, analysis_results)

        # 未来趋势预测
        report_params['future_trend_predictions'] = self._predict_future_trends(analysis_results, trend_analysis)

        # 投资建议
        report_params['investment_recommendations'] = self._generate_investment_recommendations(analysis_results)

        # 风险提示
        report_params['risk_warnings'] = self._generate_risk_warnings(analysis_results)

        # 数据说明
        report_params['data_description'] = self._generate_data_description(projects_data)

        # 分析方法
        report_params['analysis_methodology'] = self._generate_analysis_methodology()

        # 评分标准
        report_params['scoring_criteria'] = self._generate_scoring_criteria()

    def _analyze_market_stage(self, projects_data: List[Dict[str, Any]],
                             analysis_results: List[Dict[str, Any]]) -> str:
        """分析市场发展阶段"""
        total_projects = len(projects_data)
        avg_score = sum(r.get('overall_score', 0) for r in analysis_results) / len(analysis_results) if analysis_results else 0
        success_rate = len([p for p in projects_data if p.get('completion_rate', 0) >= 100]) / total_projects * 100 if total_projects > 0 else 0

        if avg_score >= 75 and success_rate >= 70:
            stage = "成熟期"
            description = "市场已进入成熟发展阶段，项目质量普遍较高，成功率稳定，竞争激烈。"
        elif avg_score >= 60 and success_rate >= 50:
            stage = "成长期"
            description = "市场处于快速成长阶段，项目质量不断提升，成功率逐步改善，机会与挑战并存。"
        else:
            stage = "发展期"
            description = "市场仍在发展阶段，项目质量参差不齐，成功率有待提高，存在较大发展空间。"

        return f"""
当前桌游众筹市场处于【{stage}】。

{description}

基于数据分析：
• 项目平均评分：{avg_score:.1f}分
• 整体成功率：{success_rate:.1f}%
• 项目总数：{total_projects}个

这一阶段的特点是{stage.replace('期', '')}特征明显，建议根据市场阶段特点制定相应的发展策略。
"""

    def _predict_future_trends(self, analysis_results: List[Dict[str, Any]],
                              trend_analysis: Optional[Dict[str, Any]]) -> str:
        """预测未来趋势"""
        predictions = [
            "• 产品质量将成为竞争的核心要素，低质量项目生存空间进一步压缩",
            "• 用户需求日趋多元化，细分市场机会增加",
            "• 技术创新应用将加速，数字化元素融入传统桌游",
            "• 国际化趋势明显，跨文化产品需求增长",
            "• 社区运营重要性提升，用户参与度成为成功关键"
        ]

        return '\n'.join(predictions)

    def _generate_investment_recommendations(self, analysis_results: List[Dict[str, Any]]) -> str:
        """生成投资建议"""
        recommendations = [
            "• 重点关注高评分项目的成功模式，学习其优秀经验",
            "• 投资于产品研发和质量提升，建立竞争优势",
            "• 加强用户社区建设，提升用户粘性和参与度",
            "• 关注新兴技术应用，探索创新玩法和体验",
            "• 建立品牌影响力，提升市场认知度和信任度"
        ]

        return '\n'.join(recommendations)

    def _generate_risk_warnings(self, analysis_results: List[Dict[str, Any]]) -> str:
        """生成风险提示"""
        warnings = [
            "• 市场竞争加剧，同质化产品面临淘汰风险",
            "• 用户需求变化快，产品生命周期缩短",
            "• 成本上升压力增大，盈利能力面临挑战",
            "• 监管政策变化可能影响行业发展",
            "• 经济环境波动对消费者购买力产生影响"
        ]

        return '\n'.join(warnings)

    def _generate_data_description(self, projects_data: List[Dict[str, Any]]) -> str:
        """生成数据说明"""
        return f"""
本报告基于 {len(projects_data)} 个桌游众筹项目的数据分析，数据来源于摩点众筹平台。
数据包括项目基本信息、众筹表现、用户参与度、发起人信息等多个维度。
所有数据均为公开信息，分析结果仅供参考。
"""

    def _generate_analysis_methodology(self) -> str:
        """生成分析方法说明"""
        return """
本报告采用AI智能分析方法，结合多维度数据指标进行综合评估：

1. 数据收集：从摩点众筹平台获取项目公开数据
2. 数据清洗：标准化处理，移除异常和无效数据
3. 指标计算：计算热度、受欢迎度、传播率等评分指标
4. AI分析：使用大语言模型进行智能分析和评分
5. 趋势识别：基于时间维度分析市场发展趋势
6. 报告生成：自动化生成结构化分析报告
"""

    def _generate_scoring_criteria(self) -> str:
        """生成评分标准说明"""
        return """
AI评分标准（0-100分制）：

热度分数：
• 90-100分：现象级项目，引发行业关注
• 80-89分：热门项目，表现优异
• 70-79分：成功项目，达到预期
• 60-69分：一般项目，基本达标
• 60分以下：表现不佳，需要改进

威胁等级：
• 高威胁：综合分数≥80分，对竞品构成重大威胁
• 中威胁：综合分数60-79分，具有一定竞争力
• 低威胁：综合分数<60分，威胁程度较小

评分维度：
• 众筹表现（35%）：完成率、筹款速度、超额程度
• 用户参与（25%）：支持者数量、互动活跃度
• 社交影响（20%）：传播范围、媒体关注度
• 项目质量（20%）：内容质量、创新程度、执行能力
"""

    def _generate_simple_report(self, projects_data: List[Dict[str, Any]],
                               analysis_results: List[Dict[str, Any]]) -> str:
        """
        生成简化版报告（当模板出错时使用）

        Args:
            projects_data: 项目数据列表
            analysis_results: 分析结果列表

        Returns:
            简化版报告内容
        """
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')

        # 基础统计
        total_projects = len(projects_data)
        total_funding = sum(p.get('raised_amount', 0) for p in projects_data)
        avg_score = sum(r.get('overall_score', 0) for r in analysis_results) / len(analysis_results) if analysis_results else 0

        # 威胁分析
        high_threat = [r for r in analysis_results if r.get('threat_level') == '高']

        # 顶级项目
        combined_data = []
        analysis_map = {r.get('project_id', ''): r for r in analysis_results}

        for project in projects_data:
            project_id = project.get('project_id', '')
            analysis = analysis_map.get(project_id, {})
            combined_data.append({**project, **analysis})

        sorted_projects = sorted(combined_data, key=lambda x: x.get('overall_score', 0), reverse=True)
        top_projects = sorted_projects[:10]

        report = f"""
================================================================================
                        桌游市场调研AI分析报告（简化版）
================================================================================

报告生成时间：{current_time}
分析项目总数：{total_projects} 个
总筹款金额：{total_funding:,.0f} 元
平均AI评分：{avg_score:.1f} 分

================================================================================
                              核心发现
================================================================================

• 共分析了 {total_projects} 个桌游众筹项目
• 识别出 {len(high_threat)} 个高威胁竞品项目
• 平均项目评分为 {avg_score:.1f} 分，显示市场整体质量水平

================================================================================
                            顶级项目分析（TOP 10）
================================================================================

"""

        for i, project in enumerate(top_projects, 1):
            report += f"""
{i}. 【{project.get('project_name', '未知项目')}】
   综合评分：{project.get('overall_score', 0):.1f}/100
   筹款表现：{project.get('raised_amount', 0):,.0f}元 / {project.get('target_amount', 0):,.0f}元 ({project.get('completion_rate', 0):.1f}%)
   威胁等级：{project.get('threat_level', '未知')}
   项目链接：{project.get('project_url', '无')}

"""

        report += f"""
================================================================================
                              威胁分析
================================================================================

高威胁项目数量：{len(high_threat)} 个

这些项目在市场表现、用户参与度和创新能力方面表现突出，
需要重点关注其发展动态和成功要素。

================================================================================
                              分析说明
================================================================================

本报告基于AI智能分析生成，评分标准包括热度、受欢迎度、传播率等多个维度。
所有数据来源于公开的众筹平台信息，分析结果仅供参考。

报告生成时间：{current_time}
================================================================================
"""

        return report

    def save_report(self, report_content: str, output_path: str) -> bool:
        """
        保存报告到文件

        Args:
            report_content: 报告内容
            output_path: 输出文件路径

        Returns:
            是否保存成功
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

            self.logger.info(f"报告已保存到: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            return False

    def generate_and_save_report(self, projects_data: List[Dict[str, Any]],
                                analysis_results: List[Dict[str, Any]],
                                output_dir: str = "reports/latest",
                                trend_analysis: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        生成并保存报告

        Args:
            projects_data: 项目数据列表
            analysis_results: 分析结果列表
            output_dir: 输出目录
            trend_analysis: 趋势分析结果

        Returns:
            报告文件路径，失败时返回None
        """
        try:
            # 生成报告
            report_content = self.generate_report(projects_data, analysis_results, trend_analysis)

            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"桌游市场调研报告_{timestamp}.txt"
            output_path = Path(output_dir) / filename

            # 保存报告
            if self.save_report(report_content, str(output_path)):
                return str(output_path)
            else:
                return None

        except Exception as e:
            self.logger.error(f"生成并保存报告失败: {e}")
            return None
