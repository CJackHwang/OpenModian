# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载和管理系统配置、API密钥、提示词模板等
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config_dir = Path(config_dir)
        self.config = {}
        self.prompts = {}
        self.logger = self._setup_logger()
        
        # 加载配置
        self._load_main_config()
        self._load_prompts()
    
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
        config_file = self.config_dir / "ai_config.yaml"
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # 处理环境变量
            self._process_env_variables()
            
            self.logger.info(f"成功加载配置文件: {config_file}")
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _process_env_variables(self):
        """处理配置中的环境变量"""
        def replace_env_vars(obj):
            if isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
                env_var = obj[2:-1]
                return os.getenv(env_var, obj)
            else:
                return obj
        
        self.config = replace_env_vars(self.config)
    
    def _load_prompts(self):
        """加载提示词模板"""
        prompts_dir = self.config_dir / "prompts" / "analysis"
        
        if not prompts_dir.exists():
            self.logger.warning(f"提示词目录不存在: {prompts_dir}")
            return
        
        for prompt_file in prompts_dir.glob("*.yaml"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_config = yaml.safe_load(f)
                
                prompt_name = prompt_file.stem
                self.prompts[prompt_name] = prompt_config
                
                self.logger.info(f"加载提示词模板: {prompt_name}")
                
            except Exception as e:
                self.logger.error(f"加载提示词模板失败 {prompt_file}: {e}")
    
    def get_ai_config(self, service: str = "primary") -> Dict[str, Any]:
        """
        获取AI服务配置
        
        Args:
            service: 服务名称 (primary, fallback, domestic)
            
        Returns:
            AI服务配置字典
        """
        ai_services = self.config.get("ai_services", {})
        
        if service not in ai_services:
            available_services = list(ai_services.keys())
            raise ValueError(f"未找到AI服务配置: {service}. 可用服务: {available_services}")
        
        return ai_services[service]
    
    def get_prompt_template(self, template_name: str) -> Dict[str, Any]:
        """
        获取提示词模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            提示词模板配置
        """
        if template_name not in self.prompts:
            available_prompts = list(self.prompts.keys())
            raise ValueError(f"未找到提示词模板: {template_name}. 可用模板: {available_prompts}")
        
        return self.prompts[template_name]
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """获取分析配置"""
        return self.config.get("analysis_config", {})
    
    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        return self.config.get("report_config", {})
    
    def get_data_config(self) -> Dict[str, Any]:
        """获取数据处理配置"""
        return self.config.get("data_config", {})
    
    def get_request_settings(self) -> Dict[str, Any]:
        """获取请求设置"""
        return self.config.get("request_settings", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get("logging", {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return self.config.get("cache", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.config.get("security", {})
    
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
        config_file = self.config_dir / "ai_config.yaml"
        
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
            "ai_services", "request_settings", "analysis_config",
            "report_config", "data_config"
        ]
        
        for section in required_sections:
            if section not in self.config:
                self.logger.error(f"缺少必需的配置节: {section}")
                return False
        
        # 验证AI服务配置
        ai_services = self.config.get("ai_services", {})
        if "primary" not in ai_services:
            self.logger.error("缺少主要AI服务配置")
            return False
        
        primary_config = ai_services["primary"]
        required_ai_fields = ["provider", "api_key", "model"]
        
        for field in required_ai_fields:
            if field not in primary_config:
                self.logger.error(f"主要AI服务配置缺少字段: {field}")
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
        
        # 创建子目录
        (config_path / "prompts" / "analysis").mkdir(parents=True, exist_ok=True)
        (config_path / "prompts" / "templates").mkdir(parents=True, exist_ok=True)
        (config_path / "report_templates").mkdir(parents=True, exist_ok=True)
        
        print(f"配置目录初始化完成: {config_path}")
    
    def __str__(self) -> str:
        """返回配置管理器的字符串表示"""
        return f"ConfigManager(config_dir={self.config_dir}, sections={list(self.config.keys())})"
