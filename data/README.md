# 数据目录结构说明

本目录包含摩点爬虫项目的所有数据文件，采用统一的分层存储架构。

## 📁 目录结构

```
data/
├── database/           # 数据库文件
│   ├── modian_data.db  # SQLite数据库（主要数据存储）
│   └── db_manager.py   # 数据库管理模块
├── raw/               # 爬虫原始输出数据
│   ├── json/          # JSON格式数据
│   ├── excel/         # Excel格式数据（.xls/.xlsx）
│   └── csv/           # CSV格式数据
├── processed/         # 处理后的数据
├── cache/            # 缓存数据
│   └── dynamic/      # 动态数据缓存（Selenium获取的数据）
├── exports/          # 用户导出的数据
└── reports/          # 报告文件
    ├── summary/      # 摘要报告（.txt格式）
    └── stats/        # 统计报告（.json格式）
```

## 📊 数据类型说明

### 1. 数据库文件 (`database/`)
- **modian_data.db**: 主要的SQLite数据库，存储所有爬取的项目数据
- **db_manager.py**: 数据库管理模块，提供CRUD操作接口

### 2. 原始数据 (`raw/`)
- **json/**: 爬虫直接输出的JSON格式数据
- **excel/**: 爬虫输出的Excel文件（.xls格式）
- **csv/**: 爬虫输出的CSV文件

### 3. 缓存数据 (`cache/`)
- **dynamic/**: 动态数据缓存，包含通过Selenium获取的交互数据（点赞数、评论数等）

### 4. 报告文件 (`reports/`)
- **summary/**: 文本格式的摘要报告，包含爬取统计和数据分析
- **stats/**: JSON格式的详细统计数据

### 5. 导出数据 (`exports/`)
- 用户通过Web UI或API导出的数据文件

### 6. 处理数据 (`processed/`)
- 经过清洗、转换或分析后的数据文件

## 🔄 数据流向

```
网页数据 → 爬虫 → raw/ → 数据库 → exports/
                ↓
              cache/ (动态数据)
                ↓
            reports/ (统计报告)
```

## 📝 文件命名规范

- **时间戳格式**: `YYYYMMDD_HHMMSS`
- **JSON文件**: `modian_projects_YYYYMMDD_HHMMSS.json`
- **Excel文件**: `摩点众筹-主要信息_YYYYMMDD_HHMMSS.xls`
- **统计报告**: `spider_stats_YYYYMMDD_HHMMSS.json`
- **摘要报告**: `spider_summary_YYYYMMDD_HHMMSS.txt`

## 🗄️ 数据管理

### 自动清理
- 缓存文件会根据配置自动过期清理
- 旧的报告文件可以定期归档

### 备份策略
- 数据库文件定期自动备份
- 重要的原始数据文件保留历史版本

### 访问接口
- 通过 `data.database.db_manager.DatabaseManager` 访问数据库
- 通过 Web UI 的 `/api/database/*` 接口访问数据
- 直接读取文件系统中的原始数据文件

## 🔧 配置文件更新

相关配置文件已更新以使用新的目录结构：

- `config/spider_config.yaml`: 更新了数据库路径和输出目录
- `spider/config.py`: 更新了输出目录和缓存目录配置
- `web_ui/app.py`: 更新了数据库和JSON文件路径

## 📈 数据完整性

- 所有数据文件都包含时间戳，便于追踪数据版本
- 数据库使用哈希值进行去重，避免重复数据
- 支持增量更新和历史数据追踪
