# 摩点桌游市场调研工具 (OpenModian)

一个专业的桌游市场调研工具，专注于摩点众筹平台的数据采集、分析和可视化。采用现代化的前后端分离架构，提供完整的数据管理和分析解决方案。

## 🎯 项目概述

OpenModian 是一个全功能的桌游市场调研平台，主要功能包括：

- **智能数据爬虫**：基于摩点API的高效数据采集系统
- **实时数据监控**：WebSocket实时日志和任务状态监控
- **数据可视化分析**：历史趋势图表、增长率分析、项目对比
- **项目关注系统**：支持项目收藏、批量导入、定制监控
- **数据库管理**：完整的数据备份、导出、恢复功能
- **现代化界面**：基于Material Design 3的响应式Web界面

## 🏗️ 技术架构

### 后端技术栈
- **Web框架**：Flask + Flask-SocketIO
- **数据库**：SQLite（支持备份和迁移）
- **数据爬虫**：基于摩点API的智能爬虫系统
- **任务调度**：内置任务调度器，支持定时任务
- **实时通信**：WebSocket实时日志和状态推送
- **API设计**：RESTful API，完整的MCP集成支持

### 前端技术栈
- **框架**：Vue 3 + Composition API
- **UI组件库**：Vuetify 3 + Material Design 3
- **状态管理**：Pinia
- **路由管理**：Vue Router 4
- **图表可视化**：Chart.js + Vue-ChartJS
- **构建工具**：Vite
- **开发语言**：JavaScript + SCSS

### 数据架构
- **统一数据目录**：分层存储架构（原始数据、缓存、导出、报告）
- **增量数据更新**：支持断点续传和增量爬取
- **数据去重**：基于哈希值的智能去重机制
- **多格式支持**：JSON、CSV、Excel多种数据格式

## 📁 项目结构

```
spider_modian-main/
├── 📱 前端界面
│   └── web_ui_vue/              # Vue3 + Vuetify3 前端
│       ├── src/
│       │   ├── components/      # 可复用组件
│       │   ├── views/          # 页面视图
│       │   ├── stores/         # Pinia状态管理
│       │   ├── composables/    # 组合式函数
│       │   └── styles/         # 样式文件
│       ├── dist/               # 构建输出
│       └── package.json        # 前端依赖
│
├── 🔧 后端核心
│   ├── app.py                  # Flask主应用
│   ├── api/                    # API路由模块
│   │   ├── routes/            # 路由定义
│   │   ├── middleware/        # 中间件
│   │   └── websocket/         # WebSocket处理
│   ├── core/                   # 核心功能模块
│   │   ├── managers/          # 管理器类
│   │   ├── monitors/          # 监控模块
│   │   ├── logging/           # 日志系统
│   │   └── exceptions/        # 异常处理
│   └── services/              # 业务服务层
│
├── 🕷️ 爬虫系统
│   └── spider/                 # 爬虫核心模块
│       ├── core.py            # 爬虫核心逻辑
│       ├── api_data_fetcher.py # API数据获取
│       ├── scheduler.py       # 任务调度
│       ├── extractors/        # 数据提取器
│       ├── processors/        # 数据处理器
│       └── config.py          # 爬虫配置
│
├── 📊 数据管理
│   └── data/                   # 统一数据目录
│       ├── database/          # SQLite数据库
│       ├── raw/               # 原始爬取数据
│       ├── cache/             # 缓存数据
│       ├── exports/           # 导出数据
│       ├── processed/         # 处理后数据
│       └── reports/           # 分析报告
│
├── 📝 配置文件
│   ├── config/                # 配置文件目录
│   ├── requirements.txt       # Python依赖
│   └── start_vue_ui.py        # 启动脚本
│
└── 📚 文档
    ├── API_DOCUMENTATION.md   # 完整API文档
    └── README.md              # 项目说明（本文件）
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+ (推荐 3.9+)
- **Node.js**: 18.0+ (前端构建)
- **操作系统**: macOS / Linux / Windows

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd spider_modian-main
```

#### 2. 安装Python依赖
```bash
# 推荐使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip3 install -r requirements.txt
```

#### 3. 安装前端依赖
```bash
cd web_ui_vue
npm install
cd ..
```

### 启动方式

#### 开发模式（推荐）
```bash
# 启动开发模式（前后端分离，支持热重载）
python3 start_vue_ui.py dev

# 访问地址：
# 前端: http://localhost:3000
# 后端API: http://localhost:8080
```

