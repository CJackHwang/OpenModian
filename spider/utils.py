# -*- coding: utf-8 -*-
"""
爬虫工具类
提供网络请求、数据处理、缓存等通用功能
"""

import os
import re
import json
import time
import random
import hashlib
import pickle
import socket
import urllib.request
import urllib.error
import html
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import requests
from bs4 import BeautifulSoup

from .config import SpiderConfig, RegexPatterns


class NetworkUtils:
    """网络请求工具类"""
    
    def __init__(self, config: SpiderConfig):
        self.config = config
        self.session = requests.Session()
        self.request_count = 0
        self.last_request_time = 0
        
    def get_headers(self, header_type: str = "desktop") -> Dict[str, str]:
        """获取请求头"""
        headers = self.config.REQUEST_HEADERS.get(header_type, {}).copy()
        
        # 添加时间戳防止缓存
        if header_type == "mobile":
            headers["Timestamp"] = str(int(time.time()))
            
        return headers
    
    def _rate_limit(self):
        """速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        min_delay, max_delay = self.config.REQUEST_DELAY
        required_delay = random.uniform(min_delay, max_delay)
        
        if time_since_last < required_delay:
            sleep_time = required_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def make_request(self, url: str, method: str = "GET", 
                    header_type: str = "desktop", **kwargs) -> Optional[str]:
        """发送HTTP请求"""
        self._rate_limit()
        
        headers = self.get_headers(header_type)
        timeout = random.randint(*self.config.TIMEOUT_RANGE)
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, headers=headers, timeout=timeout, **kwargs
                    )
                else:
                    response = self.session.request(
                        method, url, headers=headers, timeout=timeout, **kwargs
                    )
                
                response.raise_for_status()
                return response.text
                
            except (requests.RequestException, socket.timeout, 
                   urllib.error.URLError, ConnectionResetError) as e:
                print(f"请求失败 (尝试 {attempt + 1}/{self.config.MAX_RETRIES}): {e}")
                print(f"URL: {url}")
                
                if attempt < self.config.MAX_RETRIES - 1:
                    delay = random.uniform(*self.config.RETRY_DELAY) * (attempt + 1)
                    time.sleep(delay)
                else:
                    print(f"所有重试都失败了: {url}")
                    return None
        
        return None
    
    def make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发送API请求"""
        url = self.config.get_api_url(endpoint)
        
        try:
            response = self.session.get(
                url, 
                params=params or {},
                headers=self.get_headers("mobile"),
                timeout=random.randint(*self.config.TIMEOUT_RANGE)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API请求失败: {e}")
            return None
    
    def get_request_stats(self) -> Dict[str, Any]:
        """获取请求统计信息"""
        return {
            "total_requests": self.request_count,
            "last_request_time": self.last_request_time,
            "session_cookies": len(self.session.cookies)
        }


class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def extract_number(text: str, default: str = "0") -> str:
        """提取数字"""
        if not text:
            return default
            
        # 移除常见的非数字字符
        cleaned = re.sub(r'[^\d.]', '', str(text))
        
        # 验证是否为有效数字
        try:
            float(cleaned) if '.' in cleaned else int(cleaned)
            return cleaned
        except ValueError:
            return default
    
    @staticmethod
    def extract_percentage(text: str, default: str = "0") -> str:
        """提取百分比"""
        if not text:
            return default
            
        match = re.search(RegexPatterns.PERCENTAGE_PATTERN, str(text))
        return match.group(1) if match else default
    
    @staticmethod
    def extract_project_id(url: str) -> str:
        """从URL提取项目ID"""
        if not url:
            return ""
            
        match = re.search(RegexPatterns.PROJECT_ID_PATTERN, url)
        return match.group(1) if match else ""
    
    @staticmethod
    def extract_user_id(url: str) -> str:
        """从URL提取用户ID"""
        if not url:
            return ""
            
        match = re.search(RegexPatterns.USER_ID_PATTERN, url)
        return match.group(1) if match else ""
    
    @staticmethod
    def clean_text(text: str, max_length: int = None) -> str:
        """清理文本"""
        if not text:
            return ""
            
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()
        
        # 限制长度
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            
        return cleaned
    
    @staticmethod
    def parse_time(time_str: str) -> str:
        """解析时间字符串"""
        if not time_str or time_str in ["none", "创意中", "预热中", "众筹中"]:
            return time_str
            
        # 尝试不同的时间格式
        for pattern in RegexPatterns.TIME_PATTERNS:
            match = re.search(pattern, str(time_str))
            if match:
                return match.group(0)
        
        return time_str
    
    @staticmethod
    def validate_url(url: str) -> str:
        """验证和修正URL"""
        if not url or url == "none":
            return "none"
            
        url = str(url).strip()
        
        # 补全相对URL
        if url.startswith("/"):
            url = SpiderConfig.BASE_URL + url
        elif not url.startswith("http"):
            url = "https://" + url
            
        return url
    
    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """安全的JSON解析"""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default or {}
    
    @staticmethod
    def format_money(amount: str) -> str:
        """格式化金额"""
        if not amount or amount == "0":
            return "0"

        # 移除货币符号和逗号
        cleaned = re.sub(r'[￥¥,]', '', str(amount))

        try:
            # 转换为浮点数再转回字符串，确保格式一致
            return str(float(cleaned))
        except ValueError:
            return "0"

    @staticmethod
    def fix_encoding(text: str) -> str:
        """修复编码问题"""
        if not text:
            return ""

        try:
            # 尝试修复常见的编码问题
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')

            # 清理特殊字符
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(text))

            return text.strip()
        except Exception:
            return str(text).strip()

    @staticmethod
    def clean_reward_text(text: str) -> str:
        """清理回报文本"""
        if not text:
            return "none"

        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()

        # 移除特殊字符
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff，。！？；：""''（）【】《》、]', '', cleaned)

        # 限制长度
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."

        return cleaned if cleaned else "none"

    @staticmethod
    def fix_encoding(text: str) -> str:
        """修复编码问题"""
        if not text:
            return text

        try:
            # 方法1: 处理常见的编码错误模式
            encoding_map = {
                'ç¥å¥æ¨äºº': '神奇木人',
                'ä¸æµ·ä¼æ©æå': '上海伟恩文化',
                'é¢è®¡åæ¥åæ¾æ¶é´': '预计发货发放时间',
                'ä¸\\x8dé\\x9c\\x80è¦\\x81å\\x9b\\x9eæ\\x8a¥ï¼\\x8cæ\\x88\\x91å\\x': '不需要回报，我只是支持有梦想的人。',
                'ç®æ éé¢': '目标金额',
                'å·²ç­¹': '已筹',
                'æ¯æäººæ°': '支持人数',
                'å©ä½æ¶é´': '剩余时间'
            }

            # 检查是否有直接映射
            if text in encoding_map:
                return encoding_map[text]

            # 方法2: HTML解码
            decoded = html.unescape(text)
            if decoded != text:
                return decoded

            # 方法3: 处理Unicode转义序列
            if '\\x' in text:
                try:
                    # 将\\x转义序列转换为实际字符
                    fixed = text.encode().decode('unicode_escape')
                    return fixed
                except:
                    pass

            # 方法4: 处理UTF-8编码问题
            if any(ord(c) > 127 for c in text):
                try:
                    # 尝试重新编码
                    fixed = text.encode('latin1').decode('utf-8')
                    return fixed
                except:
                    pass

            return text
        except Exception:
            return text

    @staticmethod
    def clean_reward_text(text: str) -> str:
        """清理回报文本"""
        if not text:
            return "none"

        # 修复编码
        fixed = DataUtils.fix_encoding(text)

        # 清理文本
        cleaned = re.sub(r'\s+', ' ', fixed).strip()

        # 移除特殊字符
        cleaned = re.sub(r'[^\w\s\u4e00-\u9fff.,!?()（），。！？]', '', cleaned)

        return cleaned if cleaned else "none"


