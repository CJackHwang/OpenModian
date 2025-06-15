# 📁 项目目录结构说明

## 🎯 重构后的目录结构

经过重构，项目采用了更加清晰和合理的目录结构：

```
spider_modian-main/
├── 📄 app.py                    # Flask后端主应用（Web API服务）
├── 📄 start_vue_ui.py           # 项目启动脚本
├── 📄 requirements.txt          # Python依赖
├── 📄 README.md                 # 项目说明
├── 📄 TODO.txt                  # 开发任务清单
├── 📄 LICENSE                   # 开源协议
├── 📄 PROJECT_STRUCTURE.md      # 本文件
│
├── 📁 config/                   # 配置文件
│   └── spider_config.yaml       # 爬虫配置
│
├── 📁 spider/                   # 爬虫核心模块
│   ├── __init__.py
│   ├── config.py                # 爬虫配置类
│   ├── core.py                  # 爬虫核心逻辑
│   ├── exporter.py              # 数据导出器
│   ├── lightning_fast_dynamic.py # 动态数据获取
│   ├── monitor.py               # 爬虫监控
│   ├── utils.py                 # 工具函数
│   └── validator.py             # 数据验证
│
├── 📁 data/                     # 统一数据目录
│   ├── README.md                # 数据目录说明
│   ├── database/                # 数据库文件
│   │   ├── modian_data.db       # SQLite数据库
│   │   └── db_manager.py        # 数据库管理器
│   ├── raw/                     # 原始爬取数据
│   │   ├── json/                # JSON格式数据
│   │   ├── excel/               # Excel格式数据
│   │   └── csv/                 # CSV格式数据
│   ├── cache/                   # 缓存数据
│   │   └── dynamic/             # 动态数据缓存
│   ├── processed/               # 处理后的数据
│   ├── exports/                 # 用户导出数据
│   └── reports/                 # 报告文件
│       ├── summary/             # 摘要报告
│       └── stats/               # 统计报告
│
├── 📁 logs/                     # 日志文件
│   ├── spider/                  # 爬虫日志
│   ├── webui/                   # Web UI日志
│   └── system/                  # 系统日志
│
├── 📁 web_ui_vue/               # Vue前端项目
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.js           # Vite构建配置
│   ├── index.html               # 入口HTML
│   ├── src/                     # Vue源码
│   ├── public/                  # 静态资源
│   ├── dist/                    # 构建输出
│   └── node_modules/            # 前端依赖
│
└── 📁 tests/                    # 测试文件
    ├── __init__.py
    └── test_spider.py           # 爬虫测试
```

## 🔄 重构改进点

### 1. **Web应用结构优化**
- **之前**: `web_ui/app.py` 单独目录存放Flask应用
- **现在**: `app.py` 直接放在根目录，更符合Flask项目惯例
- **优势**: 
  - 减少不必要的目录层级
  - 便于部署和维护
  - 符合Python Web项目标准结构

### 2. **数据存储统一化**
- **之前**: 数据分散在多个目录（`data/spider/`, `web_ui/data/`, `database/`, `reports/`）
- **现在**: 统一到 `data/` 目录下，按数据类型分层
- **优势**:
  - 清晰的数据分类和管理
  - 避免重复存储
  - 便于备份和维护

### 3. **前后端分离清晰**
- **后端**: `app.py` - Flask API服务
- **前端**: `web_ui_vue/` - Vue.js单页应用
- **启动**: `start_vue_ui.py` - 统一启动脚本

## 🚀 启动方式

### 生产模式（推荐）
```bash
python3 start_vue_ui.py prod
```
- 单端口运行（http://localhost:8080）
- 前后端整合
- 适合生产环境

### 开发模式
```bash
python3 start_vue_ui.py dev
```
- 前端开发服务器（http://localhost:3001）
- 后端API服务器（http://localhost:8080）
- 支持热重载

### 仅构建前端
```bash
python3 start_vue_ui.py build
```

## 📊 数据流向

```
网页数据 → 爬虫模块 → data/raw/ → data/database/ → Web UI
                    ↓
                data/cache/ (缓存)
                    ↓
                data/reports/ (报告)
                    ↓
                data/exports/ (导出)
```

## 🔧 配置文件更新

所有配置文件已更新以适应新的目录结构：

- `config/spider_config.yaml`: 数据库和输出路径
- `spider/config.py`: 输出目录和缓存目录
- `app.py`: 数据库连接路径
- `start_vue_ui.py`: Flask应用路径

## 📝 开发建议

1. **新增功能**: 在对应的模块目录下添加文件
2. **数据处理**: 使用 `data/database/db_manager.py` 进行数据操作
3. **前端开发**: 在 `web_ui_vue/src/` 下开发Vue组件
4. **测试**: 在 `tests/` 目录下添加测试文件
5. **日志**: 查看 `logs/` 目录下的相应日志文件

## 🎉 重构效果

- ✅ 目录结构更加清晰合理
- ✅ 数据存储统一管理
- ✅ 前后端分离明确
- ✅ 部署和维护更加便捷
- ✅ 符合Python Web项目最佳实践
