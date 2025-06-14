<template>
  <div>
    <!-- 页面标题 -->
    <div class="q-mb-lg">
      <h1 class="text-h4 text-weight-bold text-primary q-mb-sm">
        <q-icon name="storage" class="q-mr-sm" />
        数据管理
      </h1>
      <p class="text-subtitle1 text-grey-7">
        查看、搜索和管理爬取的项目数据
      </p>
    </div>

    <!-- 临时内容 -->
    <q-card>
      <q-card-section>
        <div class="text-h6">数据管理面板</div>
        <p>此页面正在开发中，请稍后...</p>
      </q-card-section>
    </q-card>

    <!-- 数据统计卡片 -->
    <v-row class="mb-4">
      <v-col cols="12" sm="4">
        <v-card color="primary" variant="tonal" class="text-center pa-4">
          <v-icon size="40" class="mb-2">mdi-database</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.totalProjects }}</div>
          <div class="text-subtitle-2">总项目数</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card color="success" variant="tonal" class="text-center pa-4">
          <v-icon size="40" class="mb-2">mdi-calendar-today</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.todayProjects }}</div>
          <div class="text-subtitle-2">今日新增</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4">
        <v-card color="info" variant="tonal" class="text-center pa-4">
          <v-icon size="40" class="mb-2">mdi-calendar-week</v-icon>
          <div class="text-h5 font-weight-bold">{{ stats.weekProjects }}</div>
          <div class="text-subtitle-2">本周新增</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 数据操作工具栏 -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedPeriod"
              :items="timePeriods"
              item-title="label"
              item-value="value"
              label="时间范围"
              @update:model-value="loadData"
            />
          </v-col>
          
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              label="搜索项目"
              prepend-inner-icon="mdi-magnify"
              clearable
              @input="searchData"
            />
          </v-col>
          
          <v-col cols="12" md="2">
            <v-select
              v-model="selectedCategory"
              :items="categories"
              item-title="label"
              item-value="value"
              label="分类筛选"
              @update:model-value="filterData"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <div class="d-flex ga-2">
              <v-btn
                color="primary"
                prepend-icon="mdi-refresh"
                @click="refreshData"
                :loading="loading"
              >
                刷新
              </v-btn>
              
              <v-btn
                color="success"
                prepend-icon="mdi-download"
                @click="exportData"
              >
                导出
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 数据表格 -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2">mdi-table</v-icon>
        项目数据
        <v-spacer />
        <v-chip variant="outlined">
          共 {{ filteredProjects.length }} 条记录
        </v-chip>
      </v-card-title>
      
      <v-data-table
        :headers="headers"
        :items="filteredProjects"
        :loading="loading"
        :items-per-page="itemsPerPage"
        :search="searchQuery"
        class="elevation-0"
        item-value="id"
      >
        <!-- 项目名称列 -->
        <template #item.project_name="{ item }">
          <div class="d-flex align-center">
            <v-avatar
              v-if="item.project_image"
              size="32"
              class="me-3"
            >
              <v-img :src="item.project_image" />
            </v-avatar>
            <div>
              <div class="font-weight-medium">{{ item.project_name }}</div>
              <div class="text-caption text-medium-emphasis">
                ID: {{ item.project_id }}
              </div>
            </div>
          </div>
        </template>

        <!-- 分类列 -->
        <template #item.category="{ item }">
          <v-chip
            size="small"
            variant="tonal"
            :color="getCategoryColor(item.category)"
          >
            {{ item.category || '未知' }}
          </v-chip>
        </template>

        <!-- 金额列 -->
        <template #item.raised_amount="{ item }">
          <div class="text-right">
            <div class="font-weight-bold text-success">
              ¥{{ formatNumber(item.raised_amount) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              目标: ¥{{ formatNumber(item.target_amount) }}
            </div>
          </div>
        </template>

        <!-- 完成率列 -->
        <template #item.completion_rate="{ item }">
          <div class="text-center">
            <v-progress-circular
              :model-value="item.completion_rate"
              :color="getProgressColor(item.completion_rate)"
              size="40"
              width="4"
            >
              {{ Math.round(item.completion_rate) }}%
            </v-progress-circular>
          </div>
        </template>

        <!-- 支持者列 -->
        <template #item.backer_count="{ item }">
          <div class="text-center">
            <div class="font-weight-bold">{{ formatNumber(item.backer_count) }}</div>
            <div class="text-caption text-medium-emphasis">支持者</div>
          </div>
        </template>

        <!-- 互动数据列 -->
        <template #item.interactions="{ item }">
          <div class="text-center">
            <v-tooltip text="点赞数">
              <template #activator="{ props }">
                <v-chip
                  v-bind="props"
                  size="x-small"
                  variant="text"
                  prepend-icon="mdi-thumb-up"
                  class="ma-1"
                >
                  {{ item.supporter_count || 0 }}
                </v-chip>
              </template>
            </v-tooltip>
            
            <v-tooltip text="评论数">
              <template #activator="{ props }">
                <v-chip
                  v-bind="props"
                  size="x-small"
                  variant="text"
                  prepend-icon="mdi-comment"
                  class="ma-1"
                >
                  {{ item.comment_count || 0 }}
                </v-chip>
              </template>
            </v-tooltip>
          </div>
        </template>

        <!-- 爬取时间列 -->
        <template #item.crawl_time="{ item }">
          <div class="text-center">
            <div>{{ formatDate(item.crawl_time) }}</div>
            <div class="text-caption text-medium-emphasis">
              {{ formatTime(item.crawl_time) }}
            </div>
          </div>
        </template>

        <!-- 操作列 -->
        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn
              icon="mdi-open-in-new"
              size="small"
              variant="text"
              :href="item.project_url"
              target="_blank"
            />
            <v-btn
              icon="mdi-information"
              size="small"
              variant="text"
              @click="showProjectDetails(item)"
            />
          </div>
        </template>

        <!-- 加载状态 -->
        <template #loading>
          <v-skeleton-loader type="table-row@10" />
        </template>

        <!-- 无数据状态 -->
        <template #no-data>
          <div class="text-center pa-8">
            <v-icon size="64" class="mb-4 text-medium-emphasis">mdi-database-off</v-icon>
            <div class="text-h6 text-medium-emphasis">暂无数据</div>
            <div class="text-subtitle-2 text-medium-emphasis mb-4">
              请先运行爬虫任务获取数据
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

    <!-- 项目详情对话框 -->
    <v-dialog
      v-model="detailDialog"
      max-width="800"
      scrollable
    >
      <v-card v-if="selectedProject">
        <v-card-title class="d-flex align-center">
          <v-icon class="me-2">mdi-information</v-icon>
          项目详情
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="detailDialog = false"
          />
        </v-card-title>
        
        <v-card-text>
          <!-- 项目详情内容 -->
          <v-row>
            <v-col cols="12" md="4">
              <v-img
                v-if="selectedProject.project_image"
                :src="selectedProject.project_image"
                aspect-ratio="1"
                class="rounded"
              />
            </v-col>
            <v-col cols="12" md="8">
              <h3 class="text-h5 mb-2">{{ selectedProject.project_name }}</h3>
              <p class="text-subtitle-1 text-medium-emphasis mb-4">
                {{ selectedProject.category }}
              </p>
              
              <v-row>
                <v-col cols="6">
                  <div class="text-caption text-medium-emphasis">已筹金额</div>
                  <div class="text-h6 text-success">¥{{ formatNumber(selectedProject.raised_amount) }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-medium-emphasis">目标金额</div>
                  <div class="text-h6">¥{{ formatNumber(selectedProject.target_amount) }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-medium-emphasis">支持者数</div>
                  <div class="text-h6">{{ formatNumber(selectedProject.backer_count) }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption text-medium-emphasis">完成率</div>
                  <div class="text-h6">{{ Math.round(selectedProject.completion_rate) }}%</div>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="primary"
            :href="selectedProject.project_url"
            target="_blank"
            prepend-icon="mdi-open-in-new"
          >
            查看原页面
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import axios from 'axios'
import dayjs from 'dayjs'

const appStore = useAppStore()

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const selectedPeriod = ref('all')
const selectedCategory = ref('all')
const itemsPerPage = ref(25)
const detailDialog = ref(false)
const selectedProject = ref(null)

const projects = ref([])
const stats = reactive({
  totalProjects: 0,
  todayProjects: 0,
  weekProjects: 0
})

// 时间范围选项
const timePeriods = [
  { value: 'all', label: '全部时间' },
  { value: 'day', label: '今日' },
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' }
]

// 分类选项
const categories = [
  { value: 'all', label: '全部分类' },
  { value: 'games', label: '游戏' },
  { value: 'publishing', label: '出版' },
  { value: 'tablegames', label: '桌游' },
  { value: 'toys', label: '潮玩模型' },
  { value: 'cards', label: '卡牌' },
  { value: 'technology', label: '科技' },
  { value: 'others', label: '其他' }
]

// 表格列定义
const headers = [
  { title: '项目名称', key: 'project_name', sortable: true, width: '300px' },
  { title: '分类', key: 'category', sortable: true, width: '120px' },
  { title: '筹款金额', key: 'raised_amount', sortable: true, width: '150px' },
  { title: '完成率', key: 'completion_rate', sortable: true, width: '100px' },
  { title: '支持者', key: 'backer_count', sortable: true, width: '100px' },
  { title: '互动', key: 'interactions', sortable: false, width: '120px' },
  { title: '爬取时间', key: 'crawl_time', sortable: true, width: '150px' },
  { title: '操作', key: 'actions', sortable: false, width: '100px' }
]

// 计算属性
const filteredProjects = computed(() => {
  let filtered = projects.value

  // 分类筛选
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }

  return filtered
})

// 方法
const loadData = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/api/database/projects?period=${selectedPeriod.value}&limit=1000`)
    
    if (response.data.success) {
      projects.value = response.data.projects
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await axios.get('/api/database/stats')
    
    if (response.data.success) {
      const data = response.data.stats
      stats.totalProjects = data.total_projects || 0
      stats.todayProjects = data.today_projects || 0
      stats.weekProjects = data.week_projects || 0
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const refreshData = async () => {
  await Promise.all([loadData(), loadStats()])
}

const searchData = () => {
  // 搜索功能由 v-data-table 的 search 属性处理
}

const filterData = () => {
  // 筛选功能由计算属性处理
}

const exportData = async () => {
  try {
    const url = `/api/database/export?period=${selectedPeriod.value}`
    const link = document.createElement('a')
    link.href = url
    link.download = `modian_data_${selectedPeriod.value}_${dayjs().format('YYYY-MM-DD')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const showProjectDetails = (project) => {
  selectedProject.value = project
  detailDialog.value = true
}

const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatDate = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD')
}

const formatTime = (dateStr) => {
  return dayjs(dateStr).format('HH:mm:ss')
}

const getCategoryColor = (category) => {
  const colors = {
    'games': 'purple',
    'publishing': 'blue',
    'tablegames': 'green',
    'toys': 'orange',
    'cards': 'red',
    'technology': 'cyan'
  }
  return colors[category] || 'grey'
}

const getProgressColor = (progress) => {
  if (progress >= 100) return 'success'
  if (progress >= 80) return 'warning'
  if (progress >= 50) return 'info'
  return 'error'
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.v-data-table {
  border-radius: 8px;
}

.v-chip {
  font-size: 0.75rem;
}
</style>
