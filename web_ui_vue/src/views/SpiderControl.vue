<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          <v-icon icon="mdi-spider" class="me-3" size="large" />
          爬虫控制
        </h1>
        <p class="text-h6 text-medium-emphasis">
          配置和管理爬虫任务
        </p>
      </v-col>
    </v-row>

    <v-row>
      <!-- 左侧配置面板 -->
      <v-col cols="12" lg="4">
        <v-card elevation="2" class="mb-4">
          <v-card-title>
            <v-icon icon="mdi-cog" class="me-3" />
            爬虫配置
          </v-card-title>

          <v-card-text>
            <v-form ref="configForm" v-model="formValid">
              <!-- 页面范围 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">页面范围</v-label>
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="config.startPage"
                      label="起始页"
                      type="number"
                      :min="1"
                      :rules="[v => v >= 1 || '起始页必须大于0']"
                      variant="outlined"
                      density="compact"
                    />
                  </v-col>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="config.endPage"
                      label="结束页"
                      type="number"
                      :min="config.startPage"
                      :rules="[v => v >= config.startPage || '结束页必须大于等于起始页']"
                      variant="outlined"
                      density="compact"
                    />
                  </v-col>
                </v-row>
              </div>

              <!-- 项目分类 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">项目分类</v-label>
                <v-select
                  v-model="config.category"
                  :items="categories"
                  item-title="label"
                  item-value="value"
                  label="选择分类"
                  variant="outlined"
                  density="compact"
                />
              </div>

              <!-- 并发设置 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">并发请求数: {{ config.maxConcurrent }}</v-label>
                <v-slider
                  v-model="config.maxConcurrent"
                  :min="1"
                  :max="10"
                  :step="1"
                  show-ticks
                  tick-size="4"
                  color="primary"
                />
              </div>

              <!-- 延迟设置 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">请求延迟 (秒)</v-label>
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="config.delayMin"
                      label="最小延迟"
                      type="number"
                      :min="0"
                      :step="0.1"
                      variant="outlined"
                      density="compact"
                    />
                  </v-col>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="config.delayMax"
                      label="最大延迟"
                      type="number"
                      :min="config.delayMin"
                      :step="0.1"
                      variant="outlined"
                      density="compact"
                    />
                  </v-col>
                </v-row>
              </div>

              <!-- 🔧 新增：后台定时任务配置 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">任务类型</v-label>
                <v-switch
                  v-model="config.isScheduled"
                  label="后台定时任务"
                  color="primary"
                  inset
                  hide-details
                />
                <div v-if="config.isScheduled" class="mt-3">
                  <v-text-field
                    v-model.number="config.scheduleInterval"
                    label="执行间隔 (秒)"
                    type="number"
                    :min="5"
                    hint="最小间隔5秒，默认3600秒(1小时)"
                    variant="outlined"
                    density="compact"
                  />
                </div>
              </div>

              <!-- API数据获取说明 -->
              <div class="mb-4">
                <v-alert
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="text-caption"
                >
                  <v-icon start icon="mdi-api"></v-icon>
                  现在使用高性能API获取完整数据，速度提升10倍+，数据更完整
                </v-alert>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- 操作按钮 -->
        <v-card elevation="2">
          <v-card-title>
            <v-icon icon="mdi-play-circle" class="me-3" />
            任务控制
          </v-card-title>

          <v-card-text>
            <v-btn
              v-if="!isRunning"
              block
              color="primary"
              size="large"
              prepend-icon="mdi-play"
              @click="startCrawling"
              :disabled="!formValid"
              :loading="starting"
              variant="elevated"
              class="mb-3"
            >
              开始爬取
            </v-btn>

            <v-btn
              v-else
              block
              color="error"
              size="large"
              prepend-icon="mdi-stop"
              @click="stopCrawling"
              :loading="stopping"
              variant="elevated"
              class="mb-3"
            >
              停止爬取
            </v-btn>

            <v-btn
              block
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="loadDefaultConfig"
              :disabled="isRunning"
            >
              重置配置
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 右侧状态面板 -->
      <v-col cols="12" lg="8">
        <!-- 当前任务状态 -->
        <v-card elevation="2" class="mb-4">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-information" class="me-3" />
            当前任务状态
            <v-spacer />
            <v-chip
              v-if="currentTask"
              :color="getTaskStatusColor(currentTask.status)"
              variant="flat"
            >
              {{ getTaskStatusText(currentTask.status) }}
            </v-chip>
          </v-card-title>

          <v-card-text>
            <div v-if="currentTask && currentTask.id">
              <!-- 任务信息 -->
              <v-row class="mb-4">
                <v-col cols="12" md="6">
                  <div class="text-subtitle-2 mb-1">任务ID</div>
                  <div class="text-body-2 font-mono">{{ currentTask.id }}</div>
                </v-col>
                <v-col cols="12" md="6">
                  <div class="text-subtitle-2 mb-1">开始时间</div>
                  <div class="text-body-2">{{ formatTime(currentTask.startTime) }}</div>
                </v-col>
              </v-row>

              <!-- 进度条 -->
              <div class="mb-4">
                <div class="d-flex justify-space-between mb-2">
                  <span class="text-subtitle-2">爬取进度</span>
                  <span class="text-subtitle-2">{{ Math.round(currentTask.progress || 0) }}%</span>
                </div>
                <v-progress-linear
                  :model-value="currentTask.progress || 0"
                  height="12"
                  rounded
                  color="primary"
                  striped
                />
              </div>

              <!-- 详细进度信息 -->
              <div class="mb-4" v-if="currentTask.stats">
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-1">页面进度</div>
                    <div class="text-body-2">
                      {{ currentTask.stats.current_page || 0 }} / {{ currentTask.stats.total_pages || 0 }} 页
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-1">项目进度</div>
                    <div class="text-body-2">
                      {{ currentTask.stats.projects_processed || 0 }} / {{ currentTask.stats.total_projects || 0 }} 个项目
                    </div>
                  </v-col>
                </v-row>
              </div>

              <!-- 统计信息 -->
              <v-row class="text-center">
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-primary">
                    {{ currentTask.stats?.pagesCrawled || 0 }}
                  </div>
                  <div class="text-caption text-medium-emphasis">已爬页面</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-success">
                    {{ currentTask.stats?.projectsFound || 0 }}
                  </div>
                  <div class="text-caption text-medium-emphasis">发现项目</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-info">
                    {{ currentTask.stats?.projectsProcessed || 0 }}
                  </div>
                  <div class="text-caption text-medium-emphasis">已处理</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-error">
                    {{ currentTask.stats?.errors || 0 }}
                  </div>
                  <div class="text-caption text-medium-emphasis">错误数</div>
                </v-col>
              </v-row>
            </div>

            <div v-else class="text-center py-8 text-medium-emphasis">
              <v-icon icon="mdi-sleep" size="64" class="mb-4" />
              <div class="text-h6">暂无活跃任务</div>
              <div class="text-subtitle-2">配置参数后点击"开始爬取"启动任务</div>
            </div>
          </v-card-text>
        </v-card>

        <!-- 实时日志 -->
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-console" class="me-3" />
            实时日志
            <v-spacer />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              @click="clearLogs"
              :disabled="!logs.length"
            />
          </v-card-title>

          <v-card-text class="pa-0">
            <div class="log-container">
              <div v-if="logs.length === 0" class="text-center pa-4 text-medium-emphasis">
                暂无日志信息
              </div>
              <div
                v-for="(log, index) in logs"
                :key="index"
                :class="['log-entry', `log-${log.level}`]"
              >
                <span class="log-timestamp">[{{ log.timestamp }}]</span>
                <span class="log-level">[{{ log.level.toUpperCase() }}]</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import axios from 'axios'
