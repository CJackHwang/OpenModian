# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理爬虫系统配置
"""

import yaml
import logging
from typing import Dict, Any
from pathlib import Path


class ConfigManager:
    """爬虫配置管理器"""

    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器

        Args:
            config_dir: 配置文件目录路径
        """
        self.config_dir = Path(config_dir)
        self.config = {}
        self.logger = self._setup_logger()

        # 加载配置
        self._load_main_config()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_main_config(self):
        """加载主配置文件"""
        config_file = self.config_dir / "spider_config.yaml"

        if not config_file.exists():
            # 如果配置文件不存在，创建默认配置
            self._create_default_config()
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            self.logger.info(f"成功加载配置文件: {config_file}")

        except Exception as e:
            self.logger.warning(f"加载配置文件失败，使用默认配置: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config = {
            "spider_settings": {
                "max_pages": 10,
                "max_retries": 5,
                "retry_delay": 2,
                "request_timeout": [10, 20],
                "save_interval": 5,
                "max_concurrent_requests": 3,
                "request_delay": [1.0, 3.0]
            },
            "output_settings": {
                "output_dir": "output",
                "cache_dir": "cache",
                "formats": ["excel", "csv", "json"],
                "excel_filename": "摩点众筹-主要信息.xls"
            },
            "database_settings": {
                "db_path": "database/modian_data.db",
                "enable_deduplication": True,
                "auto_backup": True
            },
            "web_ui_settings": {
                "host": "0.0.0.0",
                "port_range": [8080, 8090],
                "debug": False,
                "auto_open_browser": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/spider.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }

        # 保存默认配置
        self.save_config()
        self.logger.info("已创建默认配置文件")
    
    def get_spider_settings(self) -> Dict[str, Any]:
        """获取爬虫设置"""
        return self.config.get("spider_settings", {})

    def get_output_settings(self) -> Dict[str, Any]:
        """获取输出设置"""
        return self.config.get("output_settings", {})

    def get_database_settings(self) -> Dict[str, Any]:
        """获取数据库设置"""
        return self.config.get("database_settings", {})

    def get_web_ui_settings(self) -> Dict[str, Any]:
        """获取Web UI设置"""
        return self.config.get("web_ui_settings", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get("logging", {})

    def get_setting(self, section: str, key: str, default=None):
        """
        获取特定配置项

        Args:
            section: 配置节名称
            key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        return self.config.get(section, {}).get(key, default)
    
    def update_config(self, section: str, updates: Dict[str, Any]):
        """
        更新配置
        
        Args:
            section: 配置节名称
            updates: 更新的配置项
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(updates)
        self.logger.info(f"更新配置节: {section}")
    
    def save_config(self):
        """保存配置到文件"""
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        config_file = self.config_dir / "spider_config.yaml"

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False,
                         allow_unicode=True, indent=2)

            self.logger.info(f"配置已保存到: {config_file}")

        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            raise

    def validate_config(self) -> bool:
        """
        验证配置的有效性

        Returns:
            配置是否有效
        """
        required_sections = [
            "spider_settings", "output_settings", "database_settings",
            "web_ui_settings", "logging"
        ]

        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"缺少必需的配置节: {section}")
                return False

        # 验证爬虫设置
        spider_settings = self.config.get("spider_settings", {})
        required_spider_fields = ["max_pages", "max_retries", "request_timeout"]

        for field in required_spider_fields:
            if field not in spider_settings:
                self.logger.error(f"爬虫设置缺少字段: {field}")
                return False

        self.logger.info("配置验证通过")
        return True
    
    @classmethod
    def init_config(cls, config_dir: str = "config"):
        """
        初始化配置目录和默认配置文件

        Args:
            config_dir: 配置目录路径
        """
        config_path = Path(config_dir)
        config_path.mkdir(exist_ok=True)

        # 创建配置管理器实例以生成默认配置
        config_manager = cls(config_dir)

        print(f"配置目录初始化完成: {config_path}")
        return config_manager

    def __str__(self) -> str:
        """返回配置管理器的字符串表示"""
        return f"ConfigManager(config_dir={self.config_dir}, sections={list(self.config.keys())})"
