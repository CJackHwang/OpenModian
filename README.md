# 摩点爬虫管理系统

一个专业的摩点众筹数据爬虫管理系统，提供完整的数据采集、存储和管理功能。

## 🎯 项目特色

- **智能数据采集**：高效稳定的摩点众筹平台数据爬取（34个数据字段）
- **多格式输出**：支持 Excel、JSON、CSV 等多种数据格式
- **可视化界面**：Web UI界面，支持实时监控和任务管理
- **数据库集成**：SQLite数据库存储，支持时间分类和去重
- **并发爬取**：支持多线程并发，提高爬取效率
- **智能重试**：自动重试机制，确保数据完整性
- **缓存系统**：内置缓存机制，避免重复请求
- **数据验证**：完整的数据验证和质量检查

## 📁 项目结构

```
spider_modian-main/
├── main.py                    # 主爬虫程序（兼容版本）
├── requirements.txt           # 项目依赖
├── config/                    # 配置文件目录
├── modules/                   # 核心模块
│   ├── data_processor.py     # 数据处理器
│   └── config_manager.py     # 配置管理器
├── spider/                    # 爬虫核心模块
│   ├── core.py               # 爬虫核心逻辑
│   ├── config.py             # 爬虫配置
│   ├── exporter.py           # 数据导出器
│   ├── validator.py          # 数据验证器
│   ├── monitor.py            # 监控模块
│   └── utils.py              # 工具函数
├── tests/                     # 测试文件
├── data/                      # 数据目录
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后数据
│   └── cache/                # 缓存数据
├── output/                    # 输出文件
├── logs/                      # 日志文件
├── database/                  # 数据库文件
│   ├── db_manager.py         # 数据库管理器
│   └── modian_data.db        # SQLite数据库
└── web_ui/                    # Web界面
    ├── app.py                # Flask应用
    ├── templates/            # HTML模板
    └── static/               # 静态资源
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd spider_modian-main

# 安装依赖
pip3 install -r requirements.txt
```

### 2. 启动Web UI管理界面

```bash
# 启动Web UI
python3 web_ui/app.py
```

然后在浏览器中访问 `http://localhost:8080`

### 3. 使用命令行爬虫（可选）

```bash
# 运行主爬虫程序
python3 main.py
```

## 📊 输出文件说明

### 数据文件
- **Excel 格式**：`output/modian_projects_*.xlsx`
- **JSON 格式**：`output/modian_projects_*.json`
- **CSV 格式**：`output/modian_projects_*.csv`
- **数据质量报告**：`output/modian_projects_*_quality_report.txt`

### 数据库文件
- **SQLite数据库**：`database/modian_data.db`
- **数据库导出**：通过Web UI可导出Excel格式

## ⚙️ 配置说明

### 爬虫配置
在 `main.py` 中可以调整：
- `MAX_PAGES`：爬取页数（默认3页）
- `REQUEST_TIMEOUT`：请求超时时间
- `MAX_RETRIES`：重试次数

### Web UI配置
在 `web_ui/app.py` 中可以调整：
- 端口范围：8080-8090
- 并发设置：最大并发请求数
- 延迟设置：请求间隔时间

### 系统配置
配置文件会自动生成在 `config/spider_config.yaml`：
```yaml
spider_settings:
  max_pages: 10
  max_retries: 5
  request_timeout: [10, 20]

web_ui_settings:
  host: "0.0.0.0"
  port_range: [8080, 8090]
```

## 🔧 功能模块

### 数据采集模块
- **智能解析**：自动识别项目信息、用户数据、众筹状态
- **错误处理**：完善的重试机制和异常处理
- **数据验证**：确保数据完整性和准确性
- **并发爬取**：多线程并发提高效率

### Web UI管理模块
- **任务管理**：启动、停止、监控爬虫任务
- **实时监控**：进度显示、日志输出、统计信息
- **数据管理**：数据库查看、导出、时间分类

### 数据库模块
- **自动去重**：基于数据哈希的智能去重
- **时间分类**：按日、周、月、年分类存储
- **数据导出**：支持Excel格式导出

## 🧪 测试

```bash
# 运行测试套件
python3 -m pytest tests/

# 运行特定测试
python3 tests/test_spider.py
```

## 📝 使用注意事项

1. **合规使用**：请遵守摩点平台的 robots.txt 协议
2. **频率控制**：合理控制爬取频率，避免对服务器造成压力
3. **数据用途**：仅用于学习研究和合法的市场调研目的
4. **并发设置**：建议并发数不超过5，避免被封IP
5. **数据备份**：重要数据请及时备份

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
