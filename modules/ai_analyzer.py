# -*- coding: utf-8 -*-
"""
AI分析模块
负责调用AI服务对桌游项目进行智能分析和评分
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from openai import OpenAI


class AIAnalyzer:
    """AI分析器"""
    
    def __init__(self, config_manager):
        """
        初始化AI分析器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.ai_config = config_manager.get_ai_config()
        self.request_settings = config_manager.get_request_settings()
        self.analysis_config = config_manager.get_analysis_config()
        self.logger = self._setup_logger()
        
        # 初始化AI客户端
        self.client = self._init_ai_client()
        
        # 请求计数和速率限制
        self.request_count = 0
        self.last_request_time = 0
        
        # 缓存
        self.analysis_cache = {}
    
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
    
    def _init_ai_client(self) -> OpenAI:
        """初始化AI客户端"""
        try:
            client = OpenAI(
                api_key=self.ai_config.get('api_key'),
                base_url=self.ai_config.get('base_url'),
                timeout=self.ai_config.get('timeout', 30)
            )
            
            self.logger.info(f"AI客户端初始化成功: {self.ai_config.get('provider')}")
            return client
            
        except Exception as e:
            self.logger.error(f"AI客户端初始化失败: {e}")
            raise
    
    def _rate_limit_check(self):
        """检查速率限制"""
        rate_limit = self.request_settings.get('rate_limit', 60)  # 每分钟请求数
        min_interval = 60.0 / rate_limit  # 最小请求间隔（秒）
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            self.logger.info(f"速率限制：等待 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_ai_request(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """
        发送AI请求
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            AI响应内容
        """
        # 速率限制检查
        self._rate_limit_check()
        
        # 准备请求参数
        request_params = {
            'model': self.ai_config.get('model'),
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.ai_config.get('max_tokens', 2000)),
            'temperature': kwargs.get('temperature', self.ai_config.get('temperature', 0.3)),
            'top_p': kwargs.get('top_p', 0.9),
            'frequency_penalty': kwargs.get('frequency_penalty', 0.1),
            'presence_penalty': kwargs.get('presence_penalty', 0.1)
        }
        
        # 重试机制
        max_retries = self.request_settings.get('max_retries', 3)
        retry_delay = self.request_settings.get('retry_delay', 1)
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"发送AI请求 (尝试 {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(**request_params)
                
                if response.choices and response.choices[0].message:
                    content = response.choices[0].message.content
                    self.logger.info("AI请求成功")
                    return content
                else:
                    self.logger.warning("AI响应为空")
                    return None
                    
            except Exception as e:
                self.logger.error(f"AI请求失败 (尝试 {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                else:
                    self.logger.error("所有重试都失败了")
                    return None
        
        return None
    
    def analyze_project(self, project_data: Dict[str, Any], template_name: str = "project_scoring") -> Optional[Dict[str, Any]]:
        """
        分析单个项目
        
        Args:
            project_data: 项目数据
            template_name: 提示词模板名称
            
        Returns:
            分析结果
        """
        try:
            # 检查缓存
            project_id = project_data.get('project_id', '')
            cache_key = f"{project_id}_{template_name}"
            
            if cache_key in self.analysis_cache:
                self.logger.info(f"使用缓存结果: {project_id}")
                return self.analysis_cache[cache_key]
            
            # 获取提示词模板
            prompt_template = self.config_manager.get_prompt_template(template_name)
            
            # 准备提示词参数
            prompt_params = self._prepare_prompt_params(project_data)
            
            # 格式化提示词
            formatted_prompt = prompt_template['template'].format(**prompt_params)
            
            # 准备消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的桌游市场分析师，请根据提供的数据进行客观、准确的分析。"
                },
                {
                    "role": "user", 
                    "content": formatted_prompt
                }
            ]
            
            # 发送AI请求
            template_params = prompt_template.get('parameters', {})
            response_content = self._make_ai_request(messages, **template_params)
            
            if not response_content:
                self.logger.error(f"项目分析失败: {project_id}")
                return None
            
            # 解析响应
            analysis_result = self._parse_analysis_response(response_content, project_data)
            
            # 缓存结果
            self.analysis_cache[cache_key] = analysis_result
            
            self.logger.info(f"项目分析完成: {project_id}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"分析项目时出错: {e}")
            return None
    
    def _prepare_prompt_params(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备提示词参数
        
        Args:
            project_data: 项目数据
            
        Returns:
            提示词参数字典
        """
        return {
            'project_name': project_data.get('project_name', '未知'),
            'category': project_data.get('category', '未知'),
            'start_date': project_data.get('start_date', '未知'),
            'end_date': project_data.get('end_date', '未知'),
            'project_status': project_data.get('project_status', '未知'),
            'target_amount': project_data.get('target_amount', 0),
            'raised_amount': project_data.get('raised_amount', 0),
            'completion_rate': project_data.get('completion_rate', 0),
            'backer_count': project_data.get('backer_count', 0),
            'duration_days': project_data.get('duration_days', 0),
            'daily_average': project_data.get('daily_average', 0),
            'update_count': project_data.get('update_count', 0),
            'comment_count': project_data.get('comment_count', 0),
            'favorite_count': project_data.get('favorite_count', 0),
            'supporter_count': project_data.get('supporter_count', 0),
            'author_fans': project_data.get('author_fans', 0),
            'author_following': project_data.get('author_following', 0),
            'author_likes': project_data.get('author_likes', 0),
            'author_experience': project_data.get('author_experience', ''),
            'image_count': project_data.get('image_count', 0),
            'video_count': project_data.get('video_count', 0),
            'reward_tiers': project_data.get('reward_tiers', 0),
            'reward_details': project_data.get('reward_details', '')[:500]  # 限制长度
        }
    
    def _parse_analysis_response(self, response_content: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析AI分析响应
        
        Args:
            response_content: AI响应内容
            project_data: 原始项目数据
            
        Returns:
            解析后的分析结果
        """
        try:
            # 尝试提取JSON部分
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                analysis_result = json.loads(json_str)
            else:
                # 如果没有找到JSON，创建默认结果
                analysis_result = self._create_default_analysis(project_data)
                self.logger.warning("无法解析AI响应，使用默认分析结果")
            
            # 验证和补充必需字段
            analysis_result = self._validate_analysis_result(analysis_result, project_data)
            
            return analysis_result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return self._create_default_analysis(project_data)
        except Exception as e:
            self.logger.error(f"解析分析响应时出错: {e}")
            return self._create_default_analysis(project_data)
    
    def _create_default_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建默认分析结果
        
        Args:
            project_data: 项目数据
            
        Returns:
            默认分析结果
        """
        # 基于数据的简单评分算法
        completion_rate = project_data.get('completion_rate', 0)
        backer_count = project_data.get('backer_count', 0)
        
        # 简单的评分逻辑
        heat_score = min(100, max(0, completion_rate * 0.6 + min(backer_count / 10, 40)))
        popularity_score = min(100, max(0, completion_rate * 0.5 + min(backer_count / 20, 50)))
        viral_score = min(100, max(0, completion_rate * 0.4 + min(backer_count / 30, 60)))
        overall_score = (heat_score + popularity_score + viral_score) / 3
        
        # 威胁等级
        threat_levels = self.analysis_config.get('threat_levels', {})
        if overall_score >= threat_levels.get('high', 80):
            threat_level = '高'
        elif overall_score >= threat_levels.get('medium', 60):
            threat_level = '中'
        else:
            threat_level = '低'
        
        return {
            'heat_score': round(heat_score, 1),
            'popularity_score': round(popularity_score, 1),
            'viral_score': round(viral_score, 1),
            'overall_score': round(overall_score, 1),
            'analysis_reason': f"基于众筹完成率{completion_rate}%和支持者数量{backer_count}人的基础分析。",
            'threat_level': threat_level,
            'key_insights': [
                f"众筹完成率: {completion_rate}%",
                f"支持者数量: {backer_count}人",
                "需要更详细的AI分析"
            ],
            'competitive_advantages': ["待AI分析"],
            'potential_risks': ["待AI分析"],
            'market_position': "待AI分析"
        }
    
    def _validate_analysis_result(self, analysis_result: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和补充分析结果
        
        Args:
            analysis_result: 原始分析结果
            project_data: 项目数据
            
        Returns:
            验证后的分析结果
        """
        # 必需字段及默认值
        required_fields = {
            'heat_score': 0,
            'popularity_score': 0,
            'viral_score': 0,
            'overall_score': 0,
            'analysis_reason': '分析结果不完整',
            'threat_level': '低',
            'key_insights': [],
            'competitive_advantages': [],
            'potential_risks': [],
            'market_position': '待分析'
        }
        
        # 补充缺失字段
        for field, default_value in required_fields.items():
            if field not in analysis_result:
                analysis_result[field] = default_value
        
        # 验证分数范围
        score_fields = ['heat_score', 'popularity_score', 'viral_score', 'overall_score']
        for field in score_fields:
            score = analysis_result.get(field, 0)
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                analysis_result[field] = 0
        
        # 计算综合分数（如果没有或不合理）
        if analysis_result['overall_score'] == 0:
            scores = [analysis_result[field] for field in score_fields[:3]]
            analysis_result['overall_score'] = round(sum(scores) / len(scores), 1)
        
        # 验证威胁等级
        valid_threat_levels = ['高', '中', '低']
        if analysis_result['threat_level'] not in valid_threat_levels:
            analysis_result['threat_level'] = '低'
        
        # 添加项目基本信息
        analysis_result['project_id'] = project_data.get('project_id', '')
        analysis_result['project_name'] = project_data.get('project_name', '')
        analysis_result['analysis_timestamp'] = datetime.now().isoformat()
        
        return analysis_result

    def batch_analyze_projects(self, projects_data: List[Dict[str, Any]], template_name: str = "project_scoring") -> List[Dict[str, Any]]:
        """
        批量分析项目

        Args:
            projects_data: 项目数据列表
            template_name: 提示词模板名称

        Returns:
            分析结果列表
        """
        self.logger.info(f"开始批量分析 {len(projects_data)} 个项目")

        results = []
        batch_size = self.request_settings.get('batch_size', 5)

        for i in range(0, len(projects_data), batch_size):
            batch = projects_data[i:i + batch_size]
            self.logger.info(f"处理批次 {i//batch_size + 1}/{(len(projects_data) + batch_size - 1)//batch_size}")

            for project_data in batch:
                result = self.analyze_project(project_data, template_name)
                if result:
                    results.append(result)
                else:
                    # 添加失败的项目信息
                    failed_result = self._create_default_analysis(project_data)
                    failed_result['analysis_status'] = 'failed'
                    results.append(failed_result)

            # 批次间休息
            if i + batch_size < len(projects_data):
                time.sleep(1)

        self.logger.info(f"批量分析完成，成功分析 {len(results)} 个项目")
        return results

    def analyze_trends(self, projects_data: List[Dict[str, Any]], time_period: str) -> Optional[Dict[str, Any]]:
        """
        分析市场趋势

        Args:
            projects_data: 项目数据列表
            time_period: 时间段

        Returns:
            趋势分析结果
        """
        try:
            self.logger.info(f"开始分析 {time_period} 的市场趋势")

            # 获取趋势分析提示词模板
            prompt_template = self.config_manager.get_prompt_template("trend_analysis")

            # 准备趋势分析数据
            trend_params = self._prepare_trend_params(projects_data, time_period)

            # 格式化提示词
            formatted_prompt = prompt_template['template'].format(**trend_params)

            # 准备消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的市场研究专家，请基于数据进行深度的趋势分析。"
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ]

            # 发送AI请求
            template_params = prompt_template.get('parameters', {})
            response_content = self._make_ai_request(messages, **template_params)

            if not response_content:
                self.logger.error(f"趋势分析失败: {time_period}")
                return None

            # 解析趋势分析结果
            trend_result = {
                'time_period': time_period,
                'analysis_content': response_content,
                'data_summary': trend_params,
                'analysis_timestamp': datetime.now().isoformat()
            }

            self.logger.info(f"趋势分析完成: {time_period}")
            return trend_result

        except Exception as e:
            self.logger.error(f"趋势分析时出错: {e}")
            return None

    def _prepare_trend_params(self, projects_data: List[Dict[str, Any]], time_period: str) -> Dict[str, Any]:
        """
        准备趋势分析参数

        Args:
            projects_data: 项目数据列表
            time_period: 时间段

        Returns:
            趋势分析参数
        """
        if not projects_data:
            return {}

        # 基础统计
        total_projects = len(projects_data)
        total_funding = sum(p.get('raised_amount', 0) for p in projects_data)
        average_funding = total_funding / total_projects if total_projects > 0 else 0
        successful_projects = len([p for p in projects_data if p.get('completion_rate', 0) >= 100])
        success_rate = (successful_projects / total_projects * 100) if total_projects > 0 else 0
        average_backers = sum(p.get('backer_count', 0) for p in projects_data) / total_projects if total_projects > 0 else 0

        # 分类统计
        categories = {}
        for project in projects_data:
            category = project.get('category', '未知')
            if category not in categories:
                categories[category] = {'count': 0, 'total_funding': 0}
            categories[category]['count'] += 1
            categories[category]['total_funding'] += project.get('raised_amount', 0)

        category_breakdown = []
        for category, stats in categories.items():
            category_breakdown.append(f"{category}: {stats['count']}个项目, 总筹款{stats['total_funding']:,.0f}元")

        # 时间趋势（简化版）
        temporal_trends = "基于项目发起时间的分布分析"

        # 顶级项目
        sorted_projects = sorted(projects_data, key=lambda x: x.get('raised_amount', 0), reverse=True)
        top_projects = []
        for i, project in enumerate(sorted_projects[:10]):
            top_projects.append(f"{i+1}. {project.get('project_name', '未知')} - {project.get('raised_amount', 0):,.0f}元")

        # 时间范围
        start_dates = [p.get('start_date') for p in projects_data if p.get('start_date')]
        start_date = min(start_dates) if start_dates else '未知'
        end_date = max(start_dates) if start_dates else '未知'

        return {
            'time_period': time_period,
            'start_date': start_date,
            'end_date': end_date,
            'total_projects': total_projects,
            'total_funding': f"{total_funding:,.0f}",
            'average_funding': f"{average_funding:,.0f}",
            'successful_projects': successful_projects,
            'success_rate': f"{success_rate:.1f}",
            'average_backers': f"{average_backers:.0f}",
            'category_breakdown': '\n'.join(category_breakdown),
            'temporal_trends': temporal_trends,
            'top_projects': '\n'.join(top_projects)
        }

    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
        获取分析统计信息

        Returns:
            统计信息
        """
        return {
            'total_requests': self.request_count,
            'cache_size': len(self.analysis_cache),
            'ai_provider': self.ai_config.get('provider'),
            'ai_model': self.ai_config.get('model'),
            'last_request_time': self.last_request_time
        }

    def clear_cache(self):
        """清空分析缓存"""
        self.analysis_cache.clear()
        self.logger.info("分析缓存已清空")

    def save_cache(self, cache_file: str):
        """
        保存缓存到文件

        Args:
            cache_file: 缓存文件路径
        """
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_cache, f, ensure_ascii=False, indent=2)
            self.logger.info(f"缓存已保存到: {cache_file}")
        except Exception as e:
            self.logger.error(f"保存缓存失败: {e}")

    def load_cache(self, cache_file: str):
        """
        从文件加载缓存

        Args:
            cache_file: 缓存文件路径
        """
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                self.analysis_cache = json.load(f)
            self.logger.info(f"缓存已从文件加载: {cache_file}")
        except FileNotFoundError:
            self.logger.info("缓存文件不存在，使用空缓存")
        except Exception as e:
            self.logger.error(f"加载缓存失败: {e}")
