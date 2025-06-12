# -*- coding: utf-8 -*-
"""
爬虫自动化测试
包含单元测试、集成测试和性能测试
"""

import unittest
import time
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from spider import SpiderConfig, SpiderCore, NetworkUtils, DataUtils, CacheUtils
from spider.monitor import SpiderMonitor
from spider.validator import DataValidator
from spider.exporter import DataExporter


class TestSpiderConfig(unittest.TestCase):
    """测试爬虫配置"""
    
    def setUp(self):
        self.config = SpiderConfig()
    
    def test_config_initialization(self):
        """测试配置初始化"""
        self.assertIsNotNone(self.config.BASE_URL)
        self.assertIsNotNone(self.config.REQUEST_HEADERS)
        self.assertGreater(self.config.MAX_RETRIES, 0)
        self.assertGreater(self.config.MAX_CONCURRENT_REQUESTS, 0)
    
    def test_get_full_url(self):
        """测试URL生成"""
        url = self.config.get_full_url("all", 1)
        self.assertIn("zhongchou.modian.com", url)
        self.assertIn("/all/top_time/all/1", url)
    
    def test_get_api_url(self):
        """测试API URL生成"""
        api_url = self.config.get_api_url("/test")
        self.assertIn("apim.modian.com", api_url)
        self.assertIn("/test", api_url)
    
    def test_create_directories(self):
        """测试目录创建"""
        self.config.create_directories()
        self.assertTrue(os.path.exists(self.config.OUTPUT_DIR))
        self.assertTrue(os.path.exists(self.config.CACHE_DIR))


