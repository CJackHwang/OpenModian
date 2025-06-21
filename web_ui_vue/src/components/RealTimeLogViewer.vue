<template>
  <v-card elevation="2" class="log-viewer">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-console" class="me-3" />
      实时日志
      <v-chip 
        :color="connectionStatus ? 'success' : 'error'" 
        size="small" 
        class="ms-3"
      >
        {{ connectionStatus ? '已连接' : '未连接' }}
      </v-chip>
      <v-spacer />
      
      <!-- 日志类型选择 -->
      <v-select
        v-model="selectedLogType"
        :items="logTypes"
        item-title="label"
        item-value="value"
        density="compact"
        variant="outlined"
        hide-details
        class="me-2"
        style="max-width: 120px;"
        @update:model-value="changeLogType"
      />
      
      <!-- 日志级别过滤 -->
      <v-select
        v-model="selectedLevel"
        :items="logLevels"
        item-title="label"
        item-value="value"
        density="compact"
        variant="outlined"
        hide-details
        class="me-2"
        style="max-width: 100px;"
        @update:model-value="applyFilters"
      />
      
      <!-- 搜索框 -->
      <v-text-field
        v-model="searchTerm"
        placeholder="搜索日志..."
        density="compact"
        variant="outlined"
        hide-details
        prepend-inner-icon="mdi-magnify"
        clearable
        class="me-2"
        style="max-width: 200px;"
        @update:model-value="applyFilters"
      />
      
      <!-- 操作按钮 -->
      <v-btn
        icon="mdi-refresh"
        variant="text"
        size="small"
        @click="refreshLogs"
        :disabled="!connectionStatus"
        class="me-1"
      />
      <v-btn
        icon="mdi-delete"
        variant="text"
        size="small"
        @click="clearLogs"
        :disabled="!logs.length"
      />
    </v-card-title>

    <v-card-text class="pa-0">
      <div class="log-container" ref="logContainer">
        <div v-if="filteredLogs.length === 0" class="text-center pa-4 text-medium-emphasis">
          <v-icon icon="mdi-information-outline" size="48" class="mb-2" />
          <div>{{ connectionStatus ? '暂无日志信息' : '等待连接...' }}</div>
        </div>
        
        <div
          v-for="(log, index) in displayedLogs"
          :key="`${log.timestamp}-${index}`"
          :class="['log-entry', `log-${log.level.toLowerCase()}`]"
        >
          <span class="log-timestamp">[{{ log.timestamp }}]</span>
          <span class="log-level">[{{ log.level.toUpperCase() }}]</span>
          <span v-if="log.source" class="log-source">[{{ log.source }}]</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        
        <!-- 加载更多按钮 -->
        <div v-if="hasMoreLogs" class="text-center pa-2">
          <v-btn
            variant="text"
            size="small"
            @click="loadMoreLogs"
            :loading="loadingMore"
          >
            加载更多
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useAppStore } from '@/stores/app'

// Props
const props = defineProps({
  height: {
    type: String,
    default: '400px'
  },
  maxLogs: {
    type: Number,
    default: 500
  },
  autoScroll: {
    type: Boolean,
    default: true
  }
})

// Store
const appStore = useAppStore()

// 响应式数据
const logs = ref([])
const filteredLogs = ref([])
const displayedLogs = ref([])
const connectionStatus = ref(false)
const selectedLogType = ref('all')
const selectedLevel = ref('all')
const searchTerm = ref('')
const loadingMore = ref(false)
const displayLimit = ref(100)

// 日志容器引用
const logContainer = ref(null)

// 配置选项
const logTypes = [
  { label: '全部', value: 'all' },
  { label: '系统', value: 'system' },
  { label: '爬虫', value: 'spider' },
  { label: 'Web界面', value: 'webui' }
]

const logLevels = [
  { label: '全部', value: 'all' },
  { label: 'DEBUG', value: 'debug' },
  { label: 'INFO', value: 'info' },
  { label: 'WARNING', value: 'warning' },
  { label: 'ERROR', value: 'error' }
]

// 计算属性
const hasMoreLogs = computed(() => {
  return filteredLogs.value.length > displayedLogs.value.length
})

// 本地存储键名
const STORAGE_KEY = 'realtime_logs_cache'
const SETTINGS_KEY = 'log_viewer_settings'

