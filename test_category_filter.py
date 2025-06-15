#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分类筛选功能
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from spider.config import SpiderConfig


def test_category_urls():
    """测试分类URL生成"""
    print("🔍 测试分类筛选功能")
    print("=" * 60)
    
    config = SpiderConfig()
    
    # 测试所有分类
    test_categories = [
        'all', 'games', 'publishing', 'tablegames', 'toys', 
        'cards', 'technology', 'film-video', 'music', 'activities',
        'design', 'curio', 'home', 'food', 'comics', 'charity',
        'animals', 'wishes', 'others'
    ]
    
    print("📋 分类URL测试:")
    for category in test_categories:
        url = config.get_full_url(category, 1)
        print(f"  {category:12} -> {url}")
    
    print("\n🔍 无效分类测试:")
    invalid_url = config.get_full_url("invalid_category", 1)
    print(f"  invalid      -> {invalid_url} (应该回退到all)")
    
    print("\n✅ 分类筛选功能测试完成")


if __name__ == "__main__":
    test_category_urls()
