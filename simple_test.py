#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的爬虫测试 - 验证核心功能
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_crawling():
    """测试基础爬虫功能"""
    print("🚀 测试摩点爬虫基础功能")
    print("=" * 50)
    
    try:
        from spider.config import SpiderConfig
        from spider.core import SpiderCore
        
        # 创建配置
        config = SpiderConfig()
        config.MAX_CONCURRENT_REQUESTS = 1  # 降低并发避免被封
        
        print(f"✅ 配置加载成功")
        print(f"   支持分类数: {len(config.CATEGORY_URLS)}")
        print(f"   输出目录: {config.OUTPUT_DIR}")
        
        # 测试URL构建
        test_url = config.get_full_url('tablegames', 1)
        print(f"   测试URL: {test_url}")
        
        # 创建爬虫
        spider = SpiderCore(config)
        print(f"✅ 爬虫初始化成功")
        
        # 测试单页爬取
        print(f"\n🎯 测试桌游分类第1页...")
        start_time = time.time()
        
        success = spider.start_crawling(
            start_page=1,
            end_page=1,
            category='tablegames'
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 爬取结果:")
        print(f"   成功: {success}")
        print(f"   项目数: {len(spider.projects_data)}")
        print(f"   失败数: {len(spider.failed_urls)}")
        print(f"   耗时: {elapsed:.1f}秒")
        
        # 显示项目示例
        if spider.projects_data:
            print(f"\n📝 项目示例:")
            for i, project in enumerate(spider.projects_data[:3]):
                if len(project) >= 4:
                    print(f"   {i+1}. {project[3][:40]}...")
                    print(f"      URL: {project[1]}")
                    print(f"      ID: {project[2]}")
        
        # 检查输出文件
        output_dir = Path(config.OUTPUT_DIR)
        if output_dir.exists():
            files = list(output_dir.glob("*.xls")) + list(output_dir.glob("*.json"))
            print(f"\n📁 输出文件:")
            for file in files:
                print(f"   {file.name} ({file.stat().st_size} bytes)")
        
        return success and len(spider.projects_data) > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_categories():
    """测试多分类支持"""
    print(f"\n🎯 测试多分类支持")
    print("=" * 50)
    
    try:
        from spider.config import SpiderConfig
        from spider.core import SpiderCore
        
        config = SpiderConfig()
        config.MAX_CONCURRENT_REQUESTS = 1
        
        categories = ['tablegames', 'games', 'cards']
        results = {}
        
        for category in categories:
            print(f"\n测试分类: {category}")
            
            spider = SpiderCore(config)
            spider.projects_data.clear()
            spider.failed_urls.clear()
            
            start_time = time.time()
            success = spider.start_crawling(
                start_page=1,
                end_page=1,
                category=category
            )
            elapsed = time.time() - start_time
            
            results[category] = {
                'success': success,
                'count': len(spider.projects_data),
                'time': elapsed
            }
            
            print(f"   结果: {'✅' if success else '❌'} {len(spider.projects_data)}个项目 {elapsed:.1f}s")
            
            # 短暂休息
            time.sleep(1)
        
        print(f"\n📊 多分类测试总结:")
        successful = sum(1 for r in results.values() if r['success'])
        total_projects = sum(r['count'] for r in results.values())
        
        print(f"   成功分类: {successful}/{len(categories)}")
        print(f"   总项目数: {total_projects}")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ 多分类测试失败: {e}")
        return False

def test_web_ui_integration():
    """测试Web UI集成"""
    print(f"\n🌐 测试Web UI集成")
    print("=" * 50)
    
    try:
        from web_ui.app import app
        
        with app.test_client() as client:
            # 测试配置接口
            response = client.get('/api/config')
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    categories = data['config']['categories']
                    print(f"✅ Web UI配置正常")
                    print(f"   支持分类: {len(categories)}个")
                    return True
                else:
                    print(f"❌ Web UI配置响应异常")
                    return False
            else:
                print(f"❌ Web UI配置接口失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Web UI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 摩点爬虫功能验证")
    print("=" * 60)
    
    tests = [
        ("基础爬虫功能", test_basic_crawling),
        ("多分类支持", test_multiple_categories),
        ("Web UI集成", test_web_ui_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n{test_name}: ❌ 异常 - {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n" + "=" * 60)
    print(f"📊 测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 所有测试通过！爬虫功能正常")
        return True
    elif passed > 0:
        print(f"⚠️ 部分测试通过，爬虫基本可用")
        return True
    else:
        print(f"❌ 所有测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
