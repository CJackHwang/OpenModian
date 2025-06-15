<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          <v-icon icon="mdi-database" class="me-3" size="large" />
          数据管理
        </h1>
        <p class="text-h6 text-medium-emphasis">
          查看、搜索和管理爬取的项目数据
        </p>
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="primary"
          prepend-icon="mdi-download"
          @click="exportData"
          :loading="exporting"
          variant="elevated"
          class="me-2"
        >
          导出数据
        </v-btn>
        <v-btn
          color="secondary"
          prepend-icon="mdi-refresh"
          @click="refreshData"
          :loading="loading"
          variant="elevated"
        >
          刷新
        </v-btn>
      </v-col>
    </v-row>

    <!-- 数据统计 -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4" color="primary-container" elevation="2">
          <v-icon icon="mdi-database" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">{{ stats.total }}</div>
          <div class="text-caption">总项目数</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4" color="secondary-container" elevation="2">
          <v-icon icon="mdi-calendar-today" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">{{ stats.today }}</div>
          <div class="text-caption">今日新增</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4" color="tertiary-container" elevation="2">
          <v-icon icon="mdi-calendar-week" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">{{ stats.week }}</div>
          <div class="text-caption">本周新增</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center pa-4" color="surface-variant" elevation="2">
          <v-icon icon="mdi-currency-cny" size="32" class="mb-2" />
          <div class="text-h6 font-weight-bold">{{ formatCurrency(stats.totalAmount) }}</div>
          <div class="text-caption">总筹款金额</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 筛选和搜索 -->
    <v-card elevation="2" class="mb-6">
      <v-card-title>
        <v-icon icon="mdi-filter" class="me-3" />
        数据筛选
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.period"
              :items="periodOptions"
              label="时间范围"
              variant="outlined"
              density="compact"
              @update:model-value="applyFilters"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.category"
              :items="categoryOptions"
              label="项目分类"
              variant="outlined"
              density="compact"
              @update:model-value="applyFilters"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="filters.search"
              label="搜索项目名称"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              @update:model-value="debounceSearch"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              block
              color="primary"
              @click="applyFilters"
              :loading="loading"
            >
              搜索
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 数据表格 -->
    <v-card elevation="2">
      <v-card-title>
        <v-icon icon="mdi-table" class="me-3" />
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
        class="elevation-0"
        item-value="id"
      >
        <!-- 项目名称列 -->
        <template #item.project_name="{ item }">
          <div class="d-flex align-center">
            <div>
              <v-btn
                variant="text"
                color="primary"
                class="text-left pa-0 font-weight-medium"
                style="text-transform: none; justify-content: flex-start;"
                @click="goToProjectDetail(item.project_id)"
              >
                {{ item.project_name || '未知项目' }}
              </v-btn>
              <div class="text-caption text-medium-emphasis">
                ID: {{ item.project_id || '-' }}
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
            {{ getCategoryDisplayName(item.category) }}
          </v-chip>
        </template>

        <!-- 作者列 -->
        <template #item.author_name="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="24" class="me-2">
              <v-img
                v-if="item.author_image"
                :src="item.author_image"
                :alt="item.author_name"
              />
              <v-icon v-else icon="mdi-account" size="16" />
            </v-avatar>
            <span class="text-truncate">{{ item.author_name || '未知作者' }}</span>
          </div>
        </template>

        <!-- 金额列 -->
        <template #item.raised_amount="{ item }">
          <div class="text-right">
            <div class="font-weight-bold text-success">
              ¥{{ formatNumber(item.raised_amount || 0) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              目标: ¥{{ formatNumber(item.target_amount || 0) }}
            </div>
            <div class="text-caption" :class="getCompletionColor(item.completion_rate)">
              {{ formatPercentage(item.completion_rate) }}
            </div>
          </div>
        </template>

        <!-- 支持者数列 -->
        <template #item.backer_count="{ item }">
          <div class="text-center">
            <v-chip size="small" color="primary" variant="tonal">
              {{ formatNumber(item.backer_count || 0) }}
            </v-chip>
          </div>
        </template>

        <!-- 评论数列 -->
        <template #item.comment_count="{ item }">
          <div class="text-center">
            <v-chip size="small" color="info" variant="tonal">
              {{ formatNumber(item.comment_count || 0) }}
            </v-chip>
          </div>
        </template>

        <!-- 看好数列 -->
        <template #item.supporter_count="{ item }">
          <div class="text-center">
            <v-chip size="small" color="success" variant="tonal">
              {{ formatNumber(item.supporter_count || 0) }}
            </v-chip>
          </div>
        </template>

        <!-- 状态列 -->
        <template #item.project_status="{ item }">
          <v-chip
            size="small"
            :color="getStatusColor(item.project_status)"
            variant="tonal"
          >
            {{ getStatusText(item.project_status) }}
          </v-chip>
        </template>

        <!-- 爬取时间列 -->
        <template #item.crawl_time="{ item }">
          <div class="text-caption">
            {{ formatDateTime(item.crawl_time) }}
          </div>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const projects = ref([])
const itemsPerPage = ref(25)

const stats = reactive({
  total: 0,
  today: 0,
  week: 0,
  totalAmount: 0
})

const filters = reactive({
  period: 'all',
  category: 'all',
  search: ''
})

// 选项数据
const periodOptions = [
  { value: 'all', title: '全部时间' },
  { value: 'today', title: '今天' },
  { value: 'week', title: '本周' },
  { value: 'month', title: '本月' }
]

const categoryOptions = [
  { value: 'all', title: '全部分类' },
  { value: 'games', title: '游戏' },
  { value: 'publishing', title: '出版' },
  { value: 'tablegames', title: '桌游' },
  { value: 'toys', title: '潮玩模型' },
  { value: 'cards', title: '卡牌' },
  { value: 'technology', title: '科技' },
  { value: 'film-video', title: '影视' },
  { value: 'music', title: '音乐' },
  { value: 'activities', title: '活动' },
  { value: 'design', title: '设计' },
  { value: 'curio', title: '文玩' },
  { value: 'home', title: '家居' },
  { value: 'food', title: '食品' },
  { value: 'comics', title: '动漫' },
  { value: 'charity', title: '爱心通道' },
  { value: 'animals', title: '动物救助' },
  { value: 'wishes', title: '个人愿望' },
  { value: 'others', title: '其他' }
]

// 分类显示名称映射
const categoryDisplayNames = {
  'games': '游戏',
  'publishing': '出版',
  'tablegames': '桌游',
  'toys': '潮玩模型',
  'cards': '卡牌',
  'technology': '科技',
  'film-video': '影视',
  'music': '音乐',
  'activities': '活动',
  'design': '设计',
  'curio': '文玩',
  'home': '家居',
  'food': '食品',
  'comics': '动漫',
  'charity': '爱心通道',
  'animals': '动物救助',
  'wishes': '个人愿望',
  'others': '其他',
  // 支持中文分类（向后兼容）
  '桌游': '桌游',
  '游戏': '游戏',
  '出版': '出版',
  '潮玩模型': '潮玩模型',
  '卡牌': '卡牌',
  '科技': '科技',
  '影视': '影视',
  '音乐': '音乐',
  '活动': '活动',
  '设计': '设计',
  '文玩': '文玩',
  '家居': '家居',
  '食品': '食品',
  '动漫': '动漫',
  '爱心通道': '爱心通道',
  '动物救助': '动物救助',
  '个人愿望': '个人愿望'
}

// 表格列定义
const headers = [
  { title: '项目名称', key: 'project_name', sortable: true, width: '250px' },
  { title: '分类', key: 'category', sortable: true, width: '100px' },
  { title: '作者', key: 'author_name', sortable: true, width: '120px' },
  { title: '筹款金额', key: 'raised_amount', sortable: true, width: '130px' },
  { title: '支持者', key: 'backer_count', sortable: true, width: '80px' },
  { title: '评论数', key: 'comment_count', sortable: true, width: '80px' },
  { title: '看好数', key: 'supporter_count', sortable: true, width: '80px' },
  { title: '状态', key: 'project_status', sortable: true, width: '100px' },
  { title: '爬取时间', key: 'crawl_time', sortable: true, width: '150px' }
]

// 计算属性 - 现在主要用于显示，实际筛选通过API完成
const filteredProjects = computed(() => {
  // 如果有搜索条件，在前端进行实时搜索筛选
  if (filters.search) {
    return projects.value.filter(p =>
      p.project_name?.toLowerCase().includes(filters.search.toLowerCase())
    )
  }

  // 否则直接返回从API获取的数据
  return projects.value
})

// 方法
const refreshData = async () => {
  try {
    loading.value = true

    // 构建查询参数
    const params = new URLSearchParams({
      period: filters.period,
      limit: '1000'
    })

    // 添加分类筛选参数
    if (filters.category !== 'all') {
      params.append('category', filters.category)
    }

    // 加载项目数据
    const projectsResponse = await axios.get(`/api/database/projects?${params.toString()}`)
    if (projectsResponse.data.success) {
      projects.value = projectsResponse.data.projects || []
      console.log(`📊 加载项目数据: ${projects.value.length} 条，分类筛选: ${filters.category}`)
      if (projects.value.length > 0) {
        console.log('📊 前5个项目的分类:', projects.value.slice(0, 5).map(p => ({ name: p.project_name, category: p.category })))
      }
    }

    // 加载统计数据
    const statsResponse = await axios.get('/api/database/stats')
    if (statsResponse.data.success) {
      const data = statsResponse.data.stats
      stats.total = data.total_projects || 0
      stats.today = data.today_projects || 0
      stats.week = data.week_projects || 0
      stats.totalAmount = data.total_amount || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  // 重新加载数据以应用筛选条件
  refreshData()
}

const debounceSearch = (() => {
  let timeout
  return () => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      applyFilters()
    }, 300)
  }
})()

const exportData = async () => {
  try {
    exporting.value = true
    const url = `/api/database/export?period=${filters.period}&category=${filters.category}`
    const link = document.createElement('a')
    link.href = url
    link.download = `modian_data_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('导出失败:', error)
  } finally {
    exporting.value = false
  }
}

const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatCurrency = (num) => {
  if (!num) return '¥0'
  return '¥' + new Intl.NumberFormat('zh-CN').format(num)
}

const getCategoryColor = (category) => {
  const colors = {
    'games': 'purple',
    'publishing': 'blue',
    'tablegames': 'green',
    'toys': 'orange',
    'cards': 'red',
    'technology': 'cyan',
    '桌游': 'green',
    '游戏': 'purple',
    '出版': 'blue',
    '潮玩模型': 'orange',
    '卡牌': 'red',
    '科技': 'cyan'
  }
  return colors[category] || 'grey'
}

const getCategoryDisplayName = (category) => {
  return categoryDisplayNames[category] || category || '未知分类'
}

const getStatusColor = (status) => {
  const colors = {
    'active': 'success',
    'completed': 'primary',
    'failed': 'error',
    'cancelled': 'warning',
    '进行中': 'success',
    '已完成': 'primary',
    '失败': 'error',
    '已取消': 'warning'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    'active': '进行中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return texts[status] || status || '未知'
}

const getCompletionColor = (rate) => {
  if (!rate) return 'text-medium-emphasis'
  const percentage = parseFloat(rate)
  if (percentage >= 100) return 'text-success'
  if (percentage >= 50) return 'text-warning'
  return 'text-error'
}

const formatPercentage = (rate) => {
  if (!rate) return '0%'
  return `${parseFloat(rate).toFixed(1)}%`
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

const goToProjectDetail = (projectId) => {
  if (projectId) {
    router.push(`/projects/${projectId}`)
  }
}

// 监听筛选条件变化
watch([() => filters.category, () => filters.period], () => {
  console.log(`🔄 筛选条件变化: 分类=${filters.category}, 时间=${filters.period}`)
  applyFilters()
})

// 生命周期
onMounted(() => {
  refreshData()
})
</script>