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
    
    def __init__(self, db_path: str = "database/modian_data.db"):
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
                    collect_count INTEGER,
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_hash ON projects(data_hash)')
            
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

    def get_all_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有历史任务记录"""
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

                    # 计算运行时长
                    if task_dict['start_time'] and task_dict['end_time']:
                        start = datetime.fromisoformat(task_dict['start_time'])
                        end = datetime.fromisoformat(task_dict['end_time'])
                        task_dict['duration'] = str(end - start)
                    else:
                        task_dict['duration'] = None

                    tasks.append(task_dict)

                return tasks

        except Exception as e:
            print(f"获取任务历史失败: {e}")
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
        """删除任务记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM crawl_tasks WHERE task_id = ?', (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除任务失败: {e}")
            return False

    def save_projects(self, projects_data: List[List[Any]], task_id: str = None) -> int:
        """保存项目数据到数据库"""
        saved_count = 0
        duplicate_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for project in projects_data:
                    try:
                        # 解析项目数据
                        project_data = self._parse_project_data(project)
                        
                        # 生成数据哈希用于去重
                        data_hash = self._generate_data_hash(project_data)
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
                                supporter_count, collect_count, project_status,
                                rewards_data, content_images, content_videos, data_hash
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            project_data['project_id'],
                            project_data['project_url'],
                            project_data['project_name'],
                            project_data['project_image'],
                            project_data['category'],
                            project_data['author_name'],
                            project_data['author_link'],
                            project_data['author_image'],
                            project_data['start_time'],
                            project_data['end_time'],
                            project_data['raised_amount'],
                            project_data['target_amount'],
                            project_data['completion_rate'],
                            project_data['backer_count'],
                            project_data['update_count'],
                            project_data['comment_count'],
                            project_data['supporter_count'],
                            project_data['collect_count'],
                            project_data['project_status'],
                            project_data['rewards_data'],
                            project_data['content_images'],
                            project_data['content_videos'],
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
    
    def _parse_project_data(self, project: List[Any]) -> Dict[str, Any]:
        """解析项目数据"""
        # 根据爬虫输出的数据结构解析
        return {
            'project_id': str(project[2]) if len(project) > 2 else '',
            'project_url': str(project[1]) if len(project) > 1 else '',
            'project_name': str(project[3]) if len(project) > 3 else '',
            'project_image': str(project[4]) if len(project) > 4 else '',
            'category': str(project[7]) if len(project) > 7 else '',
            'author_name': str(project[8]) if len(project) > 8 else '',
            'author_link': str(project[5]) if len(project) > 5 else '',
            'author_image': str(project[6]) if len(project) > 6 else '',
            'start_time': str(project[13]) if len(project) > 13 else '',
            'end_time': str(project[14]) if len(project) > 14 else '',
            'raised_amount': self._safe_float(project[15]) if len(project) > 15 else 0.0,
            'target_amount': self._safe_float(project[17]) if len(project) > 17 else 0.0,
            'completion_rate': self._safe_float(project[16]) if len(project) > 16 else 0.0,
            'backer_count': self._safe_int(project[18]) if len(project) > 18 else 0,
            'update_count': self._safe_int(project[20]) if len(project) > 20 else 0,
            'comment_count': self._safe_int(project[21]) if len(project) > 21 else 0,
            'supporter_count': self._safe_int(project[22]) if len(project) > 22 else 0,
            'collect_count': self._safe_int(project[23]) if len(project) > 23 else 0,
            'project_status': str(project[12]) if len(project) > 12 else '',
            'rewards_data': str(project[19]) if len(project) > 19 else '',
            'content_images': str(project[25]) if len(project) > 25 else '',
            'content_videos': str(project[27]) if len(project) > 27 else ''
        }
    
    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数"""
        if value is None or value == 'none' or value == '':
            return 0.0
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return 0.0

    def _safe_int(self, value: Any) -> int:
        """安全转换为整数"""
        if value is None or value == 'none' or value == '':
            return 0
        try:
            return int(float(str(value).replace(',', '')))
        except (ValueError, TypeError):
            return 0

    def _generate_data_hash(self, project_data: Dict[str, Any]) -> str:
        """生成项目数据哈希用于去重"""
        # 使用关键字段生成哈希
        key_fields = [
            project_data['project_id'],
            project_data['project_name'],
            project_data['raised_amount'],
            project_data['backer_count']
        ]

        hash_string = '|'.join(str(field) for field in key_fields)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def get_projects_by_time(self, time_period: str = 'day', limit: int = 100) -> List[Dict[str, Any]]:
        """按时间周期获取项目数据"""
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
                output_path = f"output/database_export_{time_period}_{timestamp}.xlsx"
            
            # 确保输出目录存在
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 导出到Excel
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            print(f"数据已导出到: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"导出Excel失败: {e}")
            return None