class CacheUtils:
    """缓存工具类"""
    
    def __init__(self, config: SpiderConfig):
        self.config = config
        self.cache_dir = Path(config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_key(self, url: str) -> str:
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """检查缓存是否有效"""
        if not cache_path.exists():
            return False
            
        # 检查缓存时间
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        expire_time = cache_time + timedelta(hours=self.config.CACHE_EXPIRE_HOURS)
        
        return datetime.now() < expire_time
    
    def get_cache(self, url: str) -> Optional[str]:
        """获取缓存内容"""
        if not self.config.ENABLE_CACHE:
            return None
            
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"读取缓存失败: {e}")
                
        return None
    
    def set_cache(self, url: str, content: str):
        """设置缓存内容"""
        if not self.config.ENABLE_CACHE:
            return
            
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"写入缓存失败: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            print("缓存已清空")
        except Exception as e:
            print(f"清空缓存失败: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_count": len(cache_files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir)
        }


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def ensure_directory(path: str):
        """确保目录存在"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def backup_file(file_path: str) -> str:
        """备份文件"""
        if not os.path.exists(file_path):
            return ""
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"备份文件失败: {e}")
            return ""
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """生成安全的文件名"""
        # 移除或替换不安全的字符
        safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return safe_chars[:255]  # 限制文件名长度


class ParserUtils:
    """解析工具类"""
    
    @staticmethod
    def safe_find(soup: BeautifulSoup, *args, **kwargs) -> Optional[Any]:
        """安全的元素查找"""
        try:
            return soup.find(*args, **kwargs)
        except Exception:
            return None
    
    @staticmethod
    def safe_find_all(soup: BeautifulSoup, *args, **kwargs) -> List[Any]:
        """安全的多元素查找"""
        try:
            return soup.find_all(*args, **kwargs)
        except Exception:
            return []
    
    @staticmethod
    def safe_get_text(element, default: str = "") -> str:
        """安全获取元素文本"""
        try:
            return element.get_text(strip=True) if element else default
        except Exception:
            return default
    
    @staticmethod
    def safe_get_attr(element, attr: str, default: str = "") -> str:
        """安全获取元素属性"""
        try:
            return element.get(attr, default) if element else default
        except Exception:
            return default
