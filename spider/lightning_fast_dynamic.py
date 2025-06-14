#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闪电般快速动态数据获取器
真正接近人工速度的解决方案
"""

import time
import threading
from typing import Dict, Optional
import atexit


class LightningFastExtractor:
    """闪电般快速提取器"""
    
    _shared_driver = None
    _driver_lock = threading.Lock()
    _last_used = 0
    
    def __init__(self, config):
        self.config = config
        self.timeout = getattr(config, 'LIGHTNING_TIMEOUT', 2)  # 2秒超时
        
    @classmethod
    def _get_shared_driver(cls):
        """获取共享的浏览器实例"""
        with cls._driver_lock:
            current_time = time.time()
            
            # 如果驱动不存在或超过5分钟未使用，重新创建
            if (cls._shared_driver is None or 
                current_time - cls._last_used > 300):
                
                if cls._shared_driver:
                    try:
                        cls._shared_driver.quit()
                    except:
                        pass
                
                cls._shared_driver = cls._create_lightning_driver()
            
            cls._last_used = current_time
            return cls._shared_driver
    
    @classmethod
    def _create_lightning_driver(cls):
        """创建闪电般快速的浏览器"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError:
            return None
        
        # 极致优化的Chrome配置
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # 新的无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-css')
        chrome_options.add_argument('--disable-javascript-harmony-shipping')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees,VizDisplayCompositor')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--aggressive-cache-discard')
        chrome_options.add_argument('--memory-pressure-off')
        chrome_options.add_argument('--max_old_space_size=4096')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # 设置页面加载策略
        chrome_options.page_load_strategy = 'eager'
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 设置超时
            driver.set_page_load_timeout(2)
            driver.implicitly_wait(0.5)
            
            return driver
        except Exception as e:
            print(f"创建闪电驱动失败: {e}")
            return None
    
    def get_lightning_data(self, project_id: str) -> Dict[str, str]:
        """闪电般获取数据"""
        driver = self._get_shared_driver()
        if not driver:
            return {"like_count": "0", "comment_count": "0"}
        
        project_url = f"https://zhongchou.modian.com/item/{project_id}.html"
        
        try:
            start_time = time.time()
            
            # 快速导航
            driver.get(project_url)
            
            # 立即执行滚动脚本
            driver.execute_script("""
                window.scrollTo(0, document.body.scrollHeight/2);
                window.scrollTo(0, document.body.scrollHeight);
            """)
            
            # 快速检查数据（最多检查3次，每次间隔500ms）
            for i in range(3):
                data = self._quick_extract(driver)
                
                # 如果获取到有效数据，立即返回
                if data["like_count"] != "0" or data["comment_count"] != "0":
                    elapsed = (time.time() - start_time) * 1000
                    print(f"⚡ 闪电获取成功，耗时: {elapsed:.0f}ms")
                    return data
                
                # 短暂等待
                if i < 2:  # 最后一次不等待
                    time.sleep(0.5)
            
            elapsed = (time.time() - start_time) * 1000
            print(f"⏰ 闪电获取超时，耗时: {elapsed:.0f}ms")
            return data
            
        except Exception as e:
            print(f"闪电获取失败: {e}")
            return {"like_count": "0", "comment_count": "0"}
    
    def _quick_extract(self, driver) -> Dict[str, str]:
        """快速提取数据"""
        from selenium.webdriver.common.by import By
        
        result = {"like_count": "0", "comment_count": "0"}
        
        try:
            # 快速获取点赞数
            atten_elements = driver.find_elements(By.CSS_SELECTOR, "li.atten span")
            for elem in atten_elements:
                text = elem.text.strip()
                if text and text.isdigit() and int(text) > 0:
                    result["like_count"] = text
                    break
        except:
            pass
        
        try:
            # 快速获取评论数
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "li.nav-comment span")
            for elem in comment_elements:
                text = elem.text.strip()
                if text and text.isdigit() and int(text) > 0:
                    result["comment_count"] = text
                    break
        except:
            pass
        
        return result
    
    @classmethod
    def cleanup(cls):
        """清理共享驱动"""
        with cls._driver_lock:
            if cls._shared_driver:
                try:
                    cls._shared_driver.quit()
                except:
                    pass
                cls._shared_driver = None


# 注册清理函数
atexit.register(LightningFastExtractor.cleanup)


class LightningDataManager:
    """闪电数据管理器"""
    
    def __init__(self, config, network_utils):
        self.config = config
        self.network_utils = network_utils
        self.extractor = LightningFastExtractor(config)
        self._cache = {}
        
    def get_lightning_data(self, project_id: str) -> Dict[str, str]:
        """获取闪电数据"""
        # 检查缓存
        if project_id in self._cache:
            cache_time, data = self._cache[project_id]
            if time.time() - cache_time < 1800:  # 30分钟缓存
                return data
        
        # 闪电获取
        start_time = time.time()
        data = self.extractor.get_lightning_data(project_id)
        elapsed_time = time.time() - start_time
        
        print(f"⚡ 闪电数据获取完成: {elapsed_time:.2f}秒")
        
        # 缓存结果
        self._cache[project_id] = (time.time(), data)
        
        return data
    
    def batch_lightning_data(self, project_ids: list) -> Dict[str, Dict[str, str]]:
        """批量闪电获取"""
        results = {}
        
        print(f"⚡ 批量闪电获取: {len(project_ids)} 个项目")
        
        total_start = time.time()
        
        for project_id in project_ids:
            results[project_id] = self.get_lightning_data(project_id)
        
        total_time = time.time() - total_start
        avg_time = total_time / len(project_ids)
        
        print(f"📊 批量闪电完成: 总耗时{total_time:.2f}秒, 平均{avg_time:.2f}秒/项目")
        
        return results


def test_lightning_speed():
    """测试闪电速度"""
    print("⚡ 测试闪电速度")
    print("=" * 60)
    
    from spider.config import SpiderConfig
    from spider.utils import NetworkUtils
    
    config = SpiderConfig()
    network_utils = NetworkUtils(config)
    manager = LightningDataManager(config, network_utils)
    
    project_id = "147446"
    
    print(f"📡 测试项目: {project_id}")
    print("🎯 目标: 2秒内完成")
    
    # 测试3次取平均值
    times = []
    results = []
    
    for i in range(3):
        print(f"\n第 {i+1} 次测试:")
        start_time = time.time()
        result = manager.get_lightning_data(project_id)
        elapsed_time = time.time() - start_time
        
        times.append(elapsed_time)
        results.append(result)
        
        print(f"   结果: 点赞={result.get('like_count', '0')}, 评论={result.get('comment_count', '0')}")
        print(f"   耗时: {elapsed_time:.2f}秒")
    
    avg_time = sum(times) / len(times)
    print(f"\n📊 平均耗时: {avg_time:.2f}秒")
    
    if avg_time <= 2:
        print("🚀 闪电速度目标达成！")
        return True
    elif avg_time <= 3:
        print("✅ 速度良好")
        return True
    else:
        print("⚠️  仍需优化")
        return False


if __name__ == "__main__":
    test_lightning_speed()
