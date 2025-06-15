# 摩点众筹爬虫管理系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.0+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

**专业的摩点众筹数据采集与分析平台**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [使用指南](#-使用指南) • [开发文档](#-开发文档)

</div>

## 📋 项目简介

摩点众筹爬虫管理系统是一个专业的数据采集与分析平台，专门用于摩点众筹网站的数据抓取、存储、管理和分析。系统采用现代化的前后端分离架构，提供直观的Web界面和强大的数据管理功能。

### 🎯 核心价值

- **高效数据采集**：智能爬虫引擎，支持动态数据获取，数据完整性达98%+
- **实时监控管理**：Web UI实时监控爬虫状态，支持任务控制和日志查看
- **强大数据管理**：SQL-like数据管理界面，支持高级筛选、排序和批量操作
- **现代化界面**：基于Vue 3 + Vuetify 3 + Material Design 3的现代化UI

## ✨ 功能特性

### 🕷️ 智能爬虫引擎
- **多模式数据采集**：支持静态HTML解析和动态数据获取
- **闪电快速动态数据**：优化的Selenium集成，快速获取异步加载数据
- **智能适配解析**：自动适配摩点网站的各种页面结构
- **并发控制**：多线程并发爬取，支持速率限制和错误重试
- **数据验证**：实时数据完整性验证，确保数据质量

### 🎛️ Web管理界面
- **实时监控仪表板**：爬虫状态、进度监控、系统统计
- **任务管理**：启动/停止爬虫、任务历史记录、失败重试
- **实时日志**：WebSocket实时日志显示，支持全屏模式
- **响应式设计**：支持桌面和移动端访问

### 🗄️ 高级数据管理
- **SQL-like界面**：类似数据库管理工具的直观操作界面
- **高级筛选**：多条件组合筛选，支持数值范围、文本匹配、日期范围
- **智能排序**：多字段优先级排序，自定义排序规则
- **批量操作**：批量编辑、删除、导出数据
- **数据导入导出**：支持CSV、JSON、Excel格式

### 📊 数据存储与分析
- **SQLite数据库**：轻量级数据库存储，支持时间分类管理
- **历史数据追踪**：项目数据变化历史记录和对比分析
- **重复数据处理**：智能去重机制，避免数据冗余
- **数据质量报告**：自动生成数据完整性和质量报告

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **Node.js**: 16.0+
- **npm**: 8.0+
- **操作系统**: macOS, Linux, Windows

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd spider_modian-main

# 一键启动（自动安装依赖并启动）
python3 start_vue_ui.py
```

### 启动模式

#### 🔥 开发模式（推荐）
```bash
# 前后端分离，支持热重载
python3 start_vue_ui.py dev

# 访问地址
# 前端: http://localhost:3001 (热重载)
# 后端: http://localhost:8080 (API服务)
```

#### 🚀 生产模式
```bash
# 单端口集成模式
python3 start_vue_ui.py prod

# 访问地址: http://localhost:8080
```

#### 🔨 仅构建
```bash
# 仅构建前端，不启动服务
python3 start_vue_ui.py build
```

### 手动安装

```bash
# 1. 安装Python依赖
pip3 install -r requirements.txt

# 2. 安装前端依赖
cd web_ui_vue
npm install

# 3. 构建前端
npm run build

# 4. 启动服务
cd ../web_ui
python3 app.py
```

## 🏗️ 技术架构

### 后端技术栈
- **核心框架**: Flask 2.3+ + Flask-SocketIO
- **数据库**: SQLite3 + pandas
- **爬虫引擎**: requests + BeautifulSoup4 + Selenium
- **数据处理**: pandas + numpy
- **配置管理**: YAML + 环境变量

### 前端技术栈
- **框架**: Vue 3 + Composition API
- **UI组件**: Vuetify 3 + Material Design 3
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **实时通信**: Socket.IO Client

### 项目结构
```
spider_modian-main/
├── spider/                 # 爬虫核心模块
│   ├── core.py            # 爬虫引擎
│   ├── config.py          # 配置管理
│   ├── lightning_fast_dynamic.py  # 动态数据获取
│   └── ...
├── web_ui/                # Flask后端
│   └── app.py            # Web API服务
├── web_ui_vue/           # Vue3前端
│   ├── src/              # 源代码
│   ├── dist/             # 构建输出
│   └── package.json      # 依赖配置
├── database/             # 数据库模块
│   ├── db_manager.py     # 数据库管理
│   └── modian_data.db    # SQLite数据库
├── data/                 # 数据存储目录
├── logs/                 # 日志文件
├── config/               # 配置文件
├── tests/                # 测试文件
├── start_vue_ui.py       # 一键启动脚本
├── requirements.txt      # Python依赖
└── README.md            # 项目文档
```

## 📖 使用指南

### 1. 启动爬虫任务

1. 访问Web界面：http://localhost:8080
2. 进入"爬虫控制"页面
3. 配置爬取参数：
   - 起始页码和结束页码
   - 项目分类（科技、设计、游戏等）
   - 爬取模式（静态/动态）
4. 点击"开始爬取"启动任务

### 2. 监控爬取进度

- **仪表板**：查看实时统计数据和系统状态
- **实时日志**：监控爬虫执行过程和错误信息
- **任务历史**：查看历史任务记录和执行结果

### 3. 数据管理

- **数据查看**：浏览所有爬取的项目数据
- **高级筛选**：使用多条件筛选查找特定数据
- **数据编辑**：直接编辑项目信息
- **批量操作**：批量删除或导出数据
- **数据导出**：导出为CSV、JSON或Excel格式

### 4. 系统配置

- **爬虫设置**：调整爬取参数和性能配置
- **数据库管理**：查看数据库统计和维护
- **日志管理**：配置日志级别和存储

## 🔧 开发文档

### API接口

#### 爬虫控制
- `POST /api/spider/start` - 启动爬虫任务
- `POST /api/spider/stop` - 停止爬虫任务
- `GET /api/spider/status` - 获取爬虫状态

#### 数据管理
- `GET /api/data/projects` - 获取项目列表
- `PUT /api/data/projects/<id>` - 更新项目信息
- `DELETE /api/data/projects/<id>` - 删除项目
- `POST /api/data/export` - 导出数据

#### 系统信息
- `GET /api/system/stats` - 获取系统统计
- `GET /api/system/logs` - 获取系统日志

### 配置文件

#### 爬虫配置 (`config/spider_config.yaml`)
```yaml
spider:
  delay_range: [1, 3]      # 请求延迟范围
  max_retries: 3           # 最大重试次数
  timeout: 30              # 请求超时时间
  concurrent_limit: 5      # 并发限制

database:
  path: "database/modian_data.db"
  backup_enabled: true

export:
  formats: ["csv", "json", "excel"]
  output_dir: "data/exports"
```

### 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd spider_modian-main

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 安装开发依赖
pip install -r requirements.txt

# 4. 启动开发模式
python3 start_vue_ui.py dev
```

## 🧪 测试

```bash
# 运行单元测试
python3 -m pytest tests/

# 运行爬虫测试
python3 tests/test_spider.py

# 测试覆盖率
python3 -m pytest --cov=spider tests/
```

## 📝 更新日志

### v2.0.0 (2025-06-15)
- ✨ 全新Vue 3 + Material Design 3界面
- 🚀 闪电快速动态数据获取
- 🗄️ 高级SQL-like数据管理界面
- 📊 实时监控仪表板
- 🔧 一键启动脚本

### v1.0.0
- 🕷️ 基础爬虫功能
- 💾 数据存储和导出
- 🌐 简单Web界面

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [摩点网](https://www.modian.com/) - 数据来源
- [Vue.js](https://vuejs.org/) - 前端框架
- [Vuetify](https://vuetifyjs.com/) - UI组件库
- [Flask](https://flask.palletsprojects.com/) - 后端框架

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐**

Made with ❤️ by Spider Team

</div>
