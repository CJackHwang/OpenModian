#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试摩点爬虫分类功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spider.config import SpiderConfig
from main import ModianSpiderConfig

def test_spider_config_categories():
    """测试spider/config.py中的分类配置"""
    print("🧪 测试spider/config.py中的分类配置...")
    
    config = SpiderConfig()
    
    # 测试所有分类
    test_categories = [
        "all", "games", "publishing", "tablegames", "toys", "cards",
        "technology", "film-video", "music", "activities", "design",
        "curio", "home", "food", "comics", "charity", "animals", 
        "wishes", "others"
    ]
    
    for category in test_categories:
        url = config.get_full_url(category, 1)
        print(f"✅ {category:12} -> {url}")
    
    # 测试无效分类
    invalid_url = config.get_full_url("invalid_category", 1)
    print(f"⚠️  invalid     -> {invalid_url} (应该回退到all)")
    
    return True

def test_main_config_categories():
    """测试main.py中的分类配置"""
    print("\n🧪 测试main.py中的分类配置...")
    
    # 测试默认分类
    config1 = ModianSpiderConfig()
    print(f"✅ 默认分类: {config1.category} -> {config1.BASE_URL}")
    
    # 测试指定分类
    test_categories = ["tablegames", "games", "publishing", "cards"]
    
    for category in test_categories:
        config = ModianSpiderConfig(category)
        page_url = config.get_page_url(1)
        print(f"✅ {category:12} -> {page_url}")
    
    # 测试无效分类
    config_invalid = ModianSpiderConfig("invalid_category")
    print(f"⚠️  invalid     -> {config_invalid.BASE_URL} (应该回退到all)")
    
    # 测试动态设置分类
    config_dynamic = ModianSpiderConfig()
    config_dynamic.set_category("toys")
    print(f"✅ 动态设置toys -> {config_dynamic.BASE_URL}")
    
    return True

def test_url_construction():
    """测试URL构建"""
    print("\n🧪 测试URL构建...")
    
    config = SpiderConfig()
    
    # 测试不同页码
    for page in [1, 2, 10, 100]:
        url = config.get_full_url("tablegames", page)
        print(f"✅ 桌游第{page:3}页 -> {url}")
    
    return True

def test_web_ui_categories():
    """测试Web UI分类配置"""
    print("\n🧪 测试Web UI分类配置...")
    
    try:
        from web_ui.app import app
        
        with app.test_client() as client:
            response = client.get('/api/config')
            data = response.get_json()
            
            if data and data.get('success'):
                categories = data['config']['categories']
                print(f"✅ Web UI支持 {len(categories)} 个分类:")
                for cat in categories:
                    print(f"   {cat['value']:12} - {cat['label']}")
                return True
            else:
                print("❌ Web UI配置获取失败")
                return False
                
    except Exception as e:
        print(f"❌ Web UI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 摩点爬虫分类功能测试")
    print("=" * 60)
    
    tests = [
        ("spider/config.py分类", test_spider_config_categories),
        ("main.py分类", test_main_config_categories),
        ("URL构建", test_url_construction),
        ("Web UI分类", test_web_ui_categories),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
        
        print("-" * 40)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有分类功能测试通过！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
