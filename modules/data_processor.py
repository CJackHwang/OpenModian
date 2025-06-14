# -*- coding: utf-8 -*-
"""
数据处理模块
负责Excel数据的读取、清洗、格式化和转换
"""

import pandas as pd
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config_manager=None):
        """
        初始化数据处理器

        Args:
            config_manager: 配置管理器实例（可选）
        """
        self.config_manager = config_manager
        self.logger = self._setup_logger()

        # 默认配置
        self.data_config = self._get_default_data_config()
        if config_manager:
            # 如果有配置管理器，尝试获取配置
            try:
                spider_settings = config_manager.get_spider_settings()
                output_settings = config_manager.get_output_settings()
                self.data_config.update({
                    'cleaning_rules': spider_settings.get('cleaning_rules', {}),
                    'output_formats': output_settings.get('formats', ['excel', 'csv', 'json'])
                })
            except:
                pass  # 使用默认配置

        # 数据缓存
        self.raw_data = None
        self.processed_data = None
    
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

    def _get_default_data_config(self) -> Dict[str, Any]:
        """获取默认数据配置"""
        return {
            'cleaning_rules': {
                'remove_test_projects': True,
                'min_title_length': 2,
                'max_title_length': 100,
                'invalid_amount_threshold': 0
            },
            'time_periods': {
                'two_weeks': 14,
                'one_month': 30,
                'three_months': 90,
                'six_months': 180,
                'one_year': 365,
                'three_years': 1095
            },
            'output_formats': ['excel', 'csv', 'json']
        }

    def load_excel_data(self, file_path: str) -> pd.DataFrame:
        """
        加载Excel数据文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            pandas DataFrame
        """
        try:
            # 尝试不同的编码方式读取Excel文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            
            for encoding in encodings:
                try:
                    if file_path.endswith('.xlsx'):
                        df = pd.read_excel(file_path, engine='openpyxl')
                    else:
                        df = pd.read_excel(file_path, encoding=encoding)
                    
                    self.logger.info(f"成功加载Excel文件: {file_path} (编码: {encoding})")
                    self.logger.info(f"数据形状: {df.shape}")
                    
                    self.raw_data = df
                    return df
                    
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    self.logger.error(f"读取Excel文件失败 (编码: {encoding}): {e}")
                    continue
            
            raise Exception("无法使用任何编码方式读取Excel文件")
            
        except Exception as e:
            self.logger.error(f"加载Excel数据失败: {e}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        self.logger.info("开始数据清洗...")
        
        # 复制数据避免修改原始数据
        cleaned_df = df.copy()
        
        # 获取清洗规则
        cleaning_rules = self.data_config.get('cleaning_rules', {})
        
        # 1. 移除测试项目
        if cleaning_rules.get('remove_test_projects', True):
            test_keywords = ['测试', 'test', 'Test', 'TEST', '可汗游戏大会']
            for keyword in test_keywords:
                if '项目名称' in cleaned_df.columns:
                    mask = ~cleaned_df['项目名称'].astype(str).str.contains(keyword, na=False)
                    cleaned_df = cleaned_df[mask]
        
        # 2. 清理项目名称
        if '项目名称' in cleaned_df.columns:
            # 移除无效字符
            cleaned_df['项目名称'] = cleaned_df['项目名称'].astype(str).str.strip()
            
            # 长度过滤
            min_length = cleaning_rules.get('min_title_length', 2)
            max_length = cleaning_rules.get('max_title_length', 100)
            
            mask = (cleaned_df['项目名称'].str.len() >= min_length) & \
                   (cleaned_df['项目名称'].str.len() <= max_length)
            cleaned_df = cleaned_df[mask]
        
        # 3. 清理金额数据
        amount_columns = ['已筹金额', '目标金额']
        for col in amount_columns:
            if col in cleaned_df.columns:
                # 移除非数字字符，保留数字和小数点
                cleaned_df[col] = cleaned_df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                # 转换为数值类型
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                # 填充NaN值为0
                cleaned_df[col] = cleaned_df[col].fillna(0)
        
        # 4. 清理百分比数据
        if '百分比' in cleaned_df.columns:
            cleaned_df['百分比'] = cleaned_df['百分比'].astype(str).str.replace('%', '')
            cleaned_df['百分比'] = pd.to_numeric(cleaned_df['百分比'], errors='coerce')
            cleaned_df['百分比'] = cleaned_df['百分比'].fillna(0)
        
        # 5. 清理数量数据
        count_columns = ['支持者(数量)', '项目更新数', '评论数', '收藏数']
        for col in count_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.replace(r'[^\d]', '', regex=True)
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                cleaned_df[col] = cleaned_df[col].fillna(0)
        
        # 6. 标准化时间格式
        time_columns = ['开始时间', '结束时间']
        for col in time_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = self._standardize_datetime(cleaned_df[col])
        
        # 7. 过滤无效数据
        invalid_threshold = cleaning_rules.get('invalid_amount_threshold', 0)
        if '已筹金额' in cleaned_df.columns:
            mask = cleaned_df['已筹金额'] > invalid_threshold
            cleaned_df = cleaned_df[mask]
        
        # 8. 移除重复项目
        if '项目6位id' in cleaned_df.columns:
            cleaned_df = cleaned_df.drop_duplicates(subset=['项目6位id'], keep='first')
        
        self.logger.info(f"数据清洗完成，从 {len(df)} 行减少到 {len(cleaned_df)} 行")
        
        return cleaned_df
    
    def _standardize_datetime(self, datetime_series: pd.Series) -> pd.Series:
        """
        标准化时间格式
        
        Args:
            datetime_series: 时间数据Series
            
        Returns:
            标准化后的时间Series
        """
        def parse_datetime(dt_str):
            if pd.isna(dt_str) or dt_str in ['none', 'None', '']:
                return None
            
            dt_str = str(dt_str).strip()
            
            # 常见时间格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            
            # 如果都不匹配，返回None
            return None
        
        return datetime_series.apply(parse_datetime)
    
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算衍生指标
        
        Args:
            df: 清洗后的DataFrame
            
        Returns:
            包含衍生指标的DataFrame
        """
        self.logger.info("计算衍生指标...")
        
        result_df = df.copy()
        
        # 1. 计算完成率（如果没有百分比列）
        if '百分比' not in result_df.columns and '已筹金额' in result_df.columns and '目标金额' in result_df.columns:
            result_df['完成率'] = (result_df['已筹金额'] / result_df['目标金额'] * 100).fillna(0)
        else:
            result_df['完成率'] = result_df.get('百分比', 0)
        
        # 2. 计算众筹天数
        if '开始时间' in result_df.columns and '结束时间' in result_df.columns:
            start_time = pd.to_datetime(result_df['开始时间'], errors='coerce')
            end_time = pd.to_datetime(result_df['结束时间'], errors='coerce')
            
            duration = (end_time - start_time).dt.days
            result_df['众筹天数'] = duration.fillna(0).astype(int)
        
        # 3. 计算平均每日筹款
        if '已筹金额' in result_df.columns and '众筹天数' in result_df.columns:
            result_df['平均每日筹款'] = (result_df['已筹金额'] / result_df['众筹天数'].replace(0, 1)).fillna(0)
        
        # 4. 计算支持者密度
        if '支持者(数量)' in result_df.columns and '众筹天数' in result_df.columns:
            result_df['支持者密度'] = (result_df['支持者(数量)'] / result_df['众筹天数'].replace(0, 1)).fillna(0)
        
        # 5. 计算平均支持金额
        if '已筹金额' in result_df.columns and '支持者(数量)' in result_df.columns:
            result_df['平均支持金额'] = (result_df['已筹金额'] / result_df['支持者(数量)'].replace(0, 1)).fillna(0)
        
        # 6. 计算互动指数（更新数 + 评论数）
        update_col = '项目更新数' if '项目更新数' in result_df.columns else 0
        comment_col = '评论数' if '评论数' in result_df.columns else 0
        
        result_df['互动指数'] = result_df.get(update_col, 0) + result_df.get(comment_col, 0)
        
        # 7. 添加时间标签
        if '开始时间' in result_df.columns:
            start_time = pd.to_datetime(result_df['开始时间'], errors='coerce')
            current_time = datetime.now()
            
            # 计算项目年龄（天数）
            result_df['项目年龄'] = (current_time - start_time).dt.days.fillna(0).astype(int)
            
            # 添加时间段标签
            result_df['时间段'] = result_df['项目年龄'].apply(self._categorize_time_period)
        
        self.logger.info("衍生指标计算完成")
        
        return result_df
    
    def _categorize_time_period(self, age_days: int) -> str:
        """
        根据项目年龄分类时间段

        Args:
            age_days: 项目年龄（天数）

        Returns:
            时间段标签
        """
        time_periods = self.data_config.get('time_periods', {})

        if age_days <= time_periods.get('two_weeks', 14):
            return '2周内'
        elif age_days <= time_periods.get('one_month', 30):
            return '1个月内'
        elif age_days <= time_periods.get('three_months', 90):
            return '3个月内'
        elif age_days <= time_periods.get('six_months', 180):
            return '6个月内'
        elif age_days <= time_periods.get('one_year', 365):
            return '1年内'
        elif age_days <= time_periods.get('three_years', 1095):
            return '3年内'
        else:
            return '历史'
    
    def convert_to_json_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        将DataFrame转换为JSON格式
        
        Args:
            df: 处理后的DataFrame
            
        Returns:
            JSON格式的项目数据列表
        """
        self.logger.info("转换数据为JSON格式...")
        
        json_data = []
        
        for _, row in df.iterrows():
            project_data = {
                # 基本信息
                'project_id': str(row.get('项目6位id', '')),
                'project_name': str(row.get('项目名称', '')),
                'project_url': str(row.get('项目link', '')),
                'project_image': str(row.get('项目图', '')),
                'category': str(row.get('分类', '')),
                'project_status': str(row.get('项目结果', '')),
                
                # 时间信息
                'start_date': self._format_datetime(row.get('开始时间')),
                'end_date': self._format_datetime(row.get('结束时间')),
                'duration_days': int(row.get('众筹天数', 0)),
                'project_age': int(row.get('项目年龄', 0)),
                'time_period': str(row.get('时间段', '')),
                
                # 众筹数据
                'target_amount': float(row.get('目标金额', 0)),
                'raised_amount': float(row.get('已筹金额', 0)),
                'completion_rate': float(row.get('完成率', 0)),
                'backer_count': int(row.get('支持者(数量)', 0)),
                'daily_average': float(row.get('平均每日筹款', 0)),
                'average_support': float(row.get('平均支持金额', 0)),
                'backer_density': float(row.get('支持者密度', 0)),
                
                # 用户参与数据
                'update_count': int(row.get('项目更新数', 0)),
                'comment_count': int(row.get('评论数', 0)),
                'favorite_count': int(row.get('收藏数', 0)),
                'supporter_count': int(row.get('项目支持者/点赞数', 0)),
                'interaction_index': int(row.get('互动指数', 0)),
                
                # 发起人信息
                'author_name': str(row.get('用户名', '')),
                'author_uid': str(row.get('用户UID(data-username)', '')),
                'author_homepage': str(row.get('用户主页(链接)', '')),
                'author_avatar': str(row.get('用户头像(图片链接)', '')),
                'author_fans': int(row.get('作者页-粉丝数', 0)),
                'author_following': int(row.get('作者页-关注数', 0)),
                'author_likes': int(row.get('作者页-获赞数', 0)),
                'author_details': str(row.get('作者页-详情', '')),
                'author_experience': str(row.get('作者页-其他信息', '')),
                
                # 项目内容
                'image_count': int(row.get('项目详情-图片数量', 0)),
                'video_count': int(row.get('项目详情-视频数量', 0)),
                'reward_tiers': int(row.get('回报列表项目数', 0)),
                'reward_details': str(row.get('回报列表信息(字符串)', '')),
                
                # 原始数据索引
                'original_index': int(row.get('序号', 0))
            }
            
            json_data.append(project_data)
        
        self.logger.info(f"转换完成，共 {len(json_data)} 个项目")
        
        return json_data
    
    def _format_datetime(self, dt) -> Optional[str]:
        """
        格式化时间为ISO字符串
        
        Args:
            dt: 时间对象
            
        Returns:
            ISO格式时间字符串或None
        """
        if pd.isna(dt) or dt is None:
            return None
        
        if isinstance(dt, str):
            return dt
        
        try:
            return dt.isoformat()
        except:
            return str(dt)
    
    def save_processed_data(self, data: List[Dict[str, Any]], output_path: str):
        """
        保存处理后的数据
        
        Args:
            data: 处理后的数据
            output_path: 输出文件路径
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"处理后的数据已保存到: {output_path}")
            
        except Exception as e:
            self.logger.error(f"保存处理后的数据失败: {e}")
            raise
    
    def process_excel_file(self, input_file: str, output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        完整的Excel文件处理流程
        
        Args:
            input_file: 输入Excel文件路径
            output_file: 输出JSON文件路径（可选）
            
        Returns:
            处理后的JSON格式数据
        """
        self.logger.info(f"开始处理Excel文件: {input_file}")
        
        # 1. 加载数据
        df = self.load_excel_data(input_file)
        
        # 2. 清洗数据
        cleaned_df = self.clean_data(df)
        
        # 3. 计算衍生指标
        processed_df = self.calculate_derived_metrics(cleaned_df)
        
        # 4. 转换为JSON格式
        json_data = self.convert_to_json_format(processed_df)
        
        # 5. 保存处理后的数据
        if output_file:
            self.save_processed_data(json_data, output_file)
        
        self.processed_data = json_data
        self.logger.info("Excel文件处理完成")
        
        return json_data
