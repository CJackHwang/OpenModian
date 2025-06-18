<template>
  <div>
    <!-- 页面标题 - M3风格 -->
    <v-row class="mb-8">
      <v-col>
        <div class="d-flex align-center mb-4">
          <div class="title-icon-container me-4">
            <v-icon icon="mdi-database" size="32" />
          </div>
          <div>
            <h1 class="text-headline-large font-weight-medium text-primary mb-1">
              数据管理
            </h1>
            <p class="text-body-large text-on-surface-variant">
              查看、搜索和管理爬取的项目数据
            </p>
          </div>
        </div>
      </v-col>
      <v-col cols="auto" class="d-flex align-center gap-3">
        <v-btn
          color="primary"
          prepend-icon="mdi-download"
          @click="exportData"
          :loading="exporting"
          variant="elevated"
          size="large"
          class="elevation-2"
        >
          导出数据
        </v-btn>
        <v-btn
          color="secondary"
          prepend-icon="mdi-refresh"
          @click="refreshData"
          :loading="loading"
          variant="elevated"
          size="large"
          class="elevation-2"
        >
          刷新
        </v-btn>
      </v-col>
    </v-row>

    <!-- 数据统计 - M3风格响应式 -->
    <v-row class="mb-8 responsive-spacing">
      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card class="text-center stats-card interactive-hover responsive-spacing" color="primary-container" elevation="2">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-database" size="40" />
          </div>
          <div class="text-headline-medium font-weight-medium mb-2 text-on-primary-container">{{ stats.total }}</div>
          <div class="text-body-medium text-on-primary-container opacity-80">总项目数</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card class="text-center stats-card interactive-hover responsive-spacing" color="secondary-container" elevation="2">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-calendar-today" size="40" />
          </div>
          <div class="text-headline-medium font-weight-medium mb-2 text-on-secondary-container">{{ stats.today }}</div>
          <div class="text-body-medium text-on-secondary-container opacity-80">今日新增</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card class="text-center stats-card interactive-hover responsive-spacing" color="tertiary-container" elevation="2">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-calendar-week" size="40" />
          </div>
          <div class="text-headline-medium font-weight-medium mb-2 text-on-tertiary-container">{{ stats.week }}</div>
          <div class="text-body-medium text-on-tertiary-container opacity-80">本周新增</div>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3" xl="3" xxl="2">
        <v-card class="text-center stats-card interactive-hover responsive-spacing" color="surface-container-high" elevation="2">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-currency-cny" size="40" />
          </div>
          <div class="text-headline-medium font-weight-medium mb-2 text-on-surface">{{ formatCurrency(stats.totalAmount) }}</div>
          <div class="text-body-medium text-on-surface-variant">总筹款金额</div>
        </v-card>
      </v-col>

      <!-- 超大屏幕额外统计 -->
      <v-col cols="12" sm="6" md="6" xl="6" xxl="2" class="d-none d-xxl-flex">
        <v-card class="text-center stats-card interactive-hover responsive-spacing" color="error-container" elevation="2">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-percent" size="40" />
          </div>
          <div class="text-headline-medium font-weight-medium mb-2 text-on-error-container">
            {{ Math.round((stats.today / Math.max(stats.total, 1)) * 100) }}%
          </div>
          <div class="text-body-medium text-on-error-container opacity-80">今日占比</div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="6" xl="6" xxl="2" class="d-none d-xxl-flex">
        <v-card class="text-center stats-card interactive-hover responsive-spacing" color="surface-container" elevation="2">
          <div class="stats-icon-wrapper mb-4">
            <v-icon icon="mdi-chart-timeline-variant" size="40" />
          </div>
          <div class="text-headline-medium font-weight-medium mb-2 text-on-surface">
            {{ Math.round(stats.week / 7) }}
          </div>
          <div class="text-body-medium text-on-surface-variant">日均新增</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 选项卡导航 -->
    <v-card elevation="2" class="mb-6">
      <v-tabs
        v-model="activeTab"
        color="primary"
        align-tabs="start"
      >
        <v-tab value="data">
          <v-icon icon="mdi-table" class="me-2" />
          数据查看
        </v-tab>
        <v-tab value="backup">
          <v-icon icon="mdi-backup-restore" class="me-2" />
          备份管理
        </v-tab>
      </v-tabs>
    </v-card>

    <!-- 选项卡内容 -->
    <v-window v-model="activeTab">
      <!-- 数据查看选项卡 -->
      <v-window-item value="data">
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
                v-if="isValidImageUrl(item.author_image)"
                :src="item.author_image"
                :alt="item.author_name"
              >
                <template v-slot:error>
                  <v-icon icon="mdi-account" size="16" />
                </template>
              </v-img>
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
      </v-window-item>

      <!-- 备份管理选项卡 -->
      <v-window-item value="backup">
        <BackupManager />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import BackupManager from '@/components/BackupManager.vue'
