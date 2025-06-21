# -*- coding: utf-8 -*-
"""
爬虫相关API路由
处理爬虫任务的启动、停止、状态查询等
"""

from flask import request, jsonify


def register_spider_routes(app, spider_service):
    """注册爬虫相关路由"""
    
    @app.route('/api/start_crawl', methods=['POST'])
    def start_crawl():
        """启动爬虫任务"""
        try:
            data = request.json
            result = spider_service.create_crawl_task(data)
            # 保持与原版本兼容的响应格式
            return jsonify({
                'success': True,
                'task_id': result['task_id'],
                'message': result['message'],
                'is_scheduled': result.get('is_scheduled', False)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'启动失败: {str(e)}'
            }), 500
    
    @app.route('/api/stop_crawl/<task_id>', methods=['POST'])
    def stop_crawl(task_id):
        """停止爬虫任务"""
        try:
            success = spider_service.stop_task(task_id)
            if success:
                return jsonify({
                    'success': True,
                    'message': '任务已停止'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '任务不存在'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'停止失败: {str(e)}'
            }), 500
    
    @app.route('/api/config')
    def get_config():
        """获取默认配置"""
        from spider.config import SpiderConfig
        config = SpiderConfig()
        return jsonify({
            'success': True,
            'config': {
                'start_page': 1,
                'end_page': 10,
                'category': 'all',
                'max_concurrent': config.MAX_CONCURRENT_REQUESTS,
                'delay_min': config.REQUEST_DELAY[0],
                'delay_max': config.REQUEST_DELAY[1],
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
                    {'value': 'design', 'label': '设计'},
                    {'value': 'curio', 'label': '文玩'},
                    {'value': 'home', 'label': '家居'},
                    {'value': 'food', 'label': '食品'},
                    {'value': 'comics', 'label': '动漫'},
                    {'value': 'charity', 'label': '爱心通道'},
                    {'value': 'animals', 'label': '动物救助'},
                    {'value': 'wishes', 'label': '个人愿望'},
                    {'value': 'others', 'label': '其他'}
                ]
            }
        })