import pageCache from '@/utils/pageCache'
import socketManager from '@/utils/socketManager'

const appStore = useAppStore()

// 响应式数据
const formValid = ref(false)
const starting = ref(false)
const stopping = ref(false)
const categories = ref([])
const logs = ref([])
const currentTask = ref(null)

// 配置数据
const config = reactive({
  startPage: 1,
  endPage: 10,
  category: 'all',
  maxConcurrent: 3,
  delayMin: 1.0,
  delayMax: 3.0,
  isScheduled: false,
  scheduleInterval: 3600
})

// 计算属性
const isRunning = computed(() => {
  return currentTask.value && ['starting', 'running'].includes(currentTask.value.status)
})

// 方法
const loadDefaultConfig = async () => {
  try {
    const response = await axios.get('/api/config')
    if (response.data.success) {
      const defaultConfig = response.data.config
      config.startPage = defaultConfig.start_page
      config.endPage = defaultConfig.end_page
      config.category = defaultConfig.category
      config.maxConcurrent = defaultConfig.max_concurrent
      config.delayMin = defaultConfig.delay_min
      config.delayMax = defaultConfig.delay_max
      categories.value = defaultConfig.categories
    }
  } catch (error) {
    console.error('加载默认配置失败:', error)
  }
}

const startCrawling = async () => {
  if (!formValid.value) return

  starting.value = true
  try {
    const requestData = {
      start_page: config.startPage,
      end_page: config.endPage,
      category: config.category,
      max_concurrent: config.maxConcurrent,
      delay_min: config.delayMin,
      delay_max: config.delayMax,
      is_scheduled: config.isScheduled,
      schedule_interval: config.scheduleInterval
    }

    const response = await axios.post('/api/start_crawl', requestData)

    if (response.data.success) {
      if (config.isScheduled) {
        addLog('success', `定时任务已创建: ${response.data.task_id}`)
        addLog('info', `执行间隔: ${config.scheduleInterval}秒`)
      } else {
        addLog('success', `任务已启动: ${response.data.task_id}`)
        // 开始轮询任务状态
        startPolling()
      }
    } else {
      addLog('error', `启动失败: ${response.data.message}`)
    }
  } catch (error) {
    addLog('error', `启动失败: ${error.message}`)
  } finally {
    starting.value = false
  }
}

