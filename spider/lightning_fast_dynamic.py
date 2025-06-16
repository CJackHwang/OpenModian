#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闪电般快速动态数据获取器
真正接近人工速度的解决方案
"""

import time
import threading
from typing import Dict, Optional


class LightningFastExtractor:
    """闪电般快速提取器 - 修复并发问题版本"""

    def __init__(self, config, stop_flag=None):
        self.config = config
        self.timeout = getattr(config, 'LIGHTNING_TIMEOUT', 10)  # 10秒超时，等待特效完成
        self._driver = None  # 每个实例独立的驱动
        self._driver_lock = threading.Lock()
        self.stop_flag = stop_flag  # 添加停止标志

    def _log(self, level: str, message: str):
        """简单日志输出"""
        print(f"[{level.upper()}] {message}")

    def _should_stop(self):
        """检查是否应该停止"""
        return self.stop_flag and self.stop_flag.is_set()

    def _get_driver(self):
        """获取当前实例的独立浏览器实例"""
        with self._driver_lock:
            if self._driver is None:
                self._driver = self._create_lightning_driver()
            return self._driver

    def _cleanup_driver(self):
        """清理当前实例的驱动"""
        with self._driver_lock:
            if self._driver:
                try:
                    self._driver.quit()
                except:
                    pass
                self._driver = None
    
    def _create_lightning_driver(self):
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
            
            # 设置超时 - 增加超时时间解决渲染问题
            driver.set_page_load_timeout(8)
            driver.implicitly_wait(1)
            
            return driver
        except Exception as e:
            print(f"创建闪电驱动失败: {e}")
            return None
    
    def get_lightning_data(self, project_id: str) -> Dict[str, str]:
        """闪电般获取数据 - 修复并发问题版本"""
        # 检查停止标志
        if self._should_stop():
            print(f"⏹️ 收到停止信号，取消项目 {project_id} 的数据获取")
            return {"like_count": "0", "comment_count": "0"}

        driver = self._get_driver()
        if not driver:
            return {"like_count": "0", "comment_count": "0"}

        project_url = f"https://zhongchou.modian.com/item/{project_id}.html"

        # 🔧 修复并发问题：使用独立驱动实例，确保数据不混淆
        for attempt in range(3):
            # 每次尝试前检查停止标志
            if self._should_stop():
                print(f"⏹️ 收到停止信号，中断项目 {project_id} 第{attempt+1}次尝试")
                return {"like_count": "0", "comment_count": "0"}

            try:
                start_time = time.time()

                # 快速导航到项目页面
                driver.get(project_url)
                print(f"🌐 访问项目 {project_id} (第{attempt+1}次尝试)")

                # 检查停止标志
                if self._should_stop():
                    print(f"⏹️ 收到停止信号，中断项目 {project_id} 页面加载后")
                    return {"like_count": "0", "comment_count": "0"}

                # 立即执行滚动脚本并等待动画完成
                driver.execute_script("""
                    window.scrollTo(0, document.body.scrollHeight/2);
                    window.scrollTo(0, document.body.scrollHeight);

                    // 尝试触发数字动画完成
                    setTimeout(function() {
                        var event = new Event('scroll');
                        window.dispatchEvent(event);
                    }, 100);
                """)

                # 🔧 等待时间递增：第1次2秒，第2次4秒，第3次6秒
                wait_time = 2 + (attempt * 2)

                # 分段等待，每0.5秒检查一次停止标志
                for i in range(int(wait_time * 2)):  # 每0.5秒检查一次
                    if self._should_stop():
                        print(f"⏹️ 收到停止信号，中断项目 {project_id} 等待过程")
                        return {"like_count": "0", "comment_count": "0"}
                    time.sleep(0.5)

                # 获取数据
                data = self._quick_extract(driver)

                elapsed = (time.time() - start_time) * 1000

                # 如果获取到有效数据，或者是第3次尝试，返回结果
                if (data["like_count"] != "0" or data["comment_count"] != "0") or attempt == 2:
                    if data["like_count"] != "0" or data["comment_count"] != "0":
                        print(f"⚡ 项目 {project_id} 获取成功 (第{attempt+1}次)，看好数={data['like_count']}, 评论数={data['comment_count']}, 耗时: {elapsed:.0f}ms")
                    else:
                        print(f"⏰ 项目 {project_id} 获取完成 (第{attempt+1}次)，耗时: {elapsed:.0f}ms")
                    return data
                else:
                    print(f"🔄 项目 {project_id} 第{attempt+1}次尝试未获取到数据，继续重试...")

            except Exception as e:
                print(f"项目 {project_id} 第{attempt+1}次闪电获取失败: {e}")
                if attempt == 2:  # 最后一次尝试
                    return {"like_count": "0", "comment_count": "0"}

        return {"like_count": "0", "comment_count": "0"}
    
    def _wait_for_stable_data(self, driver, start_time) -> Dict[str, str]:
        """等待数据稳定 - 基于你的观察，第三次数据是真实的"""
        from selenium.webdriver.common.by import By

        # 🔧 基于用户观察：第三次数据是真实的，调整策略
        # 先等待足够长的时间让特效完成，然后进行稳定性检查

        initial_wait = 3.0  # 初始等待3秒，让特效基本完成
        max_wait_time = 10  # 最大等待10秒
        check_interval = 0.5  # 每500ms检查一次
        stability_checks = 2  # 需要连续2次相同才认为稳定

        # 第一阶段：等待特效完成
        self._log("info", f"⏳ 等待数字特效完成 ({initial_wait}秒)...")
        time.sleep(initial_wait)

        # 第二阶段：检查数据稳定性
        previous_values = []
        stable_count = 0

        while time.time() - start_time < max_wait_time:
            # 检查停止标志
            if self._should_stop():
                self._log("warning", "⏹️ 收到停止信号，中断数据稳定性检查")
                return previous_values[-1] if previous_values else {"like_count": "0", "comment_count": "0"}

            current_data = self._quick_extract(driver)

            # 如果获取到数据
            if current_data["like_count"] != "0" or current_data["comment_count"] != "0":
                # 检查是否与之前的值相同
                if previous_values and previous_values[-1] == current_data:
                    stable_count += 1
                    self._log("info", f"📊 数据稳定检查 {stable_count}/{stability_checks}: 看好数={current_data['like_count']}, 评论数={current_data['comment_count']}")

                    if stable_count >= stability_checks:
                        # 数据已稳定，返回结果
                        self._log("info", "✅ 数据已稳定，返回最终结果")
                        return current_data
                else:
                    # 数据发生变化，重置稳定计数
                    if previous_values:
                        self._log("info", f"🔄 数据变化: {previous_values[-1]} -> {current_data}")
                    stable_count = 0

                # 记录当前值
                previous_values.append(current_data.copy())

                # 只保留最近3次的记录
                if len(previous_values) > 3:
                    previous_values.pop(0)

            time.sleep(check_interval)

        # 超时后返回最后一次获取的数据
        final_data = previous_values[-1] if previous_values else {"like_count": "0", "comment_count": "0"}
        self._log("info", f"⏰ 等待超时，返回最后获取的数据: {final_data}")
        return final_data

    def _quick_extract(self, driver) -> Dict[str, str]:
        """快速提取数据"""
        from selenium.webdriver.common.by import By

        result = {"like_count": "0", "comment_count": "0"}

        try:
            # 快速获取点赞数
            atten_elements = driver.find_elements(By.CSS_SELECTOR, "li.atten span")
            for elem in atten_elements:
                text = elem.text.strip()
                if text and text.isdigit() and int(text) >= 0:  # 允许0值
                    result["like_count"] = text
                    break
        except:
            pass

        try:
            # 快速获取评论数
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "li.nav-comment span")
            for elem in comment_elements:
                text = elem.text.strip()
                if text and text.isdigit() and int(text) >= 0:  # 允许0值
                    result["comment_count"] = text
                    break
        except:
            pass

        return result
    
    def cleanup(self):
        """清理当前实例的驱动"""
        self._cleanup_driver()

    def __del__(self):
        """析构函数，确保驱动被清理"""
        try:
            self.cleanup()
        except:
            pass


class LightningDataManager:
    """闪电数据管理器 - 修复并发问题版本"""

    def __init__(self, config, network_utils, stop_flag=None):
        self.config = config
        self.network_utils = network_utils
        self.stop_flag = stop_flag
        self.extractor = LightningFastExtractor(config, stop_flag)  # 每个管理器独立的提取器
        self._cache = {}

    def get_lightning_data(self, project_id: str) -> Dict[str, str]:
        """获取闪电数据 - 确保每个项目获取独有数据"""
        # 检查停止标志
        if self.stop_flag and self.stop_flag.is_set():
            print(f"⏹️ 收到停止信号，取消项目 {project_id} 的闪电数据获取")
            return {"like_count": "0", "comment_count": "0"}

        # 检查缓存
        if project_id in self._cache:
            cache_time, data = self._cache[project_id]
            if time.time() - cache_time < 1800:  # 30分钟缓存
                print(f"📦 使用缓存数据: 项目 {project_id}")
                return data

        # 闪电获取
        start_time = time.time()
        data = self.extractor.get_lightning_data(project_id)
        elapsed_time = time.time() - start_time

        print(f"⚡ 项目 {project_id} 闪电数据获取完成: {elapsed_time:.2f}秒")

        # 缓存结果
        self._cache[project_id] = (time.time(), data)

        return data

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'extractor'):
            self.extractor.cleanup()

    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except:
            pass
    
    def batch_lightning_data(self, project_ids: list) -> Dict[str, Dict[str, str]]:
        """批量闪电获取"""
        results = {}

        print(f"⚡ 批量闪电获取: {len(project_ids)} 个项目")

        total_start = time.time()

        for i, project_id in enumerate(project_ids):
            # 检查停止标志
            if self.stop_flag and self.stop_flag.is_set():
                print(f"⏹️ 收到停止信号，批量获取在第 {i+1}/{len(project_ids)} 个项目时中断")
                break

            results[project_id] = self.get_lightning_data(project_id)

        total_time = time.time() - total_start
        completed_count = len(results)
        if completed_count > 0:
            avg_time = total_time / completed_count
            print(f"📊 批量闪电完成: {completed_count}/{len(project_ids)} 个项目，总耗时{total_time:.2f}秒, 平均{avg_time:.2f}秒/项目")

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
