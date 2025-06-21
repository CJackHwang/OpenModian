import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { io } from 'socket.io-client'
import axios from 'axios'

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref(false)
  const socket = ref(null)
  const connectionStatus = ref(false)
  
  const systemStats = reactive({
    totalProjects: 0,
    todayProjects: 0,
    weekProjects: 0,
    activeTasks: 0,
    completedTasks: 0,
    failedTasks: 0
  })

  const currentTask = reactive({
    id: null,
    status: 'idle',
    progress: 0,
    stats: {
      pagesCrawled: 0,
      projectsFound: 0,
      projectsProcessed: 0,
      errors: 0
    },
    logs: []
  })

  // Actions
  const initialize = async () => {
    try {
      loading.value = true
      
      // 初始化WebSocket连接
      initializeSocket()
      
      // 加载初始数据
      await loadSystemStats()
      await loadTasks()
      
    } catch (error) {
      console.error('初始化失败:', error)
    } finally {
      loading.value = false
    }
  }

  const initializeSocket = () => {
    return new Promise((resolve, reject) => {
      try {
        // 如果已有连接，先断开
        if (socket.value) {
          console.log('🔌 断开现有WebSocket连接')
          socket.value.disconnect()
          socket.value = null
        }

        // 单端口模式下直接连接当前域名
        const socketUrl = window.location.origin
        console.log('🔌 正在连接WebSocket:', socketUrl)

        socket.value = io(socketUrl, {
          transports: ['websocket', 'polling'],
          timeout: 20000,
          reconnection: true,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          reconnectionAttempts: 10,
          forceNew: true,  // 强制创建新连接
          autoConnect: true,
          upgrade: true,
          rememberUpgrade: true
        })

        socket.value.on('connect', () => {
          connectionStatus.value = true
          console.log('✅ WebSocket连接成功')
          console.log('🔗 连接ID:', socket.value.id)
          resolve(socket.value)
        })

        socket.value.on('disconnect', (reason) => {
          connectionStatus.value = false
          console.log('❌ WebSocket连接断开:', reason)
        })

        socket.value.on('connect_error', (error) => {
          connectionStatus.value = false
          console.error('❌ WebSocket连接失败:', error)
          reject(error)
        })

        socket.value.on('reconnect', (attemptNumber) => {
          connectionStatus.value = true
          console.log('🔄 WebSocket重连成功，尝试次数:', attemptNumber)
        })

        socket.value.on('reconnect_error', (error) => {
          console.error('🔄 WebSocket重连失败:', error)
        })

        socket.value.on('connected', (data) => {
          console.log('📨 收到服务器确认:', data)
        })

        socket.value.on('task_update', (data) => {
          console.log('📊 收到任务更新:', data)
          handleTaskUpdate(data)
        })

        // 日志相关事件监听
        socket.value.on('log_update', (data) => {
          console.log('📡 收到日志更新:', data)
          // 这个事件会被RealTimeLogViewer组件监听
        })

        socket.value.on('log_history', (data) => {
          console.log('📝 收到历史日志:', data)
          // 这个事件会被RealTimeLogViewer组件监听
        })

        socket.value.on('log_subscribed', (data) => {
          console.log('✅ 日志订阅成功:', data)
        })

        socket.value.on('log_unsubscribed', (data) => {
          console.log('❌ 日志取消订阅:', data)
        })

        socket.value.on('log_cleared', (data) => {
          console.log('🗑️ 日志已清空:', data)
        })

        // 手动触发连接（如果需要）
        setTimeout(() => {
          if (!socket.value.connected) {
            console.log('🔄 手动触发WebSocket连接...')
            socket.value.connect()
          }
        }, 1000)

        // 设置超时
        setTimeout(() => {
          if (!socket.value.connected) {
            reject(new Error('WebSocket连接超时'))
          }
        }, 10000)

      } catch (error) {
        console.error('❌ 初始化WebSocket失败:', error)
        connectionStatus.value = false
        reject(error)
      }
    })
  }

  const handleTaskUpdate = (data) => {
    if (data.task_id === currentTask.id || !currentTask.id) {
      currentTask.id = data.task_id
      currentTask.status = data.stats.status
      currentTask.progress = data.stats.progress || 0
      currentTask.stats = {
        pagesCrawled: data.stats.pages_crawled || 0,
        projectsFound: data.stats.projects_found || 0,
        projectsProcessed: data.stats.projects_processed || 0,
        errors: data.stats.errors || 0
      }
      currentTask.logs = data.stats.logs || []

      console.log('📊 全局任务状态更新:', currentTask)
    }
  }

  const loadSystemStats = async () => {
    try {
      const response = await axios.get('/api/database/stats', {
        timeout: 10000
      })
      if (response.data && response.data.success) {
        const stats = response.data.stats
        systemStats.totalProjects = stats.total_projects || 0
        systemStats.todayProjects = stats.today_projects || 0
        systemStats.weekProjects = stats.week_projects || 0
      } else {
        console.warn('API返回数据格式异常:', response.data)
      }
    } catch (error) {
      console.error('加载系统统计失败:', error.message)
      // 设置默认值
      systemStats.totalProjects = 0
      systemStats.todayProjects = 0
      systemStats.weekProjects = 0
    }
  }

  const loadTasks = async () => {
    try {
      const response = await axios.get('/api/tasks', {
        timeout: 10000
      })
      if (response.data && response.data.success) {
        const tasks = response.data.tasks || []

        // 统计任务状态
        systemStats.activeTasks = tasks.filter(t =>
          t.stats && (t.stats.status === 'running' || t.stats.status === 'starting')
        ).length

        systemStats.completedTasks = tasks.filter(t =>
          t.stats && t.stats.status === 'completed'
        ).length

        systemStats.failedTasks = tasks.filter(t =>
          t.stats && (t.stats.status === 'failed' || t.stats.status === 'error')
        ).length

        // 更新当前任务状态
        const runningTask = tasks.find(t =>
          t.stats && (t.stats.status === 'running' || t.stats.status === 'starting')
        )

        if (runningTask) {
          currentTask.id = runningTask.task_id
          currentTask.status = runningTask.stats.status
          currentTask.progress = runningTask.stats.progress || 0
          currentTask.stats = {
            pagesCrawled: runningTask.stats.pages_crawled || 0,
            projectsFound: runningTask.stats.projects_found || 0,
            projectsProcessed: runningTask.stats.projects_processed || 0,
            errors: runningTask.stats.errors || 0
          }
          console.log('🔄 更新全局任务状态:', currentTask)
        } else if (currentTask.id && !['completed', 'failed', 'stopped'].includes(currentTask.status)) {
          // 如果当前有任务但服务器没有运行中的任务，重置状态
          currentTask.id = null
          currentTask.status = 'idle'
          currentTask.progress = 0
          currentTask.stats = {
            pagesCrawled: 0,
            projectsFound: 0,
            projectsProcessed: 0,
            errors: 0
          }
          console.log('🧹 重置全局任务状态')
        }

        console.log('📊 任务统计更新:', {
          active: systemStats.activeTasks,
          completed: systemStats.completedTasks,
          failed: systemStats.failedTasks
        })
      } else {
        console.warn('任务API返回数据格式异常:', response.data)
        // 设置默认值
        systemStats.activeTasks = 0
        systemStats.completedTasks = 0
        systemStats.failedTasks = 0
      }
    } catch (error) {
      console.error('加载任务列表失败:', error.message)
      // 设置默认值
      systemStats.activeTasks = 0
      systemStats.completedTasks = 0
      systemStats.failedTasks = 0
    }
  }

  const startCrawlTask = async (config) => {
    try {
      loading.value = true
      const response = await axios.post('/api/start_crawl', config)
      
      if (response.data.success) {
        currentTask.id = response.data.task_id
        currentTask.status = 'starting'
        currentTask.progress = 0
        return { success: true, taskId: response.data.task_id }
      } else {
        return { success: false, message: response.data.message }
      }
    } catch (error) {
      console.error('启动爬虫任务失败:', error)
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  const stopCrawlTask = async (taskId) => {
    try {
      const response = await axios.post(`/api/stop_crawl/${taskId}`)
      
      if (response.data.success) {
        currentTask.status = 'stopped'
        return { success: true }
      } else {
        return { success: false, message: response.data.message }
      }
    } catch (error) {
      console.error('停止爬虫任务失败:', error)
      return { success: false, message: error.message }
    }
  }

  const refreshData = async () => {
    await Promise.all([
      loadSystemStats(),
      loadTasks()
    ])
  }

  return {
    // 状态
    loading,
    socket,
    connectionStatus,
    systemStats,
    currentTask,

    // Actions
    initialize,
    initializeSocket,
    startCrawlTask,
    stopCrawlTask,
    refreshData,
    loadSystemStats,
    loadTasks
  }
})
