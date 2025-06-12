# -*- coding: utf-8 -*-
"""
数据验证模块
提供数据质量检查、格式验证和完整性验证功能
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .config import SpiderConfig, RegexPatterns


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 数据质量评分 0-100
    
    def add_error(self, message: str):
        """添加错误"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def calculate_score(self, total_fields: int):
        """计算质量评分"""
        if total_fields == 0:
            self.score = 0
            return
        
        error_penalty = len(self.errors) * 10
        warning_penalty = len(self.warnings) * 2
        
        self.score = max(0, 100 - error_penalty - warning_penalty)


class DataValidator:
    """数据验证器"""
    
    def __init__(self, config: SpiderConfig):
        self.config = config
        self.validation_rules = self._init_validation_rules()
    
    def _init_validation_rules(self) -> Dict[str, Dict]:
        """初始化验证规则"""
        return {
            "项目名称": {
                "required": True,
                "min_length": self.config.MIN_TITLE_LENGTH,
                "max_length": self.config.MAX_TITLE_LENGTH,
                "forbidden_keywords": self.config.SKIP_KEYWORDS
            },
            "项目link": {
                "required": True,
                "pattern": r"https://zhongchou\.modian\.com/item/\d+\.html",
                "format": "url"
            },
            "项目6位id": {
                "required": True,
                "pattern": r"^\d+$",
                "min_length": 1
            },
            "分类": {
                "required": True,
                "min_length": 1,
                "max_length": 50
            },
            "已筹金额": {
                "required": True,
                "pattern": r"^\d+(\.\d+)?$",
                "format": "number"
            },
            "目标金额": {
                "required": True,
                "pattern": r"^\d+(\.\d+)?$",
                "format": "number"
            },
            "百分比": {
                "required": False,
                "pattern": r"^\d+(\.\d+)?$",
                "format": "percentage"
            },
            "支持者(数量)": {
                "required": True,
                "pattern": r"^\d+$",
                "format": "integer"
            },
            "开始时间": {
                "required": False,
                "format": "datetime"
            },
            "结束时间": {
                "required": False,
                "format": "datetime"
            },
            "用户名": {
                "required": True,
                "min_length": 1,
                "max_length": 100
            },
            "用户主页(链接)": {
                "required": False,
                "format": "url"
            }
        }
    
    def validate_project_data(self, project_data: List[Any]) -> ValidationResult:
        """验证项目数据"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[], score=0)
        
        if not project_data:
            result.add_error("项目数据为空")
            result.calculate_score(0)
            return result
        
        # 检查数据长度
        expected_length = len(self.config.REQUIRED_FIELDS)
        if len(project_data) < expected_length:
            result.add_error(f"数据字段不完整，期望{expected_length}个字段，实际{len(project_data)}个")
        
        # 验证必需字段
        field_mapping = self._get_field_mapping()
        
        for field_name, rules in self.validation_rules.items():
            if field_name in field_mapping:
                field_index = field_mapping[field_name]
                if field_index < len(project_data):
                    field_value = project_data[field_index]
                    self._validate_field(field_name, field_value, rules, result)
                elif rules.get("required", False):
                    result.add_error(f"缺少必需字段: {field_name}")
        
        # 业务逻辑验证
        self._validate_business_logic(project_data, result)
        
        result.calculate_score(len(self.validation_rules))
        return result
    
    def _get_field_mapping(self) -> Dict[str, int]:
        """获取字段映射"""
        # 根据Excel列名映射到索引
        from .config import FieldMapping
        mapping = {}
        for i, column_name in enumerate(FieldMapping.EXCEL_COLUMNS):
            mapping[column_name] = i
        return mapping
    
    def _validate_field(self, field_name: str, field_value: Any, 
                       rules: Dict, result: ValidationResult):
        """验证单个字段"""
        value_str = str(field_value).strip()
        
        # 检查必需字段
        if rules.get("required", False) and not value_str:
            result.add_error(f"{field_name} 不能为空")
            return
        
        if not value_str:
            return  # 非必需字段为空时跳过其他验证
        
        # 检查长度
        min_length = rules.get("min_length")
        max_length = rules.get("max_length")
        
        if min_length and len(value_str) < min_length:
            result.add_error(f"{field_name} 长度不能少于{min_length}个字符")
        
        if max_length and len(value_str) > max_length:
            result.add_warning(f"{field_name} 长度超过{max_length}个字符")
        
        # 检查正则表达式
        pattern = rules.get("pattern")
        if pattern and not re.match(pattern, value_str):
            result.add_error(f"{field_name} 格式不正确: {value_str}")
        
        # 检查格式
        format_type = rules.get("format")
        if format_type:
            self._validate_format(field_name, value_str, format_type, result)
        
        # 检查禁用关键词
        forbidden_keywords = rules.get("forbidden_keywords", [])
        for keyword in forbidden_keywords:
            if keyword in value_str:
                result.add_warning(f"{field_name} 包含禁用关键词: {keyword}")
    
    def _validate_format(self, field_name: str, value: str, 
                        format_type: str, result: ValidationResult):
        """验证格式"""
        if format_type == "url":
            if not self._is_valid_url(value):
                result.add_error(f"{field_name} URL格式不正确: {value}")
        
        elif format_type == "number":
            if not self._is_valid_number(value):
                result.add_error(f"{field_name} 数字格式不正确: {value}")
        
        elif format_type == "integer":
            if not self._is_valid_integer(value):
                result.add_error(f"{field_name} 整数格式不正确: {value}")
        
        elif format_type == "percentage":
            if not self._is_valid_percentage(value):
                result.add_error(f"{field_name} 百分比格式不正确: {value}")
        
        elif format_type == "datetime":
            if not self._is_valid_datetime(value):
                result.add_warning(f"{field_name} 时间格式可能不正确: {value}")
    
    def _validate_business_logic(self, project_data: List[Any], result: ValidationResult):
        """验证业务逻辑"""
        field_mapping = self._get_field_mapping()
        
        try:
            # 验证金额逻辑
            raised_idx = field_mapping.get("已筹金额")
            target_idx = field_mapping.get("目标金额")
            percent_idx = field_mapping.get("百分比")
            
            if (raised_idx and target_idx and percent_idx and 
                raised_idx < len(project_data) and 
                target_idx < len(project_data) and 
                percent_idx < len(project_data)):
                
                raised = self._safe_float(project_data[raised_idx])
                target = self._safe_float(project_data[target_idx])
                percent = self._safe_float(project_data[percent_idx])
                
                if target > 0:
                    calculated_percent = (raised / target) * 100
                    if abs(calculated_percent - percent) > 5:  # 允许5%的误差
                        result.add_warning(f"完成率计算不一致: 计算值{calculated_percent:.1f}%, 实际值{percent}%")
                
                if raised < 0 or target <= 0:
                    result.add_error("金额数据异常")
            
            # 验证支持者数量
            backer_idx = field_mapping.get("支持者(数量)")
            if backer_idx and backer_idx < len(project_data):
                backer_count = self._safe_int(project_data[backer_idx])
                if backer_count < 0:
                    result.add_error("支持者数量不能为负数")
            
            # 验证项目ID和链接一致性
            id_idx = field_mapping.get("项目6位id")
            link_idx = field_mapping.get("项目link")
            
            if (id_idx and link_idx and 
                id_idx < len(project_data) and 
                link_idx < len(project_data)):
                
                project_id = str(project_data[id_idx])
                project_link = str(project_data[link_idx])
                
                if project_id and project_link != "none":
                    if project_id not in project_link:
                        result.add_error("项目ID与链接不匹配")
        
        except Exception as e:
            result.add_warning(f"业务逻辑验证出错: {e}")
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))
    
    def _is_valid_number(self, value: str) -> bool:
        """验证数字格式"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_integer(self, value: str) -> bool:
        """验证整数格式"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_percentage(self, value: str) -> bool:
        """验证百分比格式"""
        try:
            percent = float(value)
            return 0 <= percent <= 1000  # 允许超过100%的情况
        except ValueError:
            return False
    
    def _is_valid_datetime(self, value: str) -> bool:
        """验证时间格式"""
        if value in ["none", "创意中", "预热中", "众筹中"]:
            return True
        
        for pattern in RegexPatterns.TIME_PATTERNS:
            if re.match(pattern, value):
                return True
        
        return False
    
    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数"""
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value: Any) -> int:
        """安全转换为整数"""
        try:
            return int(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return 0
    
    def validate_batch(self, projects_data: List[List[Any]]) -> Dict[str, Any]:
        """批量验证项目数据"""
        results = []
        total_score = 0
        valid_count = 0
        
        for i, project_data in enumerate(projects_data):
            result = self.validate_project_data(project_data)
            results.append({
                "index": i,
                "is_valid": result.is_valid,
                "score": result.score,
                "errors": result.errors,
                "warnings": result.warnings
            })
            
            total_score += result.score
            if result.is_valid:
                valid_count += 1
        
        return {
            "total_projects": len(projects_data),
            "valid_projects": valid_count,
            "invalid_projects": len(projects_data) - valid_count,
            "average_score": total_score / len(projects_data) if projects_data else 0,
            "validation_rate": (valid_count / len(projects_data) * 100) if projects_data else 0,
            "results": results
        }
    
    def get_validation_summary(self, validation_results: Dict[str, Any]) -> str:
        """获取验证摘要"""
        summary = f"""
数据验证摘要:
- 总项目数: {validation_results['total_projects']}
- 有效项目: {validation_results['valid_projects']}
- 无效项目: {validation_results['invalid_projects']}
- 验证通过率: {validation_results['validation_rate']:.1f}%
- 平均质量评分: {validation_results['average_score']:.1f}/100
"""
        
        # 统计错误类型
        error_types = {}
        warning_types = {}
        
        for result in validation_results['results']:
            for error in result['errors']:
                error_types[error] = error_types.get(error, 0) + 1
            for warning in result['warnings']:
                warning_types[warning] = warning_types.get(warning, 0) + 1
        
        if error_types:
            summary += "\n常见错误:\n"
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                summary += f"  - {error}: {count}次\n"
        
        if warning_types:
            summary += "\n常见警告:\n"
            for warning, count in sorted(warning_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                summary += f"  - {warning}: {count}次\n"
        
        return summary
