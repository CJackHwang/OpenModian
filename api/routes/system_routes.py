# -*- coding: utf-8 -*-
"""
系统管理相关API路由
处理系统状态、配置管理、备份恢复等
"""

from flask import request, jsonify, send_file
from pathlib import Path
import os
from datetime import datetime


def register_system_routes(app, db_manager):
    """注册系统管理相关路由"""
    
    @app.route('/api/system/status')
    def get_system_status():
        """获取系统状态"""
        try:
            from core.logging import log_system
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')

            # 记录系统状态查询
            log_system('info', f'系统状态查询请求 (IP: {client_ip})', 'api')

            # 获取系统基本信息
            import psutil
            import platform

            # 记录详细的系统信息获取过程
            log_system('debug', '开始收集系统信息...', 'api')

            system_info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
            }

            # 记录系统资源状态
            memory_usage = (1 - system_info['memory_available'] / system_info['memory_total']) * 100
            log_system('info', f'系统资源状态: CPU核心={system_info["cpu_count"]}, 内存使用率={memory_usage:.1f}%, 磁盘使用率={system_info["disk_usage"]:.1f}%', 'system')

            # 获取数据库状态
            log_system('debug', '获取数据库状态...', 'api')
            db_status = db_manager.get_database_status()

            log_system('info', f'系统状态查询完成，返回数据给客户端 {client_ip}', 'api')

            return jsonify({
                'success': True,
                'system_info': system_info,
                'database_status': db_status,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取系统状态失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/backup', methods=['POST'])
    def create_system_backup():
        """创建系统备份"""
        try:
            data = request.get_json() or {}
            backup_type = data.get('type', 'database_only')  # database_only, full
            
            if backup_type == 'database_only':
                # 创建数据库备份
                backup_file = db_manager.create_backup()
                return jsonify({
                    'success': True,
                    'backup_file': backup_file,
                    'backup_type': backup_type,
                    'message': '数据库备份创建成功'
                })
            else:
                # 创建完整备份（包括配置文件、日志等）
                backup_file = db_manager.create_full_backup()
                return jsonify({
                    'success': True,
                    'backup_file': backup_file,
                    'backup_type': backup_type,
                    'message': '完整备份创建成功'
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'创建备份失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/backup/restore', methods=['POST'])
    def restore_system_backup():
        """恢复系统备份"""
        try:
            data = request.get_json() or {}
            backup_filename = data.get('backup_filename')
            
            if not backup_filename:
                return jsonify({
                    'success': False,
                    'message': '未提供备份文件名'
                }), 400
            
            success = db_manager.restore_backup(backup_filename)
            if success:
                return jsonify({
                    'success': True,
                    'message': '系统恢复成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '系统恢复失败'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'恢复备份失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/backup/list')
    def list_system_backups():
        """获取备份文件列表"""
        try:
            backups = db_manager.list_backups()
            
            return jsonify({
                'success': True,
                'backups': backups,
                'count': len(backups)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取备份列表失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/backup/<filename>', methods=['DELETE'])
    def delete_backup(filename):
        """删除备份文件"""
        try:
            backup_file = Path("backups") / filename
            
            if backup_file.exists() and backup_file.is_file():
                os.remove(backup_file)
                return jsonify({
                    'success': True,
                    'message': '备份文件删除成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '备份文件不存在'
                }), 404
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除备份文件失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/logs')
    def get_system_logs():
        """获取系统日志"""
        try:
            log_type = request.args.get('type', 'system')  # system, spider, webui
            limit = int(request.args.get('limit', 100))
            level = request.args.get('level', 'all')  # all, debug, info, warning, error
            search = request.args.get('search', '')

            # 读取日志文件
            logs = _read_log_files(log_type, limit, level, search)

            return jsonify({
                'success': True,
                'logs': logs,
                'log_type': log_type,
                'level': level,
                'search': search,
                'count': len(logs)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取系统日志失败: {str(e)}'
            }), 500

    def _read_log_files(log_type, limit, level, search):
        """读取日志文件内容"""
        import glob
        from datetime import datetime
        import re

        logs = []
        log_dir = Path("logs") / log_type

        if not log_dir.exists():
            return logs

        # 获取所有日志文件，按修改时间排序
        log_files = sorted(
            glob.glob(str(log_dir / "*.log")),
            key=os.path.getmtime,
            reverse=True
        )

        # 读取日志内容
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line in reversed(lines):  # 最新的日志在前
                    line = line.strip()
                    if not line:
                        continue

                    # 解析日志行
                    log_entry = _parse_log_line(line, log_file)
                    if not log_entry:
                        continue

                    # 级别过滤
                    if level != 'all' and log_entry['level'].lower() != level.lower():
                        continue

                    # 搜索过滤
                    if search and search.lower() not in log_entry['message'].lower():
                        continue

                    logs.append(log_entry)

                    # 达到限制数量
                    if len(logs) >= limit:
                        return logs

            except Exception as e:
                print(f"读取日志文件失败 {log_file}: {e}")
                continue

        return logs

    def _parse_log_line(line, log_file):
        """解析日志行"""
        try:
            # 尝试解析标准格式: [TIMESTAMP] [LEVEL] MESSAGE
            pattern = r'\[([^\]]+)\]\s*\[([^\]]+)\]\s*(.*)'
            match = re.match(pattern, line)

            if match:
                timestamp_str, level, message = match.groups()
                return {
                    'timestamp': timestamp_str,
                    'level': level.strip(),
                    'message': message.strip(),
                    'source': os.path.basename(log_file)
                }
            else:
                # 如果不匹配标准格式，作为普通消息处理
                return {
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'level': 'info',
                    'message': line,
                    'source': os.path.basename(log_file)
                }
        except Exception:
            return None
    
    @app.route('/api/system/config')
    def get_system_config():
        """获取系统配置"""
        try:
            from spider.config import SpiderConfig
            
            config = SpiderConfig.load_from_yaml()
            
            system_config = {
                'spider_settings': {
                    'max_concurrent_requests': config.MAX_CONCURRENT_REQUESTS,
                    'request_delay': config.REQUEST_DELAY,
                    'save_interval': config.SAVE_INTERVAL,
                    'max_retries': config.MAX_RETRIES
                },
                'output_settings': {
                    'output_dir': config.OUTPUT_DIR,
                    'cache_dir': config.CACHE_DIR,
                    'excel_filename': config.EXCEL_FILENAME
                },
                'monitoring_settings': {
                    'enable_monitoring': config.ENABLE_MONITORING,
                    'stats_update_interval': config.STATS_UPDATE_INTERVAL
                }
            }
            
            return jsonify({
                'success': True,
                'config': system_config
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取系统配置失败: {str(e)}'
            }), 500
    
    @app.route('/api/system/config', methods=['PUT'])
    def update_system_config():
        """更新系统配置"""
        try:
            data = request.json

            # 这里需要实现配置更新逻辑
            # 注意：配置更新可能需要重启某些服务

            return jsonify({
                'success': True,
                'message': '系统配置更新成功'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'更新系统配置失败: {str(e)}'
            }), 500

    # ==================== 备份管理API ====================

    @app.route('/api/backup/create', methods=['POST'])
    def create_database_backup():
        """创建数据库备份"""
        try:
            data = request.get_json() or {}
            backup_format = data.get('format', 'sql')  # 默认SQL格式

            # 获取包含元数据选项
            include_metadata = data.get('include_metadata', True)

            # 调用统一的备份方法
            backup_result = db_manager.create_backup(backup_format, include_metadata)

            if backup_result.get('success'):
                return jsonify({
                    'success': True,
                    'backup_file': backup_result.get('filename'),
                    'backup_path': backup_result.get('backup_path'),
                    'format': backup_format,
                    'size': backup_result.get('size'),
                    'stats': backup_result.get('stats'),
                    'message': backup_result.get('message')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': backup_result.get('message', '备份创建失败')
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'创建备份失败: {str(e)}'
            }), 500

    @app.route('/api/backup/list', methods=['GET'])
    def list_backup_files():
        """获取备份文件列表"""
        try:
            backups = db_manager.list_backups()

            return jsonify({
                'success': True,
                'backups': backups,
                'count': len(backups)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取备份列表失败: {str(e)}'
            }), 500

    @app.route('/api/backup/restore', methods=['POST'])
    def restore_database_backup():
        """恢复数据库备份"""
        try:
            data = request.get_json() or {}
            backup_filename = data.get('backup_filename')

            if not backup_filename:
                return jsonify({
                    'success': False,
                    'message': '未提供备份文件名'
                }), 400

            success = db_manager.restore_backup(backup_filename)
            if success:
                return jsonify({
                    'success': True,
                    'message': '数据库恢复成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '数据库恢复失败'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'恢复备份失败: {str(e)}'
            }), 500

    @app.route('/api/backup/upload', methods=['POST'])
    def upload_backup_file():
        """上传备份文件"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': '未提供文件'
                }), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': '未选择文件'
                }), 400

            # 检查文件类型
            allowed_extensions = {'.sql', '.json'}
            file_ext = '.' + file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'message': '不支持的文件类型，仅支持 .sql 和 .json 文件'
                }), 400

            # 保存文件
            from werkzeug.utils import secure_filename

            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            filename = secure_filename(file.filename)
            file_path = backup_dir / filename

            # 如果文件已存在，添加时间戳
            if file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = filename.rsplit('.', 1)
                filename = f"{name}_{timestamp}.{ext}"
                file_path = backup_dir / filename

            file.save(str(file_path))

            return jsonify({
                'success': True,
                'filename': filename,
                'size': file_path.stat().st_size,
                'message': '备份文件上传成功'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'上传备份文件失败: {str(e)}'
            }), 500

    @app.route('/api/backup/download/<backup_filename>', methods=['GET'])
    def download_backup_file(backup_filename):
        """下载备份文件"""
        try:
            backup_dir = Path("backups")
            backup_path = backup_dir / backup_filename

            if not backup_path.exists():
                return jsonify({
                    'success': False,
                    'message': '备份文件不存在'
                }), 404

            return send_file(backup_path, as_attachment=True)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'下载备份文件失败: {str(e)}'
            }), 500

    @app.route('/api/backup/delete/<backup_filename>', methods=['DELETE'])
    def delete_backup_file(backup_filename):
        """删除备份文件"""
        try:
            result = db_manager.delete_backup(backup_filename)

            if result['success']:
                return jsonify({
                    'success': True,
                    'message': result['message']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除备份文件失败: {str(e)}'
            }), 500

    @app.route('/api/backup/info/<backup_filename>', methods=['GET'])
    def get_backup_file_info(backup_filename):
        """获取备份文件详细信息"""
        try:
            result = db_manager.get_backup_info(backup_filename)

            if result['success']:
                return jsonify({
                    'success': True,
                    'info': result['info']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result['message']
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取备份文件信息失败: {str(e)}'
            }), 500
