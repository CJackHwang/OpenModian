# -*- coding: utf-8 -*-
"""
网络请求优化模块
提供连接池、请求缓存、智能重试等网络优化功能
"""

import time
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import pickle
import os
from pathlib import Path


@dataclass
class NetworkStats:
    """网络统计信息"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    retry_requests: int = 0
    total_bytes_downloaded: int = 0
    average_response_time: float = 0.0
    connection_pool_hits: int = 0
    connection_pool_misses: int = 0


class SmartCache:
    """智能缓存系统"""
    
    def __init__(self, cache_dir: str = "data/cache/network", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_mb = max_size_mb
        self.cache_index = {}
        self._lock = threading.RLock()
        
        # 加载缓存索引
        self._load_cache_index()
    
    def _load_cache_index(self):
        """加载缓存索引"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.cache_index = json.load(f)
        except Exception as e:
            print(f"⚠️ 加载缓存索引失败: {e}")
            self.cache_index = {}
    
    def _save_cache_index(self):
        """保存缓存索引"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存缓存索引失败: {e}")
    
    def _get_cache_key(self, url: str, headers: Dict = None, params: Dict = None) -> str:
        """生成缓存键"""
        cache_data = {
            'url': url,
            'headers': headers or {},
            'params': params or {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get(self, url: str, headers: Dict = None, params: Dict = None, max_age: int = 3600) -> Optional[Dict]:
        """获取缓存"""
        with self._lock:
            cache_key = self._get_cache_key(url, headers, params)
            
            if cache_key not in self.cache_index:
                return None
            
            cache_info = self.cache_index[cache_key]
            
            # 检查是否过期
            if time.time() - cache_info['timestamp'] > max_age:
                self._remove_cache_entry(cache_key)
                return None
            
            # 读取缓存文件
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            try:
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
            except Exception as e:
                print(f"⚠️ 读取缓存失败: {e}")
                self._remove_cache_entry(cache_key)
            
            return None
    
    def set(self, url: str, response_data: Dict, headers: Dict = None, params: Dict = None):
        """设置缓存"""
        with self._lock:
            cache_key = self._get_cache_key(url, headers, params)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            try:
                # 保存缓存数据
                with open(cache_file, 'wb') as f:
                    pickle.dump(response_data, f)
                
                # 更新索引
                self.cache_index[cache_key] = {
                    'url': url,
                    'timestamp': time.time(),
                    'size': cache_file.stat().st_size
                }
                
                # 检查缓存大小
                self._cleanup_if_needed()
                
                # 保存索引
                self._save_cache_index()
                
            except Exception as e:
                print(f"⚠️ 保存缓存失败: {e}")
    
    def _remove_cache_entry(self, cache_key: str):
        """删除缓存条目"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                cache_file.unlink()
            
            if cache_key in self.cache_index:
                del self.cache_index[cache_key]
        except Exception as e:
            print(f"⚠️ 删除缓存条目失败: {e}")
    
    def _cleanup_if_needed(self):
        """根据需要清理缓存"""
        total_size = sum(info.get('size', 0) for info in self.cache_index.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            print(f"🧹 缓存大小超限 ({total_size/1024/1024:.1f}MB)，开始清理...")
            
            # 按时间戳排序，删除最旧的缓存
            sorted_entries = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            for cache_key, _ in sorted_entries:
                self._remove_cache_entry(cache_key)
                total_size = sum(info.get('size', 0) for info in self.cache_index.values())
                
                if total_size <= max_size_bytes * 0.8:  # 清理到80%
                    break
            
            print(f"🧹 缓存清理完成，当前大小: {total_size/1024/1024:.1f}MB")


class OptimizedHTTPAdapter(HTTPAdapter):
    """优化的HTTP适配器"""
    
    def __init__(self, pool_connections=20, pool_maxsize=50, max_retries=3, **kwargs):
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        super().__init__(max_retries=retry_strategy, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        """初始化连接池管理器"""
        kwargs['num_pools'] = self.pool_connections
        kwargs['maxsize'] = self.pool_maxsize
        kwargs['block'] = False  # 非阻塞模式
        return super().init_poolmanager(*args, **kwargs)


class NetworkOptimizer:
    """网络优化器"""
    
    def __init__(self, config=None):
        self.config = config
        self.stats = NetworkStats()
        self.cache = SmartCache()
        self._lock = threading.RLock()
        
        # 创建优化的会话
        self.session = self._create_optimized_session()
        
        # 请求历史（用于分析）
        self.request_history = []
        self.max_history_size = 1000
    
    def _create_optimized_session(self) -> requests.Session:
        """创建优化的请求会话"""
        session = requests.Session()
        
        # 配置连接池适配器
        http_adapter = OptimizedHTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=3
        )
        https_adapter = OptimizedHTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=3
        )
        
        session.mount("http://", http_adapter)
        session.mount("https://", https_adapter)
        
        # 设置默认超时
        session.timeout = 30
        
        # 设置默认头部
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def make_request(self, url: str, method: str = 'GET', use_cache: bool = True, 
                    cache_max_age: int = 3600, **kwargs) -> Optional[requests.Response]:
        """发起优化的网络请求"""
        start_time = time.time()
        
        with self._lock:
            self.stats.total_requests += 1
        
        # 尝试从缓存获取
        if use_cache and method.upper() == 'GET':
            cached_data = self.cache.get(
                url, 
                headers=kwargs.get('headers'),
                params=kwargs.get('params'),
                max_age=cache_max_age
            )
            
            if cached_data:
                with self._lock:
                    self.stats.cached_requests += 1
                    self.stats.successful_requests += 1
                
                # 创建模拟响应对象
                response = requests.Response()
                response._content = cached_data['content'].encode() if isinstance(cached_data['content'], str) else cached_data['content']
                response.status_code = cached_data['status_code']
                response.headers.update(cached_data['headers'])
                response.url = url
                
                return response
        
        # 发起实际请求
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            request_time = time.time() - start_time
            
            with self._lock:
                self.stats.successful_requests += 1
                self.stats.total_bytes_downloaded += len(response.content)
                self._update_average_response_time(request_time)
            
            # 缓存GET请求的响应
            if use_cache and method.upper() == 'GET' and response.status_code == 200:
                cache_data = {
                    'content': response.text,
                    'status_code': response.status_code,
                    'headers': dict(response.headers)
                }
                self.cache.set(url, cache_data, kwargs.get('headers'), kwargs.get('params'))
            
            # 记录请求历史
            self._record_request_history(url, method, request_time, True)
            
            return response
            
        except Exception as e:
            request_time = time.time() - start_time
            
            with self._lock:
                self.stats.failed_requests += 1
            
            self._record_request_history(url, method, request_time, False, str(e))
            print(f"❌ 网络请求失败: {url} - {e}")
            return None
    
    def _update_average_response_time(self, request_time: float):
        """更新平均响应时间"""
        if self.stats.successful_requests == 1:
            self.stats.average_response_time = request_time
        else:
            # 使用移动平均
            alpha = 0.1  # 平滑因子
            self.stats.average_response_time = (
                alpha * request_time + 
                (1 - alpha) * self.stats.average_response_time
            )
    
    def _record_request_history(self, url: str, method: str, request_time: float, 
                               success: bool, error: str = None):
        """记录请求历史"""
        history_entry = {
            'timestamp': time.time(),
            'url': url,
            'method': method,
            'request_time': request_time,
            'success': success,
            'error': error
        }
        
        self.request_history.append(history_entry)
        
        # 限制历史记录大小
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
    
    def get_network_stats(self) -> Dict[str, Any]:
        """获取网络统计信息"""
        with self._lock:
            success_rate = (
                self.stats.successful_requests / self.stats.total_requests * 100
                if self.stats.total_requests > 0 else 0
            )
            
            cache_hit_rate = (
                self.stats.cached_requests / self.stats.total_requests * 100
                if self.stats.total_requests > 0 else 0
            )
            
            return {
                'total_requests': self.stats.total_requests,
                'successful_requests': self.stats.successful_requests,
                'failed_requests': self.stats.failed_requests,
                'cached_requests': self.stats.cached_requests,
                'success_rate': success_rate,
                'cache_hit_rate': cache_hit_rate,
                'total_bytes_downloaded': self.stats.total_bytes_downloaded,
                'average_response_time': self.stats.average_response_time,
                'recent_requests': len(self.request_history)
            }
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析网络性能"""
        if not self.request_history:
            return {'message': '暂无请求历史数据'}
        
        recent_requests = self.request_history[-100:]  # 最近100个请求
        
        successful_requests = [r for r in recent_requests if r['success']]
        failed_requests = [r for r in recent_requests if not r['success']]
        
        if successful_requests:
            response_times = [r['request_time'] for r in successful_requests]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        return {
            'recent_requests_count': len(recent_requests),
            'success_rate': len(successful_requests) / len(recent_requests) * 100,
            'average_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'common_errors': self._get_common_errors(failed_requests)
        }
    
    def _get_common_errors(self, failed_requests: List[Dict]) -> Dict[str, int]:
        """获取常见错误统计"""
        error_counts = {}
        for request in failed_requests:
            error = request.get('error', 'Unknown')
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # 返回前5个最常见的错误
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def clear_cache(self):
        """清空缓存"""
        try:
            import shutil
            shutil.rmtree(self.cache.cache_dir)
            self.cache.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache.cache_index = {}
            print("🧹 网络缓存已清空")
        except Exception as e:
            print(f"❌ 清空缓存失败: {e}")
    
    def close(self):
        """关闭网络优化器"""
        if hasattr(self, 'session'):
            self.session.close()


# 全局网络优化器实例
_global_network_optimizer = None
_optimizer_lock = threading.Lock()


def get_network_optimizer():
    """获取全局网络优化器实例（单例模式）"""
    global _global_network_optimizer
    
    if _global_network_optimizer is None:
        with _optimizer_lock:
            if _global_network_optimizer is None:
                _global_network_optimizer = NetworkOptimizer()
    
    return _global_network_optimizer
