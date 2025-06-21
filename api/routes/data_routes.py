# -*- coding: utf-8 -*-
"""
数据管理相关API路由
处理数据库查询、项目数据获取等
"""

from flask import request, jsonify, send_file


def register_data_routes(app, db_manager):
    """注册数据管理相关路由"""
    
    @app.route('/api/database/stats')
    def get_database_stats():
        """获取数据库统计信息"""
        try:
            stats = db_manager.get_statistics()
            return jsonify({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取统计信息失败: {str(e)}'
            }), 500
    
    @app.route('/api/database/projects')
    def get_database_projects():
        """获取数据库中的项目数据"""
        try:
            time_period = request.args.get('period', 'all')
            category = request.args.get('category', 'all')
            limit = int(request.args.get('limit', 100))

            # 如果有分类筛选，使用搜索功能
            if category != 'all':
                conditions = {'category': category}
                projects = db_manager.search_projects(conditions, limit, 0)
                print(f"🔍 分类筛选 '{category}': 找到 {len(projects)} 个项目")
            else:
                projects = db_manager.get_projects_by_time(time_period, limit)
                print(f"📊 时间筛选 '{time_period}': 找到 {len(projects)} 个项目")

            # 清理无效的图片URL
            projects = _clean_image_urls(projects)

            return jsonify({
                'success': True,
                'projects': projects,
                'count': len(projects)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取项目数据失败: {str(e)}'
            }), 500
    
    @app.route('/api/database/search', methods=['POST'])
    def search_database_projects():
        """搜索项目"""
        try:
            data = request.json
            conditions = data.get('conditions', {})
            limit = int(data.get('limit', 100))
            offset = int(data.get('offset', 0))

            projects = db_manager.search_projects(conditions, limit, offset)
            total_count = db_manager.count_projects(conditions)

            return jsonify({
                'success': True,
                'projects': projects,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'搜索失败: {str(e)}'
            }), 500
    
    @app.route('/api/database/project/<int:project_id>', methods=['GET'])
    def get_project(project_id):
        """获取单个项目详情"""
        try:
            project = db_manager.get_project_by_id(project_id)
            if project:
                return jsonify({
                    'success': True,
                    'project': project
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '项目不存在'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取项目失败: {str(e)}'
            }), 500

    @app.route('/api/database/project/<int:project_id>', methods=['PUT'])
    def update_project(project_id):
        """更新项目信息"""
        try:
            data = request.get_json()
            success = db_manager.update_project(project_id, data)

            if success:
                return jsonify({
                    'success': True,
                    'message': '项目更新成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '项目不存在或更新失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'更新项目失败: {str(e)}'
            }), 500

    @app.route('/api/database/project/<int:project_id>', methods=['DELETE'])
    def delete_project(project_id):
        """删除项目"""
        try:
            success = db_manager.delete_project(project_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': '项目删除成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '项目不存在或删除失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除项目失败: {str(e)}'
            }), 500
    
    @app.route('/api/database/export')
    def export_database():
        """导出数据库数据"""
        try:
            time_period = request.args.get('period', 'all')

            output_path = db_manager.export_to_excel(time_period)

            if output_path:
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({
                    'success': False,
                    'message': '导出失败或没有数据'
                }), 404

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'导出失败: {str(e)}'
            }), 500

    @app.route('/api/database/projects/batch', methods=['DELETE'])
    def batch_delete_projects():
        """批量删除项目"""
        try:
            data = request.get_json()
            project_ids = data.get('project_ids', [])

            if not project_ids:
                return jsonify({
                    'success': False,
                    'message': '请提供要删除的项目ID列表'
                }), 400

            deleted_count = db_manager.batch_delete_projects(project_ids)

            return jsonify({
                'success': True,
                'message': f'成功删除 {deleted_count} 个项目',
                'deleted_count': deleted_count
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'批量删除失败: {str(e)}'
            }), 500

    @app.route('/api/database/projects/search', methods=['POST'])
    def search_projects():
        """高级搜索项目"""
        try:
            data = request.get_json()
            conditions = data.get('conditions', {})
            sort_config = data.get('sort', [])
            limit = data.get('limit', 100)
            offset = data.get('offset', 0)

            projects = db_manager.search_projects(conditions, limit, offset, sort_config)
            total_count = db_manager.count_projects(conditions)

            # 清理无效的图片URL
            projects = _clean_image_urls(projects)

            return jsonify({
                'success': True,
                'projects': projects,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'sort_config': sort_config
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"搜索失败: {str(e)}"
            }), 500

    @app.route('/api/database/import_json', methods=['POST'])
    def import_json_data():
        """从JSON文件导入数据到数据库"""
        try:
            import json
            from pathlib import Path

            # JSON文件路径 - 使用统一的数据目录
            json_file = Path("data/raw/json/modian_projects.json")

            if not json_file.exists():
                return jsonify({
                    'success': False,
                    'message': f'JSON文件不存在: {json_file}'
                }), 404

            # 读取JSON数据
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            projects = data.get('projects', [])

            if not projects:
                return jsonify({
                    'success': False,
                    'message': '没有找到项目数据'
                }), 400

            # 清空现有数据（可选）
            clear_existing = request.json.get('clear_existing', False)
            if clear_existing:
                import sqlite3
                with sqlite3.connect(db_manager.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM projects')
                    conn.commit()

            # 导入数据
            saved_count = db_manager.save_projects(projects, task_id="json_import")

            return jsonify({
                'success': True,
                'message': f'成功导入 {saved_count} 条数据',
                'imported_count': saved_count,
                'total_count': len(projects)
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'导入失败: {str(e)}'
            }), 500

    @app.route('/api/database/filter_options')
    def get_filter_options():
        """获取基于数据库实际数据的动态筛选选项"""
        try:
            # 获取所有可用的分类
            categories = db_manager.get_distinct_values('category')

            # 获取所有可用的项目状态
            statuses = db_manager.get_distinct_values('project_status')

            # 获取作者列表（限制前100个）
            authors = db_manager.get_distinct_values('author_name', limit=100)

            # 获取数据统计信息
            stats = db_manager.get_statistics()

            # 构建筛选选项
            filter_options = {
                'categories': [
                    {'value': 'all', 'label': '全部分类', 'count': stats.get('total_projects', 0)}
                ] + [
                    {'value': cat, 'label': cat, 'count': 0} for cat in categories if cat
                ],
                'statuses': [
                    {'value': 'all', 'label': '全部状态', 'count': stats.get('total_projects', 0)}
                ] + [
                    {'value': status, 'label': status, 'count': 0} for status in statuses if status
                ],
                'authors': [
                    {'value': 'all', 'label': '全部作者', 'count': stats.get('total_projects', 0)}
                ] + [
                    {'value': author, 'label': author, 'count': 0} for author in authors if author
                ],
                'date_ranges': [
                    {'value': 'all', 'label': '全部时间'},
                    {'value': 'day', 'label': '今天'},
                    {'value': 'week', 'label': '本周'},
                    {'value': 'month', 'label': '本月'}
                ],
                'amount_ranges': [
                    {'value': 'all', 'label': '全部金额'},
                    {'value': '0-1000', 'label': '0-1000元'},
                    {'value': '1000-10000', 'label': '1000-10000元'},
                    {'value': '10000-100000', 'label': '1万-10万元'},
                    {'value': '100000+', 'label': '10万元以上'}
                ]
            }

            # 🔧 获取每个分类和状态的实际项目数量
            for category_option in filter_options['categories'][1:]:  # 跳过"全部"选项
                count = db_manager.count_projects({'category': category_option['value']})
                category_option['count'] = count

            for status_option in filter_options['statuses'][1:]:  # 跳过"全部"选项
                count = db_manager.count_projects({'status': status_option['value']})
                status_option['count'] = count

            return jsonify({
                'success': True,
                'filter_options': filter_options,
                'statistics': stats
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取筛选选项失败: {str(e)}'
            }), 500

    # 项目详情相关路由
    @app.route('/api/projects/<project_id>/detail', methods=['GET'])
    def get_project_detail(project_id):
        """获取项目详情"""
        try:
            # 获取最新的项目数据
            project = db_manager.get_project_by_project_id(project_id)

            if not project:
                return jsonify({
                    'success': False,
                    'message': '项目不存在'
                }), 404

            # 清理无效的图片URL
            project = _clean_image_urls([project])[0]

            # 获取项目统计数据
            stats = db_manager.get_project_statistics(project_id)

            return jsonify({
                'success': True,
                'project': project,
                'statistics': stats
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取项目详情失败: {str(e)}'
            }), 500

    @app.route('/api/projects/<project_id>/history', methods=['GET'])
    def get_project_history(project_id):
        """获取项目历史数据"""
        try:
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)

            # 获取历史记录
            history = db_manager.get_project_history(project_id, limit + offset)

            # 应用分页
            paginated_history = history[offset:offset + limit]

            # 获取变化检测和统计数据
            changes = db_manager.detect_project_changes(project_id)
            statistics = db_manager.get_project_statistics(project_id)

            return jsonify({
                'success': True,
                'history': paginated_history,
                'total_count': len(history),
                'limit': limit,
                'offset': offset,
                'changes': changes,
                'statistics': statistics
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取项目历史失败: {str(e)}'
            }), 500

    @app.route('/api/projects/<project_id>/changes', methods=['GET'])
    def get_project_changes(project_id):
        """获取项目数据变化检测"""
        try:
            changes = db_manager.detect_project_changes(project_id)

            return jsonify({
                'success': True,
                'project_id': project_id,
                'changes': changes
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取项目变化失败: {str(e)}"
            }), 500

    @app.route('/api/projects/<project_id>/statistics', methods=['GET'])
    def get_project_statistics_api(project_id):
        """获取项目统计数据和趋势分析"""
        try:
            statistics = db_manager.get_project_statistics(project_id)

            return jsonify({
                'success': True,
                'project_id': project_id,
                'statistics': statistics
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取项目统计失败: {str(e)}"
            }), 500

    @app.route('/api/projects/<project_id>/export', methods=['GET'])
    def export_project_data(project_id):
        """导出项目历史数据"""
        try:
            # 获取所有历史记录
            history = db_manager.get_project_history(project_id, 1000)  # 最多1000条

            if not history:
                return jsonify({
                    'success': False,
                    'message': '没有找到项目数据'
                }), 404

            # 准备导出数据
            from datetime import datetime
            export_data = {
                'project_id': project_id,
                'project_name': history[0]['project_name'] if history else '',
                'export_time': datetime.now().isoformat(),
                'total_records': len(history),
                'history': history
            }

            # 设置响应头
            response = jsonify(export_data)
            response.headers['Content-Disposition'] = f'attachment; filename=project_{project_id}_history.json'
            response.headers['Content-Type'] = 'application/json'

            return response

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'导出数据失败: {str(e)}'
            }), 500


def _clean_image_urls(projects):
    """清理项目数据中的无效图片URL"""
    invalid_values = ['none', 'null', 'undefined', '', ' ', 'N/A', 'n/a']
    
    for project in projects:
        if project.get('author_image') in invalid_values:
            project['author_image'] = None
        if project.get('project_image') in invalid_values:
            project['project_image'] = None
    
    return projects
