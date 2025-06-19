# -*- coding: utf-8 -*-
"""
爬虫核心模块
优化版的摩点众筹爬虫，集成监控、验证、缓存等功能
"""

import time
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .config import SpiderConfig
from .utils import NetworkUtils, DataUtils, CacheUtils, ParserUtils
from .monitor import SpiderMonitor
from .validator import DataValidator
from .exporter import DataExporter


class AdaptiveParser:
    """智能适配解析器 - 重构版本，使用模块化的提取器"""

    def __init__(self, config: SpiderConfig, network_utils: NetworkUtils, web_monitor=None, stop_flag=None):
        self.config = config
        self.network_utils = network_utils
        self.data_utils = DataUtils()
        self.web_monitor = web_monitor
        self._stop_flag = stop_flag

        # 初始化各个提取器模块（保留必要的模块）
        from .extractors.list_extractor import ListExtractor

        self.list_extractor = ListExtractor(config, web_monitor)
        # ContentExtractor已移除 - 功能完全被API替代

        # 已删除的冗余提取器：
        # - detail_extractor (依赖动态获取，已弃用)
        # - author_extractor (API已包含作者信息)
        # - funding_extractor (API已包含金额信息)

        # 初始化各个处理器模块（简化版）
        from .processors.data_processor import DataProcessor
        from .processors.validation_processor import ValidationProcessor

        self.data_processor = DataProcessor(config, self.data_utils, web_monitor)
        self.validation_processor = ValidationProcessor(config, web_monitor)

        # 已移除的处理器（API时代不再需要）：
        # - status_processor (API直接提供准确状态)
        # - time_processor (API直接提供准确时间)

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def try_multiple_selectors(self, soup: BeautifulSoup, selectors: list, element_type: str = "element") -> any:
        """尝试多个选择器，返回第一个成功的结果"""
        for selector in selectors:
            try:
                if element_type == "text":
                    element = soup.select_one(selector)
                    if element:
                        return ParserUtils.safe_get_text(element)
                elif element_type == "attr":
                    element = soup.select_one(selector)
                    if element:
                        return element
                else:
                    result = soup.select(selector) if element_type == "all" else soup.select_one(selector)
                    if result:
                        return result
            except Exception:
                continue
        return None

    def adaptive_parse_project_list(self, html: str) -> List[Tuple[str, str, str, str, Dict[str, str]]]:
        """智能适配解析项目列表 - 使用ListExtractor模块"""
        return self.list_extractor.extract_project_list(html)

    # 这些方法已经移动到ListExtractor模块中，不再需要

    def _extract_js_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """从JavaScript代码中提取项目数据 - 使用DataProcessor模块"""
        return self.data_processor.extract_js_data(soup)
    
    def parse_project_status(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """已弃用：项目状态解析，现在使用API获取"""
        # API直接提供准确的项目状态，无需HTML解析
        return {
            "item_class": "未知情况",
            "status": "unknown",
            "is_crowdfunding": False,
            "is_success": False,
            "is_failed": False,
            "is_finished": False
        }
    
    # 基础信息解析方法已弃用 - 现在使用API获取完整数据
    # def parse_basic_info(self, soup: BeautifulSoup, project_status: Dict) -> List[Any]:
    #     """已弃用：基础信息解析，现在使用API获取"""
    #     pass

    # 时间解析方法已移动到TimeProcessor模块
    
    # 作者信息解析方法已移动到AuthorExtractor模块

    # 作者信息解析方法已完全移动到AuthorExtractor模块
    
    # 作者详细信息获取方法已移动到AuthorExtractor模块
    
    # 作者页面解析方法已移动到AuthorExtractor模块
    
    # 众筹信息解析方法已移动到FundingExtractor模块

    def _validate_extracted_data(self, money: str, percent: str, goal_money: str, sponsor_num: str):
        """验证提取的数据合理性 - 使用DataProcessor模块"""
        self.data_processor.validate_extracted_data(money, percent, goal_money, sponsor_num)

    # 众筹信息解析方法已移动到FundingExtractor模块
    
    # 项目内容解析方法已弃用 - 现在使用API获取完整数据
    # def parse_project_content(self, soup: BeautifulSoup) -> List[Any]:
    #     """已弃用：项目内容解析，现在使用API获取"""
    #     pass
    
    # 回报信息解析方法已移动到DetailExtractor模块
    
    # 单个回报解析方法已移动到DetailExtractor模块
    
    # 导航信息解析方法已移动到ContentExtractor模块

    # JavaScript导航数据提取方法已移动到ContentExtractor模块



    # 关键导航数据提取方法已移动到ContentExtractor模块



    # 项目ID提取方法已移动到ContentExtractor模块



    # 数据提取方法已移动到相应的提取器模块：
    # - _extract_update_count_only -> ContentExtractor
    # - _validate_nav_data -> ContentExtractor
    # - _parse_content_media -> DetailExtractor


class SpiderCore:
    """爬虫核心类"""

    def __init__(self, config: SpiderConfig = None, web_monitor=None, db_manager=None):
        # 🔧 优先从YAML配置文件加载配置
        self.config = config or SpiderConfig.load_from_yaml()
        self.config.create_directories()

        # Web UI监控器
        self.web_monitor = web_monitor

        # 数据库管理器（用于增量保存）
        self.db_manager = db_manager

        # 线程锁和停止标志（需要在初始化组件之前定义）
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._is_running = False

        # 初始化组件
        self.network_utils = NetworkUtils(self.config)
        self.cache_utils = CacheUtils(self.config)
        self.monitor = SpiderMonitor(self.config)
        self.validator = DataValidator(self.config)
        self.exporter = DataExporter(self.config)
        self.parser = AdaptiveParser(self.config, self.network_utils, self.web_monitor, self._stop_flag)

        # 初始化API获取器（新的互补架构）
        from spider.api_data_fetcher import ModianAPIFetcher
        self.api_fetcher = ModianAPIFetcher(self.config)

        # 数据存储
        self.projects_data = []
        self.failed_urls = []

        # 进度回调
        self._progress_callback = None

        # 🔧 动态保存配置：根据线程数调整保存间隔
        base_save_interval = getattr(self.config, 'SAVE_INTERVAL', 3)
        self.save_interval = max(1, min(base_save_interval, self.config.MAX_CONCURRENT_REQUESTS))
        self.current_task_id = None
        self.saved_count = 0  # 已保存的项目数量

        self._log("info", f"爬虫初始化完成，输出目录: {self.config.OUTPUT_DIR}")
        self._log("info", f"并发线程数: {self.config.MAX_CONCURRENT_REQUESTS}")
        self._log("info", f"请求延迟范围: {self.config.REQUEST_DELAY[0]}-{self.config.REQUEST_DELAY[1]}秒")
        self._log("info", f"动态保存间隔: 每{self.save_interval}个项目（基于{self.config.MAX_CONCURRENT_REQUESTS}线程优化）")

    # 清理方法已移除 - 现在使用轻量级API获取，无需复杂的资源管理

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self._progress_callback = callback

    def stop_crawling(self):
        """停止爬虫"""
        print("收到停止信号，正在停止爬虫...")
        self._stop_flag.set()
        self._is_running = False

    def is_stopped(self):
        """检查是否已停止"""
        return self._stop_flag.is_set()

    def is_running(self):
        """检查是否正在运行"""
        return self._is_running

    def start_crawling(self, start_page: int = 1, end_page: int = 50,
                      category: str = "all", task_id: str = None) -> bool:
        """开始爬取"""
        try:
            self._is_running = True
            self._stop_flag.clear()
            self.current_task_id = task_id
            self.saved_count = 0

            self._log("info", f"开始爬取摩点众筹数据...")
            self._log("info", f"页面范围: {start_page}-{end_page}")
            self._log("info", f"分类: {category}")
            self._log("info", f"任务ID: {task_id}")

            # 启动监控
            self.monitor.start_monitoring()

            # 爬取项目列表
            project_urls = self._crawl_project_lists(start_page, end_page, category)

            if self.is_stopped():
                self._log("warning", "爬取已被用户停止")
                # 即使被停止，也要保存已获取的数据
                self._save_remaining_data()
                return False

            if not project_urls:
                self._log("warning", "未找到任何项目URL")
                return False

            self._log("info", f"发现 {len(project_urls)} 个项目，开始详细爬取...")

            # 更新进度
            if self._progress_callback:
                total_pages = end_page - start_page + 1
                self._progress_callback(current_page=total_pages, total_pages=total_pages, total_projects=len(project_urls), completed_projects=0)

            # 爬取项目详情
            success = self._crawl_project_details(project_urls)

            # 停止监控
            self.monitor.stop_monitoring()

            # 保存剩余数据
            self._save_remaining_data()

            # 数据导出（如果有数据且未被停止）
            if self.projects_data and not self.is_stopped():
                self._export_data()

            # 打印统计信息
            self.monitor.print_stats()

            return success

        except KeyboardInterrupt:
            print("\n用户中断爬取")
            self._is_running = False
            self.monitor.stop_monitoring()
            return False
        except Exception as e:
            print(f"爬取过程中出现错误: {e}")
            self.monitor.record_error("crawling_error", str(e))
            self._is_running = False
            self.monitor.stop_monitoring()
            return False
        finally:
            self._is_running = False
            # 动态数据管理器已弃用，无需清理

    def _crawl_project_lists(self, start_page: int, end_page: int,
                           category: str) -> List[Tuple[str, str, str, str]]:
        """爬取项目列表页面"""
        project_urls = []

        for page in range(start_page, end_page + 1):
            # 检查停止标志
            if self.is_stopped():
                print("收到停止信号，停止爬取页面列表")
                break

            try:
                self._log("info", f"正在爬取第 {page} 页...")

                url = self.config.get_full_url(category, page)
                page_projects = self._parse_project_list_page(url, page)

                if page_projects:
                    project_urls.extend(page_projects)
                    self.monitor.record_page(True)
                    self._log("success", f"第 {page} 页发现 {len(page_projects)} 个项目")

                    # 更新进度
                    if self._progress_callback:
                        current_progress = page - start_page + 1
                        total_pages = end_page - start_page + 1
                        self._progress_callback(current_page=current_progress, total_pages=total_pages, total_projects=len(project_urls), completed_projects=0)
                else:
                    self.monitor.record_page(False)
                    self._log("warning", f"第 {page} 页未发现项目")

                # 检查是否需要停止
                if self.monitor.stats.consecutive_errors > self.config.MAX_CONSECUTIVE_ERRORS:
                    print("连续错误过多，停止爬取")
                    break

            except Exception as e:
                print(f"爬取第 {page} 页失败: {e}")
                self.monitor.record_error("page_crawl_error", str(e))
                self.monitor.record_page(False)

        return project_urls

    def _parse_project_list_page(self, url: str, page: int) -> List[Tuple[str, str, str, str, Dict[str, str]]]:
        """解析项目列表页面"""
        start_time = time.time()

        # 检查缓存
        cached_content = self.cache_utils.get_cache(url)
        if cached_content:
            html = cached_content
            self.monitor.record_request(True, 0, cached=True)
        else:
            # 发送请求
            html = self.network_utils.make_request(url)
            request_time = time.time() - start_time

            if html:
                self.cache_utils.set_cache(url, html)
                self.monitor.record_request(True, request_time)
            else:
                self.monitor.record_request(False, request_time)
                return []

        # 解析页面
        parse_start = time.time()
        projects = self._extract_projects_from_list(html)
        parse_time = time.time() - parse_start
        self.monitor.record_parse(parse_time)

        return projects

    def _extract_projects_from_list(self, html: str) -> List[Tuple[str, str, str, str, Dict[str, str]]]:
        """从列表页面提取项目信息 - 使用智能适配解析"""
        try:
            # 使用智能适配解析器
            projects = self.parser.adaptive_parse_project_list(html)

            # 过滤和验证项目
            filtered_projects = []
            for project_data in projects:
                try:
                    # 解包项目数据（兼容新旧格式）
                    if len(project_data) == 5:
                        project_url, project_id, project_name, project_image, list_data = project_data
                    else:
                        project_url, project_id, project_name, project_image = project_data
                        list_data = {}

                    # 检查是否跳过
                    if self._should_skip_project(project_name):
                        self.monitor.record_project("skipped")
                        continue

                    # 返回完整的5个字段，包含列表数据（特别是作者信息）
                    filtered_projects.append((project_url, project_id, project_name, project_image, list_data))
                    self.monitor.record_project("found")

                    # 记录列表数据用于调试
                    if list_data and any(v != "0" and v != "none" for v in list_data.values()):
                        author_name = list_data.get('list_author_name', 'none')
                        print(f"📊 列表数据: {project_name[:20]}... -> 作者:{author_name}, 支持者{list_data.get('list_backer_count', '0')}人")

                except Exception as e:
                    print(f"验证项目失败: {e}")
                    self.monitor.record_error("project_validation_error", str(e))
                    continue

            print(f"✅ 智能解析完成: 发现 {len(projects)} 个项目，过滤后 {len(filtered_projects)} 个")
            return filtered_projects

        except Exception as e:
            print(f"智能解析失败，使用传统解析: {e}")
            self.monitor.record_error("adaptive_parse_error", str(e))
            return self._fallback_extract_projects(html)

    def _fallback_extract_projects(self, html: str) -> List[Tuple[str, str, str, str, Dict[str, str]]]:
        """传统解析方法作为回退"""
        projects = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # 查找项目列表
            project_list = ParserUtils.safe_find(soup, 'div', {'class': 'pro_field'})
            if not project_list:
                return projects

            project_items = ParserUtils.safe_find_all(project_list, 'li')

            for item in project_items:
                try:
                    # 项目链接
                    link_tag = ParserUtils.safe_find(item, 'a', {'class': 'pro_name ga'})
                    if not link_tag:
                        continue

                    project_url = ParserUtils.safe_get_attr(link_tag, 'href')
                    if not project_url:
                        continue

                    project_url = self.data_utils.validate_url(project_url)

                    # 项目ID
                    project_id = self.data_utils.extract_project_id(project_url)
                    if not project_id:
                        continue

                    # 项目名称
                    title_tag = ParserUtils.safe_find(link_tag, 'h3', {'class': 'pro_title'})
                    project_name = ParserUtils.safe_get_text(title_tag) if title_tag else "未知项目"
                    project_name = self.data_utils.clean_text(project_name, self.config.MAX_TITLE_LENGTH)

                    # 检查是否跳过
                    if self._should_skip_project(project_name):
                        self.monitor.record_project("skipped")
                        continue

                    # 项目图片
                    img_tag = ParserUtils.safe_find(item, 'img')
                    project_image = ParserUtils.safe_get_attr(img_tag, 'src') if img_tag else "none"
                    project_image = self.data_utils.validate_url(project_image)

                    # 创建空的列表数据（fallback方法没有额外数据）
                    list_data = {
                        "list_backer_money": "0",
                        "list_rate": "0",
                        "list_backer_count": "0",
                        "list_author_name": "none"
                    }
                    projects.append((project_url, project_id, project_name, project_image, list_data))
                    self.monitor.record_project("found")

                except Exception as e:
                    print(f"解析项目项失败: {e}")
                    continue

        except Exception as e:
            print(f"解析项目列表失败: {e}")
            self.monitor.record_error("parse_list_error", str(e))

        return projects

    def _should_skip_project(self, project_name: str) -> bool:
        """检查是否应该跳过项目"""
        if not project_name or len(project_name) < self.config.MIN_TITLE_LENGTH:
            return True

        for keyword in self.config.SKIP_KEYWORDS:
            if keyword in project_name:
                return True

        return False

    def _crawl_project_details(self, project_urls: List[Tuple[str, str, str, str, Dict[str, str]]]) -> bool:
        """爬取项目详情（增强进度显示版本）"""
        if not project_urls:
            return False

        total_projects = len(project_urls)
        self._log("info", f"开始并发爬取 {total_projects} 个项目详情，并发数: {self.config.MAX_CONCURRENT_REQUESTS}")

        # 使用线程池并发爬取
        with ThreadPoolExecutor(max_workers=self.config.MAX_CONCURRENT_REQUESTS) as executor:
            # 提交任务
            future_to_project = {
                executor.submit(self._crawl_single_project, i, project_info): (i, project_info)
                for i, project_info in enumerate(project_urls)
            }

            # 处理结果
            completed = 0
            for future in as_completed(future_to_project):
                # 在处理每个结果前检查停止标志
                if self.is_stopped():
                    self._log("warning", "收到停止信号，正在保存已处理的数据...")
                    # 取消剩余的任务
                    for remaining_future in future_to_project:
                        if not remaining_future.done():
                            remaining_future.cancel()
                    self._save_remaining_data()
                    break

                _, project_info = future_to_project[future]

                try:
                    result = future.result(timeout=1)  # 添加超时，避免长时间阻塞
                    if result:
                        with self._lock:
                            self.projects_data.append(result)
                        self.monitor.record_project("processed")
                        self._log("success", f"项目 {project_info[2]} 处理成功")

                        # 🔧 增量保存：每处理完指定数量的项目就保存一次
                        if len(self.projects_data) % self.save_interval == 0:
                            self._save_incremental_data()
                    else:
                        self.monitor.record_project("failed")
                        self.failed_urls.append(project_info[0])
                        self._log("warning", f"项目 {project_info[2]} 处理失败")

                except TimeoutError:
                    self._log("warning", f"项目 {project_info[2]} 处理超时")
                    self.monitor.record_project("failed")
                    self.failed_urls.append(project_info[0])
                except Exception as e:
                    self._log("error", f"处理项目失败 {project_info[2]}: {e}")
                    self.monitor.record_error("project_process_error", str(e))
                    self.monitor.record_project("failed")
                    self.failed_urls.append(project_info[0])

                completed += 1

                # 更新进度到Web UI
                if self._progress_callback:
                    # 计算总体进度：页面爬取 + 项目详情爬取
                    project_progress = (completed / total_projects) * 100
                    self._progress_callback(current_page=0, total_pages=0, total_projects=total_projects, completed_projects=completed, project_progress=project_progress)

                # 定期输出进度
                if completed % 5 == 0 or completed == total_projects:
                    progress_percent = (completed / total_projects) * 100
                    self._log("info", f"项目详情进度: {completed}/{total_projects} ({progress_percent:.1f}%)")

            # 如果被停止，强制关闭线程池
            if self.is_stopped():
                self._log("warning", "强制关闭线程池...")
                executor.shutdown(wait=False)

        self._log("info", f"项目详情爬取完成，成功: {len(self.projects_data)}, 失败: {len(self.failed_urls)}")
        return len(self.projects_data) > 0

    def _crawl_single_project(self, index: int, project_info: Tuple[str, str, str, str, Dict[str, str]]) -> Optional[List[Any]]:
        """爬取单个项目详情"""
        # 解包项目信息（支持5个字段）
        if len(project_info) == 5:
            project_url, project_id, project_name, project_image, list_data = project_info
        else:
            project_url, project_id, project_name, project_image = project_info
            list_data = {}

        # 检查停止标志
        if self.is_stopped():
            self._log("warning", f"⏹️ 收到停止信号，跳过项目 {project_name}")
            return None

        try:
            start_time = time.time()

            # 检查缓存
            cached_content = self.cache_utils.get_cache(project_url)
            if cached_content:
                html = cached_content
                self.monitor.record_request(True, 0, cached=True)
            else:
                # 发送请求
                html = self.network_utils.make_request(project_url)
                request_time = time.time() - start_time

                if html:
                    self.cache_utils.set_cache(project_url, html)
                    self.monitor.record_request(True, request_time)
                else:
                    self.monitor.record_request(False, request_time)
                    return None

            # 通过API获取项目完整数据（新的互补架构）
            api_start = time.time()
            project_data = self._get_project_data_via_api(index + 1, project_url, project_id, project_name, project_image, list_data)
            api_time = time.time() - api_start
            self.monitor.record_parse(api_time)

            return project_data

        except Exception as e:
            print(f"爬取项目详情失败 {project_name}: {e}")
            self.monitor.record_error("project_detail_error", str(e))
            return None

    def _get_project_data_via_api(self, index: int, project_url: str,
                                 project_id: str, project_name: str, project_image: str, list_data: Dict[str, str] = None) -> List[Any]:
        """通过API获取项目完整数据 - 新的互补架构"""
        try:
            # 使用API获取完整项目数据
            api_data = self.api_fetcher.get_project_data(project_id)

            if not api_data or api_data.get("like_count", "0") == "0":
                self._log("warning", f"项目 {project_id} API获取失败，使用基础数据")
                # 返回基础数据
                return self._create_basic_project_data(index, project_url, project_id, project_name, project_image, list_data)

            # 转换API数据为数据库格式，使用列表数据补充作者信息
            project_data = self._convert_api_to_db_format(api_data, index, project_url, project_id, project_name, project_image, list_data)

            self._log("info", f"✅ 项目 {project_id} API数据获取成功")
            return project_data

        except Exception as e:
            self._log("error", f"项目 {project_id} API获取异常: {e}")
            return self._create_basic_project_data(index, project_url, project_id, project_name, project_image, list_data)

    def _convert_api_to_db_format(self, api_data: dict, index: int, project_url: str,
                                 project_id: str, project_name: str, project_image: str, list_data: Dict[str, str] = None) -> List[Any]:
        """将API数据转换为数据库格式，使用列表数据补充作者信息"""
        from spider.config import FieldMapping

        # 获取作者信息：优先使用列表数据，API数据作为备选
        if list_data and list_data.get("list_author_name") and list_data.get("list_author_name") != "none":
            author_name = list_data.get("list_author_name", "")
        else:
            author_name = api_data.get("author_name", "")

        # 获取作者头像：优先使用列表数据，然后API数据，最后默认头像
        author_image = ""
        if list_data and list_data.get("list_author_avatar") and list_data.get("list_author_avatar") != "none":
            author_image = list_data.get("list_author_avatar", "")
        else:
            author_image = api_data.get("author_image", "")

        # 如果仍然没有头像，使用默认头像
        if not author_image:
            author_image = "https://s.moimg.net/new/images/headPic.png"

        # 按照数据库字段顺序构建数据
        project_data = [
            index,                                          # 序号
            project_url,                                    # 项目link
            project_id,                                     # 项目6位id
            project_name,                                   # 项目名称
            project_image,                                  # 项目图
            api_data.get("start_time", ""),                # 开始时间
            api_data.get("end_time", ""),                  # 结束时间
            api_data.get("project_status", ""),           # 项目结果
            api_data.get("author_link", ""),               # 用户主页(链接)
            author_image,                                  # 用户头像(图片链接)
            api_data.get("category", ""),                  # 分类
            author_name,                                   # 用户名（优先使用列表数据）
            "",                                            # 用户UID(data-username) - API无此字段
            api_data.get("raised_amount", 0),              # 已筹金额
            api_data.get("completion_rate", 0),            # 百分比
            api_data.get("target_amount", 0),              # 目标金额
            api_data.get("backer_count", 0),               # 支持者(数量)
            "",                                            # 真实用户ID(链接提取) - 可从author_link提取
            "",                                            # 作者页-粉丝数 - API无此字段
            "",                                            # 作者页-关注数 - API无此字段
            "",                                            # 作者页-获赞数 - API无此字段
            "",                                            # 作者页-详情 - API无此字段
            "",                                            # 作者页-其他信息 - API无此字段
            "",                                            # 作者页-主页确认 - API无此字段
            str(api_data.get("rewards_data", [])),         # 回报列表信息(字符串)
            len(api_data.get("rewards_data", [])),         # 回报列表项目数
            api_data.get("update_count", 0),               # 项目更新数
            api_data.get("comment_count", 0),              # 评论数
            api_data.get("like_count", 0),                 # 看好数
            0,                                             # 项目详情-图片数量 - API无此字段
            "[]",                                          # 项目详情-图片(列表字符串) - API无此字段
            0,                                             # 项目详情-视频数量 - API无此字段
            "[]",                                          # 项目详情-视频(列表字符串) - API无此字段
        ]

        # 确保字段数量正确
        expected_length = len(FieldMapping.EXCEL_COLUMNS)
        while len(project_data) < expected_length:
            project_data.append("")

        return project_data[:expected_length]

    def _create_basic_project_data(self, index: int, project_url: str,
                                  project_id: str, project_name: str, project_image: str, list_data: Dict[str, str] = None) -> List[Any]:
        """创建基础项目数据（API获取失败时的后备方案），使用列表数据补充"""
        from spider.config import FieldMapping
        expected_length = len(FieldMapping.EXCEL_COLUMNS)

        # 获取作者信息
        author_name = ""
        if list_data and list_data.get("list_author_name") and list_data.get("list_author_name") != "none":
            author_name = list_data.get("list_author_name", "")

        # 获取作者头像：优先使用列表数据，否则使用默认头像
        author_avatar = ""
        if list_data and list_data.get("list_author_avatar") and list_data.get("list_author_avatar") != "none":
            author_avatar = list_data.get("list_author_avatar", "")
        else:
            author_avatar = "https://s.moimg.net/new/images/headPic.png"

        # 创建基础数据，在第11位（用户名）和第9位（用户头像）填入作者信息
        basic_data = [index, project_url, project_id, project_name, project_image]

        # 填充剩余字段为空值，但在特定位置填入作者信息
        while len(basic_data) < expected_length:
            if len(basic_data) == 9:  # 用户头像字段位置
                basic_data.append(author_avatar)
            elif len(basic_data) == 11:  # 用户名字段位置
                basic_data.append(author_name)
            else:
                basic_data.append("")

        return basic_data

    def _export_data(self):
        """导出数据（移除验证步骤，API数据无需验证）"""
        print("开始导出数据...")

        try:
            # 导出Excel
            excel_file = self.exporter.export_to_excel(self.projects_data, self.config.EXCEL_FILENAME)

            # 导出JSON
            json_file = self.exporter.export_to_json(self.projects_data, self.config.JSON_FILENAME)

            # 导出摘要报告
            stats = self.monitor.get_current_stats()
            summary_file = self.exporter.export_summary_report(self.projects_data, stats)

            # 保存统计报告到统一的报告目录
            stats_file = f"data/reports/stats/spider_stats_{time.strftime('%Y%m%d_%H%M%S')}.json"
            self.monitor.save_stats(stats_file)

            print(f"数据导出完成:")
            print(f"  Excel文件: {excel_file}")
            print(f"  JSON文件: {json_file}")
            print(f"  摘要报告: {summary_file}")
            print(f"  统计报告: {stats_file}")

        except Exception as e:
            print(f"数据导出失败: {e}")
            self.monitor.record_error("export_error", str(e))

    def get_crawl_stats(self) -> Dict[str, Any]:
        """获取爬取统计信息"""
        stats = self.monitor.get_current_stats()
        stats.update({
            "projects_data_count": len(self.projects_data),
            "failed_urls_count": len(self.failed_urls),
            "cache_stats": self.cache_utils.get_cache_stats(),
            "network_stats": self.network_utils.get_request_stats(),
            "export_stats": self.exporter.get_export_stats()
        })
        return stats

    def retry_failed_projects(self) -> bool:
        """重试失败的项目"""
        if not self.failed_urls:
            print("没有失败的项目需要重试")
            return True

        print(f"开始重试 {len(self.failed_urls)} 个失败的项目...")

        # 重新构造项目信息
        retry_projects = []
        for url in self.failed_urls:
            project_id = self.data_utils.extract_project_id(url)
            retry_projects.append((url, project_id, "重试项目", "none"))

        # 清空失败列表
        self.failed_urls.clear()

        # 重新爬取
        return self._crawl_project_details(retry_projects)

    def clear_cache(self):
        """清空缓存"""
        self.cache_utils.clear_cache()

    def _save_incremental_data(self):
        """增量保存数据到数据库"""
        if not self.db_manager or not self.projects_data:
            return

        try:
            # 获取未保存的数据
            unsaved_data = self.projects_data[self.saved_count:]

            if unsaved_data:
                # 保存到数据库
                saved_count = self.db_manager.save_projects(unsaved_data, self.current_task_id)
                self.saved_count += saved_count

                self._log("success", f"📦 增量保存: 本次保存 {saved_count} 条，累计已保存 {self.saved_count} 条到数据库")

                # 🔧 修复：更新Web监控器统计（支持定时任务监控器）
                if self.web_monitor:
                    self.web_monitor.update_stats(
                        projects_processed=self.saved_count,
                        projects_found=len(self.projects_data)
                    )

                    # 🔧 修复：如果是定时任务监控器，调用专门的方法
                    if hasattr(self.web_monitor, 'increment_saved_count'):
                        # 这是定时任务监控器，需要特殊处理
                        self.web_monitor.set_final_stats(
                            projects_found=len(self.projects_data),
                            projects_saved=self.saved_count
                        )

        except Exception as e:
            self._log("error", f"增量保存失败: {e}")

    def _save_remaining_data(self):
        """保存剩余的未保存数据"""
        if not self.db_manager or not self.projects_data:
            return

        try:
            # 获取未保存的数据
            unsaved_data = self.projects_data[self.saved_count:]

            if unsaved_data:
                # 保存到数据库
                saved_count = self.db_manager.save_projects(unsaved_data, self.current_task_id)
                self.saved_count += saved_count

                self._log("success", f"🔄 最终检查: 补充保存 {saved_count} 条遗漏数据，累计已保存 {self.saved_count} 条到数据库")

                # 🔧 修复：更新Web监控器统计（支持定时任务监控器）
                if self.web_monitor:
                    self.web_monitor.update_stats(
                        projects_processed=self.saved_count,
                        projects_found=len(self.projects_data)
                    )

                    # 🔧 修复：如果是定时任务监控器，调用专门的方法
                    if hasattr(self.web_monitor, 'set_final_stats'):
                        # 这是定时任务监控器，需要特殊处理
                        # 🔧 修复：统计信息应该显示处理的项目数，不是保存的项目数
                        processed_count = len(self.projects_data)  # 实际处理的项目数
                        self.web_monitor.set_final_stats(
                            projects_found=processed_count,
                            projects_saved=processed_count  # 对于定时任务，处理即为保存
                        )
                        print(f"📊 定时任务统计更新: 处理{processed_count}个项目，数据库新增{self.saved_count}个")
            else:
                self._log("success", f"✅ 数据保存完整性检查: 所有数据已通过增量保存机制保存完毕，累计 {self.saved_count} 条")

        except Exception as e:
            self._log("error", f"最终保存失败: {e}")

    def save_progress(self):
        """保存进度"""
        if self.projects_data:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            progress_file = f"{self.config.OUTPUT_DIR}/progress_{timestamp}.json"

            progress_data = {
                "timestamp": timestamp,
                "projects_count": len(self.projects_data),
                "saved_count": self.saved_count,
                "failed_urls": self.failed_urls,
                "stats": self.monitor.get_current_stats()
            }

            try:
                import json
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, ensure_ascii=False, indent=2)
                print(f"进度已保存到: {progress_file}")
            except Exception as e:
                print(f"保存进度失败: {e}")