class TestNetworkUtils(unittest.TestCase):
    """测试网络工具"""
    
    def setUp(self):
        self.config = SpiderConfig()
        self.network_utils = NetworkUtils(self.config)
    
    def test_get_headers(self):
        """测试请求头生成"""
        headers = self.network_utils.get_headers("desktop")
        self.assertIn("User-Agent", headers)
        
        mobile_headers = self.network_utils.get_headers("mobile")
        self.assertIn("User-Agent", mobile_headers)
        self.assertNotEqual(headers["User-Agent"], mobile_headers["User-Agent"])
    
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """测试成功的网络请求"""
        mock_response = Mock()
        mock_response.text = "<html>test</html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.network_utils.make_request("http://test.com")
        self.assertEqual(result, "<html>test</html>")
    
    @patch('requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """测试失败的网络请求"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.network_utils.make_request("http://test.com")
        self.assertIsNone(result)
    
    def test_request_stats(self):
        """测试请求统计"""
        stats = self.network_utils.get_request_stats()
        self.assertIn("total_requests", stats)
        self.assertIn("last_request_time", stats)


class TestDataUtils(unittest.TestCase):
    """测试数据工具"""
    
    def test_extract_number(self):
        """测试数字提取"""
        self.assertEqual(DataUtils.extract_number("123"), "123")
        self.assertEqual(DataUtils.extract_number("￥1,234.56"), "1234.56")
        self.assertEqual(DataUtils.extract_number("abc"), "0")
        self.assertEqual(DataUtils.extract_number(""), "0")
    
    def test_extract_percentage(self):
        """测试百分比提取"""
        self.assertEqual(DataUtils.extract_percentage("150%"), "150")
        self.assertEqual(DataUtils.extract_percentage("50.5%"), "50.5")
        self.assertEqual(DataUtils.extract_percentage("abc"), "0")
    
    def test_extract_project_id(self):
        """测试项目ID提取"""
        url = "https://zhongchou.modian.com/item/123456.html"
        self.assertEqual(DataUtils.extract_project_id(url), "123456")
        
        invalid_url = "https://example.com/test"
        self.assertEqual(DataUtils.extract_project_id(invalid_url), "")
    
    def test_extract_user_id(self):
        """测试用户ID提取"""
        url = "https://me.modian.com/u/detail?uid=789"
        self.assertEqual(DataUtils.extract_user_id(url), "789")
        
        invalid_url = "https://example.com/user"
        self.assertEqual(DataUtils.extract_user_id(invalid_url), "")
    
    def test_clean_text(self):
        """测试文本清理"""
        text = "  测试   文本  \n\t  "
        cleaned = DataUtils.clean_text(text)
        self.assertEqual(cleaned, "测试 文本")
        
        long_text = "a" * 100
        cleaned_long = DataUtils.clean_text(long_text, 50)
        self.assertEqual(len(cleaned_long), 53)  # 50 + "..."
    
    def test_validate_url(self):
        """测试URL验证"""
        self.assertEqual(DataUtils.validate_url("/test"), "https://zhongchou.modian.com/test")
        self.assertEqual(DataUtils.validate_url("example.com"), "https://example.com")
        self.assertEqual(DataUtils.validate_url("https://test.com"), "https://test.com")
        self.assertEqual(DataUtils.validate_url("none"), "none")
    
    def test_format_money(self):
        """测试金额格式化"""
        self.assertEqual(DataUtils.format_money("￥1,234.56"), "1234.56")
        self.assertEqual(DataUtils.format_money("1000"), "1000.0")
        self.assertEqual(DataUtils.format_money("abc"), "0")


class TestCacheUtils(unittest.TestCase):
    """测试缓存工具"""
    
    def setUp(self):
        self.config = SpiderConfig()
        self.config.CACHE_DIR = "test_cache"
        self.cache_utils = CacheUtils(self.config)
    
    def tearDown(self):
        """清理测试缓存"""
        self.cache_utils.clear_cache()
        try:
            os.rmdir(self.config.CACHE_DIR)
        except OSError:
            pass
    
    def test_cache_operations(self):
        """测试缓存操作"""
        url = "http://test.com"
        content = "<html>test content</html>"
        
        # 测试设置缓存
        self.cache_utils.set_cache(url, content)
        
        # 测试获取缓存
        cached_content = self.cache_utils.get_cache(url)
        self.assertEqual(cached_content, content)
        
        # 测试缓存统计
        stats = self.cache_utils.get_cache_stats()
        self.assertGreater(stats["cache_count"], 0)


class TestSpiderMonitor(unittest.TestCase):
    """测试爬虫监控"""
    
    def setUp(self):
        self.config = SpiderConfig()
        self.monitor = SpiderMonitor(self.config)
    
    def test_monitor_initialization(self):
        """测试监控器初始化"""
        self.assertIsNotNone(self.monitor.stats)
        self.assertEqual(self.monitor.stats.total_requests, 0)
    
    def test_record_request(self):
        """测试请求记录"""
        self.monitor.record_request(True, 1.5)
        self.assertEqual(self.monitor.stats.total_requests, 1)
        self.assertEqual(self.monitor.stats.successful_requests, 1)
        
        self.monitor.record_request(False, 2.0)
        self.assertEqual(self.monitor.stats.total_requests, 2)
        self.assertEqual(self.monitor.stats.failed_requests, 1)
    
    def test_record_project(self):
        """测试项目记录"""
        self.monitor.record_project("found")
        self.assertEqual(self.monitor.stats.projects_found, 1)
        
        self.monitor.record_project("processed")
        self.assertEqual(self.monitor.stats.projects_processed, 1)
    
    def test_record_error(self):
        """测试错误记录"""
        self.monitor.record_error("test_error", "Test error message")
        self.assertIn("test_error", self.monitor.stats.error_counts)
        self.assertEqual(self.monitor.stats.error_counts["test_error"], 1)
    
    def test_get_stats(self):
        """测试统计信息获取"""
        stats = self.monitor.get_current_stats()
        self.assertIn("total_requests", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("error_rate", stats)


class TestDataValidator(unittest.TestCase):
    """测试数据验证器"""
    
    def setUp(self):
        self.config = SpiderConfig()
        self.validator = DataValidator(self.config)
    
    def test_validate_valid_project(self):
        """测试有效项目验证"""
        valid_project = [
            1, "https://zhongchou.modian.com/item/123456.html", "123456", "测试项目", "image.jpg",
            "2024-01-01", "2024-02-01", "众筹成功",
            "https://me.modian.com/u/detail?uid=789", "avatar.jpg", "桌游", "测试用户", "test_user",
            "50000", "150", "30000", "100",
            "789", "1000", "200", "500", "{}", "{}", "https://me.modian.com/u/detail?uid=789",
            "[]", "5", "10", "20", "100", "50", "10", "[]", "2", "[]"
        ]
        
        result = self.validator.validate_project_data(valid_project)
        self.assertTrue(result.is_valid)
        self.assertGreater(result.score, 80)
    
    def test_validate_invalid_project(self):
        """测试无效项目验证"""
        invalid_project = [
            "", "", "", "", "",  # 缺少必需字段
            "", "", "",
            "", "", "", "", "",
            "", "", "", "",
            "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", ""
        ]
        
        result = self.validator.validate_project_data(invalid_project)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_batch_validation(self):
        """测试批量验证"""
        projects = [
            ["1", "https://zhongchou.modian.com/item/123.html", "123", "项目1"] + [""] * 30,
            ["2", "https://zhongchou.modian.com/item/456.html", "456", "项目2"] + [""] * 30
        ]
        
        results = self.validator.validate_batch(projects)
        self.assertEqual(results["total_projects"], 2)
        self.assertIn("validation_rate", results)


class TestDataExporter(unittest.TestCase):
    """测试数据导出器"""
    
    def setUp(self):
        self.config = SpiderConfig()
        self.config.OUTPUT_DIR = "test_output"
        self.exporter = DataExporter(self.config)
    
    def tearDown(self):
        """清理测试文件"""
        import shutil
        try:
            shutil.rmtree(self.config.OUTPUT_DIR)
        except OSError:
            pass
    
    def test_export_to_json(self):
        """测试JSON导出"""
        test_data = [
            [1, "https://test.com", "123", "测试项目"] + [""] * 30
        ]
        
        json_file = self.exporter.export_to_json(test_data, "test.json")
        self.assertTrue(os.path.exists(json_file))
    
    def test_export_stats(self):
        """测试导出统计"""
        stats = self.exporter.get_export_stats()
        self.assertIn("output_dir", stats)


class TestSpiderIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.config = SpiderConfig()
        self.config.OUTPUT_DIR = "test_integration"
        # 设置较小的测试范围
        self.config.DEFAULT_PAGE_RANGE = (1, 2)
        self.config.MAX_CONCURRENT_REQUESTS = 2
        
    def tearDown(self):
        """清理测试文件"""
        import shutil
        try:
            shutil.rmtree(self.config.OUTPUT_DIR)
        except OSError:
            pass
    
    @patch('spider.core.NetworkUtils.make_request')
    def test_spider_core_initialization(self, mock_request):
        """测试爬虫核心初始化"""
        spider = SpiderCore(self.config)
        self.assertIsNotNone(spider.network_utils)
        self.assertIsNotNone(spider.monitor)
        self.assertIsNotNone(spider.validator)
        self.assertIsNotNone(spider.exporter)
    
    @patch('spider.core.NetworkUtils.make_request')
    def test_mock_crawling_process(self, mock_request):
        """测试模拟爬取流程"""
        # 模拟列表页面响应
        list_html = '''
        <div class="pro_field">
            <li>
                <a class="pro_name ga" href="/item/123456.html">
                    <h3 class="pro_title">测试桌游项目</h3>
                </a>
                <img src="test.jpg">
            </li>
        </div>
        '''
        
        # 模拟详情页面响应
        detail_html = '''
        <div class="buttons clearfloat">
            <a>众筹成功</a>
        </div>
        <div class="sponsor-info clearfix">
            <a class="sponsor-link" href="/u/detail?uid=789">
                <span class="name" data-nickname="测试用户" data-username="test_user">测试用户</span>
            </a>
            <img class="sponsor-image" src="avatar.jpg">
            <span>项目类别：桌游</span>
        </div>
        <div class="center">
            <span backer_money="true">50000</span>
            <span rate="true">150%</span>
            <span class="goal-money">目标金额￥30000</span>
            <span backer_count="100">100人支持</span>
        </div>
        '''
        
        # 设置mock返回值
        mock_request.side_effect = [list_html, detail_html]
        
        spider = SpiderCore(self.config)
        
        # 测试项目列表解析
        projects = spider._extract_projects_from_list(list_html)
        self.assertGreater(len(projects), 0)
        
        # 测试项目详情解析
        if projects:
            project_url, project_id, project_name, project_image = projects[0]
            project_data = spider._parse_project_detail(detail_html, 1, project_url, project_id, project_name, project_image)
            self.assertIsNotNone(project_data)
            self.assertGreater(len(project_data), 10)


def run_performance_test():
    """性能测试"""
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    
    config = SpiderConfig()
    
    # 测试网络工具性能
    network_utils = NetworkUtils(config)
    start_time = time.time()
    
    # 模拟100次请求头生成
    for _ in range(100):
        network_utils.get_headers("desktop")
    
    headers_time = time.time() - start_time
    print(f"生成100个请求头耗时: {headers_time:.3f}秒")
    
    # 测试数据工具性能
    start_time = time.time()
    
    # 模拟1000次数据处理
    for i in range(1000):
        DataUtils.extract_number(f"￥{i},123.45")
        DataUtils.clean_text(f"  测试文本 {i}  ")
    
    data_time = time.time() - start_time
    print(f"处理1000次数据耗时: {data_time:.3f}秒")
    
    # 测试缓存性能
    cache_utils = CacheUtils(config)
    start_time = time.time()
    
    # 模拟100次缓存操作
    for i in range(100):
        cache_utils.set_cache(f"http://test{i}.com", f"content{i}")
        cache_utils.get_cache(f"http://test{i}.com")
    
    cache_time = time.time() - start_time
    print(f"100次缓存操作耗时: {cache_time:.3f}秒")
    
    # 清理测试缓存
    cache_utils.clear_cache()
    
    print("性能测试完成")


if __name__ == "__main__":
    # 运行单元测试
    print("开始运行爬虫自动化测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestSpiderConfig,
        TestNetworkUtils, 
        TestDataUtils,
        TestCacheUtils,
        TestSpiderMonitor,
        TestDataValidator,
        TestDataExporter,
        TestSpiderIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 运行性能测试
    run_performance_test()
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print("="*60)
