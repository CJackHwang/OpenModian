<template>
  <div>
    <!-- 页面标题 -->
    <div class="mb-8">
      <div class="d-flex align-center">
        <v-avatar color="primary" class="me-4" :size="titleIconSize">
          <v-icon icon="mdi-view-dashboard" />
        </v-avatar>
        <div class="flex-grow-1">
          <h1 class="text-h4 font-weight-bold mb-1">
            仪表板
          </h1>
          <p class="text-subtitle-1 text-medium-emphasis">
            系统概览和实时状态监控
          </p>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <v-row class="mb-10">
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-avatar color="primary-container" size="80" class="mb-4">
              <v-icon icon="mdi-database" :size="statsIconSize" color="on-primary-container" />
            </v-avatar>
            <div class="text-h4 font-weight-bold text-white mb-2">
              {{ appStore.systemStats.totalProjects }}
            </div>
            <div class="text-subtitle-1 text-white mb-1">总项目数</div>
            <div class="text-body-2 text-white opacity-80">累计爬取项目</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="secondary" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-avatar color="secondary-container" size="80" class="mb-4">
              <v-icon icon="mdi-calendar-today" :size="statsIconSize" color="on-secondary-container" />
            </v-avatar>
            <div class="text-h4 font-weight-bold text-white mb-2">
              {{ appStore.systemStats.todayProjects }}
            </div>
            <div class="text-subtitle-1 text-white mb-1">今日新增</div>
            <div class="text-body-2 text-white opacity-80">今天爬取项目</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="success" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-avatar color="success-container" size="80" class="mb-4">
              <v-icon icon="mdi-calendar-week" :size="statsIconSize" color="on-success-container" />
            </v-avatar>
            <div class="text-h4 font-weight-bold text-white mb-2">
              {{ appStore.systemStats.weekProjects }}
            </div>
            <div class="text-subtitle-1 text-white mb-1">本周新增</div>
            <div class="text-body-2 text-white opacity-80">本周爬取项目</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="info" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-avatar color="info-container" size="80" class="mb-4">
              <v-icon icon="mdi-cog" :size="statsIconSize" color="on-info-container" />
            </v-avatar>
            <div class="text-h4 font-weight-bold text-white mb-2">
              {{ appStore.systemStats.activeTasks }}
            </div>
            <div class="text-subtitle-1 text-white mb-1">活跃任务</div>
            <div class="text-body-2 text-white opacity-80">正在运行任务</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 主要内容区域 - 响应式布局 -->
    <v-row>
      <!-- 当前任务状态 -->
      <v-col cols="12" md="8" lg="8" xl="9" xxl="9">
        <v-card class="mb-4" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-spider" class="me-3" />
            当前任务状态
            <v-spacer />
            <v-chip
              :color="getTaskStatusColor(appStore.currentTask.status)"
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

      <!-- 侧边栏信息 -->
      <v-col cols="12" md="4" lg="4" xl="3" xxl="3">
        <!-- 任务统计 -->
        <v-card class="mb-4" elevation="2">
          <v-card-title>
            <v-icon icon="mdi-chart-pie" class="me-3 icon-primary" />
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
            <v-icon icon="mdi-lightning-bolt" class="me-3 icon-primary" />
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
              prepend-icon="mdi-cog"
              @click="$router.push('/settings')"
            >
              系统设置
            </v-btn>
          </v-card-text>
        </v-card>


      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useAppStore } from '@/stores/app'

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



// 生命周期
onMounted(() => {
  appStore.refreshData()
})
</script>

<style scoped>
/* 基础样式 */
.opacity-80 {
  opacity: 0.8;
}
</style>