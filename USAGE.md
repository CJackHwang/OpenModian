# 使用指南

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.7 或更高版本：

```bash
python3 --version
```

### 2. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 3. 基础数据采集

#### 方式一：使用原始爬虫（简单快速）
```bash
python3 main.py
```
- 输出文件：`摩点众筹-主要信息.xls`
- 适合：快速获取基础数据

#### 方式二：使用增强版爬虫（推荐）
```bash
python3 main_enhanced.py
```
- 输出文件：`output/modian_projects_*.json/csv/xlsx`
- 特点：多格式输出、完整日志、错误处理

### 4. AI 分析（可选）

#### 配置 AI API
编辑 `config/ai_config.yaml`：
```yaml
api:
  base_url: "https://api.openai.com/v1"
  api_key: "your-api-key-here"
  model: "gpt-3.5-turbo"
```

#### 运行 AI 分析
```bash
python3 ai_main.py
```
- 输出文件：`reports/latest/` 目录下的分析报告

## 📊 输出文件详解

### 数据文件格式

#### Excel 文件 (.xls/.xlsx)
包含以下列：
- 序号、项目链接、项目ID、项目名称、项目图片
- 开始时间、结束时间、项目结果
- 用户信息、分类、已筹金额、目标金额
- 支持者数量、更新数、评论数等

#### JSON 文件 (.json)
```json
[
  {
    "link": "https://zhongchou.modian.com/item/147341.html",
    "id": "147341",
    "title": "项目标题",
    "image": "项目图片URL"
  }
]
```

#### CSV 文件 (.csv)
适合导入其他数据分析工具，如 Excel、Tableau 等。

### AI 分析报告

#### 分析报告 (analysis_report_*.txt)
- 项目概览和统计
- 热门类别分析
- 成功率分析

#### 市场趋势报告 (market_trends_*.txt)
- 市场趋势识别
- 热门关键词
- 时间段分析

#### 项目评分报告 (project_scores_*.txt)
- 项目评分排名
- 评分标准说明
- 改进建议

## ⚙️ 配置选项

### 爬虫配置

在 `main_enhanced.py` 中修改 `ModianSpiderConfig` 类：

```python
class ModianSpiderConfig:
    def __init__(self):
        self.MAX_PAGES = 3          # 爬取页数
        self.MAX_RETRIES = 5        # 重试次数
        self.REQUEST_TIMEOUT = (10, 20)  # 请求超时
        self.SAVE_INTERVAL = 5      # 保存间隔
```

### AI 分析配置

编辑 `config/ai_config.yaml`：

```yaml
api:
  base_url: "https://api.openai.com/v1"
  api_key: "your-api-key"
  model: "gpt-3.5-turbo"
  timeout: 30

analysis:
  batch_size: 10
  max_tokens: 2000
  temperature: 0.7

output:
  format: "txt"
  include_raw_data: false
  time_periods: ["2weeks", "1month", "3months", "all"]
```

## 🔧 高级用法

### 自定义提示词模板

编辑 `config/prompts/analysis/` 目录下的 YAML 文件：

```yaml
# project_scoring.yaml
system_prompt: |
  你是一个专业的桌游市场分析师...

user_prompt_template: |
  请分析以下桌游项目：
  项目名称：{title}
  众筹金额：{amount}
  ...
```

### 自定义报告模板

编辑 `config/report_templates/main_report_template.txt`：

```
# 桌游市场调研报告

## 数据概览
- 分析时间：{analysis_time}
- 项目总数：{total_projects}
- 数据来源：摩点众筹平台

## 主要发现
{main_findings}

...
```

### 批量处理

```bash
# 处理多个时间段
python3 ai_main.py --time-periods 2weeks,1month,3months

# 指定输出目录
python3 main_enhanced.py --output-dir custom_output

# 调试模式
python3 main_enhanced.py --debug
```

## 🧪 测试

### 运行测试套件
```bash
python3 -m pytest tests/ -v
```

### 运行特定测试
```bash
python3 tests/test_spider.py
```

### 测试覆盖率
```bash
pip3 install pytest-cov
python3 -m pytest tests/ --cov=modules --cov=spider
```

## 🐛 故障排除

### 常见问题

#### 1. 网络连接错误
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**解决方案**：检查网络连接，或在代码中禁用 SSL 验证（仅测试环境）

#### 2. 依赖包安装失败
```
ERROR: Could not install packages
```
**解决方案**：
```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --no-cache-dir
```

#### 3. 权限错误
```
Permission denied: 'output/file.xlsx'
```
**解决方案**：确保输出目录有写权限，关闭正在使用的 Excel 文件

#### 4. AI API 错误
```
OpenAI API error: Invalid API key
```
**解决方案**：检查 `config/ai_config.yaml` 中的 API 密钥配置

### 日志查看

查看详细日志：
```bash
tail -f logs/spider.log
```

## 📞 技术支持

如遇到问题，请：
1. 查看日志文件 `logs/spider.log`
2. 检查配置文件是否正确
3. 确认网络连接正常
4. 提交 Issue 到项目仓库
