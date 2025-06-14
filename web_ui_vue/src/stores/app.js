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
    try {
      socket.value = io({
        transports: ['websocket', 'polling'],
        timeout: 5000,
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5
      })

      socket.value.on('connect', () => {
        connectionStatus.value = true
        console.log('WebSocket连接成功')
      })

      socket.value.on('disconnect', () => {
        connectionStatus.value = false
        console.log('WebSocket连接断开')
      })

      socket.value.on('connect_error', (error) => {
        connectionStatus.value = false
        console.warn('WebSocket连接失败:', error.message)
      })

      socket.value.on('task_update', (data) => {
        handleTaskUpdate(data)
      })
    } catch (error) {
      console.error('初始化WebSocket失败:', error)
      connectionStatus.value = false
    }
  }

  const handleTaskUpdate = (data) => {
    if (data.task_id === currentTask.id) {
      currentTask.status = data.stats.status
      currentTask.progress = data.stats.progress || 0
      currentTask.stats = {
        pagesCrawled: data.stats.pages_crawled || 0,
        projectsFound: data.stats.projects_found || 0,
        projectsProcessed: data.stats.projects_processed || 0,
        errors: data.stats.errors || 0
      }
      currentTask.logs = data.stats.logs || []
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
    startCrawlTask,
    stopCrawlTask,
    refreshData,
    loadSystemStats,
    loadTasks
  }
})
