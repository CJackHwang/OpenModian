<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="me-2">mdi-history</v-icon>
          任务历史
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          查看历史爬取任务记录和结果
        </p>
      </v-col>
    </v-row>

    <!-- 任务列表 -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2">mdi-format-list-bulleted</v-icon>
        历史任务
        <v-spacer />
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
        :items="tasks"
        :loading="loading"
        class="elevation-0"
        item-value="task_id"
      >
        <!-- 任务ID列 -->
        <template #item.task_id="{ item }">
          <code class="text-primary">{{ item.task_id.substring(0, 8) }}</code>
        </template>

        <!-- 状态列 -->
        <template #item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            variant="flat"
            size="small"
          >
            <v-icon start>{{ getStatusIcon(item.status) }}</v-icon>
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>

        <!-- 配置列 -->
        <template #item.config="{ item }">
          <div>
            <div class="text-subtitle-2">
              页面: {{ item.start_page }}-{{ item.end_page }}
            </div>
            <div class="text-caption text-medium-emphasis">
              分类: {{ item.category }}
            </div>
          </div>
        </template>

        <!-- 结果列 -->
        <template #item.results="{ item }">
          <div class="text-center">
            <div class="text-subtitle-2 text-success">
              {{ item.projects_processed || 0 }}
            </div>
            <div class="text-caption text-medium-emphasis">
              已处理项目
            </div>
          </div>
        </template>

        <!-- 时间列 -->
        <template #item.start_time="{ item }">
          <div>
            <div>{{ formatDate(item.start_time) }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ formatTime(item.start_time) }}
            </div>
          </div>
        </template>

        <!-- 操作列 -->
        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn
              icon="mdi-download"
              size="small"
              variant="text"
              @click="downloadResults(item.task_id)"
              :disabled="item.status !== 'completed'"
              title="下载结果"
            />
            <v-btn
              icon="mdi-information"
              size="small"
              variant="text"
              @click="showTaskDetails(item)"
              title="查看详情"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteTask(item.task_id)"
              :disabled="item.status === 'running'"
              title="删除任务"
            />
          </div>
        </template>

        <!-- 无数据状态 -->
        <template #no-data>
          <div class="text-center pa-8">
            <v-icon size="64" class="mb-4 text-medium-emphasis">mdi-history</v-icon>
            <div class="text-h6 text-medium-emphasis">暂无历史任务</div>
            <div class="text-subtitle-2 text-medium-emphasis mb-4">
              开始第一个爬虫任务
            </div>
            <v-btn
              color="primary"
              prepend-icon="mdi-spider"
              @click="$router.push('/spider')"
            >
              开始爬取
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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

// 表格列定义
const headers = [
  { title: '任务ID', key: 'task_id', sortable: false, width: '120px' },
  { title: '状态', key: 'status', sortable: true, width: '120px' },
  { title: '配置', key: 'config', sortable: false, width: '150px' },
  { title: '处理结果', key: 'results', sortable: true, width: '120px' },
  { title: '开始时间', key: 'start_time', sortable: true, width: '150px' },
  { title: '操作', key: 'actions', sortable: false, width: '100px' }
]

// 方法
const loadTasks = async () => {
  try {
    loading.value = true

    // 获取历史任务记录
    const response = await axios.get('/api/tasks/history')

    if (response.data.success) {
      tasks.value = response.data.tasks.map(task => ({
        task_id: task.task_id,
        status: task.status,
        start_page: task.config?.start_page || task.start_page,
        end_page: task.config?.end_page || task.end_page,
        category: task.config?.category || task.category,
        projects_processed: task.projects_processed || 0,
        projects_found: task.projects_found || 0,
        errors_count: task.errors_count || 0,
        start_time: task.start_time,
        end_time: task.end_time,
        duration: task.duration
      }))

      console.log('📊 加载历史任务:', tasks.value.length, '条')
    }
  } catch (error) {
    console.error('❌ 加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

const getStatusColor = (status) => {
  const colors = {
    'running': 'success',
    'completed': 'primary',
    'failed': 'error',
    'stopped': 'secondary',
    'starting': 'warning'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status) => {
  const icons = {
    'running': 'mdi-play',
    'completed': 'mdi-check',
    'failed': 'mdi-close',
    'stopped': 'mdi-stop',
    'starting': 'mdi-loading'
  }
  return icons[status] || 'mdi-help'
}

const getStatusText = (status) => {
  const texts = {
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'stopped': '已停止',
    'starting': '启动中'
  }
  return texts[status] || '未知'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  // 确保正确处理时区，显示北京时间
  return dayjs(dateStr).tz('Asia/Shanghai').format('YYYY-MM-DD')
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  // 确保正确处理时区，显示北京时间
  return dayjs(dateStr).tz('Asia/Shanghai').format('HH:mm:ss')
}

const downloadResults = (taskId) => {
  try {
    // 下载任务相关的数据文件
    const url = `/api/database/export?task_id=${taskId}`
    const link = document.createElement('a')
    link.href = url
    link.download = `task_${taskId}_results.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('下载失败:', error)
  }
}

const showTaskDetails = async (task) => {
  try {
    const response = await axios.get(`/api/task/${task.task_id}`)
    if (response.data.success) {
      const taskDetail = response.data.task

      // 显示任务详情对话框
      const details = [
        `任务ID: ${taskDetail.task_id}`,
        `状态: ${getStatusText(taskDetail.stats.status)}`,
        `开始时间: ${formatDateTime(taskDetail.stats.start_time)}`,
        `结束时间: ${formatDateTime(taskDetail.stats.end_time) || '未完成'}`,
        `运行时长: ${taskDetail.stats.duration || '计算中...'}`,
        `页面范围: ${taskDetail.config.start_page}-${taskDetail.config.end_page}`,
        `分类: ${taskDetail.config.category}`,
        `发现项目: ${taskDetail.stats.projects_found}个`,
        `处理项目: ${taskDetail.stats.projects_processed}个`,
        `错误数量: ${taskDetail.stats.errors_count}个`
      ].join('\n')

      alert(`任务详情:\n\n${details}`)
    }
  } catch (error) {
    console.error('获取任务详情失败:', error)
    alert('获取任务详情失败')
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('确定要删除这个任务记录吗？此操作不可恢复。')) {
    return
  }

  try {
    const response = await axios.delete(`/api/task/${taskId}`)
    if (response.data.success) {
      // 重新加载任务列表
      await loadTasks()
      alert('任务删除成功')
    } else {
      alert(`删除失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('删除任务失败:', error)
    alert('删除任务失败')
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  // 确保正确处理时区，显示北京时间
  return dayjs(dateStr).tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss')
}

// 生命周期
onMounted(() => {
  loadTasks()
})
</script>