#### 生产模式
```bash
# 启动生产模式（单端口集成）
python3 start_vue_ui.py prod

# 访问地址: http://localhost:8080
```

#### 仅后端
```bash
# 仅启动后端API服务
python3 app.py
```

### 首次使用

1. **启动服务**：使用开发模式启动项目
2. **访问界面**：打开浏览器访问 http://localhost:3000
3. **配置爬虫**：在设置页面配置爬虫参数
4. **开始爬取**：在爬虫控制页面启动数据采集任务
5. **查看数据**：在数据管理页面查看和分析采集的数据

## 📋 主要功能

### 🕷️ 智能爬虫系统
- **多并发爬取**：支持可配置的并发数量和延迟控制
- **断点续传**：支持任务中断后的断点续传
- **增量更新**：智能识别新数据，避免重复爬取
- **错误恢复**：自动重试机制和错误处理
- **定时任务**：支持定时自动爬取

### 📊 数据管理与分析
- **项目监控**：实时监控项目状态和关键指标
- **历史趋势**：可视化展示项目数据的历史变化趋势
- **增长率分析**：计算和展示各项指标的增长率
- **数据对比**：支持多项目数据对比分析
- **导出功能**：支持Excel、CSV、JSON多种格式导出

### 🎯 项目关注系统
- **收藏管理**：支持项目收藏和分类管理
- **批量导入**：支持批量导入项目ID进行监控
- **定制监控**：为关注的项目设置专门的监控策略
- **通知提醒**：项目状态变化时的实时通知

### 🔧 系统管理
- **数据库备份**：自动和手动数据库备份功能
- **系统监控**：实时系统资源使用情况监控
- **日志管理**：完整的系统日志记录和查看
- **配置管理**：灵活的系统配置管理界面

### 🎨 现代化界面
- **Material Design 3**：遵循最新的Material Design设计规范
- **响应式设计**：完美适配桌面和移动设备
- **暗色模式**：支持明暗主题切换
- **实时更新**：WebSocket实时数据更新
- **无障碍设计**：符合WCAG 2.1 AA标准

## 🔌 API文档

项目提供完整的RESTful API接口，支持第三方集成和MCP工具开发。

