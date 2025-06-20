# -*- coding: utf-8 -*-
"""
数据导出模块
支持多种格式的数据导出和备份功能
"""

import os
import json
import csv
import xlwt
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import openpyxl
from openpyxl.utils.exceptions import IllegalCharacterError
import uuid
import threading
import time

from .config import SpiderConfig, FieldMapping
from .utils import FileUtils


class DataExporter:
    """数据导出器 - 支持并发安全的文件操作"""

    def __init__(self, config: SpiderConfig):
        self.config = config
        self.output_dir = Path(config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 🔧 并发控制：文件操作锁
        self._file_lock = threading.Lock()
        self._filename_counter = 0

    def _generate_unique_filename(self, base_name: str, extension: str) -> str:
        """生成唯一文件名，避免并发冲突"""
        with self._file_lock:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            microsecond = datetime.now().microsecond // 1000  # 毫秒精度
            self._filename_counter += 1
            unique_id = str(uuid.uuid4())[:8]

            return f"{base_name}_{timestamp}_{microsecond:03d}_{self._filename_counter:03d}_{unique_id}.{extension}"

    def export_to_excel(self, projects_data: List[List[Any]],
                       filename: Optional[str] = None) -> str:
        """导出到Excel文件 - 并发安全"""
        if not filename:
            filename = self._generate_unique_filename("modian_projects", "xls")
        
        file_path = self.output_dir / filename
        
        # 备份现有文件
        if file_path.exists():
            FileUtils.backup_file(str(file_path))
        
        try:
            workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
            sheet = workbook.add_sheet('projects', cell_overwrite_ok=True)
            
            # 写入表头
            headers = FieldMapping.EXCEL_COLUMNS
            for col_idx, header in enumerate(headers):
                sheet.write(0, col_idx, header)
            
            # 写入数据
            for row_idx, project_data in enumerate(projects_data, 1):
                self._write_excel_row(sheet, row_idx, project_data, headers)
            
            workbook.save(str(file_path))
            print(f"Excel文件已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"导出Excel文件失败: {e}")
            raise
    
    def _write_excel_row(self, sheet, row_idx: int, project_data: List[Any], 
                        headers: List[str]):
        """写入Excel行数据"""
        # 确保数据长度匹配表头
        padded_data = list(project_data) + [""] * (len(headers) - len(project_data))
        
        for col_idx, cell_value in enumerate(padded_data):
            if col_idx >= len(headers):
                break
                
            cell_str = str(cell_value) if cell_value is not None else ""
            
            # 处理Excel单元格字符限制
            if len(cell_str) > 32767:
                cell_str = cell_str[:32764] + "..."
            
            try:
                sheet.write(row_idx, col_idx, cell_str)
            except (IllegalCharacterError, Exception) as e:
                # 处理非法字符
                cleaned_str = self._clean_excel_string(cell_str)
                try:
                    sheet.write(row_idx, col_idx, cleaned_str)
                except Exception:
                    sheet.write(row_idx, col_idx, "ERROR_WRITING_CELL")
    
    def _clean_excel_string(self, text: str) -> str:
        """清理Excel字符串"""
        # 移除控制字符
        import re
        cleaned = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        return cleaned
    
    def export_to_json(self, projects_data: List[List[Any]], 
                      filename: Optional[str] = None) -> str:
        """导出到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"modian_projects_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        try:
            # 转换为JSON格式
            json_data = self._convert_to_json_format(projects_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"JSON文件已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"导出JSON文件失败: {e}")
            raise
    
    def _convert_to_json_format(self, projects_data: List[List[Any]]) -> Dict[str, Any]:
        """转换为JSON格式"""
        headers = FieldMapping.EXCEL_COLUMNS
        projects = []
        
        for project_data in projects_data:
            project_dict = {}
            
            for i, header in enumerate(headers):
                value = project_data[i] if i < len(project_data) else ""
                
                # 数据类型转换
                if header in ["序号", "项目更新数", "评论数", "支持者(数量)", 
                             "收藏数", "回报列表项目数", "项目详情-图片数量", 
                             "项目详情-视频数量", "作者页-粉丝数", "作者页-关注数", "作者页-获赞数"]:
                    try:
                        project_dict[header] = int(str(value).replace(',', '')) if value else 0
                    except ValueError:
                        project_dict[header] = 0
                
                elif header in ["已筹金额", "目标金额", "百分比"]:
                    try:
                        project_dict[header] = float(str(value).replace(',', '')) if value else 0.0
                    except ValueError:
                        project_dict[header] = 0.0
                
                else:
                    project_dict[header] = str(value) if value else ""
            
            projects.append(project_dict)
        
        return {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "total_projects": len(projects),
                "format_version": "1.0"
            },
            "projects": projects
        }
    
    def export_to_csv(self, projects_data: List[List[Any]], 
                     filename: Optional[str] = None) -> str:
        """导出到CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"modian_projects_{timestamp}.csv"
        
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入表头
                headers = FieldMapping.EXCEL_COLUMNS
                writer.writerow(headers)
                
                # 写入数据
                for project_data in projects_data:
                    # 确保数据长度匹配表头
                    padded_data = list(project_data) + [""] * (len(headers) - len(project_data))
                    row_data = [str(cell) if cell is not None else "" for cell in padded_data[:len(headers)]]
                    writer.writerow(row_data)
            
            print(f"CSV文件已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"导出CSV文件失败: {e}")
            raise
    
    def export_summary_report(self, projects_data: List[List[Any]],
                            stats: Dict[str, Any]) -> str:
        """导出摘要报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spider_summary_{timestamp}.txt"

        # 使用统一的报告目录
        report_dir = Path("data/reports/summary")
        report_dir.mkdir(parents=True, exist_ok=True)
        file_path = report_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("摩点众筹爬虫数据摘要报告\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"数据项目数: {len(projects_data)}\n\n")
                
                # 统计信息
                if stats:
                    f.write("爬虫运行统计:\n")
                    f.write(f"  运行时间: {stats.get('runtime_seconds', 0):.1f}秒\n")
                    f.write(f"  总请求数: {stats.get('total_requests', 0)}\n")
                    f.write(f"  成功率: {stats.get('success_rate', 0):.1f}%\n")
                    f.write(f"  页面处理: {stats.get('pages_processed', 0)}\n")
                    f.write(f"  项目发现: {stats.get('projects_found', 0)}\n\n")
                
                # 数据分析
                if projects_data:
                    analysis = self._analyze_projects_data(projects_data)
                    f.write("数据分析:\n")
                    f.write(f"  平均筹款金额: {analysis['avg_raised']:.2f}元\n")
                    f.write(f"  平均完成率: {analysis['avg_completion']:.1f}%\n")
                    f.write(f"  成功项目数: {analysis['success_count']}\n")
                    f.write(f"  热门分类: {', '.join(analysis['top_categories'][:5])}\n\n")
                
                f.write("报告结束\n")
            
            print(f"摘要报告已保存: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"导出摘要报告失败: {e}")
            raise
    
    def _analyze_projects_data(self, projects_data: List[List[Any]]) -> Dict[str, Any]:
        """分析项目数据"""
        headers = FieldMapping.EXCEL_COLUMNS
        
        # 获取字段索引
        raised_idx = headers.index("已筹金额") if "已筹金额" in headers else -1
        completion_idx = headers.index("百分比") if "百分比" in headers else -1
        category_idx = headers.index("分类") if "分类" in headers else -1
        
        total_raised = 0
        total_completion = 0
        success_count = 0
        categories = {}
        valid_count = 0
        
        for project_data in projects_data:
            try:
                # 筹款金额
                if raised_idx >= 0 and raised_idx < len(project_data):
                    raised = float(str(project_data[raised_idx]).replace(',', ''))
                    total_raised += raised
                    valid_count += 1
                
                # 完成率
                if completion_idx >= 0 and completion_idx < len(project_data):
                    completion = float(str(project_data[completion_idx]))
                    total_completion += completion
                    if completion >= 100:
                        success_count += 1
                
                # 分类统计
                if category_idx >= 0 and category_idx < len(project_data):
                    category = str(project_data[category_idx])
                    categories[category] = categories.get(category, 0) + 1
                    
            except (ValueError, IndexError):
                continue
        
        # 排序分类
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat[0] for cat in top_categories]
        
        return {
            "avg_raised": total_raised / valid_count if valid_count > 0 else 0,
            "avg_completion": total_completion / len(projects_data) if projects_data else 0,
            "success_count": success_count,
            "top_categories": top_categories
        }
    
    def create_backup(self, projects_data: List[List[Any]]) -> str:
        """创建数据备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.output_dir / "backup" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 导出多种格式
            excel_file = self.export_to_excel(projects_data, f"backup_{timestamp}.xls")
            json_file = self.export_to_json(projects_data, f"backup_{timestamp}.json")
            
            # 移动到备份目录
            import shutil
            shutil.move(excel_file, backup_dir / f"backup_{timestamp}.xls")
            shutil.move(json_file, backup_dir / f"backup_{timestamp}.json")
            
            print(f"数据备份已创建: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            raise
    
    def get_export_stats(self) -> Dict[str, Any]:
        """获取导出统计信息"""
        try:
            files = list(self.output_dir.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            return {
                "output_dir": str(self.output_dir),
                "total_files": len([f for f in files if f.is_file()]),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "latest_files": [f.name for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]
            }
        except Exception:
            return {"error": "无法获取导出统计信息"}
