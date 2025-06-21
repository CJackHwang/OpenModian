# -*- coding: utf-8 -*-
"""
用户设置相关API路由
处理用户设置的保存、读取、更新等操作
"""

from flask import request, jsonify
from typing import Dict, Any


def register_settings_routes(app, db_manager):
    """注册用户设置相关路由"""
    
    @app.route('/api/settings', methods=['GET'])
    def get_user_settings():
        """获取所有用户设置"""
        try:
            settings = db_manager.get_all_user_settings()
            
            # 如果没有设置，返回默认设置
            if not settings:
                from spider.config import SpiderConfig
                config = SpiderConfig()
                
                default_settings = {
                    'spider_max_concurrent': config.MAX_CONCURRENT_REQUESTS,
                    'spider_delay_min': config.REQUEST_DELAY[0],
                    'spider_delay_max': config.REQUEST_DELAY[1],
                    'spider_category': 'all',
                    'spider_start_page': 1,
                    'spider_end_page': 10,
                    'theme_mode': 'light'
                }
                
                # 保存默认设置到数据库
                for key, value in default_settings.items():
                    setting_type = 'int' if isinstance(value, int) else 'float' if isinstance(value, float) else 'string'
                    db_manager.save_user_setting(key, value, setting_type, f'默认{key}设置')
                
                settings = default_settings
            
            return jsonify({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取用户设置失败: {str(e)}'
            }), 500
    
    @app.route('/api/settings', methods=['POST'])
    def save_user_settings():
        """保存用户设置"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据为空'
                }), 400
            
            settings = data.get('settings', {})
            if not settings:
                return jsonify({
                    'success': False,
                    'message': '设置数据为空'
                }), 400
            
            # 保存每个设置项
            saved_count = 0
            for key, value in settings.items():
                # 确定数据类型
                if isinstance(value, int):
                    setting_type = 'int'
                elif isinstance(value, float):
                    setting_type = 'float'
                elif isinstance(value, bool):
                    setting_type = 'bool'
                elif isinstance(value, (dict, list)):
                    setting_type = 'json'
                else:
                    setting_type = 'string'
                
                if db_manager.save_user_setting(key, value, setting_type, f'用户{key}设置'):
                    saved_count += 1
            
            return jsonify({
                'success': True,
                'message': f'成功保存 {saved_count} 个设置项',
                'saved_count': saved_count
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'保存用户设置失败: {str(e)}'
            }), 500
    
    @app.route('/api/settings/<setting_key>', methods=['GET'])
    def get_user_setting(setting_key: str):
        """获取单个用户设置"""
        try:
            value = db_manager.get_user_setting(setting_key)
            
            return jsonify({
                'success': True,
                'key': setting_key,
                'value': value
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取设置失败: {str(e)}'
            }), 500
    
    @app.route('/api/settings/<setting_key>', methods=['PUT'])
    def update_user_setting(setting_key: str):
        """更新单个用户设置"""
        try:
            data = request.get_json()
            if not data or 'value' not in data:
                return jsonify({
                    'success': False,
                    'message': '请求数据格式错误'
                }), 400
            
            value = data['value']
            setting_type = data.get('type', 'string')
            description = data.get('description', f'用户{setting_key}设置')
            
            success = db_manager.save_user_setting(setting_key, value, setting_type, description)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '设置更新成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '设置更新失败'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'更新设置失败: {str(e)}'
            }), 500
    
    @app.route('/api/settings/<setting_key>', methods=['DELETE'])
    def delete_user_setting(setting_key: str):
        """删除用户设置"""
        try:
            success = db_manager.delete_user_setting(setting_key)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '设置删除成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '设置不存在或删除失败'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除设置失败: {str(e)}'
            }), 500
    
    @app.route('/api/settings/reset', methods=['POST'])
    def reset_user_settings():
        """重置用户设置为默认值"""
        try:
            from spider.config import SpiderConfig
            config = SpiderConfig()
            
            default_settings = {
                'spider_max_concurrent': config.MAX_CONCURRENT_REQUESTS,
                'spider_delay_min': config.REQUEST_DELAY[0],
                'spider_delay_max': config.REQUEST_DELAY[1],
                'spider_category': 'all',
                'spider_start_page': 1,
                'spider_end_page': 10,
                'theme_mode': 'light'
            }
            
            # 保存默认设置
            saved_count = 0
            for key, value in default_settings.items():
                setting_type = 'int' if isinstance(value, int) else 'float' if isinstance(value, float) else 'string'
                if db_manager.save_user_setting(key, value, setting_type, f'默认{key}设置'):
                    saved_count += 1
            
            return jsonify({
                'success': True,
                'message': f'成功重置 {saved_count} 个设置项',
                'settings': default_settings
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'重置设置失败: {str(e)}'
            }), 500
    
    @app.route('/api/config/with_user_settings')
    def get_config_with_user_settings():
        """获取合并了用户设置的配置信息"""
        try:
            from spider.config import SpiderConfig
            config = SpiderConfig()
            
            # 获取用户设置
            user_settings = db_manager.get_all_user_settings()
            
            # 构建配置响应，优先使用用户设置
            response_config = {
                'start_page': user_settings.get('spider_start_page', 1),
                'end_page': user_settings.get('spider_end_page', 10),
                'category': user_settings.get('spider_category', 'all'),
                'max_concurrent': user_settings.get('spider_max_concurrent', config.MAX_CONCURRENT_REQUESTS),
                'delay_min': user_settings.get('spider_delay_min', config.REQUEST_DELAY[0]),
                'delay_max': user_settings.get('spider_delay_max', config.REQUEST_DELAY[1]),
                'categories': [
                    {'value': 'all', 'label': '全部'},
                    {'value': 'games', 'label': '游戏'},
                    {'value': 'publishing', 'label': '出版'},
                    {'value': 'tablegames', 'label': '桌游'},
                    {'value': 'toys', 'label': '潮玩模型'},
                    {'value': 'cards', 'label': '卡牌'},
                    {'value': 'technology', 'label': '科技'},
                    {'value': 'film-video', 'label': '影视'},
                    {'value': 'music', 'label': '音乐'},
                    {'value': 'activities', 'label': '活动'},
                    {'value': 'others', 'label': '其他'}
                ]
            }
            
            return jsonify({
                'success': True,
                'config': response_config,
                'user_settings': user_settings
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取配置失败: {str(e)}'
            }), 500