// 方法
const initializeLogViewer = () => {
  // 加载设置
  loadSettings()
  
  // 加载缓存的日志
  loadCachedLogs()
  
  // 设置WebSocket监听
  setupWebSocketListeners()
  
  // 订阅日志更新
  subscribeToLogs()
}

const loadSettings = () => {
  try {
    const settings = localStorage.getItem(SETTINGS_KEY)
    if (settings) {
      const parsed = JSON.parse(settings)
      selectedLogType.value = parsed.logType || 'all'
      selectedLevel.value = parsed.level || 'all'
      searchTerm.value = parsed.search || ''
    }
  } catch (error) {
    console.error('加载日志查看器设置失败:', error)
  }
}

const saveSettings = () => {
  try {
    const settings = {
      logType: selectedLogType.value,
      level: selectedLevel.value,
      search: searchTerm.value
    }
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
  } catch (error) {
    console.error('保存日志查看器设置失败:', error)
  }
}

const loadCachedLogs = () => {
  try {
    const cached = localStorage.getItem(STORAGE_KEY)
    if (cached) {
      const parsedLogs = JSON.parse(cached)
      logs.value = parsedLogs.slice(-props.maxLogs) // 只保留最新的日志
      applyFilters()
      console.log(`📝 加载缓存日志: ${logs.value.length} 条`)
    }
  } catch (error) {
    console.error('加载缓存日志失败:', error)
    logs.value = []
  }
}

const saveCachedLogs = () => {
  try {
    // 只缓存最新的日志，避免存储过大
    const logsToCache = logs.value.slice(-props.maxLogs)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(logsToCache))
  } catch (error) {
    console.error('保存日志缓存失败:', error)
    // 如果存储失败，可能是因为存储空间不足，清理旧数据
    try {
      localStorage.removeItem(STORAGE_KEY)
      const reducedLogs = logs.value.slice(-Math.floor(props.maxLogs / 2))
      localStorage.setItem(STORAGE_KEY, JSON.stringify(reducedLogs))
    } catch (retryError) {
      console.error('重试保存日志缓存也失败:', retryError)
    }
  }
}

const setupWebSocketListeners = () => {
  if (!appStore.socket) {
    console.warn('WebSocket未初始化')
    return
  }

  // 连接状态监听
  appStore.socket.on('connect', () => {
    connectionStatus.value = true
    console.log('✅ 日志查看器WebSocket已连接')
    subscribeToLogs()
  })

  appStore.socket.on('disconnect', () => {
    connectionStatus.value = false
    console.log('❌ 日志查看器WebSocket已断开')
  })

  // 日志更新监听
  appStore.socket.on('log_update', (data) => {
    handleLogUpdate(data)
  })

  // 日志历史监听
  appStore.socket.on('log_history', (data) => {
    handleLogHistory(data)
  })

  // 日志清空监听
  appStore.socket.on('log_cleared', (data) => {
    if (data.log_type === selectedLogType.value || data.log_type === 'all') {
      logs.value = []
      applyFilters()
      saveCachedLogs()
    }
  })

  // 设置初始连接状态
  connectionStatus.value = appStore.socket.connected
}

const subscribeToLogs = () => {
  if (!appStore.socket || !appStore.socket.connected) {
    return
  }

  // 订阅日志更新
  appStore.socket.emit('log_subscribe', {
    log_type: selectedLogType.value
  })

  console.log(`📡 订阅日志类型: ${selectedLogType.value}`)
}

const unsubscribeFromLogs = (logType) => {
  if (!appStore.socket || !appStore.socket.connected) {
    return
  }

  appStore.socket.emit('log_unsubscribe', {
    log_type: logType
  })
}

const handleLogUpdate = (data) => {
  if (data.entry) {
    addLogEntry(data.entry)
  }
}

const handleLogHistory = (data) => {
  if (data.logs && Array.isArray(data.logs)) {
    // 合并历史日志，避免重复
    const existingTimestamps = new Set(logs.value.map(log => `${log.timestamp}-${log.message}`))
    const newLogs = data.logs.filter(log => 
      !existingTimestamps.has(`${log.timestamp}-${log.message}`)
    )
    
    logs.value = [...newLogs, ...logs.value].slice(-props.maxLogs)
    applyFilters()
    saveCachedLogs()
    
    console.log(`📝 接收历史日志: ${newLogs.length} 条新日志`)
  }
}

