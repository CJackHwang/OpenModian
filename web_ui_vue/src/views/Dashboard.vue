<template>
  <div>
    <!-- 页面标题 - 统一设计 -->
    <div class="app-section">
      <div class="d-flex align-center">
        <v-avatar
          color="primary"
          class="me-4"
          :size="titleIconSize"
        >
          <v-icon icon="mdi-view-dashboard" />
        </v-avatar>
        <div class="flex-grow-1">
          <h1 class="text-h4 font-weight-medium mb-1">
            仪表板
          </h1>
          <p class="text-subtitle-1 text-medium-emphasis">
            系统概览和实时状态监控
          </p>
        </div>
        <v-chip
          color="success"
          prepend-icon="mdi-check-circle"
          class="d-none d-md-flex app-chip"
        >
          系统运行正常
        </v-chip>
      </div>
    </div>

    <!-- 统计卡片 - 统一设计 -->
    <v-row class="app-section">
      <v-col cols="12" sm="6" md="3">
        <v-card
          color="primary-container"
          class="app-card stats-card text-center"
        >
          <v-card-text class="p-lg">
            <v-avatar
              color="primary"
              size="80"
              class="mb-4"
            >
              <v-icon
                icon="mdi-database"
                :size="statsIconSize"
                color="on-primary"
              />
            </v-avatar>
            <div class="text-h3 font-weight-medium mb-2 text-on-primary-container">
              {{ appStore.systemStats.totalProjects }}
            </div>
            <div class="text-subtitle-1 mb-1 font-weight-medium text-on-primary-container">总项目数</div>
            <div class="text-body-2 text-on-primary-container-variant">累计爬取项目</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card
          color="secondary-container"
          class="app-card stats-card text-center"
        >
          <v-card-text class="p-lg">
            <v-avatar
              color="secondary"
              size="80"
              class="mb-4"
            >
              <v-icon
                icon="mdi-calendar-today"
                :size="statsIconSize"
                color="on-secondary"
              />
            </v-avatar>
            <div class="text-h3 font-weight-medium mb-2 text-on-secondary-container">
              {{ appStore.systemStats.todayProjects }}
            </div>
            <div class="text-subtitle-1 mb-1 font-weight-medium text-on-secondary-container">今日新增</div>
            <div class="text-body-2 text-on-secondary-container-variant">今天爬取项目</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card
          color="success-container"
          class="app-card stats-card text-center"
        >
          <v-card-text class="p-lg">
            <v-avatar
              color="success"
              size="80"
              class="mb-4"
            >
              <v-icon
                icon="mdi-calendar-week"
                :size="statsIconSize"
                color="on-success"
              />
            </v-avatar>
            <div class="text-h3 font-weight-medium mb-2 text-on-success-container">
              {{ appStore.systemStats.weekProjects }}
            </div>
            <div class="text-subtitle-1 mb-1 font-weight-medium text-on-success-container">本周新增</div>
            <div class="text-body-2 text-on-success-container-variant">本周爬取项目</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card
          color="info-container"
          class="app-card stats-card text-center"
        >
          <v-card-text class="p-lg">
            <v-avatar
              color="info"
              size="80"
              class="mb-4"
            >
              <v-icon
                icon="mdi-cog"
                :size="statsIconSize"
                color="on-info"
              />
            </v-avatar>
            <div class="text-h3 font-weight-medium mb-2 text-on-info-container">
              {{ appStore.systemStats.activeTasks }}
            </div>
            <div class="text-subtitle-1 mb-1 font-weight-medium text-on-info-container">活跃任务</div>
            <div class="text-body-2 text-on-info-container-variant">正在运行任务</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 主要内容区域 - 响应式布局 -->
    <v-row>
      <!-- 当前任务状态 - Vuetify优化 -->
      <v-col cols="12" md="8" lg="8" xl="9" xxl="9">
        <v-card
          class="mb-4"
          elevation="0"
          rounded="xl"
        >
          <v-card-title class="d-flex align-center pa-6">
            <v-avatar color="primary" size="40" class="me-3">
              <v-icon icon="mdi-spider" color="on-primary" />
            </v-avatar>
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold">当前任务状态</div>
              <div class="text-body-2 text-medium-emphasis">实时监控爬虫任务进度</div>
            </div>
            <v-chip
              :color="getTaskStatusColor(appStore.currentTask.status)"
              size="default"
              variant="tonal"
              :prepend-icon="getTaskStatusIcon(appStore.currentTask.status)"
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
                  <div class="text-caption">已爬页面</div>
                </v-col>
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-success">
                    {{ appStore.currentTask.stats.projectsFound }}
                  </div>
                  <div class="text-caption">发现项目</div>
                </v-col>
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-info">
                    {{ appStore.currentTask.stats.projectsProcessed }}
                  </div>
                  <div class="text-caption">已处理</div>
                </v-col>
                <v-col cols="3">
                  <div class="text-h6 font-weight-bold text-error">
                    {{ appStore.currentTask.stats.errors }}
                  </div>
                  <div class="text-caption">错误数</div>
                </v-col>
              </v-row>
            </div>

            <div v-else class="text-center py-8">
              <v-icon icon="mdi-sleep" size="64" class="mb-4" />
              <div class="text-h6">暂无活跃任务</div>
              <div class="text-subtitle-2">点击"爬虫控制"开始新任务</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 侧边栏信息 - Vuetify优化 -->
      <v-col cols="12" md="4" lg="4" xl="3" xxl="3">
        <!-- 任务统计 -->
        <v-card
          class="mb-4"
          elevation="0"
          rounded="xl"

        >
          <v-card-title class="pa-6">
            <v-avatar color="tertiary" size="32" class="me-3">
              <v-icon icon="mdi-chart-pie" color="on-tertiary" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">任务统计</div>
              <div class="text-body-2 text-medium-emphasis">系统任务概览</div>
            </div>
          </v-card-title>

          <v-card-text class="pa-6 pt-0">
            <v-list density="compact">
              <v-list-item class="px-0">
                <template #prepend>
                  <v-icon icon="mdi-play-circle" color="success" />
                </template>
                <v-list-item-title>活跃任务</v-list-item-title>
                <template #append>
                  <v-chip color="success" size="small" variant="tonal">
                    {{ appStore.systemStats.activeTasks }}
                  </v-chip>
                </template>
              </v-list-item>

              <v-list-item class="px-0">
                <template #prepend>
                  <v-icon icon="mdi-check-circle" color="primary" />
                </template>
                <v-list-item-title>已完成</v-list-item-title>
                <template #append>
                  <v-chip color="primary" size="small" variant="tonal">
                    {{ appStore.systemStats.completedTasks }}
                  </v-chip>
                </template>
              </v-list-item>

              <v-list-item class="px-0">
                <template #prepend>
                  <v-icon icon="mdi-alert-circle" color="error" />
                </template>
                <v-list-item-title>失败任务</v-list-item-title>
                <template #append>
                  <v-chip color="error" size="small" variant="tonal">
                    {{ appStore.systemStats.failedTasks }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- 快速操作 -->
        <v-card
          elevation="0"
          class="mb-4"
          rounded="xl"

        >
          <v-card-title class="pa-6">
            <v-avatar color="warning" size="32" class="me-3">
              <v-icon icon="mdi-lightning-bolt" color="on-warning" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">快速操作</div>
              <div class="text-body-2 text-medium-emphasis">常用功能入口</div>
            </div>
          </v-card-title>

          <v-card-text class="pa-6 pt-0">
            <v-btn
              block
              color="primary"
              class="mb-3"
              prepend-icon="mdi-play"
              @click="$router.push('/spider')"
              size="large"
            >
              开始新任务
            </v-btn>

            <v-btn
              block
              color="secondary"
              class="mb-3"
              prepend-icon="mdi-database"
              @click="$router.push('/data')"
              size="large"
            >
              查看数据
            </v-btn>

            <v-btn
              block
              prepend-icon="mdi-cog"
              @click="$router.push('/settings')"
              size="large"
              color="primary"
            >
              系统设置
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 实时日志区域 -->
    <v-row class="mt-4">
      <v-col cols="12">
        <RealTimeLogViewer
          :height="logViewerHeight"
          :min-height="'250px'"
          :max-height="'500px'"
          :max-logs="300"
          :auto-scroll="true"
          :compact="display.xs.value"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useAppStore } from '@/stores/app'
