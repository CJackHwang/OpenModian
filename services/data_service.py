# -*- coding: utf-8 -*-
"""
数据服务层
封装数据管理相关的业务逻辑
"""

from typing import Dict, Any, List, Optional
from core.exceptions import SpiderException


class DataService:
    """数据服务 - 封装数据管理业务逻辑"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            return self.db_manager.get_statistics()
        except Exception as e:
            raise SpiderException(f"获取数据库统计失败: {str(e)}")
    
    def get_projects(self, time_period: str = 'all', category: str = 'all', 
                    limit: int = 100) -> List[Dict[str, Any]]:
        """获取项目数据"""
        try:
            if category != 'all':
                conditions = {'category': category}
                projects = self.db_manager.search_projects(conditions, limit, 0)
            else:
                projects = self.db_manager.get_projects_by_time(time_period, limit)
            
            # 清理无效的图片URL
            return self._clean_image_urls(projects)
        except Exception as e:
            raise SpiderException(f"获取项目数据失败: {str(e)}")
    
    def search_projects(self, conditions: Dict[str, Any], limit: int = 100, 
                       offset: int = 0) -> Dict[str, Any]:
        """搜索项目"""
        try:
            projects = self.db_manager.search_projects(conditions, limit, offset)
            total_count = self.db_manager.count_projects(conditions)
            
            return {
                'projects': self._clean_image_urls(projects),
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
        except Exception as e:
            raise SpiderException(f"搜索项目失败: {str(e)}")
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取项目详情"""
        try:
            return self.db_manager.get_project_by_id(project_id)
        except Exception as e:
            raise SpiderException(f"获取项目详情失败: {str(e)}")
    
    def update_project(self, project_id: str, data: Dict[str, Any]) -> bool:
        """更新项目信息"""
        try:
            return self.db_manager.update_project(project_id, data)
        except Exception as e:
            raise SpiderException(f"更新项目失败: {str(e)}")
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        try:
            return self.db_manager.delete_project(project_id)
        except Exception as e:
            raise SpiderException(f"删除项目失败: {str(e)}")
    
    def create_backup(self, backup_type: str = 'database_only') -> str:
        """创建数据备份"""
        try:
            if backup_type == 'database_only':
                return self.db_manager.create_backup()
            else:
                # 完整备份功能待实现
                raise SpiderException("完整备份功能待实现")
        except Exception as e:
            raise SpiderException(f"创建备份失败: {str(e)}")
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """获取备份文件列表"""
        try:
            import os
            from pathlib import Path
            
            backup_dir = Path("backups")
            backups = []
            
            if backup_dir.exists():
                for backup_file in backup_dir.glob("*.sql"):
                    stat = backup_file.stat()
                    backups.append({
                        'filename': backup_file.name,
                        'size': stat.st_size,
                        'created_time': stat.st_mtime,
                        'type': 'database'
                    })
                
                for backup_file in backup_dir.glob("*.json"):
                    stat = backup_file.stat()
                    backups.append({
                        'filename': backup_file.name,
                        'size': stat.st_size,
                        'created_time': stat.st_mtime,
                        'type': 'database_json'
                    })
            
            # 按创建时间排序
            backups.sort(key=lambda x: x['created_time'], reverse=True)
            return backups
        except Exception as e:
            raise SpiderException(f"获取备份列表失败: {str(e)}")
    
    def delete_backup(self, filename: str) -> bool:
        """删除备份文件"""
        try:
            from pathlib import Path
            import os
            
            backup_file = Path("backups") / filename
            
            if backup_file.exists() and backup_file.is_file():
                os.remove(backup_file)
                return True
            else:
                return False
        except Exception as e:
            raise SpiderException(f"删除备份文件失败: {str(e)}")
    
    def export_data(self, format_type: str, conditions: Dict[str, Any] = None) -> str:
        """导出数据"""
        try:
            # 这里需要实现数据导出逻辑
            # 可以调用现有的exporter模块
            raise SpiderException("数据导出功能待实现")
        except Exception as e:
            raise SpiderException(f"导出数据失败: {str(e)}")
    
    def _clean_image_urls(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清理项目数据中的无效图片URL"""
        invalid_values = ['none', 'null', 'undefined', '', ' ', 'N/A', 'n/a']
        
        for project in projects:
            if project.get('author_image') in invalid_values:
                project['author_image'] = None
            if project.get('project_image') in invalid_values:
                project['project_image'] = None
        
        return projects
