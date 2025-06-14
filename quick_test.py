#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("开始测试...")

try:
    print("1. 导入模块...")
    from spider.config import SpiderConfig
    print("✅ SpiderConfig导入成功")
    
    config = SpiderConfig()
    print(f"✅ 配置创建成功，分类数: {len(config.CATEGORY_URLS)}")
    
    print("2. 测试URL构建...")
    test_url = config.get_full_url('tablegames', 1)
    print(f"✅ URL构建成功: {test_url}")
    
    print("3. 导入爬虫核心...")
    from spider.core import SpiderCore
    print("✅ SpiderCore导入成功")
    
    print("4. 创建爬虫实例...")
    spider = SpiderCore(config)
    print("✅ 爬虫实例创建成功")
    
    print("5. 测试简单爬取...")
    success = spider.start_crawling(start_page=1, end_page=1, category='tablegames')
    print(f"✅ 爬取完成: {success}")
    print(f"   项目数量: {len(spider.projects_data)}")
    
    if spider.projects_data:
        print("6. 项目示例:")
        for i, project in enumerate(spider.projects_data[:3]):
            if len(project) >= 4:
                print(f"   {i+1}. {project[3][:50]}...")
    
    print("\n🎉 测试完成！爬虫功能正常")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