const stopCrawling = async () => {
  if (!currentTask.value?.id) return

  stopping.value = true
  try {
    const response = await axios.post(`/api/stop_crawl/${currentTask.value.id}`)

    if (response.data.success) {
      addLog('warning', '任务已停止')
    } else {
      addLog('error', `停止失败: ${response.data.message}`)
    }
  } catch (error) {
    addLog('error', `停止失败: ${error.message}`)
  } finally {
    stopping.value = false
  }
}

const addLog = (level, message) => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({
    timestamp,
    level,
    message
  })

  // 只保留最近100条日志
  if (logs.value.length > 100) {
    logs.value = logs.value.slice(-100)
  }

  // 滚动到底部
  setTimeout(() => {
    const container = document.querySelector('.log-container')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  }, 100)
}

const clearLogs = () => {
  logs.value = []
}

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

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString()
}

// 轮询任务状态
let pollingInterval = null

const startPolling = () => {
  if (pollingInterval) return

  pollingInterval = setInterval(async () => {
    try {
      const response = await axios.get('/api/tasks')
      if (response.data.success && response.data.tasks.length > 0) {
        const task = response.data.tasks[0] // 获取最新任务
        currentTask.value = {
          id: task.task_id,
          status: task.stats.status,
          progress: task.stats.progress,
          startTime: task.stats.start_time,
          stats: task.stats
        }

        // 如果任务完成或失败，停止轮询
        if (['completed', 'failed', 'stopped'].includes(task.stats.status)) {
          stopPolling()
        }
      }
    } catch (error) {
      console.error('轮询任务状态失败:', error)
    }
  }, 2000) // 每2秒轮询一次
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

// 生命周期
onMounted(() => {
  loadDefaultConfig()

  // 监听WebSocket消息
  const setupWebSocketListeners = () => {
    if (appStore.socket) {
      console.log('🔌 设置WebSocket监听器')

      appStore.socket.on('task_update', (data) => {
        console.log('📊 收到任务更新:', data)

        if (data.task_id && data.stats) {
          currentTask.value = {
            id: data.task_id,
            status: data.stats.status,
            progress: data.stats.progress,
            startTime: data.stats.start_time,
            stats: data.stats
          }

          // 更新日志
          if (data.stats.logs && Array.isArray(data.stats.logs)) {
            // 替换所有日志（确保同步）
            logs.value = [...data.stats.logs]
            console.log(`📝 更新日志: ${logs.value.length} 条`)
          }
        }
      })

      appStore.socket.on('connect', () => {
        console.log('✅ WebSocket已连接，重新设置监听器')
      })
    } else {
      console.log('⚠️ WebSocket未初始化，1秒后重试')
      setTimeout(setupWebSocketListeners, 1000)
    }
  }

  setupWebSocketListeners()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.font-mono {
  font-family: 'Courier New', monospace;
}

.log-container {
  max-height: 400px;
  overflow-y: auto;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  color: #ffffff;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.log-entry {
  margin-bottom: 4px;
  line-height: 1.5;
  padding: 2px 0;
  border-left: 3px solid transparent;
  padding-left: 8px;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
  }
}

.log-timestamp {
  color: #888;
  margin-right: 8px;
  font-weight: 500;
}

.log-level {
  color: #ccc;
  margin-right: 8px;
  font-weight: 600;
  min-width: 60px;
  display: inline-block;
}

.log-message {
  color: #fff;
}

.log-info {
  border-left-color: #4fc3f7;

  .log-level {
    color: #4fc3f7;
  }
}

.log-success {
  border-left-color: #81c784;

  .log-level {
    color: #81c784;
  }
}

.log-warning {
  border-left-color: #ffb74d;

  .log-level {
    color: #ffb74d;
  }
}

.log-error {
  border-left-color: #e57373;

  .log-level {
    color: #e57373;
  }
}

/* 滚动条样式 */
.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;

  &:hover {
    background: rgba(255, 255, 255, 0.5);
  }
}
</style>