const addLogEntry = (entry) => {
  // 检查是否已存在相同的日志条目
  const exists = logs.value.some(log => 
    log.timestamp === entry.timestamp && 
    log.message === entry.message &&
    log.level === entry.level
  )
  
  if (!exists) {
    logs.value.push(entry)
    
    // 限制日志数量
    if (logs.value.length > props.maxLogs) {
      logs.value = logs.value.slice(-props.maxLogs)
    }
    
    applyFilters()
    saveCachedLogs()
    
    // 自动滚动到底部
    if (props.autoScroll) {
      nextTick(() => {
        scrollToBottom()
      })
    }
  }
}

const applyFilters = () => {
  let filtered = [...logs.value]
  
  // 级别过滤
  if (selectedLevel.value !== 'all') {
    filtered = filtered.filter(log => 
      log.level.toLowerCase() === selectedLevel.value.toLowerCase()
    )
  }
  
  // 搜索过滤
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(log => 
      log.message.toLowerCase().includes(search) ||
      log.level.toLowerCase().includes(search) ||
      (log.source && log.source.toLowerCase().includes(search))
    )
  }
  
  filteredLogs.value = filtered
  displayedLogs.value = filtered.slice(0, displayLimit.value)
  
  // 保存设置
  saveSettings()
}

const loadMoreLogs = () => {
  loadingMore.value = true
  
  setTimeout(() => {
    const currentLength = displayedLogs.value.length
    const nextBatch = filteredLogs.value.slice(currentLength, currentLength + 50)
    displayedLogs.value = [...displayedLogs.value, ...nextBatch]
    loadingMore.value = false
  }, 300)
}

const changeLogType = (newType) => {
  // 取消订阅旧类型
  unsubscribeFromLogs(selectedLogType.value)
  
  // 订阅新类型
  selectedLogType.value = newType
  subscribeToLogs()
  
  // 重新应用过滤器
  applyFilters()
}

const refreshLogs = () => {
  if (!appStore.socket || !appStore.socket.connected) {
    return
  }

  // 请求最新日志
  appStore.socket.emit('log_request', {
    log_type: selectedLogType.value,
    limit: 100,
    level: selectedLevel.value,
    search: searchTerm.value
  })
}

const clearLogs = () => {
  logs.value = []
  filteredLogs.value = []
  displayedLogs.value = []
  saveCachedLogs()
  
  // 通知服务器清空缓存
  if (appStore.socket && appStore.socket.connected) {
    appStore.socket.emit('log_clear', {
      log_type: selectedLogType.value
    })
  }
}

const scrollToBottom = () => {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

// 监听器
watch(() => appStore.connectionStatus, (newStatus) => {
  connectionStatus.value = newStatus
  if (newStatus) {
    subscribeToLogs()
  }
})

// 生命周期
onMounted(() => {
  initializeLogViewer()
})

onUnmounted(() => {
  // 取消订阅
  if (selectedLogType.value) {
    unsubscribeFromLogs(selectedLogType.value)
  }
  
  // 保存最终状态
  saveCachedLogs()
  saveSettings()
})
</script>

<style scoped>
.log-viewer {
  height: 100%;
}

.log-container {
  height: v-bind(height);
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
  background-color: rgb(var(--v-theme-surface-variant));
  padding: 8px;
}

.log-entry {
  padding: 2px 0;
  border-bottom: 1px solid rgba(var(--v-theme-on-surface), 0.05);
  word-wrap: break-word;
}

.log-entry:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.log-timestamp {
  color: rgb(var(--v-theme-on-surface-variant));
  margin-right: 8px;
}

.log-level {
  font-weight: bold;
  margin-right: 8px;
  min-width: 60px;
  display: inline-block;
}

.log-source {
  color: rgb(var(--v-theme-primary));
  margin-right: 8px;
  font-size: 12px;
}

.log-message {
  color: rgb(var(--v-theme-on-surface));
}

/* 日志级别颜色 */
.log-debug .log-level {
  color: rgb(var(--v-theme-info));
}

.log-info .log-level {
  color: rgb(var(--v-theme-success));
}

.log-warning .log-level {
  color: rgb(var(--v-theme-warning));
}

.log-error .log-level {
  color: rgb(var(--v-theme-error));
}

/* 滚动条样式 */
.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-on-surface), 0.1);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.3);
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.5);
}
</style>
