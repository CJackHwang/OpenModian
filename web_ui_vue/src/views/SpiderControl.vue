<template>
  <div>
    <!-- 页面标题 -->
    <div class="q-mb-lg">
      <h1 class="text-h4 text-weight-bold text-primary q-mb-sm">
        <q-icon name="bug_report" class="q-mr-sm" />
        爬虫控制
      </h1>
      <p class="text-subtitle1 text-grey-7">
        配置和管理爬虫任务
      </p>
    </div>

    <!-- 临时内容 -->
    <q-card>
      <q-card-section>
        <div class="text-h6">爬虫控制面板</div>
        <p>此页面正在开发中，请稍后...</p>
      </q-card-section>
    </q-card>

    <v-row>
      <!-- 左侧配置面板 -->
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-cog</v-icon>
            爬虫配置
          </v-card-title>
          
          <v-card-text>
            <v-form ref="configForm" v-model="formValid">
              <!-- 页面范围 -->
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="config.startPage"
                    label="起始页"
                    type="number"
                    :rules="[rules.required, rules.minPage]"
                    min="1"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="config.endPage"
                    label="结束页"
                    type="number"
                    :rules="[rules.required, rules.maxPage]"
                    min="1"
                  />
                </v-col>
              </v-row>

              <!-- 项目分类 -->
              <v-select
                v-model="config.category"
                :items="categories"
                item-title="label"
                item-value="value"
                label="项目分类"
                :rules="[rules.required]"
              />

              <!-- 并发设置 -->
              <v-text-field
                v-model.number="config.maxConcurrent"
                label="最大并发数"
                type="number"
                :rules="[rules.required, rules.concurrent]"
                min="1"
                max="10"
                hint="建议1-5，过高可能被封IP"
                persistent-hint
              />

              <!-- 延迟设置 -->
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="config.delayMin"
                    label="最小延迟(秒)"
                    type="number"
                    :rules="[rules.required, rules.delay]"
                    min="0.5"
                    step="0.1"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="config.delayMax"
                    label="最大延迟(秒)"
                    type="number"
                    :rules="[rules.required, rules.delayMax]"
                    min="0.5"
                    step="0.1"
                  />
                </v-col>
              </v-row>

              <!-- 操作按钮 -->
              <div class="d-flex flex-column ga-3 mt-4">
                <v-btn
                  color="success"
                  size="large"
                  :disabled="!formValid || isTaskRunning"
                  :loading="appStore.loading"
                  @click="startCrawl"
                  prepend-icon="mdi-play"
                >
                  {{ isTaskRunning ? '运行中...' : '开始爬取' }}
                </v-btn>
                
                <v-btn
                  color="error"
                  variant="outlined"
                  :disabled="!isTaskRunning"
                  @click="stopCrawl"
                  prepend-icon="mdi-stop"
                >
                  停止爬取
                </v-btn>
                
                <v-btn
                  variant="outlined"
                  @click="resetConfig"
                  prepend-icon="mdi-refresh"
                >
                  重置配置
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 右侧监控面板 -->
      <v-col cols="12" lg="8">
        <!-- 当前任务状态 -->
        <v-card class="mb-4" v-if="appStore.currentTask.id">
          <v-card-title class="d-flex align-center">
            <v-icon class="me-2">mdi-monitor</v-icon>
            当前任务
            <v-spacer />
            <v-chip
              :color="getTaskStatusColor(appStore.currentTask.status)"
              variant="flat"
            >
              {{ getTaskStatusText(appStore.currentTask.status) }}
            </v-chip>
          </v-card-title>
          
          <v-card-text>
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
                striped
              />
            </div>

            <!-- 统计信息 -->
            <v-row class="text-center">
              <v-col cols="3">
                <v-card variant="tonal" color="primary" class="pa-3">
                  <div class="text-h5 font-weight-bold">{{ appStore.currentTask.stats.pagesCrawled }}</div>
                  <div class="text-caption">已爬页面</div>
                </v-card>
              </v-col>
              <v-col cols="3">
                <v-card variant="tonal" color="success" class="pa-3">
                  <div class="text-h5 font-weight-bold">{{ appStore.currentTask.stats.projectsFound }}</div>
                  <div class="text-caption">发现项目</div>
                </v-card>
              </v-col>
              <v-col cols="3">
                <v-card variant="tonal" color="info" class="pa-3">
                  <div class="text-h5 font-weight-bold">{{ appStore.currentTask.stats.projectsProcessed }}</div>
                  <div class="text-caption">已处理</div>
                </v-card>
              </v-col>
              <v-col cols="3">
                <v-card variant="tonal" color="error" class="pa-3">
                  <div class="text-h5 font-weight-bold">{{ appStore.currentTask.stats.errors }}</div>
                  <div class="text-caption">错误数</div>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 实时日志 -->
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="me-2">mdi-console-line</v-icon>
            实时日志
            <v-spacer />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              @click="clearLogs"
            />
          </v-card-title>
          
          <v-card-text class="pa-0">
            <div class="log-container" ref="logContainer">
              <div v-if="appStore.currentTask.logs.length === 0" class="text-center pa-4 text-medium-emphasis">
                <v-icon size="48" class="mb-2">mdi-console</v-icon>
                <div>等待任务开始...</div>
              </div>
              <div
                v-for="(log, index) in appStore.currentTask.logs"
                :key="index"
                :class="['log-entry', `log-${log.level}`]"
              >
                <span class="log-timestamp">[{{ log.timestamp }}]</span>
                <span class="log-level">[{{ log.level.toUpperCase() }}]</span>
                <span class="log-message">{{ log.message }}</span>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 响应式数据
