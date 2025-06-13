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

from .config import SpiderConfig, StatusMapping
from .utils import NetworkUtils, DataUtils, CacheUtils, ParserUtils
from .monitor import SpiderMonitor
from .validator import DataValidator
from .exporter import DataExporter


class ProjectParser:
    """项目解析器"""

    def __init__(self, config: SpiderConfig, network_utils: NetworkUtils):
        self.config = config
        self.network_utils = network_utils
        self.data_utils = DataUtils()

    def _extract_js_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """从JavaScript代码中提取项目数据"""
        js_data = {
            "category": "none",
            "start_time": "none",
            "end_time": "none",
            "project_info": {}
        }

        try:
            # 查找包含PROJECT_INFO的script标签
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.get_text()

                # 提取PROJECT_INFO数据
                if 'PROJECT_INFO.push(JSON.parse(' in script_text:
                    # 使用正则表达式提取JSON字符串
                    pattern = r'PROJECT_INFO\.push\(JSON\.parse\(\'([^\']+)\'\)\);'
                    match = re.search(pattern, script_text)
                    if match:
                        json_str = match.group(1)
                        # 解码Unicode字符
                        json_str = json_str.encode().decode('unicode_escape')
                        try:
                            project_data = json.loads(json_str)
                            js_data["project_info"] = project_data
                            js_data["category"] = project_data.get("category", "none")
                        except json.JSONDecodeError:
                            pass

                # 提取时间信息
                if 'realtime_sync.pro_time(' in script_text:
                    # 提取开始和结束时间
                    time_pattern = r'realtime_sync\.pro_time\([\'"]([^\'\"]+)[\'"],\s*[\'"]([^\'\"]+)[\'"]'
                    time_match = re.search(time_pattern, script_text)
                    if time_match:
                        js_data["start_time"] = time_match.group(1)
                        js_data["end_time"] = time_match.group(2)

        except Exception as e:
            print(f"解析JavaScript数据失败: {e}")

        return js_data
    
    def parse_project_status(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """解析项目状态"""
        status_info = {
            "item_class": "未知情况",
            "is_idea": False,
            "is_preheat": False,
            "is_going": False,
            "is_success": False,
            "is_fail": False
        }
        
        button = ParserUtils.safe_find(soup, 'div', {'class': 'buttons clearfloat'})
        if button:
            button_a = ParserUtils.safe_find(button, 'a')
            if button_a:
                button_text = ParserUtils.safe_get_text(button_a).strip()
                status_info.update(StatusMapping.get_status_info(button_text))
                status_info["raw_status_text"] = button_text
        
        return status_info
    
    def parse_basic_info(self, soup: BeautifulSoup, project_status: Dict) -> List[Any]:
        """解析基础信息"""
        data = []
        
        # 时间信息
        start_time, end_time = self._parse_time_info(soup, project_status)
        data.extend([start_time, end_time, project_status["item_class"]])
        
        # 作者信息
        author_info = self._parse_author_info(soup)
        data.extend(author_info)
        
        # 众筹数据
        funding_info = self._parse_funding_info(soup, project_status)
        data.extend(funding_info)
        
        return data
    
    def _parse_time_info(self, soup: BeautifulSoup, project_status: Dict) -> Tuple[str, str]:
        """解析时间信息"""
        start_time = "none"
        end_time = "none"
        
        if project_status["is_preheat"]:
            time_div = ParserUtils.safe_find(soup, 'div', {'class': 'col2 start-time'})
            if time_div:
                h3_tags = ParserUtils.safe_find_all(time_div, 'h3')
                if h3_tags:
                    start_text = ParserUtils.safe_get_text(h3_tags[0])
                    if "开始" in start_text:
                        start_time = start_text.replace("开始", "").strip()
                    
                    if len(h3_tags) > 1:
                        end_text = ParserUtils.safe_get_text(h3_tags[1])
                        if "结束" in end_text:
                            end_time = end_text.replace("结束", "").strip()
                        else:
                            end_time = "预热中"
                    else:
                        end_time = "预热中"
        
        elif project_status["is_idea"]:
            start_time = "创意中"
            end_time = "创意中"
        
        else:
            # 首先尝试从JavaScript数据中提取时间
            js_data = self._extract_js_data(soup)
            if js_data["start_time"] != "none" and js_data["end_time"] != "none":
                start_time = js_data["start_time"]
                end_time = js_data["end_time"]
            else:
                # 回退到原有的解析逻辑
                time_div = ParserUtils.safe_find(soup, 'div', {'class': 'col2 remain-time'})
                if time_div:
                    h3_tags = ParserUtils.safe_find_all(time_div, 'h3')
                    for h3 in h3_tags:
                        start_attr = ParserUtils.safe_get_attr(h3, 'start_time')
                        end_attr = ParserUtils.safe_get_attr(h3, 'end_time')
                        if start_attr:
                            start_time = start_attr
                        if end_attr:
                            end_time = end_attr

        return self.data_utils.parse_time(start_time), self.data_utils.parse_time(end_time)
    
    def _parse_author_info(self, soup: BeautifulSoup) -> List[str]:
        """解析作者信息"""
        sponsor_info = ParserUtils.safe_find(soup, 'div', {'class': 'sponsor-info clearfix'})
        if not sponsor_info:
            sponsor_info = ParserUtils.safe_find(soup, 'div', {'class': 'sponsor-info'})

        sponsor_href = "none"
        author_image = "none"
        category = "none"
        author_name = "none"
        author_uid = "0"
        author_details = ["0", "0", "0", "{}", "{}", "none"]

        if sponsor_info:
            # 作者链接 - 优化选择器
            sponsor_link = ParserUtils.safe_find(sponsor_info, 'a', {'class': 'sponsor-link'})
            if not sponsor_link:
                # 尝试其他可能的链接选择器
                sponsor_link = ParserUtils.safe_find(sponsor_info, 'a', {'class': 'avater'})
            if not sponsor_link:
                # 查找包含modian.com的链接
                links = ParserUtils.safe_find_all(sponsor_info, 'a')
                for link in links:
                    href = ParserUtils.safe_get_attr(link, 'href')
                    if href and 'modian.com/u/detail' in href:
                        sponsor_link = link
                        break

            if sponsor_link:
                sponsor_href = ParserUtils.safe_get_attr(sponsor_link, 'href')
                sponsor_href = self.data_utils.validate_url(sponsor_href)

                # 获取作者详细信息
                if sponsor_href != "none":
                    user_id = self.data_utils.extract_user_id(sponsor_href)
                    if user_id:
                        author_details = self._fetch_author_details(sponsor_href, user_id)

            # 作者头像 - 优化选择器
            img_tag = ParserUtils.safe_find(sponsor_info, 'img', {'class': 'sponsor-image'})
            if not img_tag:
                # 尝试其他可能的图片选择器
                img_tag = ParserUtils.safe_find(sponsor_info, 'img')
            if img_tag:
                author_image = ParserUtils.safe_get_attr(img_tag, 'src')
                author_image = self.data_utils.validate_url(author_image)

            # 项目分类 - 优化解析逻辑
            # 首先尝试从JavaScript数据中提取
            js_data = self._extract_js_data(soup)
            if js_data["category"] != "none":
                category = js_data["category"]
            else:
                # 回退到HTML解析
                category_span = ParserUtils.safe_find(sponsor_info, 'span', string=lambda text: text and '项目类别：' in text)
                if category_span:
                    category = ParserUtils.safe_get_text(category_span).replace('项目类别：', '').strip()
                else:
                    # 尝试从tags区域获取分类
                    tags_p = ParserUtils.safe_find(sponsor_info, 'p', {'class': 'tags'})
                    if tags_p:
                        category_text = ParserUtils.safe_get_text(tags_p)
                        if '项目类别：' in category_text:
                            category = category_text.replace('项目类别：', '').strip()

            # 作者名称 - 优化选择器
            name_span = ParserUtils.safe_find(sponsor_info, 'span', {'data-nickname': True})
            if name_span:
                raw_name = ParserUtils.safe_get_attr(name_span, 'data-nickname') or ParserUtils.safe_get_text(name_span)
                author_name = self.data_utils.fix_encoding(raw_name)
                author_uid = ParserUtils.safe_get_attr(name_span, 'data-username', "0")
            else:
                # 尝试其他可能的名称选择器
                name_span = ParserUtils.safe_find(sponsor_info, 'span', {'class': 'name'})
                if name_span:
                    raw_name = ParserUtils.safe_get_text(name_span)
                    author_name = self.data_utils.fix_encoding(raw_name)

        result = [sponsor_href, author_image, category, author_name, author_uid]
        result.extend(author_details)
        return result
    
    def _fetch_author_details(self, author_url: str, user_id: str) -> List[str]:
        """获取作者详细信息"""
        try:
            # 尝试从API获取
            api_data = self.network_utils.make_api_request(
                "/apis/comm/user/user_info",
                {"json_type": 1, "to_user_id": user_id, "user_id": user_id}
            )
            
            if api_data and api_data.get("status") == 1:
                user_info = api_data.get("data", {})
                return [
                    str(user_info.get("fans_count", 0)),
                    str(user_info.get("following_count", 0)),
                    str(user_info.get("like_count", 0)),
                    str(user_info.get("detail", {})),
                    str(user_info.get("other_info", {})),
                    author_url
                ]
            
            # 如果API失败，尝试解析页面
            html = self.network_utils.make_request(author_url, header_type="mobile")
            if html:
                return self._parse_author_page(html, user_id, author_url)
            
        except Exception as e:
            print(f"获取作者信息失败: {e}")
        
        return ["0", "0", "0", "{}", "{}", author_url]
    
    def _parse_author_page(self, html: str, user_id: str, author_url: str) -> List[str]:
        """解析作者页面"""
        soup = BeautifulSoup(html, "html.parser")
        
        fans_num = "0"
        following_num = "0"
        likes_num = "0"
        
        # 解析粉丝、关注、获赞数
        banner_div = ParserUtils.safe_find(soup, 'div', {'class': 'banner'})
        if banner_div:
            cont_div = ParserUtils.safe_find(banner_div, 'div', {'class': 'cont'})
            if cont_div:
                # 粉丝数
                fans_span = ParserUtils.safe_find(cont_div, 'span', {'class': 'go_span fans'})
                if fans_span:
                    fans_i = ParserUtils.safe_find(fans_span, 'i')
                    if fans_i:
                        fans_text = ParserUtils.safe_get_text(fans_i)
                        fans_num = self.data_utils.extract_number(fans_text)
                
                # 关注数和获赞数
                spans = ParserUtils.safe_find_all(cont_div, 'span')
                for span in spans:
                    text = ParserUtils.safe_get_text(span)
                    if '关注' in text:
                        following_num = self.data_utils.extract_number(text)
                    elif '获赞' in text or 'ALL' in ParserUtils.safe_get_attr(span, 'id'):
                        likes_num = self.data_utils.extract_number(text)
        
        # 解析详细信息
        detail_result = {}
        detail_div = ParserUtils.safe_find(soup, 'div', {'class': 'detail'})
        if detail_div:
            items = ParserUtils.safe_find_all(detail_div, 'div', class_='item')
            for item in items:
                label = ParserUtils.safe_find(item, 'label')
                p = ParserUtils.safe_find(item, 'p')
                if label and p:
                    detail_result[ParserUtils.safe_get_text(label)] = ParserUtils.safe_get_text(p)
        
        # 解析其他信息
        other_result = {}
        other_div = ParserUtils.safe_find(soup, 'div', {'class': 'other_info'})
        if other_div:
            items = ParserUtils.safe_find_all(other_div, 'div', class_='item')
            for item in items:
                p_tags = ParserUtils.safe_find_all(item, 'p')
                if len(p_tags) >= 2:
                    key = ParserUtils.safe_get_text(p_tags[1])
                    value = ParserUtils.safe_get_text(p_tags[0])
                    if value.isdigit():
                        other_result[key] = int(value)
        
        return [
            fans_num,
            following_num, 
            likes_num,
            str(detail_result),
            str(other_result),
            author_url
        ]
    
    def _parse_funding_info(self, soup: BeautifulSoup, project_status: Dict) -> List[str]:
        """解析众筹信息"""
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
    
    def parse_project_content(self, soup: BeautifulSoup) -> List[Any]:
        """解析项目内容"""
        data = []
        
        # 回报信息
        rewards_info = self._parse_rewards(soup)
        data.extend(rewards_info)
        
        # 导航信息
        nav_info = self._parse_nav_info(soup)
        data.extend(nav_info)
        
        # 项目详情
        content_info = self._parse_content_media(soup)
        data.extend(content_info)
        
        return data
    
    def _parse_rewards(self, soup: BeautifulSoup) -> List[Any]:
        """解析回报信息"""
        rewards_list = []
        
        main_right = ParserUtils.safe_find(soup, 'div', {'class': 'main-right'})
        if main_right:
            payback_div = ParserUtils.safe_find(main_right, 'div', {'class': 'payback-lists margin36'})
            if payback_div:
                reward_items = ParserUtils.safe_find_all(payback_div, 'div', class_=lambda x: x and 'back-list' in x)
                
                for item in reward_items:
                    reward_data = self._parse_single_reward(item)
                    rewards_list.append(str(reward_data))
        
        return [str(rewards_list), len(rewards_list)]
    
    def _parse_single_reward(self, item) -> List[str]:
        """解析单个回报项"""
        # 回报金额
        head_div = ParserUtils.safe_find(item, 'div', {'class': 'head'})
        back_money = "0"
        backers = "0"

        if head_div:
            money_span = ParserUtils.safe_find(head_div, 'span')
            if money_span:
                money_text = ParserUtils.safe_get_text(money_span).replace('￥', '')
                back_money = self.data_utils.extract_number(money_text)

            em_tag = ParserUtils.safe_find(head_div, 'em')
            if em_tag:
                em_text = ParserUtils.safe_get_text(em_tag)
                if "已满" in em_text:
                    backers = "已满"
                else:
                    backers = self.data_utils.extract_number(em_text)

        # 限量信息
        sign_logo = "0"
        subhead_div = ParserUtils.safe_find(item, 'div', {'class': 'zc-subhead'})
        if subhead_div:
            sign_span = ParserUtils.safe_find(subhead_div, 'span')
            if sign_span:
                sign_text = ParserUtils.safe_get_text(sign_span)
                if "限量" in sign_text:
                    num_part = sign_text.replace("限量", "").replace("份", "").strip()
                    sign_logo = f"限量 {num_part}" if num_part.isdigit() else "限量"

        # 回报内容
        content_div = ParserUtils.safe_find(item, 'div', {'class': 'back-content'})
        title = "none"
        detail = "none"
        time_info = "none"

        if content_div:
            title_div = ParserUtils.safe_find(content_div, 'div', {'class': 'back-sub-title'})
            if title_div:
                raw_title = ParserUtils.safe_get_text(title_div)
                title = self.data_utils.clean_reward_text(raw_title)

            detail_div = ParserUtils.safe_find(content_div, 'div', {'class': 'back-detail'})
            if detail_div:
                raw_detail = ParserUtils.safe_get_text(detail_div)
                detail = self.data_utils.clean_reward_text(raw_detail)

            time_div = ParserUtils.safe_find(content_div, 'div', {'class': 'back-time'})
            if time_div:
                raw_time = ParserUtils.safe_get_text(time_div)
                time_info = self.data_utils.clean_reward_text(raw_time)

        return [title, sign_logo, back_money, backers, time_info, detail]
    
    def _parse_nav_info(self, soup: BeautifulSoup) -> List[str]:
        """解析导航信息"""
        update_count = "0"
        comment_count = "0"
        supporter_count = "0"
        collect_count = "0"
        
        nav_wrap = ParserUtils.safe_find(soup, 'div', {'class': 'nav-wrap-inner'})
        if nav_wrap:
            nav_left = ParserUtils.safe_find(nav_wrap, 'ul', {'class': 'nav-left'})
            if nav_left:
                # 更新数
                update_li = ParserUtils.safe_find(nav_left, 'li', {'class': 'pro-gengxin'})
                if update_li:
                    update_span = ParserUtils.safe_find(update_li, 'span')
                    if update_span:
                        update_count = self.data_utils.extract_number(ParserUtils.safe_get_text(update_span))
                
                # 评论数
                comment_li = ParserUtils.safe_find(nav_left, 'li', {'class': 'nav-comment'})
                if comment_li:
                    comment_span = ParserUtils.safe_find(comment_li, 'span')
                    if comment_span:
                        comment_count = self.data_utils.extract_number(ParserUtils.safe_get_text(comment_span))
                
                # 支持者/点赞数
                userlist_li = ParserUtils.safe_find(nav_left, 'li', class_='dialog_user_list')
                if userlist_li:
                    user_span = ParserUtils.safe_find(userlist_li, 'span')
                    if user_span:
                        supporter_count = self.data_utils.extract_number(ParserUtils.safe_get_text(user_span))
            
            # 收藏数
            nav_right = ParserUtils.safe_find(nav_wrap, 'ul', {'class': 'nav-right'})
            if nav_right:
                atten_li = ParserUtils.safe_find(nav_right, 'li', {'class': 'atten'})
                if atten_li:
                    atten_span = ParserUtils.safe_find(atten_li, 'span')
                    if atten_span:
                        collect_count = self.data_utils.extract_number(ParserUtils.safe_get_text(atten_span))
        
        return [update_count, comment_count, supporter_count, collect_count]
    
    def _parse_content_media(self, soup: BeautifulSoup) -> List[Any]:
        """解析项目媒体内容"""
        img_list = []
        video_list = []
        
        main_left = ParserUtils.safe_find(soup, 'div', {'class': 'main-left'})
        if main_left:
            content_div = ParserUtils.safe_find(main_left, 'div', {'class': 'project-content'})
            if content_div:
                # 图片
                img_tags = ParserUtils.safe_find_all(content_div, 'img')
                for img in img_tags:
                    src = ParserUtils.safe_get_attr(img, 'src')
                    if src:
                        img_list.append(self.data_utils.validate_url(src))
                
                # 视频
                video_tags = ParserUtils.safe_find_all(content_div, 'video')
                for video in video_tags:
                    src = ParserUtils.safe_get_attr(video, 'src')
                    if src:
                        video_list.append(self.data_utils.validate_url(src))
                    else:
                        # 检查source标签
                        sources = ParserUtils.safe_find_all(video, 'source')
                        for source in sources:
                            src = ParserUtils.safe_get_attr(source, 'src')
                            if src:
                                video_list.append(self.data_utils.validate_url(src))
                                break
        
        return [len(img_list), str(img_list), len(video_list), str(video_list)]


class SpiderCore:
    """爬虫核心类"""

    def __init__(self, config: SpiderConfig = None):
        self.config = config or SpiderConfig()
        self.config.create_directories()

        # 初始化组件
        self.network_utils = NetworkUtils(self.config)
        self.cache_utils = CacheUtils(self.config)
        self.monitor = SpiderMonitor(self.config)
        self.validator = DataValidator(self.config)
        self.exporter = DataExporter(self.config)
        self.parser = ProjectParser(self.config, self.network_utils)

        # 数据存储
        self.projects_data = []
        self.failed_urls = []

        # 线程锁
        self._lock = threading.Lock()

        print(f"爬虫初始化完成，输出目录: {self.config.OUTPUT_DIR}")

    def start_crawling(self, start_page: int = 1, end_page: int = 50,
                      category: str = "all") -> bool:
        """开始爬取"""
        try:
            print(f"开始爬取摩点众筹数据...")
            print(f"页面范围: {start_page}-{end_page}")
            print(f"分类: {category}")

            # 启动监控
            self.monitor.start_monitoring()

            # 爬取项目列表
            project_urls = self._crawl_project_lists(start_page, end_page, category)

            if not project_urls:
                print("未找到任何项目URL")
                return False

            print(f"发现 {len(project_urls)} 个项目，开始详细爬取...")

            # 爬取项目详情
            success = self._crawl_project_details(project_urls)

            # 停止监控
            self.monitor.stop_monitoring()

            # 数据验证
            if self.projects_data:
                self._validate_and_export_data()

            # 打印统计信息
            self.monitor.print_stats()

            return success

        except KeyboardInterrupt:
            print("\n用户中断爬取")
            self.monitor.stop_monitoring()
            return False
        except Exception as e:
            print(f"爬取过程中出现错误: {e}")
            self.monitor.record_error("crawling_error", str(e))
            self.monitor.stop_monitoring()
            return False

    def _crawl_project_lists(self, start_page: int, end_page: int,
                           category: str) -> List[Tuple[str, str, str, str]]:
        """爬取项目列表页面"""
        project_urls = []

        for page in range(start_page, end_page + 1):
            try:
                print(f"正在爬取第 {page} 页...")

                url = self.config.get_full_url(category, page)
                page_projects = self._parse_project_list_page(url, page)

                if page_projects:
                    project_urls.extend(page_projects)
                    self.monitor.record_page(True)
                    print(f"第 {page} 页发现 {len(page_projects)} 个项目")
                else:
                    self.monitor.record_page(False)
                    print(f"第 {page} 页未发现项目")

                # 检查是否需要停止
                if self.monitor.stats.consecutive_errors > self.config.MAX_CONSECUTIVE_ERRORS:
                    print("连续错误过多，停止爬取")
                    break

            except Exception as e:
                print(f"爬取第 {page} 页失败: {e}")
                self.monitor.record_error("page_crawl_error", str(e))
                self.monitor.record_page(False)

        return project_urls

    def _parse_project_list_page(self, url: str, page: int) -> List[Tuple[str, str, str, str]]:
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

    def _extract_projects_from_list(self, html: str) -> List[Tuple[str, str, str, str]]:
        """从列表页面提取项目信息"""
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

                    projects.append((project_url, project_id, project_name, project_image))
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

    def _crawl_project_details(self, project_urls: List[Tuple[str, str, str, str]]) -> bool:
        """爬取项目详情"""
        if not project_urls:
            return False

        # 使用线程池并发爬取
        with ThreadPoolExecutor(max_workers=self.config.MAX_CONCURRENT_REQUESTS) as executor:
            # 提交任务
            future_to_project = {
                executor.submit(self._crawl_single_project, i, project_info): project_info
                for i, project_info in enumerate(project_urls)
            }

            # 处理结果
            completed = 0
            for future in as_completed(future_to_project):
                project_info = future_to_project[future]

                try:
                    result = future.result()
                    if result:
                        with self._lock:
                            self.projects_data.append(result)
                        self.monitor.record_project("processed")
                    else:
                        self.monitor.record_project("failed")
                        self.failed_urls.append(project_info[0])

                except Exception as e:
                    print(f"处理项目失败 {project_info[2]}: {e}")
                    self.monitor.record_error("project_process_error", str(e))
                    self.monitor.record_project("failed")
                    self.failed_urls.append(project_info[0])

                completed += 1
                if completed % 10 == 0:
                    print(f"已完成 {completed}/{len(project_urls)} 个项目")

        print(f"项目详情爬取完成，成功: {len(self.projects_data)}, 失败: {len(self.failed_urls)}")
        return len(self.projects_data) > 0

    def _crawl_single_project(self, index: int, project_info: Tuple[str, str, str, str]) -> Optional[List[Any]]:
        """爬取单个项目详情"""
        project_url, project_id, project_name, project_image = project_info

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

            # 解析项目详情
            parse_start = time.time()
            project_data = self._parse_project_detail(html, index + 1, project_url, project_id, project_name, project_image)
            parse_time = time.time() - parse_start
            self.monitor.record_parse(parse_time)

            return project_data

        except Exception as e:
            print(f"爬取项目详情失败 {project_name}: {e}")
            self.monitor.record_error("project_detail_error", str(e))
            return None

    def _parse_project_detail(self, html: str, index: int, project_url: str,
                            project_id: str, project_name: str, project_image: str) -> List[Any]:
        """解析项目详情页面"""
        soup = BeautifulSoup(html, "html.parser")

        # 基础信息
        project_data = [index, project_url, project_id, project_name, project_image]

        # 解析项目状态
        project_status = self.parser.parse_project_status(soup)

        # 解析基础信息
        basic_info = self.parser.parse_basic_info(soup, project_status)
        project_data.extend(basic_info)

        # 解析项目内容
        content_info = self.parser.parse_project_content(soup)
        project_data.extend(content_info)

        return project_data

    def _validate_and_export_data(self):
        """验证和导出数据"""
        print("开始数据验证...")

        # 批量验证
        validation_results = self.validator.validate_batch(self.projects_data)

        # 记录验证结果
        for result in validation_results['results']:
            self.monitor.record_validation(result['is_valid'])

        # 打印验证摘要
        print(self.validator.get_validation_summary(validation_results))

        # 导出数据
        print("开始导出数据...")

        try:
            # 导出Excel
            excel_file = self.exporter.export_to_excel(self.projects_data, self.config.EXCEL_FILENAME)

            # 导出JSON
            json_file = self.exporter.export_to_json(self.projects_data, self.config.JSON_FILENAME)

            # 导出摘要报告
            stats = self.monitor.get_current_stats()
            summary_file = self.exporter.export_summary_report(self.projects_data, stats)

            # 保存统计报告
            stats_file = f"{self.config.OUTPUT_DIR}/spider_stats_{time.strftime('%Y%m%d_%H%M%S')}.json"
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

    def save_progress(self):
        """保存进度"""
        if self.projects_data:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            progress_file = f"{self.config.OUTPUT_DIR}/progress_{timestamp}.json"

            progress_data = {
                "timestamp": timestamp,
                "projects_count": len(self.projects_data),
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
