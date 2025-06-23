# -*- coding: utf-8 -*-
"""
项目关注功能相关API路由
处理项目收藏、关注列表管理等
"""

from flask import request, jsonify


def register_watch_routes(app, db_manager):
    """注册项目关注相关路由"""
    
    @app.route('/api/watch/add', methods=['POST'])
    def add_watched_project():
        """添加项目到关注列表"""
        try:
            data = request.json
            project_id = data.get('project_id')
            project_name = data.get('project_name', '')
            project_url = data.get('project_url', '')
            category = data.get('category', '')
            author_name = data.get('author_name', '')
            notes = data.get('notes', '')
            
            if not project_id:
                return jsonify({
                    'success': False,
                    'message': '项目ID不能为空'
                }), 400
            
            # 检查项目是否已被关注
            if db_manager.is_project_watched(project_id):
                return jsonify({
                    'success': False,
                    'message': '项目已在关注列表中'
                }), 409
            
            success = db_manager.add_watched_project(
                project_id, project_name, project_url, category, author_name, notes
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '项目已添加到关注列表'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '添加失败，请稍后重试'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'添加失败: {str(e)}'
            }), 500
    
    @app.route('/api/watch/remove', methods=['POST'])
    def remove_watched_project():
        """从关注列表移除项目"""
        try:
            data = request.json
            project_id = data.get('project_id')
            
            if not project_id:
                return jsonify({
                    'success': False,
                    'message': '项目ID不能为空'
                }), 400
            
            success = db_manager.remove_watched_project(project_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '项目已从关注列表移除'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '项目不在关注列表中'
                }), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'移除失败: {str(e)}'
            }), 500
    
    @app.route('/api/watch/list', methods=['GET'])
    def get_watched_projects():
        """获取关注项目列表"""
        try:
            active_only = request.args.get('active_only', 'true').lower() == 'true'
            projects = db_manager.get_watched_projects(active_only)
            
            return jsonify({
                'success': True,
                'projects': projects,
                'count': len(projects)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取关注列表失败: {str(e)}'
            }), 500
    
    @app.route('/api/watch/check/<project_id>', methods=['GET'])
    def check_watched_status(project_id):
        """检查项目是否已被关注"""
        try:
            is_watched = db_manager.is_project_watched(project_id)
            
            return jsonify({
                'success': True,
                'is_watched': is_watched
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'检查关注状态失败: {str(e)}'
            }), 500
    
    @app.route('/api/watch/batch_add', methods=['POST'])
    def batch_add_watched_projects():
        """批量添加项目到关注列表"""
        try:
            data = request.json
            projects = data.get('projects', [])
            
            if not projects:
                return jsonify({
                    'success': False,
                    'message': '项目列表不能为空'
                }), 400
            
            result = db_manager.batch_add_watched_projects(projects)
            
            return jsonify({
                'success': True,
                'message': f'批量添加完成：新增 {result["added"]} 个，跳过 {result["skipped"]} 个，错误 {result["errors"]} 个',
                'result': result
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'批量添加失败: {str(e)}'
            }), 500
    
    @app.route('/api/watch/batch_import', methods=['POST'])
    def batch_import_by_ids():
        """通过项目ID列表批量导入"""
        try:
            data = request.json
            project_ids = data.get('project_ids', [])
            
            if not project_ids:
                return jsonify({
                    'success': False,
                    'message': '项目ID列表不能为空'
                }), 400
            
            # 验证并获取项目信息
            projects_to_add = []
            invalid_ids = []
            
            for project_id in project_ids:
                project_id = str(project_id).strip()
                if not project_id:
                    continue
                
                # 从数据库获取项目信息
                projects = db_manager.search_projects({'project_id': project_id}, limit=1)
                project = projects[0] if projects else None
                if project:
                    projects_to_add.append({
                        'project_id': project_id,
                        'project_name': project.get('project_name', ''),
                        'project_url': project.get('project_url', ''),
                        'category': project.get('category', ''),
                        'author_name': project.get('author_name', '')
                    })
                else:
                    invalid_ids.append(project_id)
            
            # 批量添加有效项目
            result = db_manager.batch_add_watched_projects(projects_to_add)
            
            message = f'导入完成：新增 {result["added"]} 个，跳过 {result["skipped"]} 个'
            if invalid_ids:
                message += f'，无效ID {len(invalid_ids)} 个'
            
            return jsonify({
                'success': True,
                'message': message,
                'result': result,
                'invalid_ids': invalid_ids
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'批量导入失败: {str(e)}'
            }), 500
    
    @app.route('/api/watch/clear', methods=['POST'])
    def clear_watched_projects():
        """清空关注列表"""
        try:
            success = db_manager.clear_watched_projects()
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '关注列表已清空'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '清空失败，请稍后重试'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'清空失败: {str(e)}'
            }), 500
