# -*- coding: utf-8 -*-
"""
API数据获取器
基于参考项目的快速API调用方式，直接获取摩点项目数据
高性能API获取，速度快，资源消耗少，数据完整
"""

import json
import time
import re
from typing import Dict, Optional, Any
from urllib.parse import urlparse
import requests

from .crypto_utils import hex_md5, generate_timestamp
from .config import SpiderConfig


class ModianAPIFetcher:
    """摩点API数据获取器"""
    
    def __init__(self, config: SpiderConfig = None):
        self.config = config or SpiderConfig()
        self.session = requests.Session()
        
        # API配置
        self.base_url = "https://zhongchou.modian.com"
        self.api_base_url = "https://apim.modian.com"
        self.app_key = "MzgxOTg3ZDMZTgxO"  # 从参考项目获取
        
        # 默认请求头
        self.default_headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        
        # 统计信息
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
    def get_sign(self, url: str, method: str = 'GET', data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成API签名
        基于参考项目的签名算法
        """
        if data is None:
            data = {}
            
        request_url = url if url.startswith('http') else f"{self.api_base_url}{url}"
        parsed_url = urlparse(request_url)
        host_all = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        hosts = host_all.replace('http://', '').replace('https://', '')
        
        query = parsed_url.query
        props = ''
        
        # 处理POST或GET数据
        paras = []
        for key, value in data.items():
            if '/search/all' in url:
                paras.append(f"{key}={requests.utils.quote(str(value))}")
            else:
                paras.append(f"{key}={value}")
        
        paras.sort()
        props = '&'.join(paras) if paras else ''
        
        # 合并查询参数
        if method == 'GET' and props:
            if query:
                query += "&"
            query += props
        
        if query:
            query = '&'.join(sorted(query.split('&')))
        
        if method == 'GET':
            props = ''
        
        apim_data = generate_timestamp()
        
        # 计算签名
        sign_string = (
            hosts + 
            self.app_key + 
            str(apim_data) + 
            requests.utils.unquote(query or '') + 
            hex_md5(requests.utils.unquote(props or ''))
        )
        
        good_sign = hex_md5(sign_string)
        
        return {
            'sign': good_sign,
            'mt': apim_data,
            'requestUrl': f"{host_all}?{query}" if query else host_all,
            'data': data if method != 'GET' else None
        }
    
    def make_authenticated_request(self, url: str, method: str = 'GET', 
                                 data: Dict[str, Any] = None, 
                                 token: str = None, user_id: str = None) -> Optional[requests.Response]:
        """
        发起认证请求
        """
        auth_info = self.get_sign(url, method, data or {})
        
        # 构建请求头
        headers = self.default_headers.copy()
        headers.update({
            'build': '15000',
            'client': '11',
            'mt': str(auth_info['mt']),
            'sign': auth_info['sign'],
        })
        
        # 添加认证信息（如果提供）
        if token:
            headers['token'] = token
        if user_id:
            headers['user_id'] = user_id
            headers['userid'] = user_id
        
        try:
            self.request_count += 1
            
            if method.upper() == 'GET':
                response = self.session.get(
                    auth_info['requestUrl'],
                    headers=headers,
                    timeout=self.config.API_TIMEOUT
                )
            else:
                response = self.session.request(
                    method,
                    auth_info['requestUrl'],
                    headers=headers,
                    json=auth_info['data'],
                    timeout=self.config.API_TIMEOUT
                )
            
            response.raise_for_status()
            self.success_count += 1
            return response
            
        except Exception as e:
            self.error_count += 1
            print(f"API请求失败: {e}")
            return None
    
    def make_simple_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        发起普通HTTP请求（不需要认证）
        """
        headers = self.default_headers.copy()
        headers.update(kwargs.get('headers', {}))
        
        try:
            self.request_count += 1
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.config.API_TIMEOUT,
                **{k: v for k, v in kwargs.items() if k != 'headers'}
            )
            
            response.raise_for_status()
            self.success_count += 1
            return response
            
        except Exception as e:
            self.error_count += 1
            print(f"简单请求失败: {e}")
            return None
    
    def get_project_data(self, project_id: str) -> Dict[str, Any]:
        """
        获取项目完整数据 - 完全按照参考项目实现
        返回与爬虫兼容的完整数据结构
        """
        try:
            # 1. 获取项目限制状态（验证项目存在）
            limit_url = f"{self.base_url}/p/get_project_limit_status?pro_id={project_id}"
            limit_response = self.make_simple_request(limit_url)

            if not limit_response:
                print(f"项目 {project_id} 限制状态获取失败")
                return self._get_empty_result()

            # 2. 获取项目详细信息
            timestamp = int(time.time() * 1000)
            detail_url = (
                f"{self.base_url}/realtime/get_simple_product"
                f"?jsonpcallback=jQuery{timestamp}&ids={project_id}&if_all=1&_={timestamp + 1}"
            )

            detail_response = self.make_simple_request(detail_url)

            if not detail_response:
                print(f"项目 {project_id} 详情获取失败")
                return self._get_empty_result()

            # 3. 解析JSONP响应
            detail_text = detail_response.text

            # 支持两种JSONP格式
            jsonp_match = re.search(r'jQuery\d+\((.+)\);?$', detail_text)
            if not jsonp_match:
                jsonp_match = re.search(r'window\[decodeURIComponent\(\'jQuery\d+\'\)\]\((.+)\);?$', detail_text)

            if not jsonp_match:
                print(f"项目 {project_id} JSONP解析失败")
                return self._get_empty_result()

            # 4. 解析JSON数据
            projects_data = json.loads(jsonp_match.group(1))
            if not projects_data or len(projects_data) == 0:
                print(f"项目 {project_id} 数据为空")
                return self._get_empty_result()

            raw_project_data = projects_data[0]

            # 5. 按照参考项目逻辑转换数据
            transformed_data = self._transform_raw_to_clean(raw_project_data)

            print(f"✅ API获取项目 {project_id} 成功: 状态={transformed_data.get('project_status')}, 回报数={len(transformed_data.get('rewards_data', []))}个")

            return transformed_data

        except Exception as e:
            print(f"项目 {project_id} API获取失败: {e}")
            return self._get_empty_result()

    def _get_empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "like_count": "0",
            "comment_count": "0",
            "supporter_count": "0",
            "project_status": "未知情况",
            "rewards_data": [],
            "start_time": "none",
            "end_time": "none",
            "raised_amount": 0,
            "target_amount": 0,
            "completion_rate": 0,
            "backer_count": 0,
            "category": "none",
            "author_name": "none",
            "project_name": "none"
        }

    def _transform_raw_to_clean(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """将原始API数据转换为爬虫兼容的数据格式 - 完全按照参考项目逻辑"""
        try:
            # 解析金额字符串为数字
            def parse_amount(amount_str: str) -> float:
                if not amount_str:
                    return 0
                import re
                cleaned = re.sub(r'[^\d.]', '', str(amount_str))
                return float(cleaned) if cleaned else 0

            # 计算完成率
            goal_amount = parse_amount(raw_data.get('goal', '1000'))
            raised_amount = parse_amount(raw_data.get('backer_money', '0'))
            completion_rate = (raised_amount / goal_amount) * 100 if goal_amount > 0 else 0

            # 确定项目状态
            project_status = self._determine_status(
                raw_data.get('status', ''),
                raw_data.get('end_time', ''),
                completion_rate
            )

            # 处理回报档位数据
            rewards_data = self._extract_rewards_data(raw_data)

            # 返回与爬虫兼容的数据格式
            return {
                # 基础数据（爬虫需要的格式）
                "like_count": str(raw_data.get('bull_count', 0)),
                "comment_count": str(raw_data.get('comment_count', 0)),
                "supporter_count": str(raw_data.get('backer_count', 0)),

                # 项目信息
                "project_id": str(raw_data.get('id', '')),
                "project_name": raw_data.get('name', ''),
                "project_status": project_status,
                "category": raw_data.get('category', ''),

                # 作者信息
                "author_name": raw_data.get('user_info', {}).get('nickname', '') if raw_data.get('user_info') else '',
                "author_link": f"/u/{raw_data.get('user_id', '')}" if raw_data.get('user_id') else '',
                "author_image": "",  # API中没有直接的作者头像

                # 时间信息
                "start_time": raw_data.get('start_time', ''),
                "end_time": raw_data.get('end_time', ''),

                # 金额信息
                "raised_amount": raised_amount,
                "target_amount": goal_amount,
                "completion_rate": round(completion_rate, 2),
                "backer_count": raw_data.get('backer_count', 0),
                "update_count": raw_data.get('update_count', 0),

                # 回报数据
                "rewards_data": rewards_data,

                # 媒体内容
                "content_images": "[]",  # API中没有直接的图片列表
                "content_videos": "[]",  # API中没有直接的视频列表

                # 项目链接和图片
                "project_url": f"https://zhongchou.modian.com/item/{raw_data.get('id', '')}.html",
                "project_image": raw_data.get('logo2') or raw_data.get('logo', ''),
            }

        except Exception as e:
            print(f"⚠️ 数据转换失败: {e}")
            return self._get_empty_result()

    def _determine_status(self, status_str: str, end_time: str, completion_rate: float) -> str:
        """直接返回API原始状态，不进行任何映射或转换"""
        if not status_str:
            return '未知情况'

        # 直接返回API原始状态，记录日志
        print(f"📝 API原始状态: {status_str}")
        return status_str

    def _extract_project_status(self, project_data: Dict[str, Any]) -> str:
        """从API数据中提取项目状态 - 完全按照参考项目逻辑"""
        try:
            # 按照参考项目的逻辑进行状态判断
            status_str = project_data.get('status', '')
            end_time = project_data.get('end_time', '')
            backer_money = project_data.get('backer_money', '0')
            goal = project_data.get('goal', '1000')

            # 解析金额 - 按照参考项目方式
            def parse_amount(amount_str: str) -> float:
                if not amount_str:
                    return 0
                # 移除逗号和其他非数字字符，保留小数点
                import re
                cleaned = re.sub(r'[^\d.]', '', str(amount_str))
                return float(cleaned) if cleaned else 0

            goal_amount = parse_amount(goal)
            raised_amount = parse_amount(backer_money)
            completion_rate = (raised_amount / goal_amount) * 100 if goal_amount > 0 else 0

            # 直接使用_determine_status方法，避免重复代码
            return self._determine_status(status_str, end_time, completion_rate)

        except Exception as e:
            print(f"⚠️ API状态提取失败: {e}")
            return '未知情况'

    def _parse_end_time(self, end_time_str: str):
        """解析结束时间 - 按照参考项目逻辑"""
        if not end_time_str:
            return None

        try:
            from datetime import datetime
            # 处理多种可能的时间格式
            time_str = end_time_str.strip()

            # 如果时间格式是 "YYYY-MM-DD HH:mm:ss"，转换为 ISO 格式
            if time_str.find(' ') != -1 and len(time_str) == 19:
                time_str = time_str.replace(' ', 'T')

            # 如果没有时区信息，添加本地时区（中国时区）
            if 'T' not in time_str:
                time_str = time_str + 'T00:00:00'
            if '+' not in time_str and 'Z' not in time_str:
                time_str = time_str + '+08:00'

            date = datetime.fromisoformat(time_str.replace('+08:00', ''))
            return date
        except Exception as e:
            print(f"解析结束时间失败: {end_time_str}, {e}")
            return None

    def _extract_rewards_data(self, project_data: Dict[str, Any]) -> list:
        """从API数据中提取回报信息 - 完全按照参考项目逻辑"""
        try:
            # 按照参考项目的transformRewardTiers逻辑
            reward_list = project_data.get('reward_list', [])

            if not reward_list:
                return []

            # 按照参考项目的逻辑处理回报数据
            def parse_price(price_str: str) -> float:
                if not price_str:
                    return 0
                import re
                cleaned = re.sub(r'[^\d.]', '', str(price_str))
                return float(cleaned) if cleaned else 0

            rewards_list = []

            for reward in reward_list:
                # 只保留显示的档位
                if_show = reward.get('if_show', 1)
                if if_show != 1:
                    continue

                # 按照参考项目的数据结构提取
                price = parse_price(reward.get('money') or reward.get('app_money', '0'))
                max_total = reward.get('max_total', 0)
                backer_count = reward.get('back_count', 0)
                remaining_count = max(0, max_total - backer_count) if max_total > 0 else 0

                # 转换为我们的格式：[title, sign_logo, back_money, backers, time_info, detail]
                title = reward.get('title') or reward.get('name', '未命名档位')
                money = str(int(price)) if price.is_integer() else str(price)
                back_count = str(backer_count)
                content = self._clean_html_tags(reward.get('content', ''))

                # 处理限量信息
                is_limited = max_total > 0
                sign_logo = f"限量{max_total}" if is_limited else "普通"

                # 处理时间信息
                reward_day = reward.get('reward_day', '')
                time_info = reward_day if reward_day and reward_day != '1970年01月内' else ''

                reward_item = [title, sign_logo, money, back_count, time_info, content]
                rewards_list.append(reward_item)

            print(f"📦 API提取到 {len(rewards_list)} 个回报档位")
            return rewards_list

        except Exception as e:
            print(f"⚠️ API回报数据提取失败: {e}")
            return []

    def _clean_html_tags(self, text: str) -> str:
        """清理HTML标签"""
        if not text:
            return '无详细描述'

        import re
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 移除多余的空白字符
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        # 替换HTML实体
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')

        return clean_text if clean_text else '无详细描述'

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "total_requests": self.request_count,
            "success_requests": self.success_count,
            "error_requests": self.error_count,
            "success_rate": round(self.success_count / max(self.request_count, 1) * 100, 2)
        }
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()