const configForm = ref(null)
const formValid = ref(false)
const logContainer = ref(null)

const config = reactive({
  startPage: 1,
  endPage: 10,
  category: 'all',
  maxConcurrent: 3,
  delayMin: 1,
  delayMax: 3
})

const categories = [
  { value: 'all', label: '全部分类' },
  { value: 'games', label: '游戏' },
  { value: 'publishing', label: '出版' },
  { value: 'tablegames', label: '桌游' },
  { value: 'toys', label: '潮玩模型' },
  { value: 'cards', label: '卡牌' },
  { value: 'technology', label: '科技' },
  { value: 'film-video', label: '影视' },
  { value: 'music', label: '音乐' },
  { value: 'activities', label: '活动' },
  { value: 'design', label: '设计' },
  { value: 'curio', label: '文玩' },
  { value: 'home', label: '家居' },
  { value: 'food', label: '食品' },
  { value: 'comics', label: '动漫' },
  { value: 'charity', label: '爱心通道' },
  { value: 'animals', label: '动物救助' },
  { value: 'wishes', label: '个人愿望' },
  { value: 'others', label: '其他' }
]

// 表单验证规则
const rules = {
  required: value => !!value || '此字段为必填项',
  minPage: value => value >= 1 || '起始页必须大于等于1',
  maxPage: value => value >= config.startPage || '结束页必须大于等于起始页',
  concurrent: value => value >= 1 && value <= 10 || '并发数必须在1-10之间',
  delay: value => value >= 0.5 || '延迟时间必须大于等于0.5秒',
  delayMax: value => value >= config.delayMin || '最大延迟必须大于等于最小延迟'
}

// 计算属性
const isTaskRunning = computed(() => {
  return appStore.currentTask.status === 'running' || appStore.currentTask.status === 'starting'
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

const startCrawl = async () => {
  if (!formValid.value) return

  const result = await appStore.startCrawlTask({
    start_page: config.startPage,
    end_page: config.endPage,
    category: config.category,
    max_concurrent: config.maxConcurrent,
    delay_min: config.delayMin,
    delay_max: config.delayMax
  })

  if (result.success) {
    // 任务启动成功的处理
  } else {
    // 错误处理
    console.error('启动任务失败:', result.message)
  }
}

const stopCrawl = async () => {
  if (!appStore.currentTask.id) return

  const result = await appStore.stopCrawlTask(appStore.currentTask.id)
  
  if (result.success) {
    // 任务停止成功的处理
  } else {
    // 错误处理
    console.error('停止任务失败:', result.message)
  }
}

const resetConfig = () => {
  config.startPage = 1
  config.endPage = 10
  config.category = 'all'
  config.maxConcurrent = 3
  config.delayMin = 1
  config.delayMax = 3
}

const clearLogs = () => {
  appStore.currentTask.logs = []
}

// 监听日志变化，自动滚动到底部
watch(() => appStore.currentTask.logs, () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}, { deep: true })

// 生命周期
onMounted(() => {
  appStore.refreshData()
})
</script>

<style scoped>
.log-container {
  height: 400px;
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
  word-wrap: break-word;
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
  margin-right: 0.5rem;
}

.log-level {
  color: #81c784;
  font-weight: bold;
  margin-right: 0.5rem;
}

.log-message {
  color: #e0e0e0;
}
</style>
