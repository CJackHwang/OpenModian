#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据库分类数据问题
"""

import sys
import os
import sqlite3

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data.database.db_manager import DatabaseManager


def debug_database_categories():
    """调试数据库分类数据"""
    print("🔍 调试数据库分类数据问题")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    try:
        # 检查数据库连接
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. 检查表结构
            print("📋 检查表结构:")
            cursor.execute("PRAGMA table_info(projects)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]:20} {col[2]:10} {'NOT NULL' if col[3] else 'NULL'}")
            
            # 2. 检查分类字段的唯一值
            print("\n🏷️ 检查分类字段的唯一值:")
            cursor.execute("SELECT DISTINCT category FROM projects WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = cursor.fetchall()
            print(f"  数据库中的分类数量: {len(categories)}")
            for cat in categories:
                cursor.execute("SELECT COUNT(*) FROM projects WHERE category = ?", (cat[0],))
                count = cursor.fetchone()[0]
                print(f"  {cat[0]:15} -> {count:4} 个项目")
            
            # 3. 检查空分类或异常分类
            print("\n⚠️ 检查空分类或异常分类:")
            cursor.execute("SELECT COUNT(*) FROM projects WHERE category IS NULL OR category = '' OR category = 'none'")
            empty_count = cursor.fetchone()[0]
            print(f"  空分类项目数量: {empty_count}")
            
            # 4. 检查最近的项目分类
            print("\n📅 检查最近10个项目的分类:")
            cursor.execute("""
                SELECT project_name, category, crawl_time 
                FROM projects 
                ORDER BY crawl_time DESC 
                LIMIT 10
            """)
            recent_projects = cursor.fetchall()
            for proj in recent_projects:
                print(f"  {proj[1]:12} | {proj[0][:30]:30} | {proj[2]}")
            
            # 5. 检查分类筛选功能
            print("\n🔍 测试分类筛选功能:")
            test_categories = ['games', '游戏', 'tablegames', '桌游']
            for test_cat in test_categories:
                cursor.execute("SELECT COUNT(*) FROM projects WHERE category = ?", (test_cat,))
                count = cursor.fetchone()[0]
                print(f"  分类 '{test_cat}': {count} 个项目")
            
            # 6. 检查排序功能
            print("\n📊 测试排序功能:")
            sort_fields = ['raised_amount', 'backer_count', 'comment_count', 'crawl_time']
            for field in sort_fields:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM projects WHERE {field} IS NOT NULL")
                    count = cursor.fetchone()[0]
                    cursor.execute(f"SELECT MAX({field}), MIN({field}) FROM projects WHERE {field} IS NOT NULL")
                    max_val, min_val = cursor.fetchone()
                    print(f"  {field:15}: {count:4} 个有效值, 范围: {min_val} - {max_val}")
                except Exception as e:
                    print(f"  {field:15}: 错误 - {e}")
            
            # 7. 检查数据类型问题
            print("\n🔧 检查数据类型问题:")
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN raised_amount LIKE '%,%' THEN 1 END) as comma_amounts,
                    COUNT(CASE WHEN backer_count LIKE '%,%' THEN 1 END) as comma_counts,
                    COUNT(CASE WHEN raised_amount = '0' OR raised_amount = '' THEN 1 END) as zero_amounts
                FROM projects
            """)
            data_issues = cursor.fetchone()
            print(f"  总项目数: {data_issues[0]}")
            print(f"  金额包含逗号: {data_issues[1]}")
            print(f"  支持者数包含逗号: {data_issues[2]}")
            print(f"  零金额项目: {data_issues[3]}")
            
    except Exception as e:
        print(f"❌ 数据库调试失败: {e}")
        return False
    
    print("\n✅ 数据库调试完成")
    return True


def fix_category_mapping():
    """修复分类映射问题"""
    print("\n🔧 修复分类映射问题")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    # 分类映射表
    category_mapping = {
        '游戏': 'games',
        '桌游': 'tablegames',
        '出版': 'publishing',
        '潮玩模型': 'toys',
        '卡牌': 'cards',
        '科技': 'technology',
        '影视': 'film-video',
        '音乐': 'music',
        '活动': 'activities',
        '设计': 'design',
        '文玩': 'curio',
        '家居': 'home',
        '食品': 'food',
        '动漫': 'comics',
        '爱心通道': 'charity',
        '动物救助': 'animals',
        '个人愿望': 'wishes',
        '其他': 'others'
    }
    
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # 统计需要修复的数据
            total_fixed = 0
            for chinese_cat, english_cat in category_mapping.items():
                cursor.execute("SELECT COUNT(*) FROM projects WHERE category = ?", (chinese_cat,))
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  修复分类 '{chinese_cat}' -> '{english_cat}': {count} 个项目")
                    cursor.execute("UPDATE projects SET category = ? WHERE category = ?", (english_cat, chinese_cat))
                    total_fixed += count
            
            conn.commit()
            print(f"\n✅ 总共修复了 {total_fixed} 个项目的分类")
            
    except Exception as e:
        print(f"❌ 修复分类映射失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 开始数据库分类调试")
    print("=" * 60)
    
    try:
        # 调试数据库分类
        debug_success = debug_database_categories()
        
        if debug_success:
            # 询问是否修复分类映射
            response = input("\n是否修复分类映射问题? (y/n): ")
            if response.lower() == 'y':
                fix_category_mapping()
                print("\n🔄 重新检查修复后的数据:")
                debug_database_categories()
        
    except Exception as e:
        print(f"\n💥 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
