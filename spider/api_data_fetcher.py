# -*- coding: utf-8 -*-
"""
API数据获取器
基于参考项目的快速API调用方式，直接获取摩点项目数据
作为动态获取的主要方法，速度更快，资源消耗更少
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
                    timeout=self.config.LIGHTNING_TIMEOUT
                )
            else:
                response = self.session.request(
                    method,
                    auth_info['requestUrl'],
                    headers=headers,
                    json=auth_info['data'],
                    timeout=self.config.LIGHTNING_TIMEOUT
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
                timeout=self.config.LIGHTNING_TIMEOUT,
                **{k: v for k, v in kwargs.items() if k != 'headers'}
            )
            
            response.raise_for_status()
            self.success_count += 1
            return response
            
        except Exception as e:
            self.error_count += 1
            print(f"简单请求失败: {e}")
            return None
    
    def get_project_data(self, project_id: str) -> Dict[str, str]:
        """
        获取项目数据
        使用参考项目的API调用方式
        """
        try:
            # 1. 获取项目限制状态（可选，用于验证项目存在）
            limit_url = f"{self.base_url}/p/get_project_limit_status?pro_id={project_id}"
            limit_response = self.make_simple_request(limit_url)
            
            if not limit_response:
                print(f"项目 {project_id} 限制状态获取失败")
                return {"like_count": "0", "comment_count": "0"}
            
            # 2. 获取项目详细信息
            timestamp = int(time.time() * 1000)
            detail_url = (
                f"{self.base_url}/realtime/get_simple_product"
                f"?jsonpcallback=jQuery{timestamp}&ids={project_id}&if_all=1&_={timestamp + 1}"
            )
            
            detail_response = self.make_simple_request(detail_url)
            
            if not detail_response:
                print(f"项目 {project_id} 详情获取失败")
                return {"like_count": "0", "comment_count": "0"}
            
            # 3. 解析JSONP响应
            detail_text = detail_response.text
            
            # 支持两种JSONP格式
            jsonp_match = re.search(r'jQuery\d+\((.+)\);?$', detail_text)
            if not jsonp_match:
                jsonp_match = re.search(r'window\[decodeURIComponent\(\'jQuery\d+\'\)\]\((.+)\);?$', detail_text)
            
            if not jsonp_match:
                print(f"项目 {project_id} JSONP解析失败")
                return {"like_count": "0", "comment_count": "0"}
            
            # 4. 解析JSON数据
            projects_data = json.loads(jsonp_match.group(1))
            if not projects_data or len(projects_data) == 0:
                print(f"项目 {project_id} 数据为空")
                return {"like_count": "0", "comment_count": "0"}
            
            project_data = projects_data[0]
            
            # 5. 提取关键数据
            like_count = str(project_data.get('bull_count', 0))
            comment_count = str(project_data.get('comment_count', 0))
            
            print(f"✅ API获取项目 {project_id} 成功: 看好数={like_count}, 评论数={comment_count}")
            
            return {
                "like_count": like_count,
                "comment_count": comment_count
            }
            
        except Exception as e:
            print(f"项目 {project_id} API获取失败: {e}")
            return {"like_count": "0", "comment_count": "0"}
    
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
