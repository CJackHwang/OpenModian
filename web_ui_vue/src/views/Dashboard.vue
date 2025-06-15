<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          <v-icon icon="mdi-view-dashboard" class="me-3" size="large" />
          仪表板
        </h1>
        <p class="text-h6 text-medium-emphasis">
          系统概览和实时状态监控
        </p>
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="primary"
          prepend-icon="mdi-refresh"
          @click="refreshData"
          :loading="appStore.loading"
          variant="elevated"
          size="large"
        >
          刷新数据
        </v-btn>
      </v-col>
    </v-row>

    <!-- 统计卡片 -->
    <v-row class="mb-8">
      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center pa-6 stats-card"
          color="primary-container"
          variant="elevated"
          elevation="3"
        >
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-database" size="48" class="stats-icon" />
          </div>
          <div class="text-h3 font-weight-bold mb-2">{{ appStore.systemStats.totalProjects }}</div>
          <div class="text-h6 font-weight-medium mb-1">总项目数</div>
          <div class="text-caption text-medium-emphasis">累计爬取项目</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center pa-6 stats-card"
          color="secondary-container"
          variant="elevated"
          elevation="3"
        >
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-calendar-today" size="48" class="stats-icon" />
          </div>
          <div class="text-h3 font-weight-bold mb-2">{{ appStore.systemStats.todayProjects }}</div>
          <div class="text-h6 font-weight-medium mb-1">今日新增</div>
          <div class="text-caption text-medium-emphasis">今天爬取项目</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center pa-6 stats-card"
          color="tertiary-container"
          variant="elevated"
          elevation="3"
        >
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-calendar-week" size="48" class="stats-icon" />
          </div>
          <div class="text-h3 font-weight-bold mb-2">{{ appStore.systemStats.weekProjects }}</div>
          <div class="text-h6 font-weight-medium mb-1">本周新增</div>
          <div class="text-caption text-medium-emphasis">本周爬取项目</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center pa-6 stats-card"
          color="surface-variant"
          variant="elevated"
          elevation="3"
        >
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-cog" size="48" class="stats-icon" />
          </div>
          <div class="text-h3 font-weight-bold mb-2">{{ appStore.systemStats.activeTasks }}</div>
          <div class="text-h6 font-weight-medium mb-1">活跃任务</div>
          <div class="text-caption text-medium-emphasis">正在运行任务</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 主要内容区域 -->
    <v-row>
      <!-- 当前任务状态 -->
      <v-col cols="12" lg="8">
        <v-card class="mb-4" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-spider" class="me-3" />
            当前任务状态
            <v-spacer />
            <v-chip
              :color="getTaskStatusColor(appStore.currentTask.status)"
              variant="flat"
              size="small"
            >
              {{ getTaskStatusText(appStore.currentTask.status) }}
            </v-chip>
          </v-card-title>

          <v-card-text>
            <div v-if="appStore.currentTask.id">
              <!-- 进度条 -->
              <div class="mb-4">
                <div class="d-flex justify-space-between mb-2">
                  <span class="text-subtitle-2">爬取进度</span>
                  <span class="text-subtitle-2">{{ Math.round(appStore.currentTask.progress) }}%</span>
                </div>
                <v-progress-linear
                  :model-value="appStore.currentTask.progress"
                  height="12"
                  rounded
                  color="primary"
                />
              </div>

              <!-- 统计信息 -->
              <v-row class="text-center">
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-primary">
                    {{ appStore.currentTask.stats.pagesCrawled }}
                  </div>
                  <div class="text-caption text-medium-emphasis">已爬页面</div>
                </v-col>
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-success">
                    {{ appStore.currentTask.stats.projectsFound }}
                  </div>
                  <div class="text-caption text-medium-emphasis">发现项目</div>
                </v-col>
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-info">
                    {{ appStore.currentTask.stats.projectsProcessed }}
                  </div>
                  <div class="text-caption text-medium-emphasis">已处理</div>
                </v-col>
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-error">
                    {{ appStore.currentTask.stats.errors }}
                  </div>
                  <div class="text-caption text-medium-emphasis">错误数</div>
                </v-col>
              </v-row>
            </div>

            <div v-else class="text-center py-8 text-medium-emphasis">
              <v-icon icon="mdi-sleep" size="64" class="mb-4" />
              <div class="text-h6">暂无活跃任务</div>
              <div class="text-subtitle-2">点击"爬虫控制"开始新任务</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 侧边栏信息 -->
      <v-col cols="12" lg="4">
        <!-- 任务统计 -->
        <v-card class="mb-4" elevation="2">
          <v-card-title>
            <v-icon icon="mdi-chart-pie" class="me-3" />
            任务统计
          </v-card-title>

          <v-card-text>
            <div class="d-flex justify-space-between align-center mb-3">
              <span>活跃任务</span>
              <v-chip color="success" size="small">{{ appStore.systemStats.activeTasks }}</v-chip>
            </div>
            <div class="d-flex justify-space-between align-center mb-3">
              <span>已完成</span>
              <v-chip color="primary" size="small">{{ appStore.systemStats.completedTasks }}</v-chip>
            </div>
            <div class="d-flex justify-space-between align-center">
              <span>失败任务</span>
              <v-chip color="error" size="small">{{ appStore.systemStats.failedTasks }}</v-chip>
            </div>
          </v-card-text>
        </v-card>

        <!-- 快速操作 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-lightning-bolt" class="me-3" />
            快速操作
          </v-card-title>

          <v-card-text>
            <v-btn
              block
              color="primary"
              class="mb-3"
              prepend-icon="mdi-play"
              @click="$router.push('/spider')"
              variant="elevated"
            >
              开始新任务
            </v-btn>

            <v-btn
              block
              color="secondary"
              class="mb-3"
              prepend-icon="mdi-database"
              @click="$router.push('/data')"
              variant="elevated"
            >
              查看数据
            </v-btn>

            <v-btn
              block
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="refreshData"
              :loading="appStore.loading"
            >
              刷新数据
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- 实时终端 -->
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-console" class="me-3" />
            实时终端
            <v-spacer />
            <v-btn
              icon="mdi-fullscreen"
              variant="text"
              size="small"
              @click="toggleTerminalFullscreen"
              class="me-2"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              @click="clearTerminal"
              :disabled="!terminalLogs.length"
            />
          </v-card-title>

          <v-card-text class="pa-0">
            <div :class="['terminal-container', { 'terminal-fullscreen': terminalFullscreen }]">
              <div v-if="terminalLogs.length === 0" class="text-center pa-4 text-medium-emphasis">
                等待系统日志...
              </div>
              <div
                v-for="(log, index) in terminalLogs"
                :key="index"
                :class="['terminal-entry', `terminal-${log.level}`]"
              >
                <span class="terminal-timestamp">[{{ log.timestamp }}]</span>
                <span class="terminal-level">[{{ log.level.toUpperCase() }}]</span>
                <span class="terminal-message">{{ log.message }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 终端日志
const terminalLogs = ref([])
const terminalFullscreen = ref(false)

// 方法
const getTaskStatusColor = (status) => {
  const colors = {
    'idle': 'grey',
    'starting': 'warning',
    'running': 'success',
    'completed': 'primary',
    'failed': 'error',
    'stopped': 'secondary'
  }
  return colors[status] || 'grey'
}

const getTaskStatusText = (status) => {
  const texts = {
    'idle': '空闲',
    'starting': '启动中',
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'stopped': '已停止'
  }
  return texts[status] || '未知'
}

const refreshData = () => {
  appStore.refreshData()
}

const clearTerminal = () => {
  terminalLogs.value = []
}

const toggleTerminalFullscreen = () => {
  terminalFullscreen.value = !terminalFullscreen.value
}

const addTerminalLog = (level, message) => {
  const timestamp = new Date().toLocaleTimeString()
  terminalLogs.value.push({
    timestamp,
    level,
    message
  })

  // 只保留最近50条日志
  if (terminalLogs.value.length > 50) {
    terminalLogs.value = terminalLogs.value.slice(-50)
  }

  // 滚动到底部
  setTimeout(() => {
    const container = document.querySelector('.terminal-container')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, 100)
}

// 生命周期
onMounted(() => {
  appStore.refreshData()

  // 设置WebSocket监听器
  const setupWebSocketListeners = () => {
    if (appStore.socket) {
      console.log('🔌 Dashboard设置WebSocket监听器')

      // 监听任务更新
      appStore.socket.on('task_update', (data) => {
        if (data.stats && data.stats.logs) {
          // 添加新的日志到终端
          data.stats.logs.forEach(log => {
            addTerminalLog(log.level, log.message)
          })
        }
      })

      // 监听系统日志
      appStore.socket.on('system_log', (data) => {
        addTerminalLog(data.level || 'info', data.message)
      })

      appStore.socket.on('connect', () => {
        addTerminalLog('success', 'WebSocket连接成功')
      })

      appStore.socket.on('disconnect', () => {
        addTerminalLog('warning', 'WebSocket连接断开')
      })
    } else {
      setTimeout(setupWebSocketListeners, 1000)
    }
  }

  setupWebSocketListeners()

  // 添加初始日志
  addTerminalLog('info', '仪表板已加载')
})

onUnmounted(() => {
  // 清理WebSocket监听器
  if (appStore.socket) {
    appStore.socket.off('task_update')
    appStore.socket.off('system_log')
  }
})
</script>

<style scoped>
.stats-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
  }
}

