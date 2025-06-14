<template>
  <div>
    <!-- 页面标题 -->
    <div class="q-mb-lg">
      <h1 class="text-h4 text-weight-bold text-primary q-mb-sm">
        <q-icon name="dashboard" class="q-mr-sm" />
        仪表板
      </h1>
      <p class="text-subtitle1 text-grey-7">
        系统概览和实时状态监控
      </p>
    </div>

    <!-- 统计卡片 -->
    <div class="row q-gutter-md q-mb-xl">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="text-center q-pa-lg bg-primary text-white">
          <q-icon name="storage" size="48px" class="q-mb-md" />
          <div class="text-h4 text-weight-bold">{{ appStore.systemStats.totalProjects }}</div>
          <div class="text-subtitle2">总项目数</div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="text-center q-pa-lg bg-positive text-white">
          <q-icon name="today" size="48px" class="q-mb-md" />
          <div class="text-h4 text-weight-bold">{{ appStore.systemStats.todayProjects }}</div>
          <div class="text-subtitle2">今日新增</div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="text-center q-pa-lg bg-info text-white">
          <q-icon name="date_range" size="48px" class="q-mb-md" />
          <div class="text-h4 text-weight-bold">{{ appStore.systemStats.weekProjects }}</div>
          <div class="text-subtitle2">本周新增</div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card class="text-center q-pa-lg bg-warning text-white">
          <q-icon name="settings" size="48px" class="q-mb-md" />
          <div class="text-h4 text-weight-bold">{{ appStore.systemStats.activeTasks }}</div>
          <div class="text-subtitle2">活跃任务</div>
        </q-card>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="row q-gutter-md">
      <!-- 当前任务状态 -->
      <div class="col-12 col-lg-8">
        <q-card class="q-mb-md">
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">
                  <q-icon name="bug_report" class="q-mr-sm" />
                  当前任务状态
                </div>
              </div>
              <div class="col-auto">
                <q-chip
                  :color="getTaskStatusColor(appStore.currentTask.status)"
                  text-color="white"
                  :label="getTaskStatusText(appStore.currentTask.status)"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-section>
            <div v-if="appStore.currentTask.id">
              <!-- 进度条 -->
              <div class="q-mb-md">
                <div class="row justify-between q-mb-sm">
                  <span class="text-subtitle2">爬取进度</span>
                  <span class="text-subtitle2">{{ Math.round(appStore.currentTask.progress) }}%</span>
                </div>
                <q-linear-progress
                  :value="appStore.currentTask.progress / 100"
                  size="12px"
                  color="primary"
                  rounded
                />
              </div>

              <!-- 统计信息 -->
              <div class="row text-center q-gutter-md">
                <div class="col">
                  <div class="text-h6 text-weight-bold text-primary">
                    {{ appStore.currentTask.stats.pagesCrawled }}
                  </div>
                  <div class="text-caption text-grey-7">已爬页面</div>
                </div>
                <div class="col">
                  <div class="text-h6 text-weight-bold text-positive">
                    {{ appStore.currentTask.stats.projectsFound }}
                  </div>
                  <div class="text-caption text-grey-7">发现项目</div>
                </div>
                <div class="col">
                  <div class="text-h6 text-weight-bold text-info">
                    {{ appStore.currentTask.stats.projectsProcessed }}
                  </div>
                  <div class="text-caption text-grey-7">已处理</div>
                </div>
                <div class="col">
                  <div class="text-h6 text-weight-bold text-negative">
                    {{ appStore.currentTask.stats.errors }}
                  </div>
                  <div class="text-caption text-grey-7">错误数</div>
                </div>
              </div>
            </div>

            <div v-else class="text-center q-py-xl text-grey-7">
              <q-icon name="bedtime" size="64px" class="q-mb-md" />
              <div class="text-h6">暂无活跃任务</div>
              <div class="text-subtitle2">点击"爬虫控制"开始新任务</div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 实时日志 -->
        <q-card>
          <q-card-section>
            <div class="row items-center">
              <div class="col">
                <div class="text-h6">
                  <q-icon name="terminal" class="q-mr-sm" />
                  实时日志
                </div>
              </div>
              <div class="col-auto">
                <q-btn
                  icon="delete"
                  flat
                  round
                  size="sm"
                  @click="clearLogs"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-section class="q-pa-none">
            <div class="log-container">
              <div v-if="appStore.currentTask.logs.length === 0" class="text-center q-pa-md text-grey-7">
                暂无日志信息
              </div>
              <div
                v-for="(log, index) in appStore.currentTask.logs"
                :key="index"
                :class="['log-entry', `log-${log.level}`]"
              >
                <span class="log-timestamp">[{{ log.timestamp }}]</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 侧边栏信息 -->
      <div class="col-12 col-lg-4">
        <!-- 任务统计 -->
        <q-card class="q-mb-md">
          <q-card-section>
            <div class="text-h6">
              <q-icon name="pie_chart" class="q-mr-sm" />
              任务统计
            </div>
          </q-card-section>

          <q-card-section>
            <div class="row justify-between items-center q-mb-sm">
              <span>活跃任务</span>
              <q-chip color="positive" text-color="white" :label="appStore.systemStats.activeTasks" />
            </div>
            <div class="row justify-between items-center q-mb-sm">
              <span>已完成</span>
              <q-chip color="primary" text-color="white" :label="appStore.systemStats.completedTasks" />
            </div>
            <div class="row justify-between items-center">
              <span>失败任务</span>
              <q-chip color="negative" text-color="white" :label="appStore.systemStats.failedTasks" />
            </div>
          </q-card-section>
        </q-card>

        <!-- 快速操作 -->
        <q-card>
          <q-card-section>
            <div class="text-h6">
              <q-icon name="flash_on" class="q-mr-sm" />
              快速操作
            </div>
          </q-card-section>

          <q-card-section>
            <q-btn
              unelevated
              color="primary"
              class="full-width q-mb-sm"
              icon="play_arrow"
              label="开始新任务"
              @click="$router.push('/spider')"
            />

            <q-btn
              unelevated
              color="secondary"
              class="full-width q-mb-sm"
              icon="storage"
              label="查看数据"
              @click="$router.push('/data')"
            />

            <q-btn
              outline
              color="primary"
              class="full-width"
              icon="refresh"
              label="刷新数据"
              @click="refreshData"
              :loading="appStore.loading"
            />
          </q-card-section>
        </q-card>
      </div>
    </div>
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
    'running': 'positive',
    'completed': 'primary',
    'failed': 'negative',
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

const clearLogs = () => {
  appStore.currentTask.logs = []
}

const refreshData = () => {
  appStore.refreshData()
}

// 生命周期
onMounted(() => {
  appStore.refreshData()
})
</script>

<style scoped>
.log-container {
  height: 300px;
  overflow-y: auto;
  background-color: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  padding: 1rem;
}

.log-entry {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border-left: 3px solid transparent;
}

.log-entry.log-info {
  border-left-color: #2196f3;
  background-color: rgba(33, 150, 243, 0.1);
}

.log-entry.log-success {
  border-left-color: #4caf50;
  background-color: rgba(76, 175, 80, 0.1);
}

.log-entry.log-warning {
  border-left-color: #ffc107;
  background-color: rgba(255, 193, 7, 0.1);
}

.log-entry.log-error {
  border-left-color: #f44336;
  background-color: rgba(244, 67, 54, 0.1);
}

.log-timestamp {
  color: #9e9e9e;
  font-size: 0.8rem;
}
</style>
