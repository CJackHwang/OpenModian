# -*- coding: utf-8 -*-
"""
众筹数据提取器
负责从项目页面提取众筹相关的数据（金额、百分比、支持者等）
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from ..config import SpiderConfig
from ..utils import DataUtils, ParserUtils


class FundingExtractor:
    """众筹数据提取器"""

    def __init__(self, config: SpiderConfig, web_monitor=None):
        self.config = config
        self.data_utils = DataUtils()
        self.web_monitor = web_monitor

    def _log(self, level: str, message: str):
        """统一日志输出"""
        print(message)
        if self.web_monitor:
            self.web_monitor.add_log(level, message)

    def extract_funding_info(self, soup: BeautifulSoup, project_status: Dict) -> List[str]:
        """智能适配解析众筹信息"""
        money = "0"
        percent = "0"
        goal_money = "0"
        sponsor_num = "0"

        try:
            self._log("info", "开始解析众筹信息...")

            # 1. 提取已筹金额
            backer_money_spans = soup.find_all('span', attrs={'backer_money': True})
            for span in backer_money_spans:
                span_text = ParserUtils.safe_get_text(span).strip()
                if span_text:
                    # 清理文本，移除货币符号和逗号
                    clean_money = span_text.replace(',', '').replace('¥', '').replace('￥', '').strip()
                    if clean_money.replace('.', '').isdigit():
                        money = clean_money
                        self._log("info", f"✅ 从backer_money属性提取已筹金额: ¥{money}")
                        break

            # 2. 提取完成率
            percent_elements = soup.find_all('span', class_='percent')
            for elem in percent_elements:
                percent_text = ParserUtils.safe_get_text(elem).strip()
                if percent_text and '%' in percent_text:
                    percent = percent_text.replace('%', '').strip()
                    self._log("info", f"✅ 从percent类提取完成率: {percent}%")
                    break

            # 如果percent类没找到，尝试rate属性
            if percent == "0":
                rate_spans = soup.find_all('span', attrs={'rate': True})
                for span in rate_spans:
                    span_text = ParserUtils.safe_get_text(span).strip()
                    if span_text and '%' in span_text:
                        percent = span_text.replace('%', '').strip()
                        self._log("info", f"✅ 从rate属性提取完成率: {percent}%")
                        break

            # 3. 提取支持者数量
            support_people_divs = soup.find_all('div', class_='col3 support-people')
            for div in support_people_divs:
                span = div.find('span')
                if span:
                    span_text = ParserUtils.safe_get_text(span).strip()
                    if span_text.isdigit():
                        sponsor_num = span_text
                        self._log("info", f"✅ 从support-people类提取支持者数量: {sponsor_num}人")
                        break

            # 如果support-people类没找到，尝试backer_count属性
            if sponsor_num == "0":
                backer_count_spans = soup.find_all('span', attrs={'backer_count': True})
                for span in backer_count_spans:
                    span_text = ParserUtils.safe_get_text(span).strip()
                    if span_text and span_text.isdigit():
                        sponsor_num = span_text
                        self._log("info", f"✅ 从backer_count属性提取支持者数量: {sponsor_num}人")
                        break

            # 4. 提取目标金额
            goal_money_elements = soup.find_all('span', class_='goal-money')
            for elem in goal_money_elements:
                goal_text = ParserUtils.safe_get_text(elem).strip()
                # 处理目标金额文本
                if '¥' in goal_text:
                    goal_money = goal_text[goal_text.index('¥')+1:].replace(',', '').strip()
                elif '￥' in goal_text:
                    goal_money = goal_text[goal_text.index('￥')+1:].replace(',', '').strip()
                else:
                    # 提取数字部分
                    goal_match = re.search(r'([0-9,]+)', goal_text)
                    if goal_match:
                        goal_money = goal_match.group(1).replace(',', '')

                if goal_money and goal_money.isdigit():
                    self._log("info", f"✅ 从goal-money类提取目标金额: ¥{goal_money}")
                    break

            # 回退到文本解析（如果HTML属性提取失败）
            if money == "0" or goal_money == "0" or sponsor_num == "0":
                self._log("info", "HTML属性提取不完整，回退到文本解析...")
                text_data = self._extract_from_text(soup)
                
                if money == "0" and text_data["money"] != "0":
                    money = text_data["money"]
                if goal_money == "0" and text_data["goal_money"] != "0":
                    goal_money = text_data["goal_money"]
                if percent == "0" and text_data["percent"] != "0":
                    percent = text_data["percent"]
                if sponsor_num == "0" and text_data["sponsor_num"] != "0":
                    sponsor_num = text_data["sponsor_num"]

            # 智能金额匹配（如果仍有缺失数据）
            if money == "0" or goal_money == "0":
                money, goal_money = self._smart_money_matching(soup, money, goal_money, percent)

            # 验证数据合理性
            self._validate_extracted_data(money, percent, goal_money, sponsor_num)

            self._log("info", f"✅ 众筹信息解析完成: 已筹¥{money}, 目标¥{goal_money}, 完成率{percent}%, 支持者{sponsor_num}人")

        except Exception as e:
            self._log("warning", f"众筹信息解析失败: {e}")
            # 回退到传统解析
            return self._parse_funding_info_fallback(soup, project_status)

        return [money, percent, goal_money, sponsor_num]

    def _extract_from_text(self, soup: BeautifulSoup) -> Dict[str, str]:
        """从页面文本中提取众筹数据"""
        page_text = soup.get_text()
        result = {"money": "0", "goal_money": "0", "percent": "0", "sponsor_num": "0"}

        # 解析已筹金额 - 处理编码问题 "已筹¥1,608"
        money_patterns = [
            r'已筹[¥￥Â¥]([0-9,]+)',  # 正常编码
            r'å·²ç­¹[¥￥Â¥]([0-9,]+)',  # 编码后的中文
            r'已筹.*?[¥￥Â¥]\s*([0-9,]+)',  # 宽松匹配
            r'å·²ç­¹.*?[¥￥Â¥]\s*([0-9,]+)'   # 编码后宽松匹配
        ]

        for pattern in money_patterns:
            money_match = re.search(pattern, page_text)
            if money_match:
                result["money"] = self.data_utils.format_money(money_match.group(1).replace(',', ''))
                self._log("info", f"文本解析找到已筹金额: ¥{result['money']}")
                break

        # 解析目标金额 - 处理编码问题和多种格式
        goal_patterns = [
            r'目标金额\s*[¥￥Â¥]([0-9,]+)',  # 正常编码
            r'ç®æ éé¢\s*[¥￥Â¥]([0-9,]+)',  # 编码后的中文
            r'目标金额.*?[¥￥Â¥]\s*([0-9,]+)',  # 宽松匹配
            r'ç®æ éé¢.*?[¥￥Â¥]\s*([0-9,]+)',   # 编码后宽松匹配
            r'目标[¥￥Â¥]([0-9,]+)',  # 简化格式
            r'ç®æ[¥￥Â¥]([0-9,]+)',  # 编码后简化格式
            r'目标.*?([0-9,]+)',  # 最宽松匹配
            r'ç®æ.*?([0-9,]+)'   # 编码后最宽松匹配
        ]

        for pattern in goal_patterns:
            goal_match = re.search(pattern, page_text)
            if goal_match:
                result["goal_money"] = self.data_utils.format_money(goal_match.group(1).replace(',', ''))
                self._log("info", f"文本解析找到目标金额: ¥{result['goal_money']}")
                break

        # 解析完成百分比 - "160.8%"
        percent_match = re.search(r'([0-9.]+)%', page_text)
        if percent_match:
            result["percent"] = percent_match.group(1)
            self._log("info", f"文本解析找到完成百分比: {result['percent']}%")

        # 解析支持者数量
        supporter_matches = re.findall(r'(\d+)\s*支持者', page_text)
        if supporter_matches:
            result["sponsor_num"] = supporter_matches[0]
            self._log("info", f"文本解析找到支持者数量: {result['sponsor_num']}人")
        else:
            # 回退到其他模式
            supporter_patterns = [
                r'(\d+)\s*人\s*支持',
                r'支持者\s*(\d+)',
                r'支持人数\s*(\d+)',
                r'(\d+)\s*人',  # 最宽松的模式
            ]

            for pattern in supporter_patterns:
                supporter_match = re.search(pattern, page_text)
                if supporter_match:
                    result["sponsor_num"] = supporter_match.group(1)
                    self._log("info", f"文本解析回退模式找到支持者数量: {result['sponsor_num']}人")
                    break

        return result

    def _smart_money_matching(self, soup: BeautifulSoup, money: str, goal_money: str, percent: str) -> tuple:
        """智能金额匹配"""
        page_text = soup.get_text()
        all_money_matches = re.findall(r'[¥￥]\s*([0-9,]+)', page_text)
        
        if len(all_money_matches) >= 2:
            # 清理并转换为数字
            money_values = []
            for match in all_money_matches:
                clean_value = match.replace(',', '')
                if clean_value.isdigit():
                    money_values.append(int(clean_value))

            if len(money_values) >= 2:
                # 根据百分比智能判断哪个是已筹，哪个是目标
                if percent != "0":
                    try:
                        percent_val = float(percent)
                        if percent_val > 100:
                            # 超额完成，已筹应该是较大值
                            money = str(max(money_values))
                            remaining = [v for v in money_values if v != max(money_values)]
                            goal_money = str(max(remaining)) if remaining else str(min(money_values))
                        else:
                            # 未完成，已筹应该是较小值
                            money = str(min(money_values))
                            remaining = [v for v in money_values if v != min(money_values)]
                            goal_money = str(max(remaining)) if remaining else str(max(money_values))

                        self._log("info", f"智能匹配金额: 已筹¥{money}, 目标¥{goal_money} (基于{percent}%)")
                    except ValueError:
                        # 如果百分比解析失败，使用默认逻辑
                        money_values.sort()
                        money = str(money_values[0])
                        goal_money = str(money_values[1])
                        self._log("info", f"默认匹配金额: 已筹¥{money}, 目标¥{goal_money}")
                else:
                    # 没有百分比信息，使用默认逻辑
                    money_values.sort()
                    money = str(money_values[0])
                    goal_money = str(money_values[1])
                    self._log("info", f"无百分比，默认匹配: 已筹¥{money}, 目标¥{goal_money}")

        return money, goal_money

    def _validate_extracted_data(self, money: str, percent: str, goal_money: str, sponsor_num: str):
        """验证提取的数据合理性（不进行反推计算）"""
        try:
            # 验证金额数据
            if money != "0":
                money_val = float(money)
                if money_val < 0:
                    self._log("warning", f"已筹金额异常: {money}")
                elif money_val > 10000000:  # 1000万
                    self._log("warning", f"已筹金额过大: {money}")

            if goal_money != "0":
                goal_val = float(goal_money)
                if goal_val < 0:
                    self._log("warning", f"目标金额异常: {goal_money}")
                elif goal_val > 50000000:  # 5000万
                    self._log("warning", f"目标金额过大: {goal_money}")

            # 验证百分比数据
            if percent != "0":
                percent_val = float(percent)
                if percent_val < 0:
                    self._log("warning", f"完成百分比异常: {percent}%")
                elif percent_val > 10000:  # 100倍
                    self._log("warning", f"完成百分比过大: {percent}%")
                else:
                    self._log("info", f"百分比数据正常: {percent}%")

            # 验证支持者数量
            if sponsor_num != "0":
                supporter_val = int(sponsor_num)
                if supporter_val < 0:
                    self._log("warning", f"支持者数量异常: {supporter_val}")
                elif supporter_val > 100000:
                    self._log("warning", f"支持者数量过大: {supporter_val}")
                else:
                    self._log("info", f"支持者数量正常: {supporter_val}")

            # 逻辑一致性检查（不修改数据）
            if money != "0" and goal_money != "0" and percent != "0":
                money_val = float(money)
                goal_val = float(goal_money)
                percent_val = float(percent)

                theoretical_percent = (money_val / goal_val) * 100
                if abs(theoretical_percent - percent_val) > 50:  # 允许较大误差
                    self._log("info", f"数据一致性提示: 显示{percent_val}%, 理论{theoretical_percent:.1f}%")
                else:
                    self._log("info", f"数据一致性良好")

        except (ValueError, ZeroDivisionError) as e:
            self._log("debug", f"数据验证跳过: {e}")

    def _parse_funding_info_fallback(self, soup: BeautifulSoup, project_status: Dict) -> List[str]:
        """传统众筹信息解析方法"""
        money = "0"
        percent = "0"
        goal_money = "0"
        sponsor_num = "0"
        
        center_div = ParserUtils.safe_find(soup, 'div', {'class': 'center'})
        if not center_div:
            return [money, percent, goal_money, sponsor_num]
        
        if project_status["is_preheat"]:
            # 预热阶段
            goal_div = ParserUtils.safe_find(center_div, 'div', {'class': 'col1 project-goal'})
            if goal_div:
                goal_span = ParserUtils.safe_find(goal_div, 'span')
                if goal_span:
                    goal_money = ParserUtils.safe_get_text(goal_span).replace('￥', '')
                    goal_money = self.data_utils.extract_number(goal_money)
            
            subscribe_span = ParserUtils.safe_find(center_div, 'span', {'subscribe_count': True})
            if subscribe_span:
                sponsor_num = ParserUtils.safe_get_attr(subscribe_span, 'subscribe_count')
                if not sponsor_num:
                    sponsor_num = ParserUtils.safe_get_text(subscribe_span).replace('人订阅', '')
                sponsor_num = self.data_utils.extract_number(sponsor_num)
        
        elif project_status["is_idea"]:
            # 创意阶段
            goal_money = 'none'
            sponsor_num = 'none'
        
        else:
            # 众筹中、成功、失败阶段
            money_span = ParserUtils.safe_find(center_div, 'span', {'backer_money': True})
            if money_span:
                money = ParserUtils.safe_get_text(money_span).replace('￥', '')
                money = self.data_utils.format_money(money)
            
            rate_span = ParserUtils.safe_find(center_div, 'span', {'rate': True})
            if rate_span:
                percent = ParserUtils.safe_get_text(rate_span).replace('%', '')
                percent = self.data_utils.extract_percentage(percent + '%')
            
            goal_span = ParserUtils.safe_find(center_div, 'span', {'class': 'goal-money'})
            if goal_span:
                goal_text = ParserUtils.safe_get_text(goal_span)
                # 处理编码问题和多种格式
                import re
                # 使用正则表达式提取金额数字
                amount_match = re.search(r'[¥￥]\s*([0-9,]+)', goal_text)
                if amount_match:
                    goal_money = amount_match.group(1).replace(',', '')
                    goal_money = self.data_utils.format_money(goal_money)
                else:
                    # 尝试直接提取数字
                    numbers = re.findall(r'[0-9,]+', goal_text)
                    if numbers:
                        goal_money = numbers[-1].replace(',', '')  # 取最后一个数字
                        goal_money = self.data_utils.format_money(goal_money)
            
            backer_span = ParserUtils.safe_find(center_div, 'span', {'backer_count': True})
            if backer_span:
                sponsor_num = ParserUtils.safe_get_attr(backer_span, 'backer_count')
                if not sponsor_num:
                    sponsor_num = ParserUtils.safe_get_text(backer_span).replace('人支持', '')
                sponsor_num = self.data_utils.extract_number(sponsor_num)
        
        return [money, percent, goal_money, sponsor_num]
