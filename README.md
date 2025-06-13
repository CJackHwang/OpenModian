# 桌游市场调研工具

一个专业的桌游市场数据采集与分析工具，基于摩点众筹平台数据进行市场调研和趋势分析。

## 🎯 项目特色

- **智能数据采集**：高效稳定的摩点众筹平台数据爬取
- **AI 驱动分析**：集成 OpenAI 兼容 API 进行深度市场分析
- **多格式输出**：支持 Excel、JSON、CSV 等多种数据格式
- **自动化报告**：生成结构化的市场调研报告
- **可配置模板**：灵活的提示词模板和报告格式
- **实时监控**：完整的日志记录和性能统计

## 📁 项目结构

```
spider_modian-main/
├── main.py                    # 主爬虫程序（最优版本）
├── ai_main.py                 # AI 分析主程序
├── requirements.txt           # 项目依赖
├── config/                    # 配置文件目录
│   ├── ai_config.yaml        # AI 分析配置
│   ├── prompts/              # 提示词模板
│   └── report_templates/     # 报告模板
├── modules/                   # 核心模块
│   ├── ai_analyzer.py        # AI 分析器
│   ├── data_processor.py     # 数据处理器
│   ├── report_generator.py   # 报告生成器
│   └── config_manager.py     # 配置管理器
├── spider/                    # 爬虫核心模块
│   ├── core.py               # 爬虫核心逻辑
│   ├── exporter.py           # 数据导出器
│   ├── validator.py          # 数据验证器
│   └── utils.py              # 工具函数
├── tests/                     # 测试文件
├── data/                      # 数据目录
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后数据
│   └── cache/                # 缓存数据
├── reports/                   # 报告目录
│   ├── latest/               # 最新报告
│   └── archive/              # 历史报告
└── logs/                      # 日志文件
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

### 2. 基础数据采集

```bash
# 运行主爬虫程序
python3 main.py
```

### 3. AI 分析（可选）

```bash
# 配置 AI API（编辑 config/ai_config.yaml）
# 运行 AI 分析
python3 ai_main.py
```

## 📊 输出文件说明

### 数据文件
- **Excel 格式**：`摩点众筹-主要信息.xls` 或 `output/modian_projects_*.xlsx`
- **JSON 格式**：`output/modian_projects_*.json`
- **CSV 格式**：`output/modian_projects_*.csv`

### 报告文件
- **AI 分析报告**：`reports/latest/analysis_report_*.txt`
- **市场趋势报告**：`reports/latest/market_trends_*.txt`
- **项目评分报告**：`reports/latest/project_scores_*.txt`

## ⚙️ 配置说明

### 爬虫配置
在 `main_enhanced.py` 中可以调整：
- `MAX_PAGES`：爬取页数（默认3页）
- `REQUEST_TIMEOUT`：请求超时时间
- `MAX_RETRIES`：重试次数

### AI 配置
编辑 `config/ai_config.yaml`：
```yaml
api:
  base_url: "https://api.openai.com/v1"  # API 地址
  api_key: "your-api-key"                # API 密钥
  model: "gpt-3.5-turbo"                 # 使用模型

analysis:
  batch_size: 10                         # 批处理大小
  max_tokens: 2000                       # 最大令牌数
```

## 🔧 功能模块

### 数据采集模块
- **智能解析**：自动识别项目信息、用户数据、众筹状态
- **错误处理**：完善的重试机制和异常处理
- **数据验证**：确保数据完整性和准确性

### AI 分析模块
- **市场趋势分析**：识别热门类别和趋势
- **项目评分**：基于多维度指标评估项目潜力
- **竞品分析**：同类项目对比和建议

### 报告生成模块
- **自动化报告**：基于模板生成专业报告
- **多时间段分析**：支持不同时间维度的数据分析
- **可视化建议**：提供数据可视化建议

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
4. **API 配置**：使用 AI 功能需要配置相应的 API 密钥

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