.stats-icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  margin: 0 auto;
}

.stats-icon {
  opacity: 0.9;
}

/* 终端样式 */
.terminal-container {
  max-height: 400px;
  overflow-y: auto;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  color: #ffffff;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.terminal-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  max-height: 100vh;
  border-radius: 0;
  margin: 0;
}

.terminal-entry {
  margin-bottom: 2px;
  line-height: 1.4;
  padding: 1px 0;
  border-left: 2px solid transparent;
  padding-left: 6px;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
  }
}

.terminal-timestamp {
  color: #888;
  margin-right: 6px;
  font-weight: 500;
  font-size: 11px;
}

.terminal-level {
  color: #ccc;
  margin-right: 6px;
  font-weight: 600;
  min-width: 50px;
  display: inline-block;
  font-size: 11px;
}

.terminal-message {
  color: #fff;
  font-size: 12px;
}

.terminal-info {
  border-left-color: #4fc3f7;

  .terminal-level {
    color: #4fc3f7;
  }
}

.terminal-success {
  border-left-color: #81c784;

  .terminal-level {
    color: #81c784;
  }
}

.terminal-warning {
  border-left-color: #ffb74d;

  .terminal-level {
    color: #ffb74d;
  }
}

.terminal-error {
  border-left-color: #e57373;

  .terminal-level {
    color: #e57373;
  }
}

/* 终端滚动条样式 */
.terminal-container::-webkit-scrollbar {
  width: 6px;
}

.terminal-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.terminal-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;

  &:hover {
    background: rgba(255, 255, 255, 0.5);
  }
}
</style>