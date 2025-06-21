<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="me-2">mdi-format-list-bulleted</v-icon>
          任务管理
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          统一管理普通任务和定时任务
        </p>
      </v-col>
    </v-row>

    <!-- 任务统计卡片 -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-card color="primary" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center">
              <v-icon size="40" class="me-3">mdi-play-circle</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ normalTasksCount }}</div>
                <div class="text-subtitle-2">运行中任务</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="success" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center">
              <v-icon size="40" class="me-3">mdi-clock-outline</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ activeScheduledTasksCount }}</div>
                <div class="text-subtitle-2">活跃定时任务</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center">
              <v-icon size="40" class="me-3">mdi-pause-circle</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ pausedScheduledTasksCount }}</div>
                <div class="text-subtitle-2">暂停定时任务</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="info" variant="flat">
          <v-card-text class="text-white">
            <div class="d-flex align-center">
              <v-icon size="40" class="me-3">mdi-format-list-bulleted</v-icon>
              <div>
                <div class="text-h5 font-weight-bold">{{ totalTasksCount }}</div>
                <div class="text-subtitle-2">总任务数</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 任务列表 -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2">mdi-format-list-bulleted</v-icon>
        任务列表
        <v-spacer />
        
        <!-- 任务类型筛选 -->
        <v-chip-group v-model="taskTypeFilter" class="me-4">
          <v-chip value="all" variant="outlined">全部</v-chip>
          <v-chip value="normal" variant="outlined">普通任务</v-chip>
          <v-chip value="scheduled" variant="outlined">定时任务</v-chip>
        </v-chip-group>
        
        <v-btn
          color="primary"
          prepend-icon="mdi-refresh"
          @click="loadTasks"
          :loading="loading"
        >
          刷新
        </v-btn>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="filteredTasks"
        :loading="loading"
        class="elevation-0"
        item-value="task_id"
        @click:row="selectTask"
      >
        <!-- 任务ID列 -->
        <template #item.task_id="{ item }">
          <div class="d-flex align-center">
            <!-- 任务类型图标 -->
            <v-icon 
              :color="item.task_type === 'scheduled' ? 'success' : 'primary'"
              class="me-2"
            >
              {{ item.task_type === 'scheduled' ? 'mdi-clock-outline' : 'mdi-play-circle' }}
            </v-icon>
            <code class="text-primary">{{ item.task_id.substring(0, 12) }}</code>
          </div>
        </template>

        <!-- 任务类型列 -->
        <template #item.task_type="{ item }">
          <v-chip
            :color="item.task_type === 'scheduled' ? 'success' : 'primary'"
            variant="flat"
            size="small"
          >
            <v-icon start>
              {{ item.task_type === 'scheduled' ? 'mdi-clock-outline' : 'mdi-play-circle' }}
            </v-icon>
            {{ item.task_type === 'scheduled' ? '定时任务' : '普通任务' }}
          </v-chip>
        </template>

        <!-- 状态列 -->
        <template #item.status="{ item }">
          <div class="d-flex align-center">
            <div
              :class="['status-indicator', `status-${item.stats.status}`]"
            ></div>
            <v-chip
              :color="getStatusColor(item.stats.status)"
              variant="flat"
              size="small"
              class="ms-2"
            >
              <v-icon start>{{ getStatusIcon(item.stats.status) }}</v-icon>
              <span class="status-text">{{ getStatusText(item.stats.status) }}</span>
            </v-chip>
          </div>
        </template>

        <!-- 配置列 -->
        <template #item.config="{ item }">
          <div>
            <div class="text-subtitle-2">
              页面: {{ item.config.start_page }}-{{ item.config.end_page }}
            </div>
            <div class="text-caption text-medium-emphasis">
              分类: {{ item.config.category }}
            </div>
          </div>
        </template>

        <!-- 进度/调度信息列 -->
        <template #item.progress="{ item }">
          <div v-if="item.task_type === 'normal'">
            <v-progress-linear
              v-if="item.stats.progress !== undefined"
              :model-value="item.stats.progress"
              color="primary"
              height="6"
              rounded
            />
            <div class="text-caption mt-1">
              {{ item.stats.progress || 0 }}%
            </div>
          </div>
          <div v-else class="text-caption">
            <div v-if="item.schedule_info.next_run_time">
              <strong>下次执行:</strong><br>
              {{ formatDateTime(item.schedule_info.next_run_time) }}
            </div>
            <div v-if="item.schedule_info.run_count > 0" class="mt-1">
              <strong>执行次数:</strong> {{ item.schedule_info.run_count }}
            </div>
            <div class="mt-1">
              <strong>间隔:</strong> {{ formatInterval(item.schedule_info.interval_seconds) }}
            </div>
          </div>
        </template>

        <!-- 操作列 -->
        <template #item.actions="{ item }">
          <div class="d-flex gap-1">
            <v-btn
              size="small"
              variant="text"
              icon="mdi-eye"
              color="primary"
              @click.stop="viewTaskDetails(item)"
            />
            
            <v-btn
              v-if="item.task_type === 'scheduled'"
              size="small"
              variant="text"
              :icon="item.is_active ? 'mdi-pause' : 'mdi-play'"
              :color="item.is_active ? 'warning' : 'success'"
              @click.stop="toggleScheduledTask(item)"
            />
            
            <v-btn
              v-if="item.task_type === 'scheduled'"
              size="small"
              variant="text"
              icon="mdi-play-speed"
              color="info"
              @click.stop="runScheduledTaskNow(item)"
              :disabled="item.is_running"
            />
            
            <v-btn
              size="small"
              variant="text"
              icon="mdi-delete"
              color="error"
              @click.stop="deleteTask(item)"
            />
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- 任务详情对话框 -->
    <v-dialog v-model="detailDialog" max-width="800px">
      <v-card v-if="selectedTask">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2">{{ selectedTask.task_type === 'scheduled' ? 'mdi-clock-outline' : 'mdi-play-circle' }}</v-icon>
          任务详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="detailDialog = false" />
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>任务ID</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedTask.task_id }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>任务类型</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="small" :color="selectedTask.task_type === 'scheduled' ? 'success' : 'primary'">
                      {{ selectedTask.task_type === 'scheduled' ? '定时任务' : '普通任务' }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>状态</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-chip size="small" :color="getStatusColor(selectedTask.stats.status)">
                      {{ getStatusText(selectedTask.stats.status) }}
                    </v-chip>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>页面范围</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedTask.config.start_page }}-{{ selectedTask.config.end_page }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>分类</v-list-item-title>
                  <v-list-item-subtitle>{{ selectedTask.config.category }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item v-if="selectedTask.task_type === 'scheduled'">
                  <v-list-item-title>执行间隔</v-list-item-title>
                  <v-list-item-subtitle>{{ formatInterval(selectedTask.schedule_info.interval_seconds) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
          
          <!-- 定时任务特有信息 -->
          <div v-if="selectedTask.task_type === 'scheduled'" class="mt-4">
            <v-divider class="mb-4" />
            <h3 class="text-h6 mb-3">调度信息</h3>
            <v-row>
              <v-col cols="12" md="6">
                <v-list density="compact">
                  <v-list-item v-if="selectedTask.schedule_info.next_run_time">
                    <v-list-item-title>下次执行时间</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(selectedTask.schedule_info.next_run_time) }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item v-if="selectedTask.schedule_info.last_run_time">
                    <v-list-item-title>上次执行时间</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDateTime(selectedTask.schedule_info.last_run_time) }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
              <v-col cols="12" md="6">
                <v-list density="compact">
                  <v-list-item>
                    <v-list-item-title>执行次数</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedTask.schedule_info.run_count }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>任务状态</v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip size="small" :color="selectedTask.is_active ? 'success' : 'warning'">
                        {{ selectedTask.is_active ? '活跃' : '暂停' }}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="detailDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

// 扩展dayjs插件
dayjs.extend(utc)
dayjs.extend(timezone)

// 响应式数据
const loading = ref(false)
const tasks = ref([])
const taskTypeFilter = ref('all')
const detailDialog = ref(false)
const selectedTask = ref(null)

// 表格列定义
const headers = [
  { title: '任务ID', key: 'task_id', sortable: false, width: '200px' },
  { title: '类型', key: 'task_type', sortable: true, width: '120px' },
  { title: '状态', key: 'status', sortable: true, width: '120px' },
  { title: '配置', key: 'config', sortable: false, width: '150px' },
  { title: '进度/调度', key: 'progress', sortable: false, width: '200px' },
  { title: '操作', key: 'actions', sortable: false, width: '150px' }
]

// 计算属性
const filteredTasks = computed(() => {
  if (taskTypeFilter.value === 'all') {
    return tasks.value
  }
  return tasks.value.filter(task => task.task_type === taskTypeFilter.value)
})

const normalTasksCount = computed(() => {
  return tasks.value.filter(task =>
    task.task_type === 'normal' &&
    (task.stats.status === 'running' || task.stats.status === 'starting')
  ).length
})

const activeScheduledTasksCount = computed(() => {
  return tasks.value.filter(task => task.task_type === 'scheduled' && task.is_active).length
})

const pausedScheduledTasksCount = computed(() => {
  return tasks.value.filter(task => task.task_type === 'scheduled' && !task.is_active).length
})

const totalTasksCount = computed(() => {
  return tasks.value.length
})

// 方法
const loadTasks = async () => {
  try {
    loading.value = true
    const response = await axios.get('/api/tasks')

    if (response.data.success) {
      tasks.value = response.data.tasks
      console.log('📊 加载任务列表:', {
        total: tasks.value.length,
        normal: response.data.normal_tasks,
        scheduled: response.data.scheduled_tasks
      })
    }
  } catch (error) {
    console.error('❌ 加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

const selectTask = (event, { item }) => {
  selectedTask.value = item
  detailDialog.value = true
}

const viewTaskDetails = (task) => {
  selectedTask.value = task
  detailDialog.value = true
}

const toggleScheduledTask = async (task) => {
  try {
    const response = await axios.post(`/api/scheduled_tasks/${task.task_id}/toggle`)
    if (response.data.success) {
      // 重新加载任务列表
      await loadTasks()
      console.log('✅ 任务状态切换成功')
    } else {
      alert(`操作失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('❌ 切换任务状态失败:', error)
    alert('切换任务状态失败')
  }
}

const runScheduledTaskNow = async (task) => {
  if (!confirm('确定要立即执行这个定时任务吗？')) {
    return
  }

  try {
    // 这里需要添加立即执行定时任务的API
    const response = await axios.post(`/api/scheduled_tasks/${task.task_id}/run_now`)
    if (response.data.success) {
      alert('任务已开始执行')
      await loadTasks()
    } else {
      alert(`执行失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('❌ 立即执行任务失败:', error)
    alert('立即执行任务失败')
  }
}

const deleteTask = async (task) => {
  const taskType = task.task_type === 'scheduled' ? '定时任务' : '普通任务'
  if (!confirm(`确定要删除这个${taskType}吗？此操作不可恢复。`)) {
    return
  }

  try {
    let response
    if (task.task_type === 'scheduled') {
      response = await axios.delete(`/api/scheduled_tasks/${task.task_id}`)
    } else {
      response = await axios.delete(`/api/task/${task.task_id}`)
    }

    if (response.data.success) {
      await loadTasks()
      alert(`${taskType}删除成功`)
    } else {
      alert(`删除失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('❌ 删除任务失败:', error)
    alert('删除任务失败')
  }
}

// 状态相关方法
const getStatusColor = (status) => {
  const statusColors = {
    'running': 'primary',
    'completed': 'success',
    'failed': 'error',
    'stopped': 'warning',
    'scheduled': 'success',
    'paused': 'warning',
    'starting': 'info'
  }
  return statusColors[status] || 'grey'
}

const getStatusIcon = (status) => {
  const statusIcons = {
    'running': 'mdi-play-circle',
    'completed': 'mdi-check-circle',
    'failed': 'mdi-alert-circle',
    'stopped': 'mdi-stop-circle',
    'scheduled': 'mdi-clock-check',
    'paused': 'mdi-pause-circle',
    'starting': 'mdi-loading'
  }
  return statusIcons[status] || 'mdi-help-circle'
}

const getStatusText = (status) => {
  const statusTexts = {
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'stopped': '已停止',
    'scheduled': '已调度',
    'paused': '已暂停',
    'starting': '启动中'
  }
  return statusTexts[status] || '未知'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss')
}

const formatInterval = (seconds) => {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`
  return `${Math.floor(seconds / 86400)}天`
}

// 生命周期
onMounted(() => {
  loadTasks()

  // 设置定时刷新
  const refreshInterval = setInterval(loadTasks, 10000) // 每10秒刷新一次

  onUnmounted(() => {
    clearInterval(refreshInterval)
  })
})
</script>
