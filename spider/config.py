# -*- coding: utf-8 -*-
"""
爬虫配置文件
集中管理所有爬虫相关的配置参数
"""

import os
from dataclasses import dataclass
from typing import Tuple, Dict


@dataclass
class SpiderConfig:
    """爬虫配置类"""
    
    # 基础配置
    BASE_URL = "https://zhongchou.modian.com"
    API_BASE_URL = "https://apim.modian.com"
    
    # 目标URL配置
    CATEGORY_URLS = {
        # 基础分类
        "all": "/all/top_time/all/",
        "success": "/all/top_time/success/",
        "going": "/all/top_time/going/",
        "preheat": "/all/top_time/preheat/",
        "idea": "/all/top_time/idea/",

        # 具体项目分类（基于摩点网站实际分类）
        "games": "/games/top_time/all/",
        "publishing": "/publishing/top_time/all/",
        "tablegames": "/tablegames/top_time/all/",
        "toys": "/toys/top_time/all/",
        "cards": "/cards/top_time/all/",
        "technology": "/technology/top_time/all/",
        "film-video": "/film-video/top_time/all/",
        "music": "/music/top_time/all/",
        "activities": "/activities/top_time/all/",
        "design": "/design/top_time/all/",
        "curio": "/curio/top_time/all/",
        "home": "/home/top_time/all/",
        "food": "/food/top_time/all/",
        "comics": "/comics/top_time/all/",
        "charity": "/charity/top_time/all/",
        "animals": "/animals/top_time/all/",
        "wishes": "/wishes/top_time/all/",
        "others": "/others/top_time/all/"
    }
    
    # 请求配置
    REQUEST_HEADERS = {
        "desktop": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        "mobile": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://m.modian.com",
            "Referer": "https://m.modian.com/"
        }
    }
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = (0.5, 2.0)  # 重试延迟范围（秒）
    TIMEOUT_RANGE = (10, 30)  # 请求超时范围（秒）
    
    # 并发配置
    MAX_CONCURRENT_REQUESTS = 5
    REQUEST_DELAY = (1.0, 3.0)  # 请求间隔（秒）
    BATCH_SIZE = 10  # 批处理大小
    SAVE_INTERVAL = 3  # 增量保存间隔（每N个项目保存一次）

    # 后台定时任务配置
    ENABLE_SCHEDULED_TASKS = True
    MIN_SCHEDULE_INTERVAL = 5  # 最小调度间隔（秒）
    DEFAULT_SCHEDULE_INTERVAL = 3600  # 默认调度间隔（1小时）
    MAX_CONCURRENT_SCHEDULED_TASKS = 3  # 最大并发定时任务数
    
    # 数据存储配置
    OUTPUT_DIR = "data/raw"
    EXCEL_FILENAME = "摩点众筹-主要信息.xls"
    JSON_FILENAME = "modian_projects.json"
    LOG_FILENAME = "spider.log"

    # 缓存配置
    ENABLE_CACHE = True
    CACHE_DIR = "data/cache"
    CACHE_EXPIRE_HOURS = 24
    
    # 过滤配置
    SKIP_KEYWORDS = ["可汗游戏大会", "测试项目"]
    MIN_TITLE_LENGTH = 2
    MAX_TITLE_LENGTH = 200
    
    # 页面配置
    DEFAULT_PAGE_RANGE = (1, 50)  # 默认爬取页面范围
    MAX_PAGE_RANGE = (1, 1000)   # 最大页面范围
    
    # 监控配置
    ENABLE_MONITORING = True
    STATS_UPDATE_INTERVAL = 10  # 统计信息更新间隔（秒）
    
    # 错误处理配置
    MAX_CONSECUTIVE_ERRORS = 5
    ERROR_THRESHOLD_PERCENTAGE = 20  # 错误率阈值
    
    # 代理配置（可选）
    ENABLE_PROXY = False
    PROXY_LIST = []  # 代理服务器列表
    
    # 数据验证配置
    REQUIRED_FIELDS = [
        "项目名称", "项目link", "项目6位id", "分类",
        "已筹金额", "目标金额", "支持者(数量)"
    ]

    # API数据获取配置
    API_TIMEOUT = 10        # API请求超时时间（秒）
    API_RETRY_COUNT = 3     # API请求重试次数
    API_CACHE_MINUTES = 30  # API数据缓存时间（分钟）
    
    @classmethod
    def get_full_url(cls, category: str, page: int = 1) -> str:
        """获取完整的URL"""
        if category not in cls.CATEGORY_URLS:
            category = "all"
        return f"{cls.BASE_URL}{cls.CATEGORY_URLS[category]}{page}"
    
    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """获取API URL"""
        # 确保endpoint以/开头
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return f"{cls.API_BASE_URL}{endpoint}"

    @classmethod
    def load_from_yaml(cls, yaml_path: str = "config/spider_config.yaml"):
        """从YAML配置文件加载配置，覆盖默认值"""
        try:
            import yaml
            import os

            if not os.path.exists(yaml_path):
                print(f"⚠️ 配置文件不存在: {yaml_path}，使用默认配置")
                return cls()

            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # 创建配置实例
            instance = cls()

            # 更新爬虫设置
            spider_settings = config_data.get('spider_settings', {})
            if 'max_concurrent_requests' in spider_settings:
                instance.MAX_CONCURRENT_REQUESTS = spider_settings['max_concurrent_requests']
            if 'request_delay' in spider_settings:
                instance.REQUEST_DELAY = tuple(spider_settings['request_delay'])
            if 'save_interval' in spider_settings:
                instance.SAVE_INTERVAL = spider_settings['save_interval']
            if 'max_retries' in spider_settings:
                instance.MAX_RETRIES = spider_settings['max_retries']
            if 'request_timeout' in spider_settings:
                instance.TIMEOUT_RANGE = tuple(spider_settings['request_timeout'])
            if 'retry_delay' in spider_settings:
                instance.RETRY_DELAY = (spider_settings['retry_delay'], spider_settings['retry_delay'] * 2)

            # 更新输出设置
            output_settings = config_data.get('output_settings', {})
            if 'output_dir' in output_settings:
                instance.OUTPUT_DIR = output_settings['output_dir']
            if 'cache_dir' in output_settings:
                instance.CACHE_DIR = output_settings['cache_dir']
            if 'excel_filename' in output_settings:
                instance.EXCEL_FILENAME = output_settings['excel_filename']

            print(f"✅ 已从 {yaml_path} 加载配置")
            print(f"   - 并发数: {instance.MAX_CONCURRENT_REQUESTS}")
            print(f"   - 请求延迟: {instance.REQUEST_DELAY}")
            print(f"   - 保存间隔: {instance.SAVE_INTERVAL}")

            return instance

        except Exception as e:
            print(f"❌ 加载YAML配置失败: {e}，使用默认配置")
            return cls()
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录"""
        directories = [
            # 数据目录
            cls.OUTPUT_DIR,
            "data/processed",
            "data/exports",
            "data/database",
            # 缓存目录
            cls.CACHE_DIR,
            "data/cache",
            # 日志目录
            "logs/spider",
            "logs/webui",
            "logs/system",
            # 报告目录
            "data/reports/summary",
            "data/reports/stats"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# 环境变量配置
class EnvConfig:
    """环境变量配置"""
    
    @staticmethod
    def get_debug_mode() -> bool:
        """获取调试模式"""
        return os.getenv("SPIDER_DEBUG", "false").lower() == "true"
    
    @staticmethod
    def get_page_range() -> Tuple[int, int]:
        """获取页面范围"""
        start = int(os.getenv("SPIDER_START_PAGE", "1"))
        end = int(os.getenv("SPIDER_END_PAGE", "50"))
        return (start, end)
    
    @staticmethod
    def get_category() -> str:
        """获取爬取分类"""
        return os.getenv("SPIDER_CATEGORY", "all")
    
    @staticmethod
    def get_output_format() -> str:
        """获取输出格式"""
        return os.getenv("SPIDER_OUTPUT_FORMAT", "excel")  # excel, json, both


# 正则表达式配置
class RegexPatterns:
    """正则表达式模式"""
    
    # 用户ID提取
    USER_ID_PATTERN = r'https://me\.modian\.com/u/detail\?uid=(\d+)'
    
    # 项目ID提取
    PROJECT_ID_PATTERN = r'https://zhongchou\.modian\.com/item/(\d+)\.html'
    
    # 金额提取
    MONEY_PATTERN = r'[\d,]+\.?\d*'
    
    # 百分比提取
    PERCENTAGE_PATTERN = r'(\d+(?:\.\d+)?)%'
    
    # 数字提取
    NUMBER_PATTERN = r'\d+'
    
    # 时间格式
    TIME_PATTERNS = [
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}',
        r'\d{4}-\d{2}-\d{2}'
    ]


# CSS选择器配置
class CSSSelectors:
    """CSS选择器配置"""
    
    # 项目列表页面
    PROJECT_LIST = 'div.pro_field li'
    PROJECT_LINK = 'a.pro_name.ga'
    PROJECT_TITLE = 'h3.pro_title'
    PROJECT_IMAGE = 'img'
    
    # 项目详情页面
    PROJECT_STATUS_BUTTON = 'div.buttons.clearfloat a'
    SPONSOR_INFO = 'div.sponsor-info.clearfix'
    PROJECT_CENTER = 'div.center'
    
    # 作者信息
    AUTHOR_LINK = 'a.sponsor-link'
    AUTHOR_IMAGE = 'img.sponsor-image'
    AUTHOR_NAME = 'span.name'
    
    # 众筹信息
    RAISED_MONEY = 'span[backer_money]'
    COMPLETION_RATE = 'span[rate]'
    TARGET_MONEY = 'span.goal-money'
    BACKER_COUNT = 'span[backer_count]'
    
    # 项目内容
    PROJECT_CONTENT = 'div.project-content'
    REWARD_LISTS = 'div.payback-lists.margin36'
    NAV_INFO = 'div.nav-wrap-inner'


# 数据字段映射
class FieldMapping:
    """数据字段映射"""
    
    # Excel列名映射
    EXCEL_COLUMNS = [
        "序号", "项目link", "项目6位id", "项目名称", "项目图",
        "开始时间", "结束时间", "项目结果",
        "用户主页(链接)", "用户头像(图片链接)", "分类", "用户名", "用户UID(data-username)",
        "已筹金额", "百分比", "目标金额", "支持者(数量)",
        "真实用户ID(链接提取)", "作者页-粉丝数", "作者页-关注数", "作者页-获赞数", 
        "作者页-详情", "作者页-其他信息", "作者页-主页确认",
        "回报列表信息(字符串)", "回报列表项目数",
        "项目更新数", "评论数", "看好数",
        "项目详情-图片数量", "项目详情-图片(列表字符串)", 
        "项目详情-视频数量", "项目详情-视频(列表字符串)"
    ]
    
    # JSON字段映射
    JSON_FIELDS = {
        "project_id": "项目6位id",
        "project_name": "项目名称", 
        "project_url": "项目link",
        "project_image": "项目图",
        "category": "分类",
        "start_time": "开始时间",
        "end_time": "结束时间",
        "status": "项目结果",
        "raised_amount": "已筹金额",
        "target_amount": "目标金额",
        "completion_rate": "百分比",
        "backer_count": "支持者(数量)",
        "author_name": "用户名",
        "author_homepage": "用户主页(链接)",
        "author_avatar": "用户头像(图片链接)"
    }


# 状态码映射
class StatusMapping:
    """项目状态映射"""
    
    STATUS_BUTTONS = {
        "看好": {"class": "创意", "is_idea": True},
        "看好项目": {"class": "预热", "is_preheat": True},
        "立即购买支持": {"class": "众筹中", "is_going": True},
        "众筹成功": {"class": "众筹成功", "is_success": True},
        "项目终止": {"class": "项目终止", "is_success": True},
        "众筹结束": {"class": "众筹失败", "is_fail": True},
        "众筹取消": {"class": "众筹取消", "is_fail": True}
    }
    
    @classmethod
    def get_status_info(cls, button_text: str) -> Dict:
        """根据按钮文本获取状态信息"""
        return cls.STATUS_BUTTONS.get(button_text, {
            "class": "未知情况",
            "is_unknown": True
        })
