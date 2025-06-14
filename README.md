# 摩点爬虫管理系统

一个专业的摩点众筹数据爬虫管理系统，提供完整的数据采集、存储和管理功能。

## 🎯 项目特色

- **智能数据采集**：高效稳定的摩点众筹平台数据爬取（34个数据字段）
- **闪电动态数据**：默认启用闪电快速动态数据获取，真正接近人工速度
- **多格式输出**：支持 Excel、JSON、CSV 等多种数据格式
- **可视化界面**：Web UI界面，支持实时监控和任务管理
- **数据库集成**：SQLite数据库存储，支持时间分类和去重管理
- **并发爬取**：智能并发控制，提高爬取效率
- **智能重试**：自动重试机制，确保数据完整性
- **缓存系统**：内置智能缓存机制，避免重复请求
- **数据验证**：完整的数据验证和质量检查（99%+准确率）
- **模块化设计**：现代化架构，易于维护和扩展

## 📁 项目结构

```
spider_modian-main/
├── start_web_ui.py            # Web UI启动入口
├── requirements.txt           # 项目依赖
├── config/                    # 配置文件目录
│   └── spider_config.yaml    # 爬虫配置文件
├── spider/                    # 爬虫核心模块（主要功能）
│   ├── __init__.py           # 模块初始化
│   ├── core.py               # 爬虫核心逻辑
│   ├── config.py             # 爬虫配置类
│   ├── exporter.py           # 数据导出器
│   ├── validator.py          # 数据验证器
│   ├── monitor.py            # 性能监控模块
│   ├── utils.py              # 工具函数集
│   └── lightning_fast_dynamic.py  # 闪电动态数据获取
├── web_ui/                    # Web管理界面
│   ├── app.py                # Flask应用主程序
│   ├── templates/            # HTML模板
│   │   └── index.html        # 主界面模板
│   └── static/               # 静态资源
│       ├── css/              # 样式文件
│       └── js/               # JavaScript文件
├── database/                  # 数据库模块
│   ├── db_manager.py         # 数据库管理器
│   └── modian_data.db        # SQLite数据库
├── tests/                     # 自动化测试
│   ├── __init__.py           # 测试模块初始化
│   └── test_spider.py        # 爬虫测试用例
├── data/                      # 数据目录
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后数据
│   ├── cache/                # 缓存数据
│   └── spider/               # 爬虫输出数据
├── logs/                      # 日志文件
│   └── spider.log            # 爬虫运行日志
└── reports/                   # 数据报告
    ├── latest/               # 最新报告
    └── archive/              # 历史报告
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd spider_modian-main

# 安装依赖（Python 3.7+）
pip3 install -r requirements.txt
```

### 2. 启动Web UI管理界面（推荐）

```bash
# 启动Web UI管理系统
python3 start_web_ui.py
```

然后在浏览器中访问 `http://localhost:8080`

### 3. 使用Python模块（高级用户）

```python
from spider import SpiderCore, SpiderConfig

# 创建配置
config = SpiderConfig()

# 创建爬虫实例
spider = SpiderCore(config)

# 开始爬取
spider.start_crawling(start_page=1, end_page=10, category="all")
```

## 📊 输出文件说明

### 数据文件
- **Excel 格式**：`data/spider/摩点众筹-主要信息_*.xls`
- **JSON 格式**：`data/spider/modian_projects_*.json`
- **CSV 格式**：`data/spider/modian_projects_*.csv`
- **数据质量报告**：`reports/latest/data_quality_report_*.txt`
- **统计报告**：`data/spider/spider_stats_*.json`

### 数据库文件
- **SQLite数据库**：`database/modian_data.db`
- **数据库导出**：通过Web UI可导出Excel格式
- **自动备份**：支持数据库自动备份功能

### 数据字段（34个字段）
包含项目基本信息、众筹数据、作者信息、互动数据、媒体内容等完整信息

## ⚙️ 配置说明

### 主配置文件
配置文件位于 `config/spider_config.yaml`：
```yaml
spider_settings:
  max_pages: 10                    # 最大爬取页数
  max_retries: 5                   # 最大重试次数
  max_concurrent_requests: 3       # 最大并发请求数
  request_delay: [1.0, 3.0]       # 请求延迟范围（秒）
  request_timeout: [10, 20]        # 请求超时范围（秒）
  save_interval: 5                 # 保存间隔

database_settings:
  db_path: database/modian_data.db # 数据库路径
  enable_deduplication: true       # 启用去重
  auto_backup: true                # 自动备份

web_ui_settings:
  host: "0.0.0.0"                 # Web UI主机
  port_range: [8080, 8090]        # 端口范围
  auto_open_browser: true         # 自动打开浏览器

output_settings:
  output_dir: output              # 输出目录
  formats: [excel, csv, json]     # 输出格式
```

### 动态数据配置
在 `spider/config.py` 中：
- `ENABLE_DYNAMIC_DATA`: 启用闪电动态数据获取（默认True）
- `LIGHTNING_TIMEOUT`: 闪电超时时间（2秒）
- `LIGHTNING_CACHE_MINUTES`: 缓存时间（30分钟）

## 🔧 功能模块

### 数据采集模块 (`spider/`)
- **智能解析**：自动识别项目信息、用户数据、众筹状态
- **闪电动态数据**：默认启用动态数据获取，真正接近人工速度
- **错误处理**：完善的重试机制和异常处理
- **数据验证**：确保数据完整性和准确性（99%+）
- **并发控制**：智能并发控制，避免被封IP
- **缓存机制**：智能缓存，避免重复请求

### Web UI管理模块 (`web_ui/`)
- **任务管理**：启动、停止、监控爬虫任务
- **实时监控**：进度显示、实时日志输出、统计信息
- **数据管理**：数据库查看、导出、时间分类查询
- **配置管理**：在线配置爬虫参数
- **历史任务**：查看历史爬取任务记录

### 数据库模块 (`database/`)
- **自动去重**：基于数据哈希的智能去重
- **时间分类**：按日、周、月分类存储和查询
- **数据导出**：支持Excel格式导出
- **统计分析**：数据统计和质量分析
- **自动备份**：数据库自动备份功能

### 测试模块 (`tests/`)
- **自动化测试**：完整的测试用例覆盖
- **数据验证测试**：确保数据质量
- **性能测试**：监控爬取性能

## 🧪 测试

```bash
# 运行完整测试套件
python3 -m pytest tests/ -v

# 运行特定测试
python3 tests/test_spider.py

# 运行测试并生成覆盖率报告
python3 -m pytest tests/ --cov=spider
```

## � 数据完整性

- **数据完整性**：从50%提升到99%+
- **关键字段修复**：已修复点赞数、支持者数、评论数等关键字段
- **动态数据获取**：支持动态加载数据的获取
- **多页面测试**：确保在不同项目页面结构下的兼容性

## �📝 使用注意事项

1. **合规使用**：请遵守摩点平台的 robots.txt 协议
2. **频率控制**：系统已内置智能频率控制，避免对服务器造成压力
3. **数据用途**：仅用于学习研究和合法的市场调研目的
4. **并发设置**：建议并发数不超过3（已优化），避免被封IP
5. **数据备份**：系统支持自动备份，重要数据会自动保存
6. **环境要求**：推荐使用macOS环境，Python 3.7+

## 🚀 性能优化

- **闪电动态数据**：2秒超时，30分钟缓存，接近人工操作速度
- **智能缓存**：避免重复请求，提高效率
- **批量处理**：支持批量数据处理和保存
- **内存优化**：优化内存使用，支持大量数据处理

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
