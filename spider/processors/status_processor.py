# -*- coding: utf-8 -*-
"""
状态处理器
负责项目状态解析和映射
"""

import re
from typing import Dict
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import ParserUtils


class StatusProcessor:
    """状态处理器 - 负责项目状态解析和映射"""

    def __init__(self, config: SpiderConfig, web_monitor=None):
        self.config = config
        self.web_monitor = web_monitor
        
        # 状态映射表
        self.status_mapping = {
            "idea": "创意",
            "preheat": "预热", 
            "crowdfunding": "众筹中",
            "success": "成功",
            "failed": "失败",
            "finished": "已结束"
        }

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def parse_project_status(self, soup: BeautifulSoup) -> Dict[str, any]:
        """解析项目状态信息"""
        status_info = {
            "item_class": "未知情况",  # 保持与原始实现一致
            "status": "unknown",
            "status_text": "未知",
            "is_idea": False,
            "is_preheat": False,
            "is_crowdfunding": False,
            "is_going": False,  # 保持与原始实现一致
            "is_success": False,
            "is_failed": False,
            "is_fail": False,  # 保持与原始实现一致
            "is_finished": False
        }

        try:
            # 方法1: 从页面class属性判断状态
            status_from_class = self._extract_status_from_class(soup)
            if status_from_class:
                status_info.update(status_from_class)
                return status_info

            # 方法2: 从状态文本判断
            status_from_text = self._extract_status_from_text(soup)
            if status_from_text:
                status_info.update(status_from_text)
                return status_info

            # 方法3: 从按钮状态判断
            status_from_button = self._extract_status_from_button(soup)
            if status_from_button:
                status_info.update(status_from_button)
                return status_info

            # 方法4: 从进度条判断
            status_from_progress = self._extract_status_from_progress(soup)
            if status_from_progress:
                status_info.update(status_from_progress)

        except Exception as e:
            self._log("warning", f"状态解析失败: {e}")

        return status_info

    def _extract_status_from_class(self, soup: BeautifulSoup) -> Dict[str, any]:
        """从页面class属性提取状态"""
        try:
            # 查找包含状态信息的元素
            status_elements = soup.find_all(class_=re.compile(r'(status|state|project-status)'))
            
            for element in status_elements:
                classes = element.get('class', [])
                class_text = ' '.join(classes).lower()
                
                if 'idea' in class_text:
                    return self._create_status_dict("idea", "创意", is_idea=True)
                elif 'preheat' in class_text:
                    return self._create_status_dict("preheat", "预热", is_preheat=True)
                elif 'crowdfunding' in class_text or 'funding' in class_text:
                    return self._create_status_dict("crowdfunding", "众筹中", is_crowdfunding=True)
                elif 'success' in class_text:
                    return self._create_status_dict("success", "成功", is_success=True, is_finished=True)
                elif 'failed' in class_text or 'fail' in class_text:
                    return self._create_status_dict("failed", "失败", is_failed=True, is_finished=True)

        except Exception as e:
            self._log("debug", f"class状态提取失败: {e}")

        return None

    def _extract_status_from_text(self, soup: BeautifulSoup) -> Dict[str, any]:
        """从状态文本提取状态"""
        try:
            # 查找状态显示区域
            status_selectors = [
                '.project-status',
                '.status-text',
                '.project-state',
                '.funding-status',
                'span[class*="status"]',
                'div[class*="status"]'
            ]

            for selector in status_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = ParserUtils.safe_get_text(element).strip()
                    status = self._parse_status_text(text)
                    if status:
                        return status

            # 从页面整体文本中查找状态关键词
            page_text = soup.get_text()
            status_keywords = {
                "创意": ("idea", "创意", True, False, False, False, False, False),
                "预热": ("preheat", "预热", False, True, False, False, False, False),
                "众筹中": ("crowdfunding", "众筹中", False, False, True, False, False, False),
                "筹款中": ("crowdfunding", "众筹中", False, False, True, False, False, False),
                "成功": ("success", "成功", False, False, False, True, False, True),
                "达成": ("success", "成功", False, False, False, True, False, True),
                "失败": ("failed", "失败", False, False, False, False, True, True),
                "未达成": ("failed", "失败", False, False, False, False, True, True),
                "已结束": ("finished", "已结束", False, False, False, False, False, True)
            }

            for keyword, status_data in status_keywords.items():
                if keyword in page_text:
                    return self._create_status_dict(*status_data)

        except Exception as e:
            self._log("debug", f"文本状态提取失败: {e}")

        return None

    def _extract_status_from_button(self, soup: BeautifulSoup) -> Dict[str, any]:
        """从按钮状态提取项目状态"""
        try:
            # 基于原始实现的按钮查找逻辑
            button_div = ParserUtils.safe_find(soup, 'div', {'class': 'buttons clearfloat'})
            if button_div:
                button_a = ParserUtils.safe_find(button_div, 'a')
                if button_a:
                    button_text = ParserUtils.safe_get_text(button_a).strip()
                    self._log("info", f"✅ 找到状态按钮文本: {button_text}")

                    # 根据按钮文本进行状态判断（与原始实现保持一致）
                    if "众筹成功" in button_text:
                        return self._create_status_dict("success", "众筹成功", is_success=True, is_finished=True)
                    elif "众筹结束" in button_text or "众筹失败" in button_text:
                        return self._create_status_dict("failed", "众筹失败", is_failed=True, is_finished=True)
                    elif "看好项目" in button_text:  # 先检查"看好项目"
                        return self._create_status_dict("preheat", "预热", is_preheat=True)
                    elif "看好创意" in button_text or "看好" in button_text:
                        return self._create_status_dict("idea", "创意", is_idea=True)
                    elif "立即购买支持" in button_text or "立即支持" in button_text:
                        return self._create_status_dict("crowdfunding", "众筹中", is_crowdfunding=True)

                    self._log("info", f"✅ 按钮状态识别完成")

            # 备用的通用按钮查找逻辑
            button_selectors = [
                'button[class*="support"]',
                'button[class*="subscribe"]',
                'a[class*="support"]',
                'a[class*="subscribe"]',
                '.support-btn',
                '.subscribe-btn'
            ]

            for selector in button_selectors:
                buttons = soup.select(selector)
                for button in buttons:
                    button_text = ParserUtils.safe_get_text(button).strip()
                    classes = button.get('class', [])

                    # 根据按钮文本和状态判断项目状态
                    if '订阅' in button_text or 'subscribe' in ' '.join(classes):
                        return self._create_status_dict("preheat", "预热", is_preheat=True)
                    elif '支持' in button_text or 'support' in ' '.join(classes):
                        if 'disabled' in classes or button.get('disabled'):
                            return self._create_status_dict("finished", "已结束", is_finished=True)
                        else:
                            return self._create_status_dict("crowdfunding", "众筹中", is_crowdfunding=True)

        except Exception as e:
            self._log("debug", f"按钮状态提取失败: {e}")

        return None

    def _extract_status_from_progress(self, soup: BeautifulSoup) -> Dict[str, any]:
        """从进度条状态提取项目状态"""
        try:
            # 查找进度条元素
            progress_elements = soup.select('.progress, .progress-bar, [class*="progress"]')
            
            for element in progress_elements:
                # 检查进度条的值
                progress_value = element.get('value') or element.get('data-progress')
                if progress_value:
                    try:
                        progress = float(progress_value)
                        if progress >= 100:
                            return self._create_status_dict("success", "成功", is_success=True, is_finished=True)
                        elif progress > 0:
                            return self._create_status_dict("crowdfunding", "众筹中", is_crowdfunding=True)
                    except ValueError:
                        pass

                # 检查进度条的class
                classes = element.get('class', [])
                if 'complete' in classes or 'success' in classes:
                    return self._create_status_dict("success", "成功", is_success=True, is_finished=True)
                elif 'failed' in classes:
                    return self._create_status_dict("failed", "失败", is_failed=True, is_finished=True)

        except Exception as e:
            self._log("debug", f"进度条状态提取失败: {e}")

        return None

    def _parse_status_text(self, text: str) -> Dict[str, any]:
        """解析状态文本"""
        if not text:
            return None

        text_lower = text.lower()
        
        # 状态关键词映射
        status_patterns = {
            r'创意|idea': ("idea", "创意", True, False, False, False, False, False),
            r'预热|preheat': ("preheat", "预热", False, True, False, False, False, False),
            r'众筹中|筹款中|crowdfunding|funding': ("crowdfunding", "众筹中", False, False, True, False, False, False),
            r'成功|达成|success|completed': ("success", "成功", False, False, False, True, False, True),
            r'失败|未达成|failed|fail': ("failed", "失败", False, False, False, False, True, True),
            r'已结束|结束|finished|ended': ("finished", "已结束", False, False, False, False, False, True)
        }

        for pattern, status_data in status_patterns.items():
            if re.search(pattern, text_lower):
                return self._create_status_dict(*status_data)

        return None

    def _create_status_dict(self, status: str, status_text: str, is_idea: bool = False,
                           is_preheat: bool = False, is_crowdfunding: bool = False,
                           is_success: bool = False, is_failed: bool = False,
                           is_finished: bool = False) -> Dict[str, any]:
        """创建状态字典"""
        # 映射到item_class字段，保持与原始实现一致
        item_class_mapping = {
            "idea": "创意",
            "preheat": "预热",
            "crowdfunding": "众筹中",
            "success": "众筹成功",
            "failed": "众筹失败",
            "finished": "已结束",
            "unknown": "未知情况"
        }

        return {
            "item_class": item_class_mapping.get(status, "未知情况"),
            "status": status,
            "status_text": status_text,
            "is_idea": is_idea,
            "is_preheat": is_preheat,
            "is_crowdfunding": is_crowdfunding,
            "is_going": is_crowdfunding,  # 保持与原始实现一致
            "is_success": is_success,
            "is_failed": is_failed,
            "is_fail": is_failed,  # 保持与原始实现一致
            "is_finished": is_finished
        }

    def get_status_priority(self, status: str) -> int:
        """获取状态优先级（用于排序）"""
        priority_map = {
            "crowdfunding": 1,  # 众筹中 - 最高优先级
            "preheat": 2,       # 预热 - 第二优先级
            "idea": 3,          # 创意 - 第三优先级
            "success": 4,       # 成功 - 第四优先级
            "failed": 5,        # 失败 - 第五优先级
            "finished": 6,      # 已结束 - 最低优先级
            "unknown": 7        # 未知 - 最低优先级
        }
        return priority_map.get(status, 7)

    def is_active_status(self, status: str) -> bool:
        """判断是否为活跃状态"""
        active_statuses = ["idea", "preheat", "crowdfunding"]
        return status in active_statuses

    def is_completed_status(self, status: str) -> bool:
        """判断是否为完成状态"""
        completed_statuses = ["success", "failed", "finished"]
        return status in completed_statuses

    def get_status_color(self, status: str) -> str:
        """获取状态对应的颜色（用于UI显示）"""
        color_map = {
            "idea": "#FFA500",      # 橙色
            "preheat": "#1E90FF",   # 蓝色
            "crowdfunding": "#32CD32", # 绿色
            "success": "#228B22",   # 深绿色
            "failed": "#DC143C",    # 红色
            "finished": "#808080",  # 灰色
            "unknown": "#696969"    # 深灰色
        }
        return color_map.get(status, "#696969")
