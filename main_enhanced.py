#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌游市场调研工具 - 增强版爬虫
主要改进：
1. 更好的错误处理和日志记录
2. 数据验证和清理
3. 进度显示和统计
4. 配置文件支持
5. 多格式输出（Excel + JSON + CSV）
6. 性能优化
"""

import random
import re
import socket
import time
import ssl
import json
import csv
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import requests
import xlwt
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.utils.exceptions import IllegalCharacterError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModianSpiderConfig:
    """爬虫配置类"""
    
    def __init__(self):
        self.BASE_URL = "https://zhongchou.modian.com/all/top_time/all/"
        self.OUTPUT_DIR = Path("output")
        self.CACHE_DIR = Path("cache")
        self.MAX_RETRIES = 5
        self.RETRY_DELAY = 2
        self.REQUEST_TIMEOUT = (10, 20)
        self.MAX_PAGES = 3  # 默认测试范围，可以修改为更大值
        self.SAVE_INTERVAL = 5  # 每5页保存一次
        
        # 请求头配置
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # 正则表达式
        self.LINK_ID_PATTERN = re.compile(r'https://zhongchou.modian.com/item/(\d+).html')
        self.USER_ID_PATTERN = re.compile(r'https://me.modian.com/u/detail\?uid=(\d+)')
        
        # 创建必要目录
        self.OUTPUT_DIR.mkdir(exist_ok=True)
        self.CACHE_DIR.mkdir(exist_ok=True)

class ModianSpiderStats:
    """爬虫统计类"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.projects_found = 0
        self.projects_processed = 0
        self.pages_processed = 0
        self.errors = {}
    
    def record_request(self, success: bool):
        """记录请求结果"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
    
    def record_error(self, error_type: str, message: str):
        """记录错误"""
        if error_type not in self.errors:
            self.errors[error_type] = []
        self.errors[error_type].append(message)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        elapsed_time = time.time() - self.start_time
        return {
            "elapsed_time": elapsed_time,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.successful_requests / max(self.total_requests, 1)) * 100,
            "projects_found": self.projects_found,
            "projects_processed": self.projects_processed,
            "pages_processed": self.pages_processed,
            "avg_time_per_page": elapsed_time / max(self.pages_processed, 1),
            "errors": self.errors
        }

class ModianSpider:
    """摩点众筹爬虫主类"""
    
    def __init__(self, config: Optional[ModianSpiderConfig] = None):
        self.config = config or ModianSpiderConfig()
        self.stats = ModianSpiderStats()
        self.session = requests.Session()
        self.session.headers.update(self.config.HEADERS)
        
        # SSL配置
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        logger.info("摩点众筹爬虫初始化完成")
    
    def make_request(self, url: str) -> Optional[str]:
        """发起网络请求"""
        for attempt in range(self.config.MAX_RETRIES):
            try:
                timeout = random.randint(*self.config.REQUEST_TIMEOUT)

                # 使用requests进行请求，自动处理gzip等编码
                response = self.session.get(url, timeout=timeout, verify=False)
                response.raise_for_status()
                response.encoding = 'utf-8'

                self.stats.record_request(True)
                return response.text

            except Exception as e:
                logger.warning(f"第{attempt + 1}次请求失败 {url}: {e}")
                self.stats.record_request(False)
                self.stats.record_error("network_error", str(e))

                if attempt == self.config.MAX_RETRIES - 1:
                    logger.error(f"请求最终失败 {url}")
                    return None

                wait_time = self.config.RETRY_DELAY * (attempt + 1)
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)

        return None
    
    def extract_project_id(self, url: str) -> str:
        """提取项目ID"""
        match = self.config.LINK_ID_PATTERN.search(url)
        return match.group(1) if match else ""
    
    def extract_user_id(self, url: str) -> str:
        """提取用户ID"""
        match = self.config.USER_ID_PATTERN.search(url)
        return match.group(1) if match else ""
    
    def clean_text(self, text: str, max_length: int = 1000) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余空白字符
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def parse_listing_page(self, html: str) -> List[Dict[str, Any]]:
        """解析列表页面"""
        projects = []
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            pro_field_div = soup.find('div', {'class': 'pro_field'})
            
            if not pro_field_div:
                logger.warning("未找到项目列表容器")
                return projects
            
            project_items = pro_field_div.find_all('li')
            logger.info(f"找到 {len(project_items)} 个项目")
            
            for item_li in project_items:
                project = self.parse_project_item(item_li)
                if project:
                    projects.append(project)
                    self.stats.projects_found += 1
            
        except Exception as e:
            logger.error(f"解析列表页面失败: {e}")
            self.stats.record_error("parse_error", str(e))
        
        return projects
    
    def parse_project_item(self, item_li) -> Optional[Dict[str, Any]]:
        """解析单个项目项"""
        try:
            # 查找项目链接
            link_tag = None
            item_link = ""
            
            for a_tag in item_li.find_all('a'):
                href = a_tag.get('href', '')
                if '/item/' in href:
                    link_tag = a_tag
                    item_link = href
                    break
            
            if not item_link:
                return None
            
            if not item_link.startswith("http"):
                item_link = "https://zhongchou.modian.com" + item_link
            
            # 提取项目信息
            project_id = self.extract_project_id(item_link)
            
            # 项目标题
            title = ""
            title_h3 = item_li.find('h3', class_='pro_title')
            if title_h3:
                title = self.clean_text(title_h3.text)
            
            # 项目图片
            img_src = ""
            img_tag = item_li.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag.get('src')
            
            # 跳过特定项目
            if "可汗游戏大会" in title:
                return None
            
            return {
                "link": item_link,
                "id": project_id,
                "title": title,
                "image": img_src
            }
            
        except Exception as e:
            logger.error(f"解析项目项失败: {e}")
            return None
    
    def run(self) -> bool:
        """运行爬虫"""
        logger.info("开始运行摩点众筹爬虫")
        
        all_projects = []
        
        try:
            for page_num in range(1, self.config.MAX_PAGES + 1):
                logger.info(f"正在处理第 {page_num} 页...")
                
                page_url = f"{self.config.BASE_URL}{page_num}"
                html = self.make_request(page_url)
                
                if not html:
                    logger.warning(f"第 {page_num} 页获取失败，跳过")
                    continue
                
                projects = self.parse_listing_page(html)
                all_projects.extend(projects)
                
                self.stats.pages_processed += 1
                
                logger.info(f"第 {page_num} 页处理完成，找到 {len(projects)} 个项目")
                
                # 定期保存
                if page_num % self.config.SAVE_INTERVAL == 0:
                    self.save_data(all_projects, f"intermediate_page_{page_num}")
                
                # 添加延迟避免过于频繁的请求
                time.sleep(random.uniform(1, 3))
            
            # 最终保存
            if all_projects:
                self.save_data(all_projects, "final")
                logger.info(f"爬取完成！共处理 {len(all_projects)} 个项目")
            else:
                logger.warning("未获取到任何项目数据")
            
            # 输出统计信息
            self.print_stats()
            
            return True
            
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
            self.stats.record_error("runtime_error", str(e))
            return False
    
    def save_data(self, projects: List[Dict[str, Any]], suffix: str = ""):
        """保存数据到多种格式"""
        if not projects:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"modian_projects_{timestamp}"
        if suffix:
            base_filename += f"_{suffix}"
        
        # 保存为JSON
        json_file = self.config.OUTPUT_DIR / f"{base_filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存为JSON: {json_file}")
        
        # 保存为CSV
        csv_file = self.config.OUTPUT_DIR / f"{base_filename}.csv"
        if projects:
            df = pd.DataFrame(projects)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            logger.info(f"数据已保存为CSV: {csv_file}")
        
        # 保存为Excel（简化版）
        excel_file = self.config.OUTPUT_DIR / f"{base_filename}.xlsx"
        try:
            df = pd.DataFrame(projects)
            df.to_excel(excel_file, index=False, engine='openpyxl')
            logger.info(f"数据已保存为Excel: {excel_file}")
        except Exception as e:
            logger.error(f"保存Excel文件失败: {e}")
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.stats.get_summary()
        
        print("\n" + "="*60)
        print("📊 爬虫运行统计")
        print("="*60)
        print(f"运行时间: {stats['elapsed_time']:.2f} 秒")
        print(f"处理页面: {stats['pages_processed']}")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"失败请求: {stats['failed_requests']}")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print(f"发现项目: {stats['projects_found']}")
        print(f"平均每页耗时: {stats['avg_time_per_page']:.2f} 秒")
        
        if stats['errors']:
            print("\n错误统计:")
            for error_type, messages in stats['errors'].items():
                print(f"  {error_type}: {len(messages)} 次")
        
        print("="*60)

def main():
    """主函数"""
    print("🚀 启动桌游市场调研工具 - 增强版")
    
    # 创建配置
    config = ModianSpiderConfig()
    
    # 创建爬虫实例
    spider = ModianSpider(config)
    
    # 运行爬虫
    success = spider.run()
    
    if success:
        print("✅ 爬虫运行完成")
    else:
        print("❌ 爬虫运行失败")
    
    return success

if __name__ == "__main__":
    main()
