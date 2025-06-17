<template>
  <div>
    <!-- 页面标题 - M3风格 -->
    <v-row class="mb-8">
      <v-col>
        <div class="d-flex align-center mb-4">
          <div class="title-icon-container me-4">
            <v-icon icon="mdi-view-dashboard" size="32" />
          </div>
          <div>
            <h1 class="text-headline-large font-weight-medium text-primary mb-1">
              仪表板
            </h1>
            <p class="text-body-large text-on-surface-variant">
              系统概览和实时状态监控
            </p>
          </div>
        </div>
      </v-col>
      <v-col cols="auto" class="d-flex align-center">
        <!-- 移除重复的刷新按钮，使用顶部应用栏的智能刷新按钮 -->
      </v-col>
    </v-row>

    <!-- 统计卡片 - M3风格响应式 -->
    <v-row class="mb-10 responsive-spacing">
      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card
          class="text-center stats-card interactive-hover responsive-spacing"
          color="primary-container"
          variant="elevated"
          elevation="2"
        >
          <div class="stats-icon-wrapper mb-6">
            <v-icon icon="mdi-database" size="56" class="stats-icon" />
          </div>
          <div class="text-display-small font-weight-medium mb-3 text-on-primary-container">
            {{ appStore.systemStats.totalProjects }}
          </div>
          <div class="text-title-medium font-weight-medium mb-2 text-on-primary-container">总项目数</div>
          <div class="text-body-medium text-on-primary-container opacity-80">累计爬取项目</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card
          class="text-center stats-card interactive-hover responsive-spacing"
          color="secondary-container"
          variant="elevated"
          elevation="2"
        >
          <div class="stats-icon-wrapper mb-6">
            <v-icon icon="mdi-calendar-today" size="56" class="stats-icon" />
          </div>
          <div class="text-display-small font-weight-medium mb-3 text-on-secondary-container">
            {{ appStore.systemStats.todayProjects }}
          </div>
          <div class="text-title-medium font-weight-medium mb-2 text-on-secondary-container">今日新增</div>
          <div class="text-body-medium text-on-secondary-container opacity-80">今天爬取项目</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card
          class="text-center stats-card interactive-hover responsive-spacing"
          color="tertiary-container"
          variant="elevated"
          elevation="2"
        >
          <div class="stats-icon-wrapper mb-6">
            <v-icon icon="mdi-calendar-week" size="56" class="stats-icon" />
          </div>
          <div class="text-display-small font-weight-medium mb-3 text-on-tertiary-container">
            {{ appStore.systemStats.weekProjects }}
          </div>
          <div class="text-title-medium font-weight-medium mb-2 text-on-tertiary-container">本周新增</div>
          <div class="text-body-medium text-on-tertiary-container opacity-80">本周爬取项目</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card
          class="text-center stats-card interactive-hover responsive-spacing"
          color="surface-container-high"
          variant="elevated"
          elevation="2"
        >
          <div class="stats-icon-wrapper mb-6">
            <v-icon icon="mdi-cog" size="56" class="stats-icon" />
          </div>
          <div class="text-display-small font-weight-medium mb-3 text-on-surface">
            {{ appStore.systemStats.activeTasks }}
          </div>
          <div class="text-title-medium font-weight-medium mb-2 text-on-surface">活跃任务</div>
          <div class="text-body-medium text-on-surface-variant">正在运行任务</div>
        </v-card>
      </v-col>

      <!-- 超大屏幕额外统计卡片 -->
      <v-col cols="12" sm="6" md="6" xl="6" xxl="2" class="d-none d-xxl-flex">
        <v-card
          class="text-center stats-card interactive-hover responsive-spacing"
          color="error-container"
          variant="elevated"
          elevation="2"
        >
          <div class="stats-icon-wrapper mb-6">
            <v-icon icon="mdi-chart-line" size="56" class="stats-icon" />
          </div>
          <div class="text-display-small font-weight-medium mb-3 text-on-error-container">
            {{ Math.round((appStore.systemStats.todayProjects / appStore.systemStats.totalProjects) * 100) || 0 }}%
          </div>
          <div class="text-title-medium font-weight-medium mb-2 text-on-error-container">增长率</div>
          <div class="text-body-medium text-on-error-container opacity-80">今日增长比例</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="6" xl="6" xxl="2" class="d-none d-xxl-flex">
        <v-card
          class="text-center stats-card interactive-hover responsive-spacing"
          color="surface-container"
          variant="elevated"
          elevation="2"
        >
          <div class="stats-icon-wrapper mb-6">
            <v-icon icon="mdi-trending-up" size="56" class="stats-icon" />
          </div>
          <div class="text-display-small font-weight-medium mb-3 text-on-surface">
            {{ Math.round(appStore.systemStats.weekProjects / 7) || 0 }}
          </div>
          <div class="text-title-medium font-weight-medium mb-2 text-on-surface">日均新增</div>
          <div class="text-body-medium text-on-surface-variant">本周平均值</div>
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
      <v-col cols="12" md="4" lg="4" xl="3" xxl="3">
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
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()



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
.title-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(var(--v-theme-primary), 0.1) 0%, rgba(var(--v-theme-primary), 0.2) 100%);
  border: 1px solid rgba(var(--v-theme-primary), 0.2);
}

.stats-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(var(--v-theme-outline-variant), 0.2);

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0px 8px 24px 4px rgba(0, 0, 0, 0.12), 0px 4px 8px 0px rgba(0, 0, 0, 0.14);
  }
}

.stats-icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 96px;
  height: 96px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.25) 100%);
  backdrop-filter: blur(10px);
  margin: 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stats-icon {
  opacity: 0.95;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}



/* M3 响应式优化 */
/* 超大屏幕：最高信息密度 */
@media (min-width: 2560px) {
  .stats-card {
    padding: 32px 24px !important;
  }

  .stats-icon-wrapper {
    width: 88px;
    height: 88px;
    border-radius: 22px;
  }



  .title-icon-container {
    width: 72px;
    height: 72px;
    border-radius: 18px;
  }
}

/* 超大屏幕：高信息密度 */
@media (min-width: 1920px) and (max-width: 2559px) {
  .stats-card {
    padding: 28px 20px !important;
  }

  .stats-icon-wrapper {
    width: 84px;
    height: 84px;
    border-radius: 21px;
  }



  .title-icon-container {
    width: 68px;
    height: 68px;
    border-radius: 17px;
  }
}

/* 大屏幕：标准信息密度 */
@media (min-width: 1264px) and (max-width: 1919px) {
  .stats-card {
    padding: 24px 18px !important;
  }

  .stats-icon-wrapper {
    width: 80px;
    height: 80px;
    border-radius: 20px;
  }


}

/* 中等屏幕：适中信息密度 */
@media (min-width: 960px) and (max-width: 1263px) {
  .stats-card {
    padding: 20px 16px !important;
  }

  .stats-icon-wrapper {
    width: 76px;
    height: 76px;
    border-radius: 19px;
  }


}

/* 平板：舒适间距 */
@media (min-width: 600px) and (max-width: 959px) {
  .stats-card {
    padding: 20px 16px !important;
  }

  .stats-icon-wrapper {
    width: 72px;
    height: 72px;
    border-radius: 18px;
  }


}

/* 手机：大间距 */
@media (max-width: 599px) {
  .title-icon-container {
    width: 56px;
    height: 56px;
    border-radius: 14px;
  }

  .stats-card {
    padding: 16px 12px !important;
  }

  .stats-icon-wrapper {
    width: 64px;
    height: 64px;
    border-radius: 16px;
  }


}
</style>