# 摩点众筹爬虫管理系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.5+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-red.svg)
![Vuetify](https://img.shields.io/badge/Vuetify-3.8+-purple.svg)
![Material Design](https://img.shields.io/badge/Material%20Design-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

**企业级摩点众筹数据采集与分析平台**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [使用指南](#-使用指南) • [开发文档](#-开发文档) • [更新日志](#-更新日志)

</div>

## 📋 项目简介

摩点众筹爬虫管理系统是一个企业级的数据采集与分析平台，专门用于摩点众筹网站的数据抓取、存储、管理和分析。系统采用现代化的前后端分离架构，提供直观的Web界面和强大的数据管理功能，支持大规模数据处理和实时监控。

### 🎯 核心价值

- **🚀 高效数据采集**：智能爬虫引擎，支持API和动态数据获取，数据完整性达98%+
- **📊 实时监控管理**：WebSocket实时通信，爬虫状态监控，支持任务控制和日志查看
- **🗄️ 企业级数据管理**：SQL-like数据管理界面，支持高级筛选、排序和批量操作
- **🎨 现代化界面**：基于Vue 3 + Vuetify 3 + Material Design 3的响应式UI设计
- **📈 智能任务调度**：支持定时任务、关注列表监控和增量数据更新
- **🔒 数据安全保障**：自动数据库备份、错误恢复和数据完整性验证
- **⚡ 性能优化**：内存优化、网络优化、并发控制和智能缓存机制

## ✨ 功能特性

### 🕷️ 智能爬虫引擎
- **🔄 多模式数据采集**：支持API数据获取、静态HTML解析和动态数据抓取
- **⚡ 高性能数据处理**：优化的并发处理，支持大规模数据采集
- **🎯 智能适配解析**：自动适配摩点网站的各种页面结构和数据格式
- **🔧 并发控制优化**：多线程并发爬取，智能速率限制和错误重试机制
- **✅ 数据质量保障**：实时数据完整性验证，确保数据准确性和一致性
- **📦 增量数据保存**：支持分批保存，防止数据丢失，提升系统稳定性

### 🎛️ 现代化Web界面
- **📊 实时监控仪表板**：爬虫状态、进度监控、系统统计和性能指标
- **🎮 任务管理中心**：启动/停止爬虫、任务历史记录、失败重试和批量操作
- **📝 实时日志系统**：WebSocket实时日志显示，支持日志筛选和全屏模式
- **📱 响应式设计**：完美支持桌面、平板和移动端访问
- **🎨 Material Design 3**：现代化UI设计，支持深色/浅色模式切换
- **🔄 实时数据同步**：WebSocket连接，实时更新数据和状态信息

### 🗄️ 企业级数据管理
- **💼 SQL-like管理界面**：类似数据库管理工具的专业操作界面
- **🔍 高级筛选系统**：多条件组合筛选，支持数值范围、文本匹配、日期范围
- **📈 智能排序功能**：多字段优先级排序，自定义排序规则
- **⚙️ 批量操作支持**：批量编辑、删除、导出数据，提升操作效率
- **📤 多格式导入导出**：支持CSV、JSON、Excel格式，兼容主流数据工具
- **🕒 筛选历史管理**：自动记录和重用筛选历史，提升操作效率
- **⭐ 项目关注列表**：支持项目收藏、批量导入和专门监控模式

### 📊 数据存储与分析
- **🗃️ 高性能数据库**：SQLite数据库存储，支持WAL模式和并发访问
- **📈 历史数据追踪**：项目数据变化历史记录和趋势分析
- **🔄 智能去重机制**：避免数据冗余，确保数据库整洁
- **📋 数据质量报告**：自动生成数据完整性和质量分析报告
- **📚 任务历史记录**：完整的爬虫任务执行历史和状态追踪
- **💾 自动备份管理**：定时数据库备份，支持SQL和JSON格式导出
- **📊 数据可视化**：支持图表展示和数据趋势分析

### 🚀 高级功能特性
- **⏰ 智能任务调度**：支持定时任务、周期性数据更新和自动化运行
- **🎯 关注列表监控**：专门的关注项目监控模式，实时跟踪重要项目
- **🔧 性能优化系统**：内存优化、网络优化、智能缓存和资源监控
- **🛡️ 错误恢复机制**：智能错误分类、自动重试和故障恢复
- **📡 实时通信系统**：WebSocket支持，实时状态更新和日志推送
- **🔒 数据安全保障**：数据完整性验证、备份恢复和访问控制

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **Node.js**: 18.0+
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
# 前端: http://localhost:3000 (热重载)
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
cd ..
python3 app.py
```

## 🏗️ 技术架构

### 后端技术栈
- **🌐 核心框架**: Flask 2.3+ + Flask-SocketIO + Flask-CORS
- **🗄️ 数据存储**: SQLite3 + pandas + numpy
- **🕷️ 爬虫引擎**: requests + BeautifulSoup4 + Selenium WebDriver
- **📊 数据处理**: pandas + numpy + openpyxl
- **⚙️ 配置管理**: YAML + 环境变量 + 动态配置
- **📝 日志系统**: Python logging + watchdog + 分级日志
- **🔧 系统监控**: psutil + 资源监控 + 性能调优
- **🔄 任务调度**: threading + 并发控制 + 任务管理器

### 前端技术栈
- **⚡ 核心框架**: Vue 3.5+ + Composition API + TypeScript支持
- **🎨 UI组件库**: Vuetify 3.8+ + Material Design 3 + MDI图标
- **🛠️ 构建工具**: Vite 6+ + 热重载 + 代码分割
- **📦 状态管理**: Pinia + 持久化存储
- **🧭 路由系统**: Vue Router 4 + 路由守卫
- **🔗 实时通信**: Socket.IO Client + 自动重连
- **📊 数据可视化**: Chart.js + Vue-ChartJS + 响应式图表
- **🎯 工具库**: @vueuse/core + dayjs + axios

### 项目架构图
```
spider_modian-main/
├── 🕷️ spider/                    # 爬虫核心模块
│   ├── core.py                   # 爬虫引擎核心逻辑
│   ├── config.py                 # 配置管理和常量定义
│   ├── api_data_fetcher.py       # API数据获取器
│   ├── exporter.py               # 数据导出模块
│   ├── monitor.py                # 爬虫监控和统计
│   ├── scheduler.py              # 任务调度器
│   ├── utils.py                  # 工具函数和辅助类
│   ├── validator.py              # 数据验证模块
│   ├── extractors/               # 数据提取器模块
│   │   ├── list_extractor.py     # 列表页面提取器
│   │   └── __init__.py
│   ├── processors/               # 数据处理器模块
│   │   ├── data_processor.py     # 数据处理器
│   │   ├── validation_processor.py # 验证处理器
│   │   └── __init__.py
│   ├── memory_optimizer.py       # 内存优化器
│   ├── network_optimizer.py      # 网络优化器
│   ├── performance_tuner.py      # 性能调优器
│   ├── error_recovery.py         # 错误恢复机制
│   └── crypto_utils.py           # 加密工具
├── 🎨 web_ui_vue/                # Vue3前端界面
│   ├── src/                      # 前端源代码
│   │   ├── components/           # Vue组件库
│   │   │   ├── ResponsiveLayout.vue # 响应式布局组件
│   │   │   ├── DataTable.vue     # 数据表格组件
│   │   │   ├── LogViewer.vue     # 日志查看器
│   │   │   └── charts/           # 图表组件
│   │   ├── views/                # 页面视图
│   │   │   ├── Dashboard.vue     # 仪表板
│   │   │   ├── SpiderControl.vue # 爬虫控制
│   │   │   ├── DataManagement.vue # 数据管理
│   │   │   ├── TaskHistory.vue   # 任务历史
│   │   │   └── WatchList.vue     # 关注列表
│   │   ├── stores/               # Pinia状态管理
│   │   │   ├── spider.js         # 爬虫状态
│   │   │   ├── data.js           # 数据状态
│   │   │   └── ui.js             # UI状态
│   │   ├── router/               # 路由配置
│   │   └── plugins/              # 插件配置
│   ├── dist/                     # 构建输出目录
│   ├── package.json              # 前端依赖配置
│   └── vite.config.js            # Vite构建配置
├── 🌐 api/                       # API路由模块
│   ├── routes/                   # API路由
│   │   ├── spider_routes.py      # 爬虫控制API
│   │   ├── data_routes.py        # 数据管理API
│   │   ├── task_routes.py        # 任务管理API
│   │   ├── system_routes.py      # 系统信息API
│   │   ├── watch_routes.py       # 关注列表API
│   │   └── settings_routes.py    # 设置管理API
│   ├── middleware/               # 中间件
│   │   ├── error_handler.py      # 错误处理
│   │   └── response_formatter.py # 响应格式化
│   └── websocket/                # WebSocket处理
│       └── handlers.py           # WebSocket事件处理
├── 🧠 core/                      # 核心管理模块
│   ├── managers/                 # 管理器模块
│   │   ├── task_manager.py       # 任务管理器
│   │   └── instance_manager.py   # 实例管理器
│   ├── monitors/                 # 监控模块
│   │   ├── web_monitor.py        # Web监控器
│   │   └── scheduled_monitor.py  # 调度监控器
│   ├── logging/                  # 日志系统
│   │   └── system_logger.py      # 系统日志器
│   └── exceptions/               # 异常处理
│       └── spider_exceptions.py  # 爬虫异常
├── �️ services/                  # 服务层模块
│   ├── spider_service.py         # 爬虫服务
│   ├── data_service.py           # 数据服务
│   ├── task_service.py           # 任务服务
│   └── log_service.py            # 日志服务
├── 🗂️ utils/                     # 工具模块
│   └── port_manager.py           # 端口管理器
├── �📁 data/                      # 数据存储目录
│   ├── database/                 # SQLite数据库文件
│   ├── raw/                      # 原始爬取数据
│   ├── exports/                  # 用户导出文件
│   ├── cache/                    # 缓存数据
│   ├── processed/                # 处理后的数据
│   └── reports/                  # 分析报告
├── 💾 backups/                   # 数据库备份文件
├── ⚙️ config/                    # 配置文件
│   └── spider_config.yaml        # 爬虫配置文件
├── 📋 logs/                      # 日志文件目录
│   ├── spider/                   # 爬虫日志
│   ├── system/                   # 系统日志
│   └── webui/                    # Web界面日志
├── 🌐 app.py                     # Flask Web服务器
├── 🚀 start_vue_ui.py            # 一键启动脚本
├── 📦 requirements.txt           # Python依赖列表
└── � README.md                  # 项目说明文档
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

- **数据查看**：浏览所有爬取的项目数据，支持分页和虚拟滚动
- **高级筛选**：使用多条件筛选查找特定数据，支持筛选历史
- **数据编辑**：直接编辑项目信息，实时验证和保存
- **批量操作**：批量选择、删除或导出数据
- **数据导出**：导出为CSV、JSON或Excel格式
- **数据备份**：一键创建数据库备份，支持SQL和JSON格式

### 4. 系统配置

- **爬虫设置**：调整爬取参数和性能配置
- **数据库管理**：查看数据库统计、备份和维护
- **任务历史**：查看和管理爬虫任务执行历史
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
- `POST /api/data/projects/batch_delete` - 批量删除项目
- `POST /api/data/export` - 导出数据
- `GET /api/data/backup` - 创建数据库备份

#### 系统信息
- `GET /api/system/stats` - 获取系统统计
- `GET /api/system/logs` - 获取系统日志
- `GET /api/system/tasks` - 获取任务历史记录

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

### v2.2.0 (2025-06-16) - 数据管理增强版本
- 🗄️ **SQL-like数据管理**：完整的数据增删改查界面，支持高级筛选和排序
- 📊 **任务历史追踪**：完善的爬虫任务执行历史记录和状态监控
- 🔍 **高级搜索功能**：多条件组合筛选，筛选历史记录和重用
- 💾 **数据备份管理**：自动数据库备份，支持SQL和JSON格式导出
- 🎛️ **批量操作支持**：批量选择、编辑、删除数据功能
- 🔧 **WebSocket优化**：修复实时通信问题，提升用户体验

### v2.1.0 (2025-06-15) - 项目优化版本
- 🧹 **项目结构优化**：清理冗余文件，统一项目架构
- 📚 **文档完善**：更新README，完善项目说明和使用指南
- 🗂️ **目录整理**：优化数据存储结构，清理测试和调试文件
- ⚡ **性能提升**：移除过时代码，提升系统运行效率
- 🔧 **配置优化**：统一配置管理，简化部署流程

### v2.0.0 (2025-06-15) - 现代化重构版本
- ✨ **全新Vue 3界面**：基于Vue 3 + Vuetify 3 + Material Design 3
- 🚀 **闪电动态数据**：优化的Selenium集成，快速获取异步数据
- 🗄️ **高级数据管理**：SQL-like数据管理界面，支持高级筛选
- 📊 **实时监控仪表板**：WebSocket实时通信，任务状态监控
- 🔧 **一键启动脚本**：自动化部署，支持开发和生产模式

### v1.0.0 - 基础功能版本
- 🕷️ **基础爬虫功能**：摩点众筹数据采集
- 💾 **数据存储导出**：Excel、CSV、JSON格式支持
- 🌐 **简单Web界面**：基础的数据查看和管理

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


</div>
