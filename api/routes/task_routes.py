# -*- coding: utf-8 -*-
"""
任务管理相关API路由
处理任务历史、任务删除、定时任务管理等
"""

from flask import request, jsonify, send_file
from pathlib import Path


def register_task_routes(app, spider_service, task_scheduler, db_manager):
    """注册任务管理相关路由"""
    
    @app.route('/api/tasks')
    def get_tasks():
        """获取所有任务状态（活跃任务 + 定时任务）"""
        tasks = []

        # 添加活跃的普通任务
        all_tasks = spider_service.get_all_tasks()
        for task_id, task_info in all_tasks.items():
            tasks.append({
                'task_id': task_id,
                'task_type': 'normal',
                'config': task_info['config'],
                'stats': task_info['monitor'].stats,
                'is_scheduled': False
            })

        # 添加定时任务
        try:
            scheduled_tasks = task_scheduler.get_scheduled_tasks()
            for scheduled_task in scheduled_tasks:
                tasks.append({
                    'task_id': scheduled_task['task_id'],
                    'task_type': 'scheduled',
                    'config': scheduled_task['config'],
                    'stats': {
                        'status': 'scheduled' if scheduled_task['is_active'] else 'paused',
                        'next_run_time': scheduled_task['next_run_time'],
                        'last_run_time': scheduled_task['last_run_time'],
                        'run_count': scheduled_task['run_count'],
                        'last_status': scheduled_task['last_status'],
                        'interval_seconds': scheduled_task['interval_seconds']
                    },
                    'is_scheduled': True,
                    'is_active': scheduled_task['is_active'],
                    'is_running': scheduled_task['is_running'],
                    'schedule_info': {
                        'interval_seconds': scheduled_task['interval_seconds'],
                        'next_run_time': scheduled_task['next_run_time'],
                        'last_run_time': scheduled_task['last_run_time'],
                        'run_count': scheduled_task['run_count']
                    }
                })
        except Exception as e:
            print(f"获取定时任务失败: {e}")

        return jsonify({
            'success': True,
            'tasks': tasks,
            'normal_tasks': len([t for t in tasks if t['task_type'] == 'normal']),
            'scheduled_tasks': len([t for t in tasks if t['task_type'] == 'scheduled'])
        })
    
    @app.route('/api/tasks/history')
    def get_task_history():
        """获取历史任务记录"""
        try:
            limit = int(request.args.get('limit', 100))
            tasks = db_manager.get_all_tasks(limit)
            
            return jsonify({
                'success': True,
                'tasks': tasks,
                'count': len(tasks)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取任务历史失败: {str(e)}'
            }), 500
    
    @app.route('/api/task/<task_id>')
    def get_task(task_id):
        """获取特定任务状态（活跃任务或历史任务）"""
        # 首先检查活跃任务 - 与原版本完全一致
        task_info = spider_service.task_manager.get_task(task_id)
        if task_info:
            return jsonify({
                'success': True,
                'task': {
                    'task_id': task_id,
                    'config': task_info['config'],
                    'stats': task_info['monitor'].stats,
                    'is_active': True
                }
            })

        # 检查历史任务
        try:
            task = db_manager.get_task_by_id(task_id)
            if task:
                return jsonify({
                    'success': True,
                    'task': {
                        'task_id': task['task_id'],
                        'config': task.get('config', {}),
                        'stats': {
                            'status': task['status'],
                            'start_time': task['start_time'],
                            'end_time': task['end_time'],
                            'projects_found': task['projects_found'],
                            'projects_processed': task['projects_processed'],
                            'errors_count': task['errors_count'],
                            'duration': task.get('duration')
                        },
                        'is_active': False
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '任务不存在'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取任务详情失败: {str(e)}'
            }), 500
    
    @app.route('/api/task/<task_id>', methods=['DELETE'])
    def delete_task(task_id):
        """删除历史任务记录"""
        try:
            # 不能删除活跃任务 - 与原版本完全一致
            if spider_service.task_manager.get_task(task_id):
                return jsonify({
                    'success': False,
                    'message': '不能删除正在运行的任务'
                }), 400

            success = db_manager.delete_task(task_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': '任务删除成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '任务不存在或删除失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除任务失败: {str(e)}'
            }), 500
    
    @app.route('/api/download/<task_id>')
    def download_results(task_id):
        """下载爬取结果"""
        try:
            # 与原版本完全一致的实现
            spider_instance = spider_service.instance_manager.get_instance(task_id)
            if spider_instance:
                # 查找最新的输出文件
                from pathlib import Path
                output_dir = Path(spider_instance.config.OUTPUT_DIR)
                excel_files = list(output_dir.glob('*.xlsx'))

                if excel_files:
                    # 返回最新的文件
                    latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
                    return send_file(latest_file, as_attachment=True)
                else:
                    return jsonify({
                        'success': False,
                        'message': '没有找到输出文件'
                    }), 404
            else:
                return jsonify({
                    'success': False,
                    'message': '任务不存在'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'下载失败: {str(e)}'
            }), 500

    # ==================== 定时任务管理API ====================

    @app.route('/api/scheduled_tasks')
    def get_scheduled_tasks():
        """获取所有定时任务"""
        try:
            tasks = task_scheduler.get_scheduled_tasks()
            return jsonify({
                'success': True,
                'tasks': tasks,
                'count': len(tasks)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取定时任务失败: {str(e)}'
            }), 500

    @app.route('/api/scheduled_tasks/<task_id>', methods=['DELETE'])
    def delete_scheduled_task(task_id):
        """删除定时任务"""
        try:
            success = task_scheduler.remove_scheduled_task(task_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': '定时任务删除成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '定时任务不存在或删除失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除定时任务失败: {str(e)}'
            }), 500

    @app.route('/api/scheduled_tasks/<task_id>/toggle', methods=['POST'])
    def toggle_scheduled_task(task_id):
        """切换定时任务状态"""
        try:
            success = task_scheduler.toggle_task_status(task_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': '任务状态切换成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '定时任务不存在或切换失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'切换任务状态失败: {str(e)}'
            }), 500

    @app.route('/api/scheduled_tasks/<task_id>/run_now', methods=['POST'])
    def run_scheduled_task_now(task_id):
        """立即执行定时任务"""
        try:
            # 这里需要实现立即执行逻辑
            success = task_scheduler.run_task_immediately(task_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': '任务已开始执行'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '定时任务不存在或执行失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'立即执行任务失败: {str(e)}'
            }), 500

    @app.route('/api/scheduled_tasks/<task_id>/history')
    def get_scheduled_task_history(task_id):
        """获取定时任务执行历史"""
        try:
            limit = int(request.args.get('limit', 20))
            history = task_scheduler.get_task_execution_history(task_id, limit)

            return jsonify({
                'success': True,
                'history': history,
                'count': len(history)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取定时任务历史失败: {str(e)}'
            }), 500

    @app.route('/api/scheduler/status')
    def get_scheduler_status():
        """获取调度器状态"""
        try:
            status = task_scheduler.get_scheduler_status()
            return jsonify({
                'success': True,
                'scheduler_status': status
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取调度器状态失败: {str(e)}'
            }), 500

    @app.route('/api/scheduler/restart', methods=['POST'])
    def restart_scheduler():
        """重启调度器 - 与原版本完全一致"""
        try:
            print("🔄 重启调度器...")
            task_scheduler.stop_scheduler()
            import time
            time.sleep(2)  # 等待调度器完全停止
            task_scheduler.start_scheduler()

            return jsonify({
                'success': True,
                'message': '调度器重启成功'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'重启调度器失败: {str(e)}'
            }), 500