import { isValidImageUrl } from '@/utils/imageUtils'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const exporting = ref(false)
const projects = ref([])
const itemsPerPage = ref(25)
const activeTab = ref('data')

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

// 表格列定义 - 响应式
const headers = [
  {
    title: '项目名称',
    key: 'project_name',
    sortable: true,
    width: '250px',
    class: 'text-left'
  },
  {
    title: '分类',
    key: 'category',
    sortable: true,
    width: '100px',
    class: 'd-none d-md-table-cell'
  },
  {
    title: '作者',
    key: 'author_name',
    sortable: true,
    width: '120px',
    class: 'd-none d-lg-table-cell'
  },
  {
    title: '筹款金额',
    key: 'raised_amount',
    sortable: true,
    width: '130px',
    class: 'text-right'
  },
  {
    title: '支持者',
    key: 'backer_count',
    sortable: true,
    width: '80px',
    class: 'd-none d-sm-table-cell text-center'
  },
  {
    title: '评论数',
    key: 'comment_count',
    sortable: true,
    width: '80px',
    class: 'd-none d-md-table-cell text-center'
  },
  {
    title: '看好数',
    key: 'supporter_count',
    sortable: true,
    width: '80px',
    class: 'd-none d-lg-table-cell text-center'
  },
  {
    title: '状态',
    key: 'project_status',
    sortable: true,
    width: '100px',
    class: 'd-none d-md-table-cell text-center'
  },
  {
    title: '爬取时间',
    key: 'crawl_time',
    sortable: true,
    width: '150px',
    class: 'd-none d-xl-table-cell text-center'
  }
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
    // 确保显示本地时间（GMT+8北京时间）
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Shanghai'  // 明确指定北京时区
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
    transform: translateY(-4px);
    box-shadow: 0px 6px 20px 2px rgba(0, 0, 0, 0.1), 0px 2px 6px 0px rgba(0, 0, 0, 0.12);
  }
}

.stats-icon-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.25) 100%);
  backdrop-filter: blur(8px);
  margin: 0 auto;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* M3 响应式优化 - 数据管理页面 */
/* 超大屏幕：最高信息密度 */
@media (min-width: 2560px) {
  .stats-card {
    padding: 32px 24px !important;
  }

  .stats-icon-wrapper {
    width: 80px;
    height: 80px;
    border-radius: 20px;
  }

  .title-icon-container {
    width: 72px;
    height: 72px;
    border-radius: 18px;
  }

  /* 表格在超大屏幕下显示更多列 */
  .v-data-table {
    font-size: 14px;
  }

  .v-data-table th,
  .v-data-table td {
    padding: 0 12px !important;
  }
}

/* 超大屏幕：高信息密度 */
@media (min-width: 1920px) and (max-width: 2559px) {
  .stats-card {
    padding: 28px 20px !important;
  }

  .stats-icon-wrapper {
    width: 76px;
    height: 76px;
    border-radius: 19px;
  }

  .title-icon-container {
    width: 68px;
    height: 68px;
    border-radius: 17px;
  }

  .v-data-table {
    font-size: 13px;
  }
}

/* 大屏幕：标准信息密度 */
@media (min-width: 1264px) and (max-width: 1919px) {
  .stats-card {
    padding: 24px 18px !important;
  }

  .stats-icon-wrapper {
    width: 72px;
    height: 72px;
    border-radius: 18px;
  }
}

/* 中等屏幕：适中信息密度 */
@media (min-width: 960px) and (max-width: 1263px) {
  .stats-card {
    padding: 20px 16px !important;
  }

  .stats-icon-wrapper {
    width: 68px;
    height: 68px;
    border-radius: 17px;
  }
}

/* 平板：舒适间距 */
@media (min-width: 600px) and (max-width: 959px) {
  .stats-card {
    padding: 20px 16px !important;
  }

  .stats-icon-wrapper {
    width: 64px;
    height: 64px;
    border-radius: 16px;
  }

  /* 平板下隐藏部分表格列 */
  .v-data-table .d-md-table-cell {
    display: none !important;
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
    width: 56px;
    height: 56px;
    border-radius: 14px;
  }

  /* 手机下只显示核心列 */
  .v-data-table .d-sm-table-cell {
    display: none !important;
  }

  .v-data-table {
    font-size: 12px;
  }

  .v-data-table th,
  .v-data-table td {
    padding: 0 8px !important;
  }
}
</style>