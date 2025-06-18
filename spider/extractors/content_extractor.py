# -*- coding: utf-8 -*-
"""
项目内容提取器
负责从项目页面提取导航信息、媒体内容等
"""

import re
import json
import threading
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import DataUtils, ParserUtils


class ContentExtractor:
    """项目内容提取器"""

    def __init__(self, config: SpiderConfig, web_monitor=None, stop_flag=None):
        self.config = config
        self.data_utils = DataUtils()
        self.web_monitor = web_monitor
        self._stop_flag = stop_flag

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def extract_nav_info(self, soup: BeautifulSoup) -> List[str]:
        """解析导航信息 - 深度优化版本，提高数据提取准确性"""
        update_count = "0"
        comment_count = "0"
        supporter_count = "0"

        self._log("debug", "开始导航信息解析...")

        # 策略0: 关键数据专门提取（最高优先级）
        critical_data = self._extract_critical_nav_data(soup)
        if critical_data and any(v != "0" for v in critical_data.values()):
            # 修复字段映射：正确分配动态获取的数据
            comment_count = critical_data.get("comment_count", "0")  # 评论数
            like_count = critical_data.get("like_count", "0")        # 看好数

            self._log("info", f"✅ 关键数据专门提取成功: 看好数={like_count}, 评论数={comment_count}")

            # 更新数仍需要通过其他方法获取
            update_count = self._extract_update_count_only(soup)

            # 重要修复：直接使用获取的数据，不要重新赋值
            # 最终返回顺序：[update_count, comment_count, like_count]
            # 对应Excel表头：["项目更新数", "评论数", "看好数"]
        else:
            # 策略1: JavaScript数据提取（最准确）
            js_data = self._extract_nav_from_javascript(soup)
            if js_data:
                update_count = js_data.get("update_count", "0")
                comment_count = js_data.get("comment_count", "0")
                supporter_count = js_data.get("supporter_count", "0")

                self._log("info", "✅ JavaScript数据提取成功")
            else:
                # 策略2: 增强的DOM解析（多重选择器）
                nav_data = self._extract_nav_from_dom_enhanced(soup)
                if nav_data and any(x != "0" for x in nav_data):
                    update_count, comment_count, supporter_count = nav_data[:3]
                    self._log("info", "✅ 增强DOM解析成功")
                else:
                    # 策略3: 优化的文本解析（更强正则）
                    text_data = self._extract_nav_from_text_enhanced(soup)
                    if text_data and any(x != "0" for x in text_data):
                        update_count, comment_count, supporter_count = text_data[:3]
                        self._log("info", "✅ 增强文本解析成功")
                    else:
                        # 策略4: 传统DOM解析（回退）
                        fallback_data = self._extract_nav_from_dom_fallback(soup)
                        update_count, comment_count, supporter_count = fallback_data[:3]
                        self._log("warning", "使用回退解析策略")

        # 数据验证和修正
        # 如果使用了关键数据提取，跳过验证以避免覆盖正确的数据
        if 'like_count' not in locals():
            update_count, comment_count, supporter_count = self._validate_nav_data(
                update_count, comment_count, supporter_count
            )

        # 根据Excel表头顺序返回：项目更新数, 评论数, 看好数
        # 如果通过关键数据提取成功，使用提取的数据
        if 'like_count' in locals():
            final_like_count = like_count      # 1641 (看好数)
            final_comment_count = comment_count # 8903 (评论数)
        else:
            # 否则使用传统方法的结果（supporter_count实际是看好数）
            final_like_count = supporter_count
            final_comment_count = comment_count

        self._log("info", f"📊 导航信息最终结果: 更新数={update_count}, 评论数={final_comment_count}, 看好数={final_like_count}")

        # 重要修复：确保返回顺序与Excel表头完全一致
        # Excel表头顺序：["项目更新数", "评论数", "看好数"]
        # 调试输出
        self._log("info", f"🔧 返回前检查: update_count={update_count}, final_comment_count={final_comment_count}, final_like_count={final_like_count}")

        return [update_count, final_comment_count, final_like_count]

    def _extract_critical_nav_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """专门提取项目详情页面导航区域的三个关键数据：点赞数、支持者数量、评论数"""
        result = {
            "like_count": "0",      # 点赞数
            "supporter_count": "0", # 支持者数量
            "comment_count": "0"    # 评论数
        }

        try:
            # 静态看好数和评论数提取方法已移除 - 这些选择器从未成功过
            # 直接跳过静态解析，使用动态数据获取
            pass

        except Exception as e:
            self._log("warning", f"关键导航数据提取失败: {e}")

        # 使用API获取作为主要方法，动态获取作为后备
        if self.config.ENABLE_DYNAMIC_DATA:
            self._log("info", "使用API获取数据（快速模式）+ 动态获取（后备模式）")
            try:
                # 首先尝试API获取
                api_data = self._get_api_data(soup)
                if api_data and (api_data.get("like_count", "0") != "0" or api_data.get("comment_count", "0") != "0"):
                    # API获取成功
                    result["like_count"] = api_data["like_count"]
                    result["comment_count"] = api_data["comment_count"]
                    self._log("info", f"✅ API数据获取成功: 看好数={result['like_count']}, 评论数={result['comment_count']}")
                else:
                    # API获取失败，使用动态获取作为后备
                    self._log("warning", "API获取失败或无数据，使用动态获取作为后备")
                    dynamic_data = self._get_complete_dynamic_data(soup)
                    if dynamic_data:
                        if dynamic_data.get("like_count", "0") != "0":
                            result["like_count"] = dynamic_data["like_count"]
                        if dynamic_data.get("comment_count", "0") != "0":
                            result["comment_count"] = dynamic_data["comment_count"]
                        self._log("info", f"✅ 动态数据获取完成（后备）: 看好数={result['like_count']}, 评论数={result['comment_count']}")
                    else:
                        self._log("warning", "动态数据获取也失败，使用默认值")
            except Exception as e:
                self._log("warning", f"数据获取失败: {e}")
        else:
            self._log("warning", "数据获取已禁用，无法获取看好数和评论数")

        # 最终验证和日志
        extracted_count = sum(1 for v in result.values() if v != "0")
        self._log("info", f"📊 导航数据提取完成: {extracted_count}/2 个字段成功（看好数、评论数）")

        return result

    def _get_api_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """使用API获取数据（主要方法）"""
        try:
            # 从页面中提取项目ID
            project_id = self._extract_project_id_from_page(soup)
            if not project_id:
                self._log("warning", "无法提取项目ID")
                return {"like_count": "0", "comment_count": "0"}

            # 使用API获取器获取数据
            from ..api_data_fetcher import ModianAPIFetcher

            # 为每个线程创建独立的API获取器实例
            thread_id = threading.current_thread().ident
            fetcher_key = f'_api_fetcher_{thread_id}'

            if not hasattr(self, fetcher_key):
                fetcher = ModianAPIFetcher(self.config)
                setattr(self, fetcher_key, fetcher)
                self._log("info", f"为线程 {thread_id} 创建独立的API获取器")

            fetcher = getattr(self, fetcher_key)
            result = fetcher.get_project_data(project_id)

            self._log("info", f"项目 {project_id} API数据获取结果: 看好数={result.get('like_count', '0')}, 评论数={result.get('comment_count', '0')}")
            return result

        except Exception as e:
            self._log("warning", f"项目API数据获取失败: {e}")
            return {"like_count": "0", "comment_count": "0"}

    def _get_complete_dynamic_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """获取完整的动态数据（修复并发问题版本）"""
        try:
            # 从页面中提取项目ID
            project_id = self._extract_project_id_from_page(soup)
            if not project_id:
                self._log("warning", "无法提取项目ID")
                return {"like_count": "0", "comment_count": "0"}

            # 修复并发问题：为每个线程创建独立的动态数据管理器
            # 使用线程本地存储确保每个并发任务都有独立的管理器实例
            thread_id = threading.current_thread().ident
            manager_key = f'_lightning_manager_{thread_id}'

            if not hasattr(self, manager_key):
                from ..lightning_fast_dynamic import LightningDataManager
                manager = LightningDataManager(self.config, None, self._stop_flag)
                setattr(self, manager_key, manager)
                self._log("info", f"为线程 {thread_id} 创建独立的动态数据管理器")

            manager = getattr(self, manager_key)
            result = manager.get_lightning_data(project_id)

            self._log("info", f"项目 {project_id} 动态数据获取结果: 看好数={result.get('like_count', '0')}, 评论数={result.get('comment_count', '0')}")
            return result

        except Exception as e:
            self._log("warning", f"项目动态数据获取失败: {e}")
            return {"like_count": "0", "comment_count": "0"}

    def _extract_project_id_from_page(self, soup: BeautifulSoup) -> str:
        """从页面中提取项目ID"""
        try:
            # 方法1: 从URL中提取
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string if script.string else ""
                # 查找realtime_sync.product_info_list调用
                import re
                match = re.search(r'realtime_sync\.product_info_list\([\'"](\d+)[\'"]', script_content)
                if match:
                    return match.group(1)

                # 查找其他可能的项目ID模式
                match = re.search(r'project_id[\'"]?\s*[:=]\s*[\'"]?(\d+)', script_content)
                if match:
                    return match.group(1)

            # 方法2: 从页面元素中提取
            elements_with_id = soup.find_all(attrs={'data-project-id': True})
            if elements_with_id:
                return elements_with_id[0].get('data-project-id')

            return None

        except Exception as e:
            self._log("warning", f"提取项目ID失败: {e}")
            return None

    def _extract_update_count_only(self, soup: BeautifulSoup) -> str:
        """专门提取更新数"""
        update_count = "0"

        try:
            # 尝试多种更新数选择器（包含拼写错误的属性）
            update_selectors = [
                'li.pro-gengxin span',
                'li[class*="gengxin"] span',
                'li[class*="update"] span',
                '.nav-update .count',
                '.update-count',
                'a[href*="update"] span',
                'span[upadte_count]',  # 修复网站的拼写错误
                'span[update_count]'   # 标准拼写
            ]

            for selector in update_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = ParserUtils.safe_get_text(element)
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        update_count = numbers[-1]
                        self._log("debug", f"更新数提取成功: {selector} -> {update_count}")
                        return update_count

            # 文本模式回退
            page_text = soup.get_text()
            update_patterns = [
                r'项目更新\s*(\d+)',
                r'更新\s*(\d+)',
                r'(\d+)\s*次更新',
                r'(\d+)\s*个更新'
            ]

            for pattern in update_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    update_count = matches[-1]
                    self._log("debug", f"更新数文本提取成功: {pattern} -> {update_count}")
                    break

        except Exception as e:
            self._log("debug", f"更新数提取失败: {e}")

        return update_count

    def _extract_nav_from_javascript(self, soup: BeautifulSoup) -> Dict[str, str]:
        """从JavaScript数据中提取导航信息"""
        try:
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text()

                # 查找包含导航数据的JavaScript变量
                patterns = [
                    r'var\s+navData\s*=\s*({[^}]+})',
                    r'window\.navInfo\s*=\s*({[^}]+})',
                    r'PROJECT_NAV\s*=\s*({[^}]+})',
                    r'"update_count"\s*:\s*(\d+)',
                    r'"comment_count"\s*:\s*(\d+)',
                    r'"supporter_count"\s*:\s*(\d+)',

                ]

                nav_data = {}
                for pattern in patterns:
                    matches = re.findall(pattern, script_text)
                    if matches:
                        self._log("debug", f"找到JavaScript导航数据: {matches}")
                        # 尝试解析JSON数据
                        for match in matches:
                            if match.isdigit():
                                continue
                            try:
                                data = json.loads(match)
                                nav_data.update(data)
                            except:
                                pass

                # 直接提取数字
                if 'update_count' in script_text:
                    update_match = re.search(r'"update_count"\s*:\s*(\d+)', script_text)
                    if update_match:
                        nav_data["update_count"] = update_match.group(1)

                if 'comment_count' in script_text:
                    comment_match = re.search(r'"comment_count"\s*:\s*(\d+)', script_text)
                    if comment_match:
                        nav_data["comment_count"] = comment_match.group(1)

                if nav_data:
                    return nav_data

        except Exception as e:
            self._log("debug", f"JavaScript数据提取失败: {e}")

        return {}

    def _extract_nav_from_dom_enhanced(self, soup: BeautifulSoup) -> List[str]:
        """增强的DOM解析"""
        # 这里可以实现更复杂的DOM解析逻辑
        return ["0", "0", "0"]

    def _extract_nav_from_text_enhanced(self, soup: BeautifulSoup) -> List[str]:
        """增强的文本解析"""
        # 这里可以实现更复杂的文本解析逻辑
        return ["0", "0", "0"]

    def _extract_nav_from_dom_fallback(self, soup: BeautifulSoup) -> List[str]:
        """传统DOM解析回退"""
        return ["0", "0", "0"]

    def _validate_nav_data(self, update_count: str, comment_count: str,
                          supporter_count: str) -> tuple:
        """验证和修正导航数据"""

        def validate_number(value: str, field_name: str, max_reasonable: int = 100000) -> str:
            """验证单个数字字段"""
            try:
                if not value or value == "0":
                    return "0"

                num = int(value)
                if num < 0:
                    self._log("warning", f"{field_name}数值异常(负数): {value}")
                    return "0"
                elif num > max_reasonable:
                    self._log("warning", f"{field_name}数值异常(过大): {value}")
                    return str(max_reasonable)
                else:
                    return str(num)
            except ValueError:
                self._log("warning", f"{field_name}数值格式错误: {value}")
                return "0"

        # 验证各字段
        update_count = validate_number(update_count, "更新数", 1000)
        comment_count = validate_number(comment_count, "评论数", 50000)  # 降低评论数上限
        supporter_count = validate_number(supporter_count, "支持者数", 100000)

        # 逻辑验证：支持者数通常不应该为0（除非是新项目）
        if supporter_count == "0" and any(x != "0" for x in [update_count, comment_count]):
            self._log("warning", "支持者数为0但有其他活动数据，可能解析有误")

        return update_count, comment_count, supporter_count
