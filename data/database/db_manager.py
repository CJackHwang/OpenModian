# -*- coding: utf-8 -*-
"""
数据库管理模块
管理爬虫数据的存储、查询和时间分类
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import shutil
import os

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "data/database/modian_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建备份目录
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    project_url TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    project_image TEXT,
                    category TEXT,
                    author_name TEXT,
                    author_link TEXT,
                    author_image TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    raised_amount REAL,
                    target_amount REAL,
                    completion_rate REAL,
                    backer_count INTEGER,
                    update_count INTEGER,
                    comment_count INTEGER,
                    supporter_count INTEGER,

                    project_status TEXT,
                    rewards_data TEXT,
                    content_images TEXT,
                    content_videos TEXT,
                    crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_hash TEXT UNIQUE,
                    UNIQUE(project_id, crawl_time)
                )
            ''')
            
            # 创建爬取任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawl_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    start_page INTEGER,
                    end_page INTEGER,
                    category TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT,
                    projects_found INTEGER DEFAULT 0,
                    projects_processed INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    config_data TEXT
                )
            ''')
            
            # 创建时间分类视图
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS projects_by_time AS
                SELECT 
                    *,
                    DATE(crawl_time) as crawl_date,
                    strftime('%Y-%m', crawl_time) as crawl_month,
                    strftime('%Y', crawl_time) as crawl_year,
                    strftime('%W', crawl_time) as crawl_week
                FROM projects
                ORDER BY crawl_time DESC
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_id ON projects(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawl_time ON projects(crawl_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON projects(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_id ON crawl_tasks(task_id)')
            
            conn.commit()
    
    def save_crawl_task(self, task_id: str, config: Dict[str, Any]) -> bool:
        """保存爬取任务信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO crawl_tasks 
                    (task_id, start_page, end_page, category, start_time, status, config_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task_id,
                    config.get('start_page'),
                    config.get('end_page'),
                    config.get('category'),
                    datetime.now(),
                    'running',
                    json.dumps(config)
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"保存爬取任务失败: {e}")
            return False
    
    def update_task_status(self, task_id: str, status: str, stats: Dict[str, Any] = None):
        """更新任务状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                update_fields = ['status = ?']
                values = [status]
                
                if status in ['completed', 'failed', 'stopped']:
                    update_fields.append('end_time = ?')
                    values.append(datetime.now())
                
                if stats:
                    if 'projects_found' in stats:
                        update_fields.append('projects_found = ?')
                        values.append(stats['projects_found'])
                    if 'projects_processed' in stats:
                        update_fields.append('projects_processed = ?')
                        values.append(stats['projects_processed'])
                    if 'errors' in stats:
                        update_fields.append('errors_count = ?')
                        values.append(stats['errors'])
                
                values.append(task_id)
                
                cursor.execute(f'''
                    UPDATE crawl_tasks 
                    SET {', '.join(update_fields)}
                    WHERE task_id = ?
                ''', values)
                
                conn.commit()
                
        except Exception as e:
            print(f"更新任务状态失败: {e}")
    
    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的爬取任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM crawl_tasks 
                    ORDER BY start_time DESC 
                    LIMIT ?
                ''', (limit,))
                
                tasks = []
                for row in cursor.fetchall():
                    task_dict = dict(row)
                    # 解析配置数据
                    if task_dict['config_data']:
                        try:
                            task_dict['config'] = json.loads(task_dict['config_data'])
                        except:
                            task_dict['config'] = {}
                    else:
                        task_dict['config'] = {}
                    
                    tasks.append(task_dict)
                
                return tasks
                
        except Exception as e:
            print(f"获取任务列表失败: {e}")
            return []
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取特定任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM crawl_tasks
                    WHERE task_id = ?
                ''', (task_id,))

                row = cursor.fetchone()
                if row:
                    task_dict = dict(row)
                    # 解析配置数据
                    if task_dict['config_data']:
                        try:
                            task_dict['config'] = json.loads(task_dict['config_data'])
                        except:
                            task_dict['config'] = {}
                    else:
                        task_dict['config'] = {}

                    return task_dict

                return None

        except Exception as e:
            print(f"获取任务详情失败: {e}")
            return None
    
    def delete_task(self, task_id: str) -> bool:
        """删除爬取任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM crawl_tasks WHERE task_id = ?', (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除任务失败: {e}")
            return False
    
    def get_project_by_project_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """根据项目ID获取最新的项目数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM projects
                    WHERE project_id = ?
                    ORDER BY crawl_time DESC
                    LIMIT 1
                ''', (project_id,))

                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None

        except Exception as e:
            print(f"获取项目失败: {e}")
            return None

    def get_project_history(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取项目的历史数据记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM projects
                    WHERE project_id = ?
                    ORDER BY crawl_time DESC
                    LIMIT ?
                ''', (project_id, limit))

                history = []
                for row in cursor.fetchall():
                    record = dict(row)
                    history.append(record)

                return history

        except Exception as e:
            print(f"获取项目历史失败: {e}")
            return []

    def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """获取项目的统计数据和趋势分析"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 获取所有历史记录 - 包含所有关键字段
                cursor.execute('''
                    SELECT raised_amount, target_amount, completion_rate,
                           backer_count, comment_count, supporter_count, update_count,
                           crawl_time, project_name
                    FROM projects
                    WHERE project_id = ?
                    ORDER BY crawl_time ASC
                ''', (project_id,))

                records = [dict(row) for row in cursor.fetchall()]

                if not records:
                    return {}

                # 计算趋势数据
                stats = {
                    'project_id': project_id,
                    'project_name': records[0]['project_name'],
                    'total_records': len(records),
                    'first_crawl': records[0]['crawl_time'],
                    'last_crawl': records[-1]['crawl_time'],
                    'current_data': records[-1],
                    'previous_data': records[-2] if len(records) >= 2 else None,
                    'trends': {},
                    'has_changes': False
                }

                # 计算各字段的变化趋势 - 包含看好数（supporter_count）
                numeric_fields = ['raised_amount', 'backer_count', 'comment_count',
                                'supporter_count', 'completion_rate', 'update_count']

                total_change_detected = False

                for field in numeric_fields:
                    values = [r[field] for r in records if r[field] is not None]
                    if len(values) >= 2:
                        first_val = values[0]
                        last_val = values[-1]
                        change = last_val - first_val

                        # 计算增长率，避免除零错误
                        if first_val > 0:
                            change_rate = (change / first_val) * 100
                        elif change > 0:
                            change_rate = 100.0  # 从0增长到正数，视为100%增长
                        else:
                            change_rate = 0.0

                        # 检测是否有变化
                        has_field_change = abs(change) > 0.001  # 对浮点数使用小的阈值
                        if has_field_change:
                            total_change_detected = True

                        # 为看好数添加友好的字段名
                        field_display_name = field
                        if field == 'supporter_count':
                            field_display_name = 'like_count'  # 在显示时使用like_count作为看好数

                        stats['trends'][field_display_name] = {
                            'first_value': first_val,
                            'last_value': last_val,
                            'change': change,
                            'change_rate': round(change_rate, 2),
                            'has_change': has_field_change,
                            'field_name_cn': self._get_field_chinese_name(field)
                        }

                stats['has_changes'] = total_change_detected

                # 添加变化摘要
                if total_change_detected:
                    stats['change_summary'] = self._generate_change_summary(stats['trends'])
                else:
                    stats['change_summary'] = "数据无变化"

                return stats

        except Exception as e:
            print(f"获取项目统计失败: {e}")
            return {}

    def _get_field_chinese_name(self, field: str) -> str:
        """获取字段的中文名称"""
        field_names = {
            'raised_amount': '筹款金额',
            'backer_count': '支持者数量',
            'comment_count': '评论数',
            'supporter_count': '看好数',
            'completion_rate': '完成率',
            'update_count': '更新数'
        }
        return field_names.get(field, field)

    def _generate_change_summary(self, trends: Dict[str, Any]) -> str:
        """生成变化摘要"""
        changes = []
        for field, data in trends.items():
            if data.get('has_change', False):
                field_name = data.get('field_name_cn', field)
                change = data['change']
                change_rate = data['change_rate']
                if change > 0:
                    changes.append(f"{field_name}增长{change}({change_rate:+.1f}%)")
                else:
                    changes.append(f"{field_name}减少{abs(change)}({change_rate:+.1f}%)")

        return "、".join(changes) if changes else "数据无变化"

    def detect_project_changes(self, project_id: str, threshold: float = 0.001) -> Dict[str, Any]:
        """检测项目数据变化 - 专门用于变化检测"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 获取最近两次记录
                cursor.execute('''
                    SELECT raised_amount, backer_count, comment_count, supporter_count,
                           completion_rate, update_count, crawl_time
                    FROM projects
                    WHERE project_id = ?
                    ORDER BY crawl_time DESC
                    LIMIT 2
                ''', (project_id,))

                records = [dict(row) for row in cursor.fetchall()]

                if len(records) < 2:
                    return {
                        'has_changes': False,
                        'message': '历史记录不足，无法检测变化',
                        'records_count': len(records)
                    }

                current = records[0]
                previous = records[1]

                changes_detected = {}
                has_any_change = False

                # 检测各字段变化
                fields_to_check = ['raised_amount', 'backer_count', 'comment_count',
                                 'supporter_count', 'completion_rate', 'update_count']

                for field in fields_to_check:
                    current_val = current.get(field, 0) or 0
                    previous_val = previous.get(field, 0) or 0

                    change = current_val - previous_val
                    has_change = abs(change) > threshold

                    if has_change:
                        has_any_change = True

                    # 计算增长率
                    if previous_val > 0:
                        growth_rate = (change / previous_val) * 100
                    elif change > 0:
                        growth_rate = 100.0
                    else:
                        growth_rate = 0.0

                    field_name = field
                    if field == 'supporter_count':
                        field_name = 'like_count'  # 显示为看好数

                    changes_detected[field_name] = {
                        'previous_value': previous_val,
                        'current_value': current_val,
                        'change': change,
                        'growth_rate': round(growth_rate, 2),
                        'has_change': has_change,
                        'field_name_cn': self._get_field_chinese_name(field)
                    }

                return {
                    'has_changes': has_any_change,
                    'changes': changes_detected,
                    'current_time': current['crawl_time'],
                    'previous_time': previous['crawl_time'],
                    'summary': self._generate_change_summary_from_detection(changes_detected)
                }

        except Exception as e:
            print(f"检测项目变化失败: {e}")
            return {
                'has_changes': False,
                'error': str(e)
            }

    def _generate_change_summary_from_detection(self, changes: Dict[str, Any]) -> str:
        """从变化检测结果生成摘要"""
        change_items = []
        for field, data in changes.items():
            if data.get('has_change', False):
                field_name = data.get('field_name_cn', field)
                change = data['change']
                growth_rate = data['growth_rate']
                if change > 0:
                    change_items.append(f"{field_name}+{change}({growth_rate:+.1f}%)")
                else:
                    change_items.append(f"{field_name}{change}({growth_rate:+.1f}%)")

        return "、".join(change_items) if change_items else "无变化"

    def save_projects(self, projects_data, task_id: str = None) -> int:
        """保存项目数据到数据库 - 支持列表和字典格式"""
        saved_count = 0
        duplicate_count = 0

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for project in projects_data:
                    try:
                        # 处理不同的数据格式
                        if isinstance(project, dict):
                            # 检查是否是中文字段名，需要转换
                            if '项目名称' in project or '项目link' in project:
                                project_data = self._convert_chinese_fields_to_english(project)
                            else:
                                project_data = project
                        elif isinstance(project, list):
                            # 假设是按照特定顺序的列表
                            project_data = self._convert_list_to_dict(project)
                        else:
                            print(f"不支持的项目数据格式: {type(project)}")
                            continue

                        # 生成数据哈希用于去重
                        data_str = json.dumps(project_data, sort_keys=True, ensure_ascii=False)
                        data_hash = hashlib.md5(data_str.encode()).hexdigest()
                        project_data['data_hash'] = data_hash

                        # 检查是否已存在相同数据
                        cursor.execute('SELECT id FROM projects WHERE data_hash = ?', (data_hash,))
                        if cursor.fetchone():
                            duplicate_count += 1
                            continue

                        # 插入数据
                        cursor.execute('''
                            INSERT INTO projects (
                                project_id, project_url, project_name, project_image,
                                category, author_name, author_link, author_image,
                                start_time, end_time, raised_amount, target_amount,
                                completion_rate, backer_count, update_count, comment_count,
                                supporter_count, project_status,
                                rewards_data, content_images, content_videos, data_hash
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            project_data.get('project_id', ''),
                            project_data.get('project_url', ''),
                            project_data.get('project_name', ''),
                            project_data.get('project_image', ''),
                            project_data.get('category', ''),
                            project_data.get('author_name', ''),
                            project_data.get('author_link', ''),
                            project_data.get('author_image', ''),
                            project_data.get('start_time', ''),
                            project_data.get('end_time', ''),
                            project_data.get('raised_amount', 0),
                            project_data.get('target_amount', 0),
                            project_data.get('completion_rate', 0),
                            project_data.get('backer_count', 0),
                            project_data.get('update_count', 0),
                            project_data.get('comment_count', 0),
                            project_data.get('supporter_count', 0),
                            project_data.get('project_status', ''),
                            project_data.get('rewards_data', ''),
                            project_data.get('content_images', ''),
                            project_data.get('content_videos', ''),
                            project_data['data_hash']
                        ))

                        saved_count += 1

                    except Exception as e:
                        print(f"保存单个项目失败: {e}")
                        continue

                conn.commit()

        except Exception as e:
            print(f"保存项目数据失败: {e}")

        print(f"数据库保存完成: 新增 {saved_count} 条，重复 {duplicate_count} 条")
        return saved_count

    def _convert_list_to_dict(self, project_list: List) -> Dict[str, Any]:
        """将列表格式的项目数据转换为字典格式"""
        # 定义字段映射 - 按照爬虫实际输出的顺序
        field_mapping = [
            'sequence_number',      # 0: 序号
            'project_url',          # 1: 项目link
            'project_id',           # 2: 项目6位id
            'project_name',         # 3: 项目名称
            'project_image',        # 4: 项目图
            'start_time',           # 5: 开始时间
            'end_time',             # 6: 结束时间
            'project_status',       # 7: 项目结果
            'author_link',          # 8: 用户主页(链接)
            'author_image',         # 9: 用户头像(图片链接)
            'category',             # 10: 分类
            'author_name',          # 11: 用户名
            'author_uid',           # 12: 用户UID(data-username)
            'raised_amount',        # 13: 已筹金额
            'completion_rate',      # 14: 百分比
            'target_amount',        # 15: 目标金额
            'backer_count',         # 16: 支持者(数量)
            'real_user_id',         # 17: 真实用户ID(链接提取)
            'author_fans',          # 18: 作者页-粉丝数
            'author_following',     # 19: 作者页-关注数
            'author_likes',         # 20: 作者页-获赞数
            'author_details',       # 21: 作者页-详情
            'author_other_info',    # 22: 作者页-其他信息
            'author_homepage_confirm', # 23: 作者页-主页确认
            'rewards_data',         # 24: 回报列表信息(字符串)
            'rewards_count',        # 25: 回报列表项目数
            'update_count',         # 26: 项目更新数
            'comment_count',        # 27: 评论数
            'supporter_count',      # 28: 看好数
            'content_images_count', # 29: 项目详情-图片数量
            'content_images',       # 30: 项目详情-图片(列表字符串)
            'content_videos_count', # 31: 项目详情-视频数量
            'content_videos'        # 32: 项目详情-视频(列表字符串)
        ]

        project_dict = {}

        # 只映射数据库表中实际存在的字段
        db_fields = {
            'project_url', 'project_id', 'project_name', 'project_image',
            'category', 'author_name', 'author_link', 'author_image',
            'start_time', 'end_time', 'raised_amount', 'target_amount',
            'completion_rate', 'backer_count', 'update_count', 'comment_count',
            'supporter_count', 'project_status', 'rewards_data',
            'content_images', 'content_videos'
        }

        for i, field in enumerate(field_mapping):
            if field in db_fields and i < len(project_list):
                project_dict[field] = project_list[i]

        # 设置默认值
        for field in db_fields:
            if field not in project_dict:
                if field in ['raised_amount', 'target_amount', 'completion_rate']:
                    project_dict[field] = 0.0
                elif field in ['backer_count', 'update_count', 'comment_count', 'supporter_count']:
                    project_dict[field] = 0
                else:
                    project_dict[field] = ''

        return project_dict

    def _convert_chinese_fields_to_english(self, chinese_project: Dict[str, Any]) -> Dict[str, Any]:
        """将中文字段名转换为英文字段名"""
        # 中文字段到英文字段的映射
        field_mapping = {
            '项目link': 'project_url',
            '项目6位id': 'project_id',
            '项目名称': 'project_name',
            '项目图': 'project_image',
            '开始时间': 'start_time',
            '结束时间': 'end_time',
            '项目结果': 'project_status',
            '用户主页(链接)': 'author_link',
            '用户头像(图片链接)': 'author_image',
            '分类': 'category',
            '用户名': 'author_name',
            '用户UID(data-username)': 'author_uid',
            '已筹金额': 'raised_amount',
            '百分比': 'completion_rate',
            '目标金额': 'target_amount',
            '支持者(数量)': 'backer_count',
            '项目更新数': 'update_count',
            '评论数': 'comment_count',
            '看好数': 'supporter_count',  # 新字段名
            '回报列表信息(字符串)': 'rewards_data',
            '项目详情-图片(列表字符串)': 'content_images',
            '项目详情-视频(列表字符串)': 'content_videos'
        }

        english_project = {}

        # 转换字段名
        for chinese_key, english_key in field_mapping.items():
            if chinese_key in chinese_project:
                value = chinese_project[chinese_key]

                # 特殊处理某些字段
                if english_key in ['raised_amount', 'target_amount', 'completion_rate']:
                    # 确保数值字段是数字类型
                    try:
                        if value is not None and value != '':
                            english_project[english_key] = float(value)
                        else:
                            english_project[english_key] = 0.0
                    except (ValueError, TypeError):
                        english_project[english_key] = 0.0

                elif english_key in ['backer_count', 'update_count', 'comment_count', 'supporter_count']:
                    # 确保计数字段是整数类型
                    try:
                        if value is not None and value != '':
                            # 处理字符串形式的数字
                            if isinstance(value, str):
                                # 移除可能的非数字字符
                                clean_value = ''.join(filter(str.isdigit, value))
                                english_project[english_key] = int(clean_value) if clean_value else 0
                            else:
                                english_project[english_key] = int(value)
                        else:
                            english_project[english_key] = 0
                    except (ValueError, TypeError):
                        english_project[english_key] = 0

                elif english_key == 'project_status':
                    # 项目状态标准化
                    if value == '未知情况':
                        english_project[english_key] = 'ongoing'
                    else:
                        english_project[english_key] = str(value) if value else 'unknown'

                else:
                    # 其他字段直接转换为字符串
                    english_project[english_key] = str(value) if value is not None else ''

        # 设置默认值
        defaults = {
            'project_url': '',
            'project_id': '',
            'project_name': '',
            'project_image': '',
            'category': '',
            'author_name': '',
            'author_link': '',
            'author_image': '',
            'start_time': '',
            'end_time': '',
            'raised_amount': 0.0,
            'target_amount': 0.0,
            'completion_rate': 0.0,
            'backer_count': 0,
            'update_count': 0,
            'comment_count': 0,
            'supporter_count': 0,
            'project_status': 'unknown',
            'rewards_data': '',
            'content_images': '',
            'content_videos': ''
        }

        for key, default_value in defaults.items():
            if key not in english_project:
                english_project[key] = default_value

        return english_project

    def get_projects_by_time(self, time_period: str = 'all', limit: int = 100) -> List[Dict[str, Any]]:
        """根据时间段获取项目数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                if time_period == 'day':
                    cursor.execute('''
                        SELECT * FROM projects_by_time
                        WHERE crawl_date = DATE('now')
                        ORDER BY crawl_time DESC
                        LIMIT ?
                    ''', (limit,))
                elif time_period == 'week':
                    cursor.execute('''
                        SELECT * FROM projects_by_time
                        WHERE crawl_week = strftime('%W', 'now')
                        AND crawl_year = strftime('%Y', 'now')
                        ORDER BY crawl_time DESC
                        LIMIT ?
                    ''', (limit,))
                elif time_period == 'month':
                    cursor.execute('''
                        SELECT * FROM projects_by_time
                        WHERE crawl_month = strftime('%Y-%m', 'now')
                        ORDER BY crawl_time DESC
                        LIMIT ?
                    ''', (limit,))
                else:  # all
                    cursor.execute('''
                        SELECT * FROM projects_by_time
                        ORDER BY crawl_time DESC
                        LIMIT ?
                    ''', (limit,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"查询项目数据失败: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 总项目数
                cursor.execute('SELECT COUNT(*) FROM projects')
                total_projects = cursor.fetchone()[0]

                # 今日新增
                cursor.execute('''
                    SELECT COUNT(*) FROM projects
                    WHERE DATE(crawl_time) = DATE('now')
                ''')
                today_projects = cursor.fetchone()[0]

                # 本周新增
                cursor.execute('''
                    SELECT COUNT(*) FROM projects
                    WHERE strftime('%W', crawl_time) = strftime('%W', 'now')
                    AND strftime('%Y', crawl_time) = strftime('%Y', 'now')
                ''')
                week_projects = cursor.fetchone()[0]

                # 分类统计
                cursor.execute('''
                    SELECT category, COUNT(*) as count
                    FROM projects
                    GROUP BY category
                    ORDER BY count DESC
                ''')
                category_stats = dict(cursor.fetchall())

                # 任务统计
                cursor.execute('SELECT COUNT(*) FROM crawl_tasks')
                total_tasks = cursor.fetchone()[0]

                cursor.execute('''
                    SELECT status, COUNT(*) as count
                    FROM crawl_tasks
                    GROUP BY status
                ''')
                task_stats = dict(cursor.fetchall())

                return {
                    'total_projects': total_projects,
                    'today_projects': today_projects,
                    'week_projects': week_projects,
                    'category_stats': category_stats,
                    'total_tasks': total_tasks,
                    'task_stats': task_stats
                }

        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {}

    def export_to_excel(self, time_period: str = 'all', output_path: str = None) -> str:
        """导出数据到Excel"""
        try:
            projects = self.get_projects_by_time(time_period, limit=10000)

            if not projects:
                return None

            df = pd.DataFrame(projects)

            # 生成文件名
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"data/exports/database_export_{time_period}_{timestamp}.xlsx"

            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # 导出到Excel
            df.to_excel(output_path, index=False, engine='openpyxl')

            print(f"数据已导出到: {output_path}")
            return output_path

        except Exception as e:
            print(f"导出Excel失败: {e}")
            return None

    def get_all_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有任务记录"""
        return self.get_recent_tasks(limit)

    def search_projects(self, conditions: Dict[str, Any], limit: int = 100, offset: int = 0, sort_config: List[Dict] = None) -> List[Dict[str, Any]]:
        """高级搜索项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 构建WHERE子句
                where_clauses = []
                params = []

                for field, value in conditions.items():
                    if value is None or value == '':
                        continue

                    if field == 'project_name':
                        where_clauses.append("project_name LIKE ?")
                        params.append(f"%{value}%")
                    elif field == 'author_name':
                        where_clauses.append("author_name LIKE ?")
                        params.append(f"%{value}%")
                    elif field == 'category':
                        # 🔧 增强分类筛选：支持中英文分类匹配
                        category_mapping = {
                            'games': ['games', '游戏'],
                            'publishing': ['publishing', '出版'],
                            'tablegames': ['tablegames', '桌游'],
                            'toys': ['toys', '潮玩模型'],
                            'cards': ['cards', '卡牌'],
                            'technology': ['technology', '科技'],
                            'film-video': ['film-video', '影视'],
                            'music': ['music', '音乐'],
                            'activities': ['activities', '活动'],
                            'design': ['design', '设计'],
                            'curio': ['curio', '文玩'],
                            'home': ['home', '家居'],
                            'food': ['food', '食品'],
                            'comics': ['comics', '动漫'],
                            'charity': ['charity', '爱心通道'],
                            'animals': ['animals', '动物救助'],
                            'wishes': ['wishes', '个人愿望'],
                            'others': ['others', '其他']
                        }

                        # 查找匹配的分类值
                        possible_values = category_mapping.get(value, [value])
                        if len(possible_values) > 1:
                            placeholders = ','.join(['?' for _ in possible_values])
                            where_clauses.append(f"category IN ({placeholders})")
                            params.extend(possible_values)
                        else:
                            where_clauses.append("category = ?")
                            params.append(value)

                        print(f"🔍 分类筛选: {value} -> 匹配值: {possible_values}")
                    elif field == 'status':
                        where_clauses.append("project_status = ?")
                        params.append(value)
                    elif field == 'min_amount':
                        where_clauses.append("raised_amount >= ?")
                        params.append(float(value))
                    elif field == 'max_amount':
                        where_clauses.append("raised_amount <= ?")
                        params.append(float(value))
                    elif field == 'date_from':
                        where_clauses.append("DATE(crawl_time) >= ?")
                        params.append(value)
                    elif field == 'date_to':
                        where_clauses.append("DATE(crawl_time) <= ?")
                        params.append(value)
                    elif field.endswith('_min'):
                        base_field = field[:-4]
                        where_clauses.append(f"{base_field} >= ?")
                        params.append(float(value))
                    elif field.endswith('_max'):
                        base_field = field[:-4]
                        where_clauses.append(f"{base_field} <= ?")
                        params.append(float(value))
                    elif field.endswith('_not'):
                        base_field = field[:-4]
                        where_clauses.append(f"{base_field} != ?")
                        params.append(value)
                    else:
                        # 默认精确匹配
                        where_clauses.append(f"{field} = ?")
                        params.append(value)

                # 构建SQL查询
                sql = "SELECT * FROM projects"

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

                # 添加排序
                if sort_config:
                    order_clauses = []
                    for sort_item in sort_config:
                        field = sort_item.get('field', 'crawl_time')
                        direction = sort_item.get('direction', 'desc').upper()
                        order_clauses.append(f"{field} {direction}")
                    sql += " ORDER BY " + ", ".join(order_clauses)
                else:
                    sql += " ORDER BY crawl_time DESC"

                # 添加分页
                sql += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            print(f"搜索项目失败: {e}")
            return []

    def count_projects(self, conditions: Dict[str, Any]) -> int:
        """统计符合条件的项目数量"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 构建WHERE子句（与search_projects相同的逻辑）
                where_clauses = []
                params = []

                for field, value in conditions.items():
                    if value is None or value == '':
                        continue

                    if field == 'project_name':
                        where_clauses.append("project_name LIKE ?")
                        params.append(f"%{value}%")
                    elif field == 'author_name':
                        where_clauses.append("author_name LIKE ?")
                        params.append(f"%{value}%")
                    elif field == 'category':
                        # 🔧 增强分类筛选：支持中英文分类匹配
                        category_mapping = {
                            'games': ['games', '游戏'],
                            'publishing': ['publishing', '出版'],
                            'tablegames': ['tablegames', '桌游'],
                            'toys': ['toys', '潮玩模型'],
                            'cards': ['cards', '卡牌'],
                            'technology': ['technology', '科技'],
                            'film-video': ['film-video', '影视'],
                            'music': ['music', '音乐'],
                            'activities': ['activities', '活动'],
                            'design': ['design', '设计'],
                            'curio': ['curio', '文玩'],
                            'home': ['home', '家居'],
                            'food': ['food', '食品'],
                            'comics': ['comics', '动漫'],
                            'charity': ['charity', '爱心通道'],
                            'animals': ['animals', '动物救助'],
                            'wishes': ['wishes', '个人愿望'],
                            'others': ['others', '其他']
                        }

                        # 查找匹配的分类值
                        possible_values = category_mapping.get(value, [value])
                        if len(possible_values) > 1:
                            placeholders = ','.join(['?' for _ in possible_values])
                            where_clauses.append(f"category IN ({placeholders})")
                            params.extend(possible_values)
                        else:
                            where_clauses.append("category = ?")
                            params.append(value)
                    elif field == 'status':
                        where_clauses.append("project_status = ?")
                        params.append(value)
                    elif field == 'min_amount':
                        where_clauses.append("raised_amount >= ?")
                        params.append(float(value))
                    elif field == 'max_amount':
                        where_clauses.append("raised_amount <= ?")
                        params.append(float(value))
                    elif field == 'date_from':
                        where_clauses.append("DATE(crawl_time) >= ?")
                        params.append(value)
                    elif field == 'date_to':
                        where_clauses.append("DATE(crawl_time) <= ?")
                        params.append(value)
                    elif field.endswith('_min'):
                        base_field = field[:-4]
                        where_clauses.append(f"{base_field} >= ?")
                        params.append(float(value))
                    elif field.endswith('_max'):
                        base_field = field[:-4]
                        where_clauses.append(f"{base_field} <= ?")
                        params.append(float(value))
                    elif field.endswith('_not'):
                        base_field = field[:-4]
                        where_clauses.append(f"{base_field} != ?")
                        params.append(value)
                    else:
                        # 默认精确匹配
                        where_clauses.append(f"{field} = ?")
                        params.append(value)

                # 构建SQL查询
                sql = "SELECT COUNT(*) FROM projects"

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

                cursor.execute(sql, params)
                return cursor.fetchone()[0]

        except Exception as e:
            print(f"统计项目数量失败: {e}")
            return 0

    def update_project(self, project_id: int, project_data: Dict[str, Any]) -> bool:
        """更新项目信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 构建更新字段
                update_fields = []
                params = []

                # 允许更新的字段
                updatable_fields = [
                    'project_name', 'category', 'author_name', 'project_status',
                    'raised_amount', 'target_amount', 'completion_rate',
                    'backer_count', 'comment_count', 'supporter_count',
                    'start_time', 'end_time', 'project_url', 'project_image',
                    'author_link', 'author_image', 'update_count',
                    'rewards_data', 'content_images', 'content_videos'
                ]

                for field in updatable_fields:
                    if field in project_data:
                        update_fields.append(f"{field} = ?")
                        params.append(project_data[field])

                if not update_fields:
                    return False

                # 添加项目ID到参数
                params.append(project_id)

                # 执行更新
                sql = f"UPDATE projects SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, params)
                conn.commit()

                return cursor.rowcount > 0

        except Exception as e:
            print(f"更新项目失败: {e}")
            return False

    def delete_project(self, project_id: int) -> bool:
        """删除单个项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除项目失败: {e}")
            return False

    def batch_delete_projects(self, project_ids: List[int]) -> int:
        """批量删除项目"""
        deleted_count = 0
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 使用IN子句批量删除
                if project_ids:
                    placeholders = ','.join(['?'] * len(project_ids))
                    sql = f"DELETE FROM projects WHERE id IN ({placeholders})"
                    cursor.execute(sql, project_ids)
                    deleted_count = cursor.rowcount
                    conn.commit()

                print(f"批量删除完成: 删除了 {deleted_count} 个项目")

        except Exception as e:
            print(f"批量删除项目失败: {e}")

        return deleted_count

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """根据数据库ID获取项目"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None

        except Exception as e:
            print(f"获取项目失败: {e}")
            return None

    # ==================== 备份管理功能 ====================

    def create_backup(self, backup_format: str = 'sql', include_metadata: bool = True) -> Dict[str, Any]:
        """
        创建数据库备份

        Args:
            backup_format: 备份格式 ('sql' 或 'json')
            include_metadata: 是否包含元数据

        Returns:
            Dict: 包含备份文件路径和相关信息的字典
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if backup_format == 'sql':
                return self._create_sql_backup(timestamp, include_metadata)
            elif backup_format == 'json':
                return self._create_json_backup(timestamp, include_metadata)
            else:
                raise ValueError(f"不支持的备份格式: {backup_format}")

        except Exception as e:
            print(f"创建备份失败: {e}")
            return {
                'success': False,
                'message': f'创建备份失败: {str(e)}'
            }

    def _create_sql_backup(self, timestamp: str, include_metadata: bool) -> Dict[str, Any]:
        """创建SQL格式备份"""
        backup_filename = f"modian_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename

        with sqlite3.connect(self.db_path) as conn:
            with open(backup_path, 'w', encoding='utf-8') as f:
                # 写入备份头信息
                f.write(f"-- 摩点爬虫数据库备份\n")
                f.write(f"-- 备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- 数据库文件: {self.db_path}\n")
                f.write(f"-- 备份格式: SQL\n\n")

                # 导出数据库结构和数据
                for line in conn.iterdump():
                    f.write(f"{line}\n")

        # 获取备份文件信息
        file_size = backup_path.stat().st_size

        # 统计备份的数据量
        stats = self._get_backup_stats()

        return {
            'success': True,
            'backup_path': str(backup_path),
            'filename': backup_filename,
            'format': 'sql',
            'size': file_size,
            'timestamp': timestamp,
            'stats': stats,
            'message': f'SQL备份创建成功: {backup_filename}'
        }

    def _create_json_backup(self, timestamp: str, include_metadata: bool) -> Dict[str, Any]:
        """创建JSON格式备份"""
        backup_filename = f"modian_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename

        backup_data = {
            'metadata': {
                'backup_time': datetime.now().isoformat(),
                'database_path': str(self.db_path),
                'backup_format': 'json',
                'version': '1.0'
            },
            'data': {}
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 导出projects表
            cursor.execute('SELECT * FROM projects ORDER BY crawl_time DESC')
            projects = [dict(row) for row in cursor.fetchall()]
            backup_data['data']['projects'] = projects

            # 导出crawl_tasks表
            cursor.execute('SELECT * FROM crawl_tasks ORDER BY start_time DESC')
            tasks = [dict(row) for row in cursor.fetchall()]
            backup_data['data']['crawl_tasks'] = tasks

            # 如果包含元数据，添加统计信息
            if include_metadata:
                backup_data['metadata']['stats'] = self._get_backup_stats()

        # 写入JSON文件
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)

        # 获取备份文件信息
        file_size = backup_path.stat().st_size

        return {
            'success': True,
            'backup_path': str(backup_path),
            'filename': backup_filename,
            'format': 'json',
            'size': file_size,
            'timestamp': timestamp,
            'stats': backup_data['metadata'].get('stats', {}),
            'message': f'JSON备份创建成功: {backup_filename}'
        }

    def _get_backup_stats(self) -> Dict[str, Any]:
        """获取备份统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 项目统计
                cursor.execute('SELECT COUNT(*) FROM projects')
                total_projects = cursor.fetchone()[0]

                # 任务统计
                cursor.execute('SELECT COUNT(*) FROM crawl_tasks')
                total_tasks = cursor.fetchone()[0]

                # 最新数据时间
                cursor.execute('SELECT MAX(crawl_time) FROM projects')
                latest_crawl = cursor.fetchone()[0]

                # 最早数据时间
                cursor.execute('SELECT MIN(crawl_time) FROM projects')
                earliest_crawl = cursor.fetchone()[0]

                return {
                    'total_projects': total_projects,
                    'total_tasks': total_tasks,
                    'latest_crawl_time': latest_crawl,
                    'earliest_crawl_time': earliest_crawl,
                    'date_range': f"{earliest_crawl} 至 {latest_crawl}" if earliest_crawl and latest_crawl else "无数据"
                }
        except Exception as e:
            print(f"获取备份统计失败: {e}")
            return {}

    def restore_backup(self, backup_file_path: str) -> Dict[str, Any]:
        """
        从备份文件恢复数据库

        Args:
            backup_file_path: 备份文件路径

        Returns:
            Dict: 恢复结果信息
        """
        try:
            backup_path = Path(backup_file_path)

            if not backup_path.exists():
                return {
                    'success': False,
                    'message': f'备份文件不存在: {backup_file_path}'
                }

            # 根据文件扩展名判断备份格式
            if backup_path.suffix.lower() == '.sql':
                return self._restore_sql_backup(backup_path)
            elif backup_path.suffix.lower() == '.json':
                return self._restore_json_backup(backup_path)
            else:
                return {
                    'success': False,
                    'message': f'不支持的备份文件格式: {backup_path.suffix}'
                }

        except Exception as e:
            print(f"恢复备份失败: {e}")
            return {
                'success': False,
                'message': f'恢复备份失败: {str(e)}'
            }

    def _restore_sql_backup(self, backup_path: Path) -> Dict[str, Any]:
        """从SQL备份恢复数据库"""
        try:
            # 创建当前数据库的备份
            current_backup = self.create_backup('sql', True)

            # 读取SQL备份文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 删除现有数据库文件
            if self.db_path.exists():
                self.db_path.unlink()

            # 创建新的数据库连接并执行SQL
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(sql_content)
                conn.commit()

            # 验证恢复结果
            stats = self._get_backup_stats()

            return {
                'success': True,
                'message': f'SQL备份恢复成功: {backup_path.name}',
                'stats': stats,
                'current_backup': current_backup.get('filename', '未知') if current_backup.get('success') else None
            }

        except Exception as e:
            print(f"SQL备份恢复失败: {e}")
            return {
                'success': False,
                'message': f'SQL备份恢复失败: {str(e)}'
            }

    def _restore_json_backup(self, backup_path: Path) -> Dict[str, Any]:
        """从JSON备份恢复数据库"""
        try:
            # 创建当前数据库的备份
            current_backup = self.create_backup('sql', True)

            # 读取JSON备份文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            # 验证备份文件格式
            if 'data' not in backup_data:
                return {
                    'success': False,
                    'message': '无效的JSON备份文件格式'
                }

            # 清空现有数据
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM projects')
                cursor.execute('DELETE FROM crawl_tasks')
                conn.commit()

            # 恢复项目数据
            projects_data = backup_data['data'].get('projects', [])
            if projects_data:
                self._restore_projects_from_json(projects_data)

            # 恢复任务数据
            tasks_data = backup_data['data'].get('crawl_tasks', [])
            if tasks_data:
                self._restore_tasks_from_json(tasks_data)

            # 验证恢复结果
            stats = self._get_backup_stats()

            return {
                'success': True,
                'message': f'JSON备份恢复成功: {backup_path.name}',
                'stats': stats,
                'restored_projects': len(projects_data),
                'restored_tasks': len(tasks_data),
                'current_backup': current_backup.get('filename', '未知') if current_backup.get('success') else None
            }

        except Exception as e:
            print(f"JSON备份恢复失败: {e}")
            return {
                'success': False,
                'message': f'JSON备份恢复失败: {str(e)}'
            }

    def _restore_projects_from_json(self, projects_data: List[Dict]) -> None:
        """从JSON数据恢复项目"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for project in projects_data:
                # 构建插入SQL
                fields = list(project.keys())
                if 'id' in fields:
                    fields.remove('id')  # 不恢复原始ID，让数据库自动生成

                placeholders = ','.join(['?' for _ in fields])
                sql = f"INSERT INTO projects ({','.join(fields)}) VALUES ({placeholders})"

                values = [project.get(field) for field in fields]
                cursor.execute(sql, values)

            conn.commit()

    def _restore_tasks_from_json(self, tasks_data: List[Dict]) -> None:
        """从JSON数据恢复任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for task in tasks_data:
                # 构建插入SQL
                fields = list(task.keys())
                if 'id' in fields:
                    fields.remove('id')  # 不恢复原始ID，让数据库自动生成

                placeholders = ','.join(['?' for _ in fields])
                sql = f"INSERT INTO crawl_tasks ({','.join(fields)}) VALUES ({placeholders})"

                values = [task.get(field) for field in fields]
                cursor.execute(sql, values)

            conn.commit()

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份文件

        Returns:
            List[Dict]: 备份文件信息列表
        """
        try:
            backups = []

            if not self.backup_dir.exists():
                return backups

            # 扫描备份目录
            sql_files = list(self.backup_dir.glob("modian_backup_*.sql"))
            json_files = list(self.backup_dir.glob("modian_backup_*.json"))
            backup_files = sql_files + json_files

            for backup_file in backup_files:
                try:
                    file_stat = backup_file.stat()

                    # 从文件名提取时间戳
                    filename = backup_file.name
                    if filename.startswith('modian_backup_') and '_' in filename:
                        timestamp_part = filename.split('_', 2)[2].split('.')[0]
                        try:
                            backup_time = datetime.strptime(timestamp_part, '%Y%m%d_%H%M%S')
                            formatted_time = backup_time.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            formatted_time = '未知时间'
                    else:
                        formatted_time = '未知时间'

                    backup_info = {
                        'filename': filename,
                        'path': str(backup_file),
                        'size': file_stat.st_size,
                        'size_formatted': self._format_file_size(file_stat.st_size),
                        'created_time': formatted_time,
                        'modified_time': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'format': backup_file.suffix[1:].upper(),  # 去掉点号并转大写
                        'is_valid': self._validate_backup_file(backup_file)
                    }

                    backups.append(backup_info)

                except Exception as e:
                    print(f"读取备份文件信息失败 {backup_file}: {e}")
                    continue

            # 按创建时间倒序排列
            backups.sort(key=lambda x: x['modified_time'], reverse=True)

            return backups

        except Exception as e:
            print(f"列出备份文件失败: {e}")
            return []

    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def _validate_backup_file(self, backup_path: Path) -> bool:
        """验证备份文件是否有效"""
        try:
            if backup_path.suffix.lower() == '.sql':
                # 简单验证SQL文件
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # 只读前1000字符
                    return 'CREATE TABLE' in content or 'INSERT INTO' in content

            elif backup_path.suffix.lower() == '.json':
                # 验证JSON文件
                with open(backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return 'data' in data and 'metadata' in data

            return False

        except Exception:
            return False

    def delete_backup(self, backup_filename: str) -> Dict[str, Any]:
        """
        删除指定的备份文件

        Args:
            backup_filename: 备份文件名

        Returns:
            Dict: 删除结果
        """
        try:
            backup_path = self.backup_dir / backup_filename

            if not backup_path.exists():
                return {
                    'success': False,
                    'message': f'备份文件不存在: {backup_filename}'
                }

            # 删除文件
            backup_path.unlink()

            return {
                'success': True,
                'message': f'备份文件已删除: {backup_filename}'
            }

        except Exception as e:
            print(f"删除备份文件失败: {e}")
            return {
                'success': False,
                'message': f'删除备份文件失败: {str(e)}'
            }

    def get_backup_info(self, backup_filename: str) -> Dict[str, Any]:
        """
        获取备份文件详细信息

        Args:
            backup_filename: 备份文件名

        Returns:
            Dict: 备份文件详细信息
        """
        try:
            backup_path = self.backup_dir / backup_filename

            if not backup_path.exists():
                return {
                    'success': False,
                    'message': f'备份文件不存在: {backup_filename}'
                }

            file_stat = backup_path.stat()

            # 基本信息
            info = {
                'success': True,
                'filename': backup_filename,
                'path': str(backup_path),
                'size': file_stat.st_size,
                'size_formatted': self._format_file_size(file_stat.st_size),
                'created_time': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified_time': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'format': backup_path.suffix[1:].upper(),
                'is_valid': self._validate_backup_file(backup_path)
            }

            # 如果是JSON格式，尝试读取元数据
            if backup_path.suffix.lower() == '.json':
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'metadata' in data:
                            info['metadata'] = data['metadata']
                except Exception as e:
                    info['metadata_error'] = str(e)

            return info

        except Exception as e:
            print(f"获取备份信息失败: {e}")
            return {
                'success': False,
                'message': f'获取备份信息失败: {str(e)}'
            }