import RealTimeLogViewer from '@/components/RealTimeLogViewer.vue'

const display = useDisplay()
const appStore = useAppStore()

// 响应式尺寸计算
const titleIconSize = computed(() => {
  if (display.xs.value) return 24
  if (display.sm.value) return 28
  return 32
})

const statsIconSize = computed(() => {
  if (display.xs.value) return 40
  if (display.sm.value) return 48
  return 56
})

// 日志查看器高度计算
const logViewerHeight = computed(() => {
  if (display.xs.value) return '300px'
  if (display.sm.value) return '350px'
  if (display.md.value) return '400px'
  return '450px'
})



// 方法
const getTaskStatusColor = (status) => {
  const colors = {
    'idle': 'secondary',
    'starting': 'warning',
    'running': 'success',
    'completed': 'primary',
    'failed': 'error',
    'stopped': 'secondary'
  }
  return colors[status] || 'secondary'
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

const getTaskStatusIcon = (status) => {
  const icons = {
    'idle': 'mdi-sleep',
    'starting': 'mdi-loading',
    'running': 'mdi-play',
    'completed': 'mdi-check',
    'failed': 'mdi-alert',
    'stopped': 'mdi-stop'
  }
  return icons[status] || 'mdi-help'
}



// 生命周期
onMounted(() => {
  appStore.refreshData()
})
</script>

<style scoped>
/* Dashboard MD3 标准样式 */
/* 样式现在完全由Vuetify defaults配置管理 - 遵循官方文档最佳实践 */
.stats-card {
  transition: background-color var(--md3-motion-duration-short) var(--md3-motion-easing-standard);
}

.stats-card .v-avatar {
  transition: none;
}

/* 透明度工具类 */
.opacity-90 {
  opacity: 0.9;
}

/* 响应式优化现在通过VAvatar的defaults配置管理 */
</style>