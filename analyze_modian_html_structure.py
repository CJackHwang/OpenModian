#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析摩点网页的真实HTML结构
找到准确的数据获取方式，避免反推计算
"""

import sys
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_modian_page_structure():
    """分析摩点页面的真实HTML结构"""
    print("🔍 分析摩点网页真实HTML结构")
    print("=" * 60)
    
    try:
        from spider.config import SpiderConfig
        from spider.utils import NetworkUtils
        
        config = SpiderConfig()
        network_utils = NetworkUtils(config)
        
        # 测试几个不同的项目页面
        test_urls = [
            "https://zhongchou.modian.com/item/2250000.html",  # 桌游项目
            "https://zhongchou.modian.com/item/2249000.html",  # 另一个项目
        ]
        
        for i, test_url in enumerate(test_urls):
            print(f"\n🌐 分析页面 {i+1}: {test_url}")
            print("-" * 50)
            
            # 获取页面内容
            html = network_utils.make_request(test_url)
            if not html:
                print(f"❌ 无法获取页面内容")
                continue
            
            soup = BeautifulSoup(html, "html.parser")
            
            # 分析页面结构
            analyze_funding_info_structure(soup, test_url)
            analyze_nav_info_structure(soup, test_url)
            analyze_author_info_structure(soup, test_url)
            
            if i == 0:  # 只分析第一个页面的详细结构
                save_html_structure_analysis(soup, test_url)
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_funding_info_structure(soup: BeautifulSoup, url: str):
    """分析众筹信息的HTML结构"""
    print(f"\n💰 众筹信息结构分析")
    print("-" * 30)
    
    # 查找所有包含金额的元素
    money_elements = []
    
    # 查找包含¥符号的元素
    for element in soup.find_all(text=re.compile(r'[¥￥]')):
        parent = element.parent
        if parent:
            text = element.strip()
            if re.search(r'[¥￥]\s*[\d,]+', text):
                money_elements.append({
                    'text': text,
                    'tag': parent.name,
                    'class': parent.get('class', []),
                    'id': parent.get('id', ''),
                    'parent_tag': parent.parent.name if parent.parent else '',
                    'parent_class': parent.parent.get('class', []) if parent.parent else []
                })
    
    print(f"📊 找到 {len(money_elements)} 个金额相关元素:")
    for i, elem in enumerate(money_elements[:10]):  # 显示前10个
        print(f"   {i+1}. 文本: '{elem['text']}'")
        print(f"      标签: <{elem['tag']} class='{elem['class']}' id='{elem['id']}'>")
        print(f"      父级: <{elem['parent_tag']} class='{elem['parent_class']}'>")
        print()
    
    # 查找包含百分比的元素
    percent_elements = []
    for element in soup.find_all(text=re.compile(r'\d+\.?\d*%')):
        parent = element.parent
        if parent:
            text = element.strip()
            percent_elements.append({
                'text': text,
                'tag': parent.name,
                'class': parent.get('class', []),
                'id': parent.get('id', ''),
            })
    
    print(f"📈 找到 {len(percent_elements)} 个百分比元素:")
    for i, elem in enumerate(percent_elements[:5]):  # 显示前5个
        print(f"   {i+1}. 文本: '{elem['text']}' 标签: <{elem['tag']} class='{elem['class']}'>")

def analyze_nav_info_structure(soup: BeautifulSoup, url: str):
    """分析导航信息的HTML结构"""
    print(f"\n🧭 导航信息结构分析")
    print("-" * 30)
    
    # 查找导航相关的容器
    nav_containers = [
        soup.find('div', class_='nav-wrap-inner'),
        soup.find('div', class_='nav-wrap'),
        soup.find('ul', class_='nav-left'),
        soup.find('ul', class_='nav-right'),
    ]
    
    for i, container in enumerate(nav_containers):
        if container:
            print(f"📦 导航容器 {i+1}: <{container.name} class='{container.get('class')}'>")
            
            # 查找所有li元素
            nav_items = container.find_all('li')
            for j, item in enumerate(nav_items):
                item_text = item.get_text().strip()
                item_class = item.get('class', [])
                
                # 查找数字
                numbers = re.findall(r'\d+', item_text)
                
                print(f"   项目 {j+1}: class='{item_class}' 文本='{item_text}' 数字={numbers}")
                
                # 查找span子元素
                spans = item.find_all('span')
                for span in spans:
                    span_text = span.get_text().strip()
                    span_class = span.get('class', [])
                    if span_text:
                        print(f"      span: class='{span_class}' 文本='{span_text}'")
            print()

def analyze_author_info_structure(soup: BeautifulSoup, url: str):
    """分析作者信息的HTML结构"""
    print(f"\n👤 作者信息结构分析")
    print("-" * 30)
    
    # 查找作者相关的容器
    author_containers = [
        soup.find('div', class_='sponsor-info'),
        soup.find('div', class_='author-info'),
        soup.find('a', class_='sponsor-link'),
    ]
    
    for i, container in enumerate(author_containers):
        if container:
            print(f"📦 作者容器 {i+1}: <{container.name} class='{container.get('class')}'>")
            print(f"   文本内容: '{container.get_text().strip()[:100]}...'")
            
            # 查找链接
            links = container.find_all('a')
            for link in links:
                href = link.get('href', '')
                text = link.get_text().strip()
                print(f"   链接: href='{href}' 文本='{text}'")
            
            # 查找图片
            images = container.find_all('img')
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                print(f"   图片: src='{src}' alt='{alt}'")
            print()

def save_html_structure_analysis(soup: BeautifulSoup, url: str):
    """保存HTML结构分析到文件"""
    print(f"\n💾 保存HTML结构分析")
    print("-" * 30)
    
    try:
        # 创建分析报告
        analysis = {
            "url": url,
            "analysis_time": str(Path(__file__).stat().st_mtime),
            "page_title": soup.title.string if soup.title else "",
            "structure_analysis": {}
        }
        
        # 分析主要容器结构
        main_containers = [
            ('main-left', soup.find('div', class_='main-left')),
            ('main-right', soup.find('div', class_='main-right')),
            ('center', soup.find('div', class_='center')),
            ('sponsor-info', soup.find('div', class_='sponsor-info')),
            ('nav-wrap-inner', soup.find('div', class_='nav-wrap-inner')),
        ]
        
        for name, container in main_containers:
            if container:
                analysis["structure_analysis"][name] = {
                    "tag": container.name,
                    "classes": container.get('class', []),
                    "id": container.get('id', ''),
                    "children_count": len(container.find_all()),
                    "text_length": len(container.get_text().strip()),
                    "has_forms": len(container.find_all('form')) > 0,
                    "has_scripts": len(container.find_all('script')) > 0,
                }
        
        # 查找所有包含数据属性的元素
        data_elements = []
        for element in soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys())):
            data_attrs = {k: v for k, v in element.attrs.items() if k.startswith('data-')}
            if data_attrs:
                data_elements.append({
                    "tag": element.name,
                    "classes": element.get('class', []),
                    "data_attributes": data_attrs,
                    "text": element.get_text().strip()[:50]
                })
        
        analysis["data_elements"] = data_elements[:20]  # 保存前20个
        
        # 保存到文件
        output_file = Path("data") / "modian_html_structure_analysis.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"✅ HTML结构分析已保存到: {output_file}")
        
        # 同时保存简化的HTML结构
        simplified_html = simplify_html_structure(soup)
        html_file = Path("data") / "modian_simplified_structure.html"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(simplified_html)
        
        print(f"✅ 简化HTML结构已保存到: {html_file}")
        
    except Exception as e:
        print(f"❌ 保存分析失败: {e}")

def simplify_html_structure(soup: BeautifulSoup) -> str:
    """简化HTML结构，只保留关键信息"""
    
    # 移除不必要的元素
    for element in soup(['script', 'style', 'meta', 'link']):
        element.decompose()
    
    # 简化文本内容
    for element in soup.find_all(text=True):
        if len(element.strip()) > 100:
            element.replace_with(element.strip()[:100] + "...")
    
    # 移除大部分属性，只保留class和id
    for element in soup.find_all():
        attrs_to_keep = {}
        if element.get('class'):
            attrs_to_keep['class'] = element.get('class')
        if element.get('id'):
            attrs_to_keep['id'] = element.get('id')
        if element.get('href'):
            attrs_to_keep['href'] = element.get('href')
        if element.get('src'):
            attrs_to_keep['src'] = element.get('src')
        
        element.attrs = attrs_to_keep
    
    return str(soup)

def extract_real_data_patterns():
    """提取真实的数据模式"""
    print(f"\n🎯 提取真实数据模式")
    print("-" * 30)
    
    try:
        from spider.config import SpiderConfig
        from spider.utils import NetworkUtils
        
        config = SpiderConfig()
        network_utils = NetworkUtils(config)
        
        test_url = "https://zhongchou.modian.com/item/2250000.html"
        html = network_utils.make_request(test_url)
        
        if not html:
            print("❌ 无法获取页面内容")
            return False
        
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text()
        
        print("📝 页面文本中的关键数据模式:")
        
        # 查找所有数字模式
        patterns = {
            "金额模式": [
                r'已筹[¥￥]\s*([0-9,]+)',
                r'目标金额[¥￥]\s*([0-9,]+)',
                r'[¥￥]\s*([0-9,]+)',
            ],
            "百分比模式": [
                r'([0-9.]+)%',
                r'完成.*?([0-9.]+)%',
            ],
            "人数模式": [
                r'(\d+)\s*人',
                r'(\d+)\s*支持者',
                r'支持者\s*(\d+)',
            ],
            "计数模式": [
                r'更新\s*(\d+)',
                r'评论\s*(\d+)',
                r'收藏\s*(\d+)',
            ]
        }
        
        for pattern_type, pattern_list in patterns.items():
            print(f"\n{pattern_type}:")
            for pattern in pattern_list:
                matches = re.findall(pattern, page_text)
                if matches:
                    print(f"   ✅ {pattern} -> {matches}")
                else:
                    print(f"   ❌ {pattern} -> 无匹配")
        
        return True
        
    except Exception as e:
        print(f"❌ 提取数据模式失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 摩点网页HTML结构分析工具")
    print("目标：找到准确的数据获取方式，避免反推计算")
    print("=" * 80)
    
    tasks = [
        ("页面结构分析", analyze_modian_page_structure),
        ("数据模式提取", extract_real_data_patterns),
    ]
    
    results = []
    
    for task_name, task_func in tasks:
        try:
            print(f"\n{'='*20} {task_name} {'='*20}")
            result = task_func()
            results.append((task_name, result))
            status = "✅ 成功" if result else "❌ 失败"
            print(f"\n{task_name}: {status}")
        except Exception as e:
            print(f"\n{task_name}: ❌ 异常 - {e}")
            results.append((task_name, False))
    
    # 总结
    print(f"\n" + "=" * 80)
    print(f"📊 HTML结构分析总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for task_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {task_name}")
    
    print(f"\n成功率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"🎉 HTML结构分析完成！")
        print(f"✅ 已识别真实的数据获取方式")
        print(f"✅ 可以避免反推计算")
        print(f"✅ 分析报告已保存到data目录")
        return True
    else:
        print(f"⚠️  部分分析任务需要进一步完善")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