### API文档位置
- **完整文档**：[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **在线文档**：启动服务后访问 `/api/docs`（如果配置）

### 主要API端点
- **爬虫控制**：`/api/spider/*` - 爬虫任务管理
- **数据管理**：`/api/data/*` - 数据查询和管理
- **任务管理**：`/api/tasks/*` - 任务调度和监控
- **系统管理**：`/api/system/*` - 系统状态和配置
- **项目关注**：`/api/watch/*` - 项目关注管理

### MCP集成支持
项目完全支持MCP（Model Context Protocol）集成，提供：
- 标准化的API接口
- 完整的错误处理
- 详细的响应格式
- Python客户端示例

## 🛠️ 开发指南

### 开发环境设置
```bash
# 1. 安装开发依赖
pip3 install -r requirements.txt

# 2. 安装前端开发依赖
cd web_ui_vue
npm install
npm run dev  # 启动前端开发服务器

# 3. 启动后端开发服务器
cd ..
python3 app.py
```

### 代码规范
- **后端**：遵循PEP 8 Python代码规范
- **前端**：使用ESLint + Prettier进行代码格式化
- **提交**：使用语义化提交信息

### 项目架构原则
- **模块化设计**：单一职责原则，模块间低耦合
- **前后端分离**：清晰的API边界，独立部署
- **配置驱动**：通过配置文件管理系统行为
- **错误处理**：统一的错误处理和日志记录

## 📈 性能优化

### 爬虫性能
- **并发控制**：智能并发数量调节
- **请求优化**：连接池和请求复用
- **缓存机制**：多层缓存减少重复请求
- **内存管理**：大数据集的流式处理

### 前端性能
- **代码分割**：按需加载减少初始包大小
- **虚拟滚动**：大列表的性能优化
- **图片优化**：懒加载和压缩
- **缓存策略**：合理的浏览器缓存配置

## 🔒 安全考虑

### 数据安全
- **本地存储**：所有数据存储在本地，无外部依赖
- **访问控制**：API访问控制和权限管理
- **数据备份**：定期自动备份防止数据丢失

### 网络安全
- **请求限制**：合理的请求频率控制
- **错误处理**：避免敏感信息泄露
- **CORS配置**：适当的跨域资源共享配置

## 🐛 故障排除

### 常见问题

#### 1. 端口占用
```bash
# 检查端口占用
lsof -i :8080
lsof -i :3000

# 或使用项目内置的端口管理
python3 start_vue_ui.py  # 自动选择可用端口
```

#### 2. 依赖安装失败
```bash
# 更新pip
pip3 install --upgrade pip

# 清理缓存重新安装
pip3 cache purge
pip3 install -r requirements.txt
```

#### 3. 前端构建失败
```bash
# 清理node_modules重新安装
cd web_ui_vue
rm -rf node_modules package-lock.json
npm install
```

#### 4. 数据库问题
```bash
# 检查数据库文件权限
ls -la data/database/

# 重新初始化数据库（注意：会清空数据）
rm data/database/modian_data.db
python3 -c "from data.database.db_manager import DatabaseManager; DatabaseManager().init_database()"
```

### 日志查看
```bash
# 系统日志
tail -f logs/system/system.log

# 爬虫日志
tail -f logs/spider/spider.log

# Web UI日志
tail -f logs/webui/webui.log
```

## 🤝 贡献指南

### 贡献方式
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- 遵循现有的代码风格和架构模式
- 添加适当的注释和文档
- 确保新功能有相应的测试
- 更新相关文档

## 📊 数据字段说明

### 摩点API数据映射
- **20362**: 评论数量 (comment_count)
- **30157**: 点赞数量 (like_count)
- **19372**: 好评数量 (good_rating_count)

### 核心数据字段
- **project_id**: 项目唯一标识符
- **title**: 项目标题
- **category**: 项目分类
- **target_amount**: 目标金额
- **current_amount**: 当前筹集金额
- **progress**: 完成进度百分比
- **backers_count**: 支持者数量
- **days_left**: 剩余天数
- **status**: 项目状态
- **created_time**: 创建时间
- **updated_time**: 最后更新时间

## 🔧 配置说明

### 爬虫配置 (config/spider_config.yaml)
```yaml
# 并发设置
concurrency:
  max_workers: 3
  delay_min: 1
  delay_max: 3

# 数据库设置
database:
  path: "data/database/modian_data.db"
  backup_interval: 3600

# 输出设置
output:
  formats: ["json", "csv", "excel"]
  directory: "data/raw"
```

### 系统配置
- **端口设置**: 默认8080（后端）、3000（前端开发）
- **日志级别**: INFO（可配置为DEBUG、WARNING、ERROR）
- **缓存策略**: 自动清理过期缓存文件
- **备份策略**: 每小时自动备份数据库

## 📱 界面功能说明

### 主要页面
1. **仪表板**: 系统概览和关键指标
2. **爬虫控制**: 启动、停止、配置爬虫任务
3. **数据管理**: 查看、搜索、导出项目数据
4. **项目详情**: 单个项目的详细信息和历史趋势
5. **关注列表**: 管理收藏的项目
6. **任务监控**: 查看爬虫任务状态和日志
7. **系统设置**: 配置系统参数和备份管理

### 响应式设计
- **桌面端**: 完整功能，多列布局，高信息密度
- **平板端**: 适配中等屏幕，保持核心功能
- **移动端**: 简化界面，触摸友好，核心功能优先

## 🚀 部署指南

### 生产环境部署
```bash
# 1. 构建前端
cd web_ui_vue
npm run build

# 2. 配置环境变量
export FLASK_ENV=production
export FLASK_DEBUG=False

# 3. 启动生产服务器
cd ..
python3 app.py
```

### Docker部署（可选）
```dockerfile
# Dockerfile示例
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python3", "app.py"]
```

### 系统服务配置
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/openmodian.service

# 启动服务
sudo systemctl enable openmodian
sudo systemctl start openmodian
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **Vue.js 团队** - 优秀的前端框架
- **Vuetify 团队** - 精美的组件库
- **Flask 团队** - 简洁强大的Python Web框架
- **摩点众筹** - 提供丰富的桌游项目数据

## 📞 联系方式

- **项目作者**：CJackHwang
- **项目版本**：1.0.0
- **最后更新**：2025-06-26

---

**OpenModian** - 让桌游市场调研变得简单高效 ❤️
