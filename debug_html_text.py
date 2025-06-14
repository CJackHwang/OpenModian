#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试HTML文本内容，查看金额数据的确切格式
"""

import sys
import re
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from spider.utils import NetworkUtils
from spider.config import SpiderConfig
from bs4 import BeautifulSoup

def debug_html_text():
    """调试HTML文本内容"""
    print("🔍 调试HTML文本内容")
    print("=" * 60)
    
    # 创建网络工具
    config = SpiderConfig()
    network_utils = NetworkUtils(config)
    
    # 测试URL - 我们知道这个项目有金额数据
    test_url = "https://zhongchou.modian.com/item/147828.html"
    
    try:
        print(f"📥 获取页面内容: {test_url}")
        html = network_utils.make_request(test_url)
        
        if not html:
            print("❌ 无法获取页面内容")
            return False
        
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text()
        
        print(f"✅ 页面内容获取成功，文本长度: {len(page_text)}")
        
        # 查找金额相关的文本片段
        print(f"\n🔍 查找金额相关文本:")
        
        # 查找包含"已筹"的行
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if '已筹' in line and line:
                print(f"   已筹相关: '{line}'")
                # 显示前后几行的上下文
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        context_line = lines[j].strip()
                        if context_line:
                            print(f"     上下文: '{context_line}'")
        
        # 查找包含"目标金额"的行
        print(f"\n🎯 查找目标金额相关文本:")
        for i, line in enumerate(lines):
            line = line.strip()
            if '目标金额' in line and line:
                print(f"   目标金额相关: '{line}'")
                # 显示前后几行的上下文
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if j != i:
                        context_line = lines[j].strip()
                        if context_line:
                            print(f"     上下文: '{context_line}'")
        
        # 查找包含"人"和"支持"的行
        print(f"\n👥 查找支持者相关文本:")
        for i, line in enumerate(lines):
            line = line.strip()
            if ('人' in line and '支持' in line) and line:
                print(f"   支持者相关: '{line}'")
        
        # 测试当前的正则表达式
        print(f"\n🧪 测试当前正则表达式:")
        
        # 测试已筹金额
        money_patterns = [
            r'已筹[¥￥]([0-9,]+)',
            r'已筹\s*[¥￥]\s*([0-9,]+)',
            r'已筹[¥￥]\s*([0-9,]+)',
            r'已筹.*?([0-9,]+)',
        ]
        
        for pattern in money_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                print(f"   ✅ 已筹金额模式 '{pattern}' 匹配: {matches}")
            else:
                print(f"   ❌ 已筹金额模式 '{pattern}' 无匹配")
        
        # 测试目标金额
        goal_patterns = [
            r'目标金额\s*[¥￥]([0-9,]+)',
            r'目标金额.*?[¥￥]\s*([0-9,]+)',
            r'目标金额.*?([0-9,]+)',
        ]
        
        for pattern in goal_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                print(f"   ✅ 目标金额模式 '{pattern}' 匹配: {matches}")
            else:
                print(f"   ❌ 目标金额模式 '{pattern}' 无匹配")
        
        # 测试支持者数量
        supporter_patterns = [
            r'(\d+)人\s*支持人数',
            r'支持人数\s*(\d+)',
            r'(\d+)\s*人\s*支持',
            r'支持者\s*(\d+)',
            r'(\d+)\s*支持者',
            r'(\d+)\s*人',
        ]
        
        for pattern in supporter_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                print(f"   ✅ 支持者模式 '{pattern}' 匹配: {matches}")
            else:
                print(f"   ❌ 支持者模式 '{pattern}' 无匹配")
        
        # 显示包含数字和货币符号的所有文本
        print(f"\n💰 所有包含金额符号的文本:")
        money_lines = []
        for line in lines:
            line = line.strip()
            if ('¥' in line or '￥' in line) and re.search(r'\d', line):
                money_lines.append(line)
        
        for line in money_lines[:10]:  # 显示前10行
            print(f"   '{line}'")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 摩点爬虫HTML文本调试")
    print("=" * 60)
    
    success = debug_html_text()
    
    if success:
        print(f"\n🎉 HTML文本调试完成！")
        print(f"✅ 已识别金额数据的确切格式")
        print(f"✅ 可以据此优化正则表达式")
        return True
    else:
        print(f"\n❌ HTML文本调试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
