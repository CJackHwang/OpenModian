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

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "data/database/modian_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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

                # 获取所有历史记录
                cursor.execute('''
                    SELECT raised_amount, target_amount, completion_rate,
                           backer_count, comment_count, supporter_count,
                           crawl_time
                    FROM projects
                    WHERE project_id = ?
                    ORDER BY crawl_time ASC
                ''', (project_id,))

                records = [dict(row) for row in cursor.fetchall()]

                if not records:
                    return {}

                # 计算趋势数据
                stats = {
                    'total_records': len(records),
                    'first_crawl': records[0]['crawl_time'],
                    'last_crawl': records[-1]['crawl_time'],
                    'current_data': records[-1],
                    'trends': {}
                }

                # 计算各字段的变化趋势
                numeric_fields = ['raised_amount', 'backer_count', 'comment_count',
                                'supporter_count', 'completion_rate']

                for field in numeric_fields:
                    values = [r[field] for r in records if r[field] is not None]
                    if len(values) >= 2:
                        stats['trends'][field] = {
                            'first_value': values[0],
                            'last_value': values[-1],
                            'change': values[-1] - values[0],
                            'change_rate': ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
                        }

                return stats

        except Exception as e:
            print(f"获取项目统计失败: {e}")
            return {}

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
