# -*- coding: utf-8 -*-
"""
数据提取模块 - 新的互补架构
保留必要的提取器，移除冗余组件
"""

from .list_extractor import ListExtractor
from .content_extractor import ContentExtractor

__all__ = [
    'ListExtractor',    # 首页列表解析
    'ContentExtractor'  # API数据获取
]

# 已移除的冗余提取器：
# - DetailExtractor (详情页解析，依赖动态获取)
# - AuthorExtractor (作者信息，API已包含)
# - FundingExtractor (金额信息，API已包含)
