<template>
  <div>
    <!-- 页面标题 -->
    <div class="page-header mb-8">
      <div class="d-flex align-center">
        <div class="title-icon-container me-4">
          <v-icon icon="mdi-view-dashboard" :size="titleIconSize" />
        </div>
        <div class="title-content">
          <h1 class="page-title mb-1">
            仪表板
          </h1>
          <p class="page-subtitle">
            系统概览和实时状态监控
          </p>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid mb-10">
      <v-card
        class="stats-card stats-card--primary"
        color="primary"
        elevation="2"
      >
        <v-card-text class="text-center pa-6">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-database" :size="statsIconSize" class="stats-icon" />
          </div>
          <div class="stats-number text-white mb-2">
            {{ appStore.systemStats.totalProjects }}
          </div>
          <div class="stats-title text-white mb-1">总项目数</div>
          <div class="stats-subtitle text-white">累计爬取项目</div>
        </v-card-text>
      </v-card>

      <v-card
        class="stats-card stats-card--secondary"
        color="secondary"
        elevation="2"
      >
        <v-card-text class="text-center pa-6">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-calendar-today" :size="statsIconSize" class="stats-icon" />
          </div>
          <div class="stats-number text-white mb-2">
            {{ appStore.systemStats.todayProjects }}
          </div>
          <div class="stats-title text-white mb-1">今日新增</div>
          <div class="stats-subtitle text-white">今天爬取项目</div>
        </v-card-text>
      </v-card>

      <v-card
        class="stats-card stats-card--tertiary"
        color="success"
        elevation="2"
      >
        <v-card-text class="text-center pa-6">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-calendar-week" :size="statsIconSize" class="stats-icon" />
          </div>
          <div class="stats-number text-white mb-2">
            {{ appStore.systemStats.weekProjects }}
          </div>
          <div class="stats-title text-white mb-1">本周新增</div>
          <div class="stats-subtitle text-white">本周爬取项目</div>
        </v-card-text>
      </v-card>

      <v-card
        class="stats-card stats-card--surface"
        color="info"
        elevation="2"
      >
        <v-card-text class="text-center pa-6">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-cog" :size="statsIconSize" class="stats-icon" />
          </div>
          <div class="stats-number text-white mb-2">
            {{ appStore.systemStats.activeTasks }}
          </div>
          <div class="stats-title text-white mb-1">活跃任务</div>
          <div class="stats-subtitle text-white">正在运行任务</div>
        </v-card-text>
      </v-card>

      <!-- 超大屏幕额外统计卡片 -->
      <v-card
        class="stats-card stats-card--extra stats-card--growth d-none d-xxl-flex"
        color="success"
        elevation="2"
      >
        <v-card-text class="text-center pa-6">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-chart-line" :size="statsIconSize" class="stats-icon" />
          </div>
          <div class="stats-number text-white mb-2">
            {{ Math.round((appStore.systemStats.todayProjects / appStore.systemStats.totalProjects) * 100) || 0 }}%
          </div>
          <div class="stats-title text-white mb-1">增长率</div>
          <div class="stats-subtitle text-white">今日增长比例</div>
        </v-card-text>
      </v-card>

      <v-card
        class="stats-card stats-card--extra stats-card--average d-none d-xxl-flex"
        color="warning"
        elevation="2"
      >
        <v-card-text class="text-center pa-6">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-trending-up" :size="statsIconSize" class="stats-icon" />
          </div>
          <div class="stats-number text-white mb-2">
            {{ Math.round(appStore.systemStats.weekProjects / 7) || 0 }}
          </div>
          <div class="stats-title text-white mb-1">日均新增</div>
          <div class="stats-subtitle text-white">本周平均值</div>
        </v-card-text>
      </v-card>
    </div>

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
/* 页面头部样式 */
.page-header {
  margin-bottom: 32px;
}

.title-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(25, 118, 210, 0.2) 100%);
  border: 1px solid rgba(25, 118, 210, 0.2);
  transition: all 0.3s ease;
}

.title-content {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 1rem;
  line-height: 1.5;
  opacity: 0.87;
}

/* 统计网格布局 */
.stats-grid {
  display: grid;
  gap: 24px;
  margin-bottom: 40px;

  /* 手机：单列 */
  grid-template-columns: 1fr;

  /* 平板：双列 */
  @media (min-width: 600px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  /* 中等屏幕：三列 */
  @media (min-width: 960px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  /* 大屏幕：四列 */
  @media (min-width: 1264px) {
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
  }

  /* 超大屏幕：六列 */
  @media (min-width: 2560px) {
    grid-template-columns: repeat(6, 1fr);
    gap: 28px;
  }
}

/* 统计卡片样式 */
.stats-card {
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-4px);

    .stats-icon-wrapper {
      transform: scale(1.05);
    }
  }

  &.stats-card--extra {
    /* 超大屏幕才显示的额外卡片 */
    @media (max-width: 2559px) {
      display: none !important;
    }
  }
}

.stats-icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;

  @media (max-width: 599px) {
    width: 72px;
    height: 72px;
    border-radius: 18px;
  }
}

.stats-icon {
  opacity: 0.95;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
  transition: all 0.3s ease;
}

.stats-number {
  font-size: 2.5rem;
  font-weight: 600;
  line-height: 1;

  @media (max-width: 599px) {
    font-size: 2rem;
  }
}

.stats-title {
  font-size: 1rem;
  font-weight: 500;

  @media (max-width: 599px) {
    font-size: 0.875rem;
  }
}

.stats-subtitle {
  font-size: 0.875rem;
  opacity: 0.8;

  @media (max-width: 599px) {
    font-size: 0.75rem;
  }
}



/* 响应式优化 */
@media (max-width: 599px) {
  .title-icon-container {
    width: 56px;
    height: 56px;
    border-radius: 14px;
  }
}
</style>