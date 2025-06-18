# -*- coding: utf-8 -*-
"""
加密工具类
提供MD5等加密功能，用于API签名
"""

import hashlib


def hex_md5(text: str) -> str:
    """
    计算字符串的MD5哈希值
    
    Args:
        text: 要计算哈希的字符串
        
    Returns:
        MD5哈希值的十六进制字符串
    """
    if not isinstance(text, str):
        text = str(text)
    
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def generate_timestamp() -> int:
    """
    生成当前时间戳（秒）
    
    Returns:
        当前时间戳
    """
    import time
    return int(time.time())


def generate_random_string(length: int = 8) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        随机字符串
    """
    import random
    import string
    
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
