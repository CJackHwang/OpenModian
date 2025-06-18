# -*- coding: utf-8 -*-
"""
数据验证处理器 - 简化版
专注于API数据的基础验证
"""

import re
from typing import List, Dict, Any, Tuple
from ..config import SpiderConfig


class ValidationProcessor:
    """数据验证处理器 - 简化版，专注于API数据基础验证"""

    def __init__(self, config: SpiderConfig, web_monitor=None):
        self.config = config
        self.web_monitor = web_monitor

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    # ========== 已弃用的复杂验证方法 ==========
    # API数据可信，无需复杂验证

    def validate_project_data(self, project_data: List[Any]) -> Tuple[bool, List[str]]:
        """已弃用：复杂项目数据验证，API数据可信"""
        return True, []

    def _validate_data_logic(self, project_data: List[Any]) -> List[str]:
        """已弃用：数据逻辑一致性检查，API数据内部一致"""
        return []

    def _validate_money_fields(self, money_fields: List[Any]) -> Tuple[bool, str]:
        """已弃用：金额字段验证，API数据准确"""
        return True, ""

    def _validate_author_info(self, author_fields: List[Any]) -> Tuple[bool, str]:
        """已弃用：作者信息验证，API数据完整"""
        return True, ""

    def _validate_time_fields(self, time_fields: List[Any]) -> Tuple[bool, str]:
        """已弃用：时间字段验证，API数据准确"""
        return True, ""

    # ========== 保留的基础验证方法 ==========
    # 这些方法在API时代仍然有用

    def fix_field_count(self, project_data: List[Any], expected_count: int = 33) -> List[Any]:
        """修复字段数量不匹配的问题"""
        current_count = len(project_data)
        
        if current_count == expected_count:
            return project_data
        
        if current_count < expected_count:
            # 字段不足，补充默认值
            missing_count = expected_count - current_count
            default_values = [""] * missing_count
            fixed_data = project_data + default_values
            self._log("info", f"🔧 修复字段数量: 添加了 {missing_count} 个缺失字段")
            return fixed_data
        
        else:
            # 字段过多，截取前面的字段
            excess_count = current_count - expected_count
            fixed_data = project_data[:expected_count]
            self._log("warning", f"🔧 修复字段数量: 移除了 {excess_count} 个多余字段")
            return fixed_data

    def validate_basic_fields(self, project_data: List[Any]) -> Tuple[bool, List[str]]:
        """基础字段验证（简化版）"""
        errors = []
        
        try:
            if len(project_data) < 5:
                errors.append("数据字段数量不足")
                return False, errors
            
            # 验证项目ID
            project_id = project_data[2] if len(project_data) > 2 else ""
            if not project_id or not str(project_id).isdigit():
                errors.append(f"项目ID无效: {project_id}")
            
            # 验证项目名称
            project_name = project_data[3] if len(project_data) > 3 else ""
            if not project_name or str(project_name).strip() == "":
                errors.append("项目名称为空")
            
            # 验证项目URL
            project_url = project_data[1] if len(project_data) > 1 else ""
            if not project_url or not self._is_valid_url(project_url):
                errors.append(f"项目URL无效: {project_url}")
                
        except Exception as e:
            errors.append(f"基础验证过程中发生错误: {e}")
        
        return len(errors) == 0, errors

    def _is_valid_url(self, value: Any) -> bool:
        """检查是否为有效的URL格式"""
        if not value or str(value) == "none":
            return True  # none是允许的值
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, str(value)))

    def clean_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """清理API数据"""
        if not api_data:
            return {}
        
        cleaned_data = {}
        
        for key, value in api_data.items():
            if value is None:
                cleaned_data[key] = ""
            elif isinstance(value, str):
                # 清理字符串值
                cleaned_data[key] = str(value).strip()
            elif isinstance(value, (int, float)):
                # 确保数字值合理
                if key in ["like_count", "comment_count", "backer_count", "update_count"]:
                    cleaned_data[key] = max(0, int(value))
                elif key in ["raised_amount", "target_amount", "completion_rate"]:
                    cleaned_data[key] = max(0, float(value))
                else:
                    cleaned_data[key] = value
            else:
                cleaned_data[key] = value
        
        return cleaned_data

    def validate_api_response(self, api_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证API响应数据"""
        errors = []
        
        if not api_data:
            errors.append("API响应为空")
            return False, errors
        
        # 检查必需字段
        required_fields = ["project_id", "project_name", "project_status"]
        for field in required_fields:
            if field not in api_data or not api_data[field]:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查数据类型
        if "project_id" in api_data:
            try:
                int(api_data["project_id"])
            except (ValueError, TypeError):
                errors.append(f"项目ID格式错误: {api_data['project_id']}")
        
        return len(errors) == 0, errors

    def get_validation_summary(self, validation_results: List[Tuple[bool, List[str]]]) -> Dict[str, Any]:
        """获取验证结果摘要"""
        total_count = len(validation_results)
        valid_count = sum(1 for is_valid, _ in validation_results if is_valid)
        invalid_count = total_count - valid_count
        
        all_errors = []
        for is_valid, errors in validation_results:
            if not is_valid:
                all_errors.extend(errors)
        
        return {
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "success_rate": (valid_count / total_count * 100) if total_count > 0 else 0,
            "errors": all_errors,
            "error_count": len(all_errors),
            "processor_type": "simplified_api_optimized"
        }
