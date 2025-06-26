# 摩点项目爬虫系统 API 开发者文档

## 概述

本文档提供摩点项目爬虫系统的完整API接口说明，适用于前端集成、第三方开发和MCP工具开发。所有API均基于RESTful设计，使用JSON格式进行数据交换。

**基础信息：**
- 基础URL: `http://localhost:5000`
- 内容类型: `application/json`
- 字符编码: `UTF-8`

## 目录

1. [爬虫控制API](#爬虫控制api)
2. [数据管理API](#数据管理api)
3. [任务管理API](#任务管理api)
4. [系统管理API](#系统管理api)
5. [用户设置API](#用户设置api)
6. [项目关注API](#项目关注api)
7. [错误代码说明](#错误代码说明)
8. [MCP集成说明](#mcp集成说明)

---

## 爬虫控制API

### 1. 启动爬虫任务

**接口地址：** `POST /api/start_crawl`

**功能说明：** 启动新的爬虫任务，支持普通任务和定时任务

**请求参数：**
```json
{
  "start_page": 1,
  "end_page": 10,
  "category": "all",
  "max_concurrent": 3,
  "delay_min": 1,
  "delay_max": 3,
  "is_scheduled": false,
  "schedule_interval": 3600
}
```

**参数说明：**
- `start_page` (int, 必填): 起始页码，默认1
- `end_page` (int, 必填): 结束页码，默认10
- `category` (string, 可选): 项目分类，默认"all"，可选值见分类列表
- `max_concurrent` (int, 可选): 最大并发数，默认3
- `delay_min` (int, 可选): 最小延迟秒数，默认1
- `delay_max` (int, 可选): 最大延迟秒数，默认3
- `is_scheduled` (bool, 可选): 是否为定时任务，默认false
- `schedule_interval` (int, 可选): 定时间隔（秒），仅定时任务需要

**成功响应：**
```json
{
  "success": true,
  "task_id": "task_20241226_143022_abc123",
  "message": "任务启动成功",
  "is_scheduled": false
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "启动失败: 参数验证错误"
}
```

### 2. 停止爬虫任务

**接口地址：** `POST /api/stop_crawl/{task_id}`

**功能说明：** 停止指定的爬虫任务

**路径参数：**
- `task_id` (string, 必填): 任务ID

**成功响应：**
```json
{
  "success": true,
  "message": "任务已停止"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "任务不存在"
}
```

### 3. 获取默认配置

**接口地址：** `GET /api/config`

**功能说明：** 获取爬虫默认配置参数

**成功响应：**
```json
{
  "success": true,
  "config": {
    "start_page": 1,
    "end_page": 10,
    "category": "all",
    "max_concurrent": 3,
    "delay_min": 1,
    "delay_max": 3,
    "categories": [
      {"value": "all", "label": "全部"},
      {"value": "games", "label": "游戏"},
      {"value": "publishing", "label": "出版"},
      {"value": "tablegames", "label": "桌游"},
      {"value": "toys", "label": "潮玩模型"},
      {"value": "cards", "label": "卡牌"},
      {"value": "technology", "label": "科技"},
      {"value": "film-video", "label": "影视"},
      {"value": "music", "label": "音乐"},
      {"value": "activities", "label": "活动"},
      {"value": "design", "label": "设计"},
      {"value": "curio", "label": "文玩"},
      {"value": "home", "label": "家居"},
      {"value": "food", "label": "食品"},
      {"value": "comics", "label": "动漫"},
      {"value": "charity", "label": "爱心通道"},
      {"value": "animals", "label": "动物救助"},
      {"value": "wishes", "label": "个人愿望"},
      {"value": "others", "label": "其他"}
    ]
  }
}
```

---

## 数据管理API

### 1. 获取数据库统计信息

**接口地址：** `GET /api/database/stats`

**功能说明：** 获取数据库中项目的统计信息

**成功响应：**
```json
{
  "success": true,
  "stats": {
    "total_projects": 1250,
    "today_projects": 45,
    "week_projects": 320,
    "category_stats": {
      "games": 450,
      "publishing": 320,
      "tablegames": 280
    },
    "total_tasks": 156,
    "task_stats": {
      "completed": 120,
      "failed": 15,
      "running": 1
    }
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取统计信息失败: 数据库连接错误"
}
```

### 2. 搜索项目数据

**接口地址：** `POST /api/database/projects/search`

**功能说明：** 根据条件搜索项目数据，支持分页和排序

**请求参数：**
```json
{
  "conditions": {
    "category": "games",
    "project_name": "关键词",
    "project_id": "123456",
    "time_period": "today"
  },
  "sort": [
    {
      "field": "raised_amount",
      "direction": "desc"
    }
  ],
  "limit": 20,
  "offset": 0
}
```

**参数说明：**
- `conditions` (object, 可选): 搜索条件
  - `category` (string): 项目分类
  - `project_name` (string): 项目名称关键词
  - `project_id` (string): 项目ID
  - `time_period` (string): 时间范围 (today/week/month/all)
- `sort` (array, 可选): 排序配置数组
  - `field` (string): 排序字段名
  - `direction` (string): 排序方向 (asc/desc)
- `limit` (int, 可选): 每页数量，默认20
- `offset` (int, 可选): 偏移量，默认0

**成功响应：**
```json
{
  "success": true,
  "projects": [
    {
      "project_url": "https://zhongchou.modian.com/item/123456.html",
      "project_id": "123456",
      "project_name": "示例项目",
      "project_image": "https://example.com/image.jpg",
      "category": "games",
      "author_name": "示例作者",
      "author_link": "https://zhongchou.modian.com/u/author123",
      "start_time": "2024-12-01 10:00:00",
      "end_time": "2025-01-01 10:00:00",
      "raised_amount": 50000.00,
      "target_amount": 100000.00,
      "completion_rate": "50%",
      "backer_count": 150,
      "update_count": 5,
      "comment_count": 25,
      "supporter_count": 150,
      "project_status": "进行中",
      "crawl_time": "2024-12-26 14:30:22"
    }
  ],
  "total_count": 1250
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "搜索项目失败: 查询参数错误"
}
```

### 3. 获取项目详情

**接口地址：** `GET /api/projects/{project_id}/detail`

**功能说明：** 获取指定项目的详细信息

**路径参数：**
- `project_id` (string, 必填): 项目ID（6位数字）

**成功响应：**
```json
{
  "success": true,
  "project": {
    "project_url": "https://zhongchou.modian.com/item/123456.html",
    "project_id": "123456",
    "project_name": "示例项目",
    "project_image": "https://example.com/image.jpg",
    "category": "games",
    "author_name": "示例作者",
    "author_link": "https://zhongchou.modian.com/u/author123",
    "start_time": "2024-12-01 10:00:00",
    "end_time": "2025-01-01 10:00:00",
    "raised_amount": 50000.00,
    "target_amount": 100000.00,
    "completion_rate": "50%",
    "backer_count": 150,
    "update_count": 5,
    "comment_count": 25,
    "supporter_count": 150,
    "project_status": "进行中",
    "rewards_data": "...",
    "content_images": "...",
    "content_videos": "...",
    "crawl_time": "2024-12-26 14:30:22"
  },
  "statistics": {
    "record_count": 15,
    "first_crawl": "2024-12-01 10:00:00",
    "last_crawl": "2024-12-26 14:30:22",
    "trends": {
      "raised_amount": {
        "first_value": 30000.00,
        "last_value": 50000.00,
        "change": 20000.00,
        "change_rate": 66.67,
        "has_change": true
      }
    },
    "has_changes": true,
    "change_summary": "筹款金额增长66.67%"
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "项目不存在"
}
```

### 4. 获取项目历史数据

**接口地址：** `GET /api/projects/{project_id}/history`

**功能说明：** 获取项目的历史数据变化

**路径参数：**
- `project_id` (string, 必填): 项目ID

**查询参数：**
- `limit` (int, 可选): 返回记录数量，默认50
- `offset` (int, 可选): 偏移量，默认0

**成功响应：**
```json
{
  "success": true,
  "history": [
    {
      "project_url": "https://zhongchou.modian.com/item/123456.html",
      "project_id": "123456",
      "project_name": "示例项目",
      "raised_amount": 50000.00,
      "target_amount": 100000.00,
      "completion_rate": "50%",
      "backer_count": 150,
      "crawl_time": "2024-12-26 14:30:22"
    }
  ],
  "total_count": 15,
  "limit": 50,
  "offset": 0,
  "changes": {
    "has_changes": true,
    "change_summary": "筹款金额增长66.67%"
  },
  "statistics": {
    "record_count": 15,
    "first_crawl": "2024-12-01 10:00:00",
    "last_crawl": "2024-12-26 14:30:22"
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取项目历史失败: 项目不存在"
}
```

### 5. 获取项目变化检测

**接口地址：** `GET /api/projects/{project_id}/changes`

**功能说明：** 获取项目数据变化检测结果

**路径参数：**
- `project_id` (string, 必填): 项目ID

**成功响应：**
```json
{
  "success": true,
  "project_id": "123456",
  "changes": {
    "has_changes": true,
    "change_summary": "筹款金额增长66.67%",
    "trends": {
      "raised_amount": {
        "first_value": 30000.00,
        "last_value": 50000.00,
        "change": 20000.00,
        "change_rate": 66.67,
        "has_change": true
      }
    }
  }
}
```

### 6. 获取项目统计数据

**接口地址：** `GET /api/projects/{project_id}/statistics`

**功能说明：** 获取项目统计数据和趋势分析

**路径参数：**
- `project_id` (string, 必填): 项目ID

**成功响应：**
```json
{
  "success": true,
  "project_id": "123456",
  "statistics": {
    "record_count": 15,
    "first_crawl": "2024-12-01 10:00:00",
    "last_crawl": "2024-12-26 14:30:22",
    "trends": {
      "raised_amount": {
        "first_value": 30000.00,
        "last_value": 50000.00,
        "change": 20000.00,
        "change_rate": 66.67,
        "has_change": true
      }
    },
    "has_changes": true,
    "change_summary": "筹款金额增长66.67%"
  }
}
```

### 7. 获取数据库项目列表

**接口地址：** `GET /api/database/projects`

**功能说明：** 获取数据库中的项目数据（支持基础筛选）

**查询参数：**
- `period` (string, 可选): 时间范围，默认"all"
- `category` (string, 可选): 项目分类，默认"all"
- `limit` (int, 可选): 返回数量限制，默认100

**成功响应：**
```json
{
  "success": true,
  "projects": [
    {
      "project_url": "https://zhongchou.modian.com/item/123456.html",
      "project_id": "123456",
      "project_name": "示例项目",
      "project_image": "https://example.com/image.jpg",
      "category": "games",
      "author_name": "示例作者",
      "raised_amount": 50000.00,
      "target_amount": 100000.00,
      "completion_rate": "50%",
      "backer_count": 150,
      "crawl_time": "2024-12-26 14:30:22"
    }
  ],
  "count": 89
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取项目数据失败: 数据库查询错误"
}
```

### 8. 搜索数据库项目（简化版）

**接口地址：** `POST /api/database/search`

**功能说明：** 搜索项目（简化版接口，与/api/database/projects/search功能相同）

**请求参数：**
```json
{
  "conditions": {
    "category": "games",
    "project_name": "关键词"
  },
  "limit": 100,
  "offset": 0
}
```

**成功响应：**
```json
{
  "success": true,
  "projects": [
    {
      "project_url": "https://zhongchou.modian.com/item/123456.html",
      "project_id": "123456",
      "project_name": "示例项目",
      "category": "games",
      "raised_amount": 50000.00,
      "crawl_time": "2024-12-26 14:30:22"
    }
  ],
  "total_count": 1250,
  "limit": 100,
  "offset": 0
}
```

### 9. 获取筛选选项

**接口地址：** `GET /api/database/filter_options`

**功能说明：** 获取可用的筛选选项

**成功响应：**
```json
{
  "success": true,
  "options": {
    "categories": [
      {"value": "all", "label": "全部"},
      {"value": "games", "label": "游戏"},
      {"value": "publishing", "label": "出版"},
      {"value": "tablegames", "label": "桌游"}
    ],
    "time_periods": [
      {"value": "all", "label": "全部时间"},
      {"value": "today", "label": "今天"},
      {"value": "week", "label": "本周"},
      {"value": "month", "label": "本月"}
    ],
    "amount_ranges": {
      "min_amount": 0,
      "max_amount": 1000000,
      "avg_amount": 25000.50
    }
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取筛选选项失败: 系统错误"
}
```

---

## 任务管理API

### 1. 获取任务列表

**接口地址：** `GET /api/tasks`

**功能说明：** 获取所有活跃任务和定时任务

**成功响应：**
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "task_20241226_143022_abc123",
      "task_type": "normal",
      "config": {
        "start_page": 1,
        "end_page": 10,
        "category": "all",
        "max_concurrent": 3,
        "delay_min": 1,
        "delay_max": 3
      },
      "stats": {
        "status": "running",
        "progress": 45.5,
        "start_time": "2024-12-26 14:30:22",
        "end_time": null,
        "duration": "15分钟",
        "projects_found": 89,
        "projects_processed": 45,
        "errors_count": 2,
        "current_page": 5,
        "total_pages": 10
      },
      "is_scheduled": false
    }
  ],
  "normal_tasks": 1,
  "scheduled_tasks": 2
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取任务列表失败: 系统错误"
}
```

### 2. 获取任务历史

**接口地址：** `GET /api/tasks/history`

**功能说明：** 获取历史任务记录

**查询参数：**
- `limit` (int, 可选): 返回数量限制，默认100

**成功响应：**
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "task_20241226_143022_abc123",
      "status": "completed",
      "start_page": 1,
      "end_page": 10,
      "category": "all",
      "projects_processed": 89,
      "projects_found": 89,
      "errors_count": 0,
      "start_time": "2024-12-26 14:30:22",
      "end_time": "2024-12-26 15:45:33",
      "duration": "1小时15分钟",
      "config": {
        "start_page": 1,
        "end_page": 10,
        "category": "all"
      }
    }
  ],
  "count": 156
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取任务历史失败: 数据库查询错误"
}
```

### 3. 获取任务详情

**接口地址：** `GET /api/task/{task_id}`

**功能说明：** 获取指定任务的详细信息（活跃任务或历史任务）

**路径参数：**
- `task_id` (string, 必填): 任务ID

**成功响应（活跃任务）：**
```json
{
  "success": true,
  "task": {
    "task_id": "task_20241226_143022_abc123",
    "config": {
      "start_page": 1,
      "end_page": 10,
      "category": "all",
      "max_concurrent": 3,
      "delay_min": 1,
      "delay_max": 3
    },
    "stats": {
      "status": "running",
      "progress": 45.5,
      "start_time": "2024-12-26 14:30:22",
      "end_time": null,
      "duration": "15分钟",
      "projects_found": 89,
      "projects_processed": 45,
      "errors_count": 2,
      "current_page": 5,
      "total_pages": 10
    },
    "is_active": true
  }
}
```

**成功响应（历史任务）：**
```json
{
  "success": true,
  "task": {
    "task_id": "task_20241226_143022_abc123",
    "status": "completed",
    "start_page": 1,
    "end_page": 10,
    "category": "all",
    "projects_processed": 89,
    "projects_found": 89,
    "errors_count": 0,
    "start_time": "2024-12-26 14:30:22",
    "end_time": "2024-12-26 15:45:33",
    "duration": "1小时15分钟",
    "is_active": false
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "任务不存在"
}
```

### 4. 定时任务控制

#### 4.1 启用/禁用定时任务

**接口地址：** `POST /api/scheduled_tasks/{task_id}/toggle`

**功能说明：** 启用/禁用定时任务

**路径参数：**
- `task_id` (string, 必填): 定时任务ID

**成功响应：**
```json
{
  "success": true,
  "message": "定时任务状态已更新"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "定时任务不存在"
}
```

#### 4.2 立即执行定时任务

**接口地址：** `POST /api/scheduled_tasks/{task_id}/run_now`

**功能说明：** 立即执行定时任务

**路径参数：**
- `task_id` (string, 必填): 定时任务ID

**成功响应：**
```json
{
  "success": true,
  "message": "任务已开始执行"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "定时任务不存在或执行失败"
}
```

### 5. 删除任务

**接口地址：** `DELETE /api/tasks/{task_id}`

**功能说明：** 删除指定任务记录

**路径参数：**
- `task_id` (string, 必填): 任务ID

**成功响应：**
```json
{
  "success": true,
  "message": "任务已删除"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "任务不存在或删除失败"
}
```

### 6. 下载任务结果

**接口地址：** `GET /api/download/{task_id}`

**功能说明：** 下载指定任务的爬取结果文件

**路径参数：**
- `task_id` (string, 必填): 任务ID

**成功响应：** 文件下载流（Excel文件）

**错误响应：**
```json
{
  "success": false,
  "message": "没有找到输出文件"
}
```

---

## 系统管理API

### 1. 获取系统状态

**接口地址：** `GET /api/system/status`

**功能说明：** 获取系统运行状态和资源使用情况

**成功响应：**
```json
{
  "success": true,
  "system_info": {
    "platform": "Darwin",
    "platform_version": "23.1.0",
    "python_version": "3.9.7",
    "cpu_count": 8,
    "memory_total": 17179869184,
    "memory_available": 8589934592,
    "disk_usage": 65.2
  },
  "database_status": {
    "connected": true,
    "total_projects": 1250,
    "total_tasks": 156,
    "db_size": "25.6 MB",
    "last_backup": "2024-12-26 10:00:00"
  },
  "timestamp": "2024-12-26T14:30:22.123456"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取系统状态失败: 系统资源访问错误"
}
```

### 2. 获取系统配置

**接口地址：** `GET /api/system/config`

**功能说明：** 获取系统配置信息

**成功响应：**
```json
{
  "success": true,
  "config": {
    "spider_settings": {
      "max_concurrent_requests": 3,
      "request_delay": [1, 3],
      "save_interval": 10,
      "max_retries": 3
    },
    "output_settings": {
      "output_dir": "./output",
      "cache_dir": "./cache",
      "excel_filename": "modian_projects_{timestamp}.xlsx"
    },
    "monitoring_settings": {
      "enable_monitoring": true,
      "stats_update_interval": 10
    }
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取系统配置失败: 配置文件读取错误"
}
```

### 3. 数据库备份

**接口地址：** `POST /api/backup/create`

**功能说明：** 创建数据库备份

**请求参数：**
```json
{
  "format": "sql",
  "include_data": true,
  "compress": true
}
```

**参数说明：**
- `format` (string, 可选): 备份格式，支持"sql"和"json"，默认"sql"
- `include_data` (bool, 可选): 是否包含数据，默认true
- `compress` (bool, 可选): 是否压缩，默认true

**成功响应：**
```json
{
  "success": true,
  "backup_file": "backup_20241226_143022.sql.gz",
  "file_size": 2048576,
  "file_path": "/path/to/backup/backup_20241226_143022.sql.gz",
  "message": "备份创建成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "备份创建失败: 磁盘空间不足"
}
```

### 4. 获取备份列表

**接口地址：** `GET /api/backup/list`

**功能说明：** 获取所有备份文件列表

**成功响应：**
```json
{
  "success": true,
  "backups": [
    {
      "filename": "backup_20241226_143022.sql.gz",
      "size": 2048576,
      "size_formatted": "2.0 MB",
      "created_time": "2024-12-26 14:30:22",
      "modified_time": "2024-12-26 14:30:22",
      "format": "sql",
      "is_valid": true
    }
  ]
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取备份列表失败: 备份目录不存在"
}
```

### 5. 下载备份文件

**接口地址：** `GET /api/backup/download/{filename}`

**功能说明：** 下载指定的备份文件

**路径参数：**
- `filename` (string, 必填): 备份文件名

**成功响应：** 文件下载流

**错误响应：**
```json
{
  "success": false,
  "message": "备份文件不存在"
}
```

### 6. 恢复数据库备份

**接口地址：** `POST /api/backup/restore`

**功能说明：** 从备份文件恢复数据库

**请求参数：**
```json
{
  "backup_filename": "backup_20241226_143022.sql.gz"
}
```

**参数说明：**
- `backup_filename` (string, 必填): 备份文件名

**成功响应：**
```json
{
  "success": true,
  "message": "数据库恢复成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "恢复备份失败: 备份文件损坏"
}
```

### 7. 上传备份文件

**接口地址：** `POST /api/backup/upload`

**功能说明：** 上传备份文件到服务器

**请求格式：** `multipart/form-data`

**请求参数：**
- `file` (file, 必填): 备份文件（支持.sql和.json格式）

**成功响应：**
```json
{
  "success": true,
  "filename": "uploaded_backup_20241226_143022.sql",
  "file_size": 2048576,
  "message": "备份文件上传成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "不支持的文件类型，仅支持 .sql 和 .json 文件"
}
```

### 8. 删除备份文件

**接口地址：** `DELETE /api/backup/delete/{filename}`

**功能说明：** 删除指定的备份文件

**路径参数：**
- `filename` (string, 必填): 备份文件名

**成功响应：**
```json
{
  "success": true,
  "message": "备份文件已删除"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "备份文件不存在或删除失败"
}
```

### 9. 系统备份管理

#### 9.1 创建系统备份

**接口地址：** `POST /api/system/backup`

**功能说明：** 创建系统级备份（包括配置文件等）

**请求参数：**
```json
{
  "type": "database_only"
}
```

**参数说明：**
- `type` (string, 可选): 备份类型，"database_only"或"full"，默认"database_only"

**成功响应：**
```json
{
  "success": true,
  "backup_file": "system_backup_20241226_143022.tar.gz",
  "backup_type": "database_only",
  "message": "数据库备份创建成功"
}
```

#### 9.2 恢复系统备份

**接口地址：** `POST /api/system/backup/restore`

**功能说明：** 恢复系统备份

**请求参数：**
```json
{
  "backup_filename": "system_backup_20241226_143022.tar.gz"
}
```

**成功响应：**
```json
{
  "success": true,
  "message": "系统恢复成功"
}
```

#### 9.3 获取系统备份列表

**接口地址：** `GET /api/system/backup/list`

**功能说明：** 获取系统备份文件列表

**成功响应：**
```json
{
  "success": true,
  "backups": [
    {
      "filename": "system_backup_20241226_143022.tar.gz",
      "size": 5242880,
      "created_time": "2024-12-26 14:30:22",
      "backup_type": "database_only"
    }
  ],
  "count": 1
}
```

#### 9.4 删除系统备份

**接口地址：** `DELETE /api/system/backup/{filename}`

**功能说明：** 删除系统备份文件

**路径参数：**
- `filename` (string, 必填): 备份文件名

**成功响应：**
```json
{
  "success": true,
  "message": "备份文件删除成功"
}
```

---

## 用户设置API

### 1. 获取用户设置

**接口地址：** `GET /api/settings`

**功能说明：** 获取所有用户设置

**成功响应：**
```json
{
  "success": true,
  "settings": {
    "spider_max_concurrent": 3,
    "spider_delay_min": 1,
    "spider_delay_max": 3,
    "spider_category": "all",
    "spider_start_page": 1,
    "spider_end_page": 10,
    "theme_mode": "light"
  }
}
```

### 2. 保存用户设置

**接口地址：** `POST /api/settings`

**功能说明：** 批量保存用户设置

**请求参数：**
```json
{
  "settings": {
    "spider_max_concurrent": 5,
    "spider_delay_min": 2,
    "spider_delay_max": 4,
    "theme_mode": "dark"
  }
}
```

**成功响应：**
```json
{
  "success": true,
  "message": "设置保存成功",
  "saved_count": 4
}
```

### 3. 更新单个设置

**接口地址：** `PUT /api/settings/{setting_key}`

**功能说明：** 更新单个用户设置

**路径参数：**
- `setting_key` (string): 设置键名

**请求参数：**
```json
{
  "value": 5,
  "type": "int",
  "description": "最大并发数设置"
}
```

**成功响应：**
```json
{
  "success": true,
  "message": "设置更新成功"
}
```

---

## 项目关注API

### 1. 添加关注项目

**接口地址：** `POST /api/watch/add`

**功能说明：** 添加项目到关注列表

**请求参数：**
```json
{
  "project_id": "123456",
  "project_name": "示例项目",
  "project_url": "https://zhongchou.modian.com/item/123456.html",
  "category": "games",
  "author_name": "示例作者",
  "notes": "备注信息"
}
```

**成功响应：**
```json
{
  "success": true,
  "message": "项目已添加到关注列表"
}
```

### 2. 获取关注列表

**接口地址：** `GET /api/watch/list`

**功能说明：** 获取用户关注的项目列表

**查询参数：**
- `active_only` (bool, 可选): 是否只返回活跃项目，默认true

**成功响应：**
```json
{
  "success": true,
  "projects": [
    {
      "id": 1,
      "project_id": "123456",
      "project_name": "示例项目",
      "project_url": "https://zhongchou.modian.com/item/123456.html",
      "category": "games",
      "author_name": "示例作者",
      "author_link": "https://zhongchou.modian.com/u/author123",
      "notes": "备注信息",
      "is_active": true,
      "added_time": "2024-12-26 14:30:22",
      "updated_time": "2024-12-26 15:00:00"
    }
  ],
  "count": 25
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "获取关注列表失败: 数据库查询错误"
}
```

### 3. 批量添加关注项目

**接口地址：** `POST /api/watch/batch_add`

**功能说明：** 批量添加项目到关注列表

**请求参数：**
```json
{
  "projects": [
    {
      "project_id": "123456",
      "project_name": "项目1",
      "category": "games"
    },
    {
      "project_id": "789012",
      "project_name": "项目2",
      "category": "publishing"
    }
  ]
}
```

**成功响应：**
```json
{
  "success": true,
  "message": "批量添加完成：新增 2 个，跳过 0 个，错误 0 个",
  "result": {
    "added": 2,
    "skipped": 0,
    "errors": 0
  }
}
```

### 4. 检查关注状态

**接口地址：** `GET /api/watch/check/{project_id}`

**功能说明：** 检查项目是否已被关注

**路径参数：**
- `project_id` (string, 必填): 项目ID

**成功响应：**
```json
{
  "success": true,
  "is_watched": true,
  "project_id": "123456"
}
```

### 5. 移除关注项目

**接口地址：** `DELETE /api/watch/remove/{project_id}`

**功能说明：** 从关注列表中移除项目

**路径参数：**
- `project_id` (string, 必填): 项目ID

**成功响应：**
```json
{
  "success": true,
  "message": "项目已从关注列表中移除"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "项目不在关注列表中"
}
```

### 6. 更新关注项目

**接口地址：** `PUT /api/watch/update/{project_id}`

**功能说明：** 更新关注项目信息

**路径参数：**
- `project_id` (string, 必填): 项目ID

**请求参数：**
```json
{
  "project_name": "更新的项目名称",
  "notes": "更新的备注信息",
  "category": "tablegames"
}
```

**参数说明：**
- `project_name` (string, 可选): 项目名称
- `notes` (string, 可选): 备注信息
- `category` (string, 可选): 项目分类

**成功响应：**
```json
{
  "success": true,
  "message": "关注项目信息已更新"
}
```

**错误响应：**
```json
{
  "success": false,
  "message": "项目不在关注列表中"
}
```

---

## 错误代码说明

### HTTP状态码

- **200 OK**: 请求成功
- **400 Bad Request**: 请求参数错误
- **401 Unauthorized**: 未授权访问
- **403 Forbidden**: 禁止访问
- **404 Not Found**: 资源不存在
- **409 Conflict**: 资源冲突（如重复添加）
- **500 Internal Server Error**: 服务器内部错误

### 业务错误代码

所有API响应都包含 `success` 字段，当 `success: false` 时，`message` 字段包含具体错误信息。

**常见错误类型：**

1. **参数验证错误**
   ```json
   {
     "success": false,
     "message": "参数验证失败: start_page必须大于0"
   }
   ```

2. **资源不存在错误**
   ```json
   {
     "success": false,
     "message": "项目不存在"
   }
   ```

3. **系统错误**
   ```json
   {
     "success": false,
     "message": "数据库连接失败"
   }
   ```

4. **业务逻辑错误**
   ```json
   {
     "success": false,
     "message": "任务正在运行中，无法启动新任务"
   }
   ```

---

## MCP集成说明

### MCP工具开发建议

1. **认证处理**: 当前系统无需认证，直接访问API即可
2. **错误处理**: 始终检查响应中的 `success` 字段，根据错误信息进行适当处理
3. **分页处理**: 使用 `limit` 和 `offset` 参数进行分页，建议单次请求不超过100条记录
4. **实时更新**: 可通过WebSocket连接获取实时日志和状态更新
5. **重试机制**: 对于网络错误或临时故障，建议实现指数退避重试策略
6. **数据缓存**: 对于不经常变化的数据（如分类列表），建议实现本地缓存

### WebSocket连接

**连接地址：** `ws://localhost:5000/socket.io/`

**连接参数：**
- 协议版本: Socket.IO v4
- 传输方式: websocket, polling

**事件类型：**
- `log_message`: 实时日志消息
- `task_update`: 任务状态更新
- `system_stats`: 系统统计更新
- `project_update`: 项目数据更新
- `backup_complete`: 备份完成通知

**连接示例：**
```javascript
const socket = io('http://localhost:5000');

socket.on('log_message', (data) => {
    console.log('日志:', data.message);
});

socket.on('task_update', (data) => {
    console.log('任务更新:', data.task_id, data.status);
});
```

### 推荐的MCP工具功能

1. **项目监控工具**: 监控关注项目的数据变化，发送变化通知
2. **批量操作工具**: 批量添加/删除关注项目，批量导入项目ID
3. **数据分析工具**: 基于API数据进行趋势分析，生成图表报告
4. **自动化爬虫工具**: 定时执行爬虫任务，智能调度策略
5. **报告生成工具**: 生成项目数据报告，支持多种格式导出
6. **备份管理工具**: 自动备份管理，定期清理旧备份
7. **数据同步工具**: 与外部系统同步项目数据
8. **预警系统**: 基于项目数据变化的智能预警

### 完整的MCP工具代码示例

```python
import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

class ModianAPIClient:
    """摩点API客户端 - 适用于MCP工具开发"""

    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ModianMCPClient/1.0'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """统一的请求处理方法"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"请求失败: {str(e)}"}

    # 爬虫控制
    def start_crawl_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """启动爬虫任务"""
        return self._make_request('POST', '/api/start_crawl', json=config)

    def stop_crawl_task(self, task_id: str) -> Dict[str, Any]:
        """停止爬虫任务"""
        return self._make_request('POST', f'/api/stop_crawl/{task_id}')

    def get_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return self._make_request('GET', '/api/config')

    # 数据管理
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计"""
        return self._make_request('GET', '/api/database/stats')

    def search_projects(self, conditions: Optional[Dict] = None,
                       sort: Optional[List[Dict]] = None,
                       limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """搜索项目"""
        data = {
            "conditions": conditions or {},
            "limit": limit,
            "offset": offset
        }
        if sort:
            data["sort"] = sort
        return self._make_request('POST', '/api/database/projects/search', json=data)

    def get_project_detail(self, project_id: str) -> Dict[str, Any]:
        """获取项目详情"""
        return self._make_request('GET', f'/api/projects/{project_id}/detail')

    def get_project_history(self, project_id: str, limit: int = 50,
                           offset: int = 0) -> Dict[str, Any]:
        """获取项目历史"""
        params = {"limit": limit, "offset": offset}
        return self._make_request('GET', f'/api/projects/{project_id}/history', params=params)

    # 任务管理
    def get_tasks(self) -> Dict[str, Any]:
        """获取任务列表"""
        return self._make_request('GET', '/api/tasks')

    def get_task_history(self, limit: int = 100) -> Dict[str, Any]:
        """获取任务历史"""
        params = {"limit": limit}
        return self._make_request('GET', '/api/tasks/history', params=params)

    def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """获取任务详情"""
        return self._make_request('GET', f'/api/task/{task_id}')

    # 项目关注
    def add_watched_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加关注项目"""
        return self._make_request('POST', '/api/watch/add', json=project_data)

    def get_watched_projects(self, active_only: bool = True) -> Dict[str, Any]:
        """获取关注列表"""
        params = {"active_only": str(active_only).lower()}
        return self._make_request('GET', '/api/watch/list', params=params)

    def batch_add_watched_projects(self, projects: List[Dict]) -> Dict[str, Any]:
        """批量添加关注项目"""
        return self._make_request('POST', '/api/watch/batch_add', json={"projects": projects})

    def remove_watched_project(self, project_id: str) -> Dict[str, Any]:
        """移除关注项目"""
        return self._make_request('DELETE', f'/api/watch/remove/{project_id}')

    # 系统管理
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return self._make_request('GET', '/api/system/status')

    def create_backup(self, format_type: str = "sql",
                     include_data: bool = True, compress: bool = True) -> Dict[str, Any]:
        """创建备份"""
        data = {
            "format": format_type,
            "include_data": include_data,
            "compress": compress
        }
        return self._make_request('POST', '/api/backup/create', json=data)

    def get_backup_list(self) -> Dict[str, Any]:
        """获取备份列表"""
        return self._make_request('GET', '/api/backup/list')

    # 用户设置
    def get_settings(self) -> Dict[str, Any]:
        """获取用户设置"""
        return self._make_request('GET', '/api/settings')

    def save_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """保存用户设置"""
        return self._make_request('POST', '/api/settings', json={"settings": settings})

# 使用示例
if __name__ == "__main__":
    client = ModianAPIClient()

    # 获取系统状态
    status = client.get_system_status()
    print("系统状态:", status)

    # 搜索游戏类项目
    projects = client.search_projects(
        conditions={"category": "games"},
        limit=10
    )
    print("找到项目:", len(projects.get("projects", [])))

    # 启动爬虫任务
    task_result = client.start_crawl_task({
        "start_page": 1,
        "end_page": 5,
        "category": "games"
    })
    print("任务启动:", task_result)
```

### 最佳实践

1. **错误处理**: 始终检查API响应的 `success` 字段
2. **超时设置**: 设置合适的请求超时时间
3. **重试策略**: 对于临时性错误实现重试机制
4. **日志记录**: 记录API调用日志便于调试
5. **数据验证**: 验证API返回的数据格式和内容
6. **性能优化**: 合理使用分页和缓存机制

---

## 更新日志

- **v1.0.0** (2024-12-26): 初始版本，包含所有核心API接口
- **v1.0.1** (2024-12-26): 完善API文档，修正响应格式和参数说明
- 后续版本将根据功能扩展持续更新

---

## 附录

### 数据字段映射表

**项目数据字段：**
- `project_url`: 项目链接
- `project_id`: 项目ID（6位数字）
- `project_name`: 项目名称
- `project_image`: 项目图片URL
- `category`: 项目分类
- `author_name`: 作者名称
- `author_link`: 作者链接
- `start_time`: 项目开始时间
- `end_time`: 项目结束时间
- `raised_amount`: 已筹金额（数值）
- `target_amount`: 目标金额（数值）
- `completion_rate`: 完成率（百分比字符串）
- `backer_count`: 支持者数量
- `update_count`: 更新数量
- `comment_count`: 评论数量
- `supporter_count`: 支持者数量
- `project_status`: 项目状态
- `crawl_time`: 爬取时间

### 分类代码对照表

| 代码 | 中文名称 | 英文名称 |
|------|----------|----------|
| all | 全部 | All |
| games | 游戏 | Games |
| publishing | 出版 | Publishing |
| tablegames | 桌游 | Board Games |
| toys | 潮玩模型 | Toys & Models |
| cards | 卡牌 | Cards |
| technology | 科技 | Technology |
| film-video | 影视 | Film & Video |
| music | 音乐 | Music |
| activities | 活动 | Activities |
| design | 设计 | Design |
| curio | 文玩 | Curios |
| home | 家居 | Home |
| food | 食品 | Food |
| comics | 动漫 | Comics |
| charity | 爱心通道 | Charity |
| animals | 动物救助 | Animal Rescue |
| wishes | 个人愿望 | Personal Wishes |
| others | 其他 | Others |

### 任务状态说明

- `starting`: 任务启动中
- `running`: 任务运行中
- `completed`: 任务已完成
- `failed`: 任务失败
- `stopped`: 任务已停止
- `paused`: 任务已暂停

### 错误代码参考

- `VALIDATION_ERROR`: 参数验证错误
- `NOT_FOUND`: 资源不存在
- `CONFLICT`: 资源冲突
- `INTERNAL_ERROR`: 服务器内部错误
- `DATABASE_ERROR`: 数据库错误
- `NETWORK_ERROR`: 网络错误

---

**注意事项：**
1. 所有时间格式均为 `YYYY-MM-DD HH:MM:SS`
2. 金额单位为人民币（元），保留2位小数
3. 项目ID为6位数字字符串
4. 分页查询建议单次不超过100条记录
5. API调用频率建议控制在每秒10次以内
6. 所有API响应都包含 `success` 字段用于判断请求是否成功
7. 错误响应中的 `message` 字段包含具体错误信息
8. 建议在生产环境中实现适当的错误重试机制

