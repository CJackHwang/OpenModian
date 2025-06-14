# 摩点爬虫Vue UI

基于Vue 3 + Quasar Framework (Material Design 3) 的现代化Web界面。

## 🚀 启动方式

### 开发模式（推荐）
```bash
# 启动开发模式（热重载）
python3 start_vue_ui.py dev

# 或者直接运行（默认开发模式）
python3 start_vue_ui.py
```

**特点**：
- ✅ 前端热重载，修改代码立即生效
- ✅ 前端: http://localhost:3000
- ✅ 后端API: http://localhost:8080
- ✅ 自动代理API请求

### 生产模式
```bash
# 启动生产模式（先构建再启动）
python3 start_vue_ui.py prod
```

**特点**：
- ✅ 优化的生产构建
- ✅ 单端口: http://localhost:8080
- ✅ 静态文件服务

### 仅构建
```bash
# 仅构建前端，不启动服务器
python3 start_vue_ui.py build
```

## 🛠️ 手动开发

如果你想手动控制前后端：

```bash
# 终端1: 启动后端
cd web_ui
python3 app.py

# 终端2: 启动前端开发服务器
cd web_ui_vue
npm run dev
```

## 📦 技术栈

- **前端**: Vue 3 + Quasar Framework + Material Design 3
- **后端**: Flask + SocketIO
- **构建**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router

## 🎨 Material Design 3

使用了真正的Material Design 3组件和设计规范：
- 动态颜色系统
- 现代化组件样式
- 流畅的动画和过渡
- 响应式设计
