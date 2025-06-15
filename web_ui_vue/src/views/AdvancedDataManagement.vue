<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-6">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary mb-2">
          <v-icon icon="mdi-database-edit" class="me-3" size="large" />
          高级数据管理
        </h1>
        <p class="text-h6 text-medium-emphasis">
          SQL-like数据操作：查询、编辑、删除和批量管理
        </p>
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="success"
          prepend-icon="mdi-plus"
          @click="showAddDialog = true"
          variant="elevated"
          class="me-2"
        >
          新增项目
        </v-btn>
        <v-btn
          color="error"
          prepend-icon="mdi-delete-multiple"
          @click="batchDelete"
          :disabled="!selectedItems.length"
          variant="elevated"
          class="me-2"
        >
          批量删除 ({{ selectedItems.length }})
        </v-btn>
        <v-btn
          color="primary"
          prepend-icon="mdi-download"
          @click="exportData"
          :loading="exporting"
          variant="elevated"
        >
          导出数据
        </v-btn>
      </v-col>
    </v-row>

    <!-- 筛选模式切换 -->
    <v-card elevation="1" class="mb-4">
      <v-card-text class="py-2">
        <v-btn-toggle
          v-model="filterMode"
          color="primary"
          variant="outlined"
          divided
          @update:model-value="onFilterModeChange"
        >
          <v-btn value="simple">
            <v-icon icon="mdi-magnify" class="me-2" />
            简单搜索
          </v-btn>
          <v-btn value="advanced">
            <v-icon icon="mdi-filter-cog" class="me-2" />
            高级筛选
          </v-btn>
        </v-btn-toggle>
      </v-card-text>
    </v-card>

    <!-- 简单搜索面板 -->
    <v-card v-if="filterMode === 'simple'" elevation="2" class="mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon icon="mdi-database-search" class="me-3" />
        快速搜索
        <v-spacer />
        <v-btn
          icon="mdi-refresh"
          variant="text"
          @click="resetSearch"
          title="重置搜索"
        />
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchConditions.project_name"
              label="项目名称"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              hint="支持模糊搜索"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchConditions.author_name"
              label="作者名称"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              density="compact"
              clearable
              hint="支持模糊搜索"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="searchConditions.category"
              :items="categoryOptions"
              label="项目分类"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="3">
            <v-text-field
              v-model.number="searchConditions.min_amount"
              label="最小金额"
              type="number"
              prepend-inner-icon="mdi-currency-cny"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model.number="searchConditions.max_amount"
              label="最大金额"
              type="number"
              prepend-inner-icon="mdi-currency-cny"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="searchConditions.date_from"
              label="开始日期"
              type="date"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="searchConditions.date_to"
              label="结束日期"
              type="date"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="searchConditions.status"
              :items="statusOptions"
              label="项目状态"
              variant="outlined"
              density="compact"
              clearable
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="pagination.itemsPerPage"
              :items="[10, 25, 50, 100]"
              label="每页显示"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="4" class="d-flex align-center ga-2">
            <v-btn
              color="primary"
              prepend-icon="mdi-magnify"
              @click="searchProjects"
              :loading="loading"
              flex
            >
              搜索
            </v-btn>
            <v-btn
              color="secondary"
              prepend-icon="mdi-refresh"
              @click="resetSearch"
              :disabled="loading"
              variant="outlined"
              flex
            >
              重置
            </v-btn>
            <v-btn
              color="info"
              prepend-icon="mdi-view-list"
              @click="showAllProjects"
              :disabled="loading"
              variant="tonal"
              flex
            >
              显示全部
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 高级筛选构建器 -->
    <FilterBuilder
      v-if="filterMode === 'advanced'"
      :loading="loading"
      @apply-filters="onAdvancedFilters"
      @filters-changed="onFiltersChanged"
    />

    <!-- 筛选历史 -->
    <FilterHistory
      ref="filterHistoryRef"
      @apply-filter="onApplyHistoryFilter"
    />

    <!-- 数据表格 -->
    <v-card elevation="2">
      <v-card-title class="d-flex align-center">
        <v-icon icon="mdi-table-edit" class="me-3" />
        项目数据表
        <v-spacer />
        <v-chip variant="outlined" color="primary">
          共 {{ totalCount }} 条记录
        </v-chip>
      </v-card-title>

      <!-- 表格容器，支持水平滚动 -->
      <div class="table-container" style="overflow-x: auto; width: 100%;">
        <v-data-table
          v-model="selectedItems"
          :headers="headers"
          :items="projects"
          :loading="loading"
          :items-per-page="pagination.itemsPerPage"
          :page="pagination.page"
          :server-items-length="totalCount"
          class="elevation-0"
          item-value="id"
          show-select
          fixed-header
          :style="{ minWidth: '1200px' }"
          @update:page="onPageChange"
          @update:items-per-page="onItemsPerPageChange"
        >
        <!-- 项目名称列 -->
        <template #item.project_name="{ item }">
          <div class="d-flex align-center">
            <div>
              <div class="font-weight-medium">{{ item.project_name || '未知项目' }}</div>
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
            <v-avatar size="20" class="me-2">
              <v-img
                v-if="item.author_image"
                :src="item.author_image"
                :alt="item.author_name"
              />
              <v-icon v-else icon="mdi-account" size="12" />
            </v-avatar>
            <span class="text-truncate text-caption">{{ item.author_name || '未知' }}</span>
          </div>
        </template>

        <!-- 金额列 -->
        <template #item.raised_amount="{ item }">
          <div class="text-right">
            <div class="font-weight-bold text-success text-caption">
              ¥{{ formatNumber(item.raised_amount || 0) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ formatPercentage(item.completion_rate) }}
            </div>
          </div>
        </template>

        <!-- 支持者数列 -->
        <template #item.backer_count="{ item }">
          <div class="text-center">
            <v-chip size="x-small" color="primary" variant="tonal">
              {{ formatNumber(item.backer_count || 0) }}
            </v-chip>
          </div>
        </template>

        <!-- 评论数列 -->
        <template #item.comment_count="{ item }">
          <div class="text-center">
            <v-chip size="x-small" color="info" variant="tonal">
              {{ formatNumber(item.comment_count || 0) }}
            </v-chip>
          </div>
        </template>

        <!-- 看好数列 -->
        <template #item.supporter_count="{ item }">
          <div class="text-center">
            <v-chip size="x-small" color="success" variant="tonal">
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
            {{ item.project_status || '未知' }}
          </v-chip>
        </template>

        <!-- 操作列 -->
        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="viewProject(item)"
              title="查看详情"
            />
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              color="primary"
              @click="editProject(item)"
              title="编辑"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteProject(item)"
              title="删除"
            />
          </div>
        </template>

        <!-- 无数据状态 -->
        <template #no-data>
          <div class="text-center pa-8">
            <v-icon size="64" class="mb-4 text-medium-emphasis">mdi-database-search</v-icon>
            <div class="text-h6 text-medium-emphasis">没有找到匹配的数据</div>
            <div class="text-subtitle-2 text-medium-emphasis mb-4">
              当前搜索条件没有匹配的项目，请尝试以下操作：
            </div>
            <div class="d-flex justify-center ga-2 mb-4">
              <v-btn
                color="primary"
                prepend-icon="mdi-refresh"
                @click="resetSearch"
                variant="outlined"
              >
                重置搜索
              </v-btn>
              <v-btn
                color="info"
                prepend-icon="mdi-view-list"
                @click="showAllProjects"
                variant="tonal"
              >
                显示全部
              </v-btn>
            </div>
            <div class="text-caption text-medium-emphasis">
              或者调整上方的搜索条件后重新搜索
            </div>
          </div>
        </template>
        </v-data-table>
      </div>
    </v-card>

    <!-- 项目详情对话框 -->
    <v-dialog v-model="showDetailDialog" max-width="800px">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-information" class="me-3" />
          项目详情
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showDetailDialog = false"
          />
        </v-card-title>
        
        <v-card-text v-if="selectedProject">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedProject.project_name"
                label="项目名称"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="getCategoryDisplayName(selectedProject.category)"
                label="分类"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedProject.author_name"
                label="作者"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="getStatusText(selectedProject.project_status)"
                label="状态"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                :model-value="'¥' + formatNumber(selectedProject.raised_amount || 0)"
                label="已筹金额"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                :model-value="'¥' + formatNumber(selectedProject.target_amount || 0)"
                label="目标金额"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                :model-value="formatPercentage(selectedProject.completion_rate)"
                label="完成度"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="3">
              <v-text-field
                :model-value="formatNumber(selectedProject.backer_count || 0)"
                label="支持者数"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                :model-value="formatNumber(selectedProject.comment_count || 0)"
                label="评论数"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field
                :model-value="formatNumber(selectedProject.supporter_count || 0)"
                label="看好数"
                readonly
                variant="outlined"
              />
            </v-col>

          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedProject.start_time"
                label="开始时间"
                readonly
                variant="outlined"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                :model-value="selectedProject.end_time"
                label="结束时间"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12">
              <v-text-field
                :model-value="selectedProject.project_url"
                label="项目链接"
                readonly
                variant="outlined"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 编辑对话框 -->
    <v-dialog v-model="showEditDialog" max-width="800px">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-pencil" class="me-3" />
          编辑项目
          <v-spacer />
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showEditDialog = false"
          />
        </v-card-title>
        
        <v-card-text v-if="editingProject">
          <v-form ref="editForm" v-model="editFormValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingProject.project_name"
                  label="项目名称"
                  :rules="[v => !!v || '项目名称不能为空']"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editingProject.category"
                  :items="categoryOptions"
                  label="分类"
                  variant="outlined"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editingProject.author_name"
                  label="作者名称"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editingProject.project_status"
                  :items="statusOptions"
                  label="项目状态"
                  variant="outlined"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="editingProject.raised_amount"
                  label="已筹金额"
                  type="number"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="editingProject.target_amount"
                  label="目标金额"
                  type="number"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="editingProject.completion_rate"
                  label="完成度(%)"
                  type="number"
                  variant="outlined"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model.number="editingProject.backer_count"
                  label="支持者数"
                  type="number"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model.number="editingProject.comment_count"
                  label="评论数"
                  type="number"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model.number="editingProject.supporter_count"
                  label="看好数"
                  type="number"
                  variant="outlined"
                />
              </v-col>

            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="grey"
            @click="showEditDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="primary"
            @click="saveProject"
            :loading="saving"
            :disabled="!editFormValid"
          >
            保存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import FilterBuilder from '@/components/FilterBuilder.vue'
import FilterHistory from '@/components/FilterHistory.vue'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const projects = ref([])
const selectedItems = ref([])
const totalCount = ref(0)
const editFormValid = ref(false)

// 对话框状态
const showDetailDialog = ref(false)
const showEditDialog = ref(false)
const showAddDialog = ref(false)

// 选中的项目
const selectedProject = ref(null)
const editingProject = ref(null)

// 筛选模式
const filterMode = ref('simple')
const currentAdvancedFilters = ref({ filters: [], sort: [] })

// 筛选历史引用
const filterHistoryRef = ref(null)

// 搜索条件
const searchConditions = reactive({
  project_name: '',
  author_name: '',
  category: '',
  min_amount: null,
  max_amount: null,
  status: '',
  date_from: '',
  date_to: ''
})

// 分页
const pagination = reactive({
  page: 1,
  itemsPerPage: 25
})

// 选项数据
const categoryOptions = [
  { value: 'games', title: '游戏' },
  { value: 'publishing', title: '出版' },
  { value: 'tablegames', title: '桌游' },
  { value: 'toys', title: '潮玩模型' },
  { value: 'cards', title: '卡牌' },
  { value: 'technology', title: '科技' },
  { value: 'others', title: '其他' }
]

const statusOptions = [
  { value: '创意', title: '创意' },
  { value: '预热', title: '预热' },
  { value: '众筹中', title: '众筹中' },
  { value: '众筹成功', title: '众筹成功' },
  { value: '项目终止', title: '项目终止' },
  { value: '众筹失败', title: '众筹失败' },
  { value: '众筹取消', title: '众筹取消' },
  { value: '未知情况', title: '未知情况' }
]

// 表格列定义
const headers = [
  { title: '项目名称', key: 'project_name', sortable: true, width: '200px' },
  { title: '分类', key: 'category', sortable: true, width: '100px' },
  { title: '作者', key: 'author_name', sortable: true, width: '120px' },
  { title: '筹款金额', key: 'raised_amount', sortable: true, width: '120px' },
  { title: '支持者', key: 'backer_count', sortable: true, width: '80px' },
  { title: '评论', key: 'comment_count', sortable: true, width: '70px' },
  { title: '看好数', key: 'supporter_count', sortable: true, width: '70px' },
  { title: '状态', key: 'project_status', sortable: true, width: '90px' },
  { title: '操作', key: 'actions', sortable: false, width: '120px' }
]

// 方法
const searchProjects = async () => {
  try {
    loading.value = true
    console.log('🔍 开始搜索项目...')

    // 清理空值
    const conditions = {}
    Object.keys(searchConditions).forEach(key => {
      if (searchConditions[key] !== '' && searchConditions[key] !== null) {
        conditions[key] = searchConditions[key]
      }
    })

    const offset = (pagination.page - 1) * pagination.itemsPerPage
    const hasSearchConditions = Object.keys(conditions).length > 0

    console.log('📊 搜索参数:', {
      conditions,
      limit: pagination.itemsPerPage,
      offset,
      hasSearchConditions
    })

    const response = await axios.post('/api/database/projects/search', {
      conditions,
      limit: pagination.itemsPerPage,
      offset
    })

    console.log('📡 API响应:', response.data)

    if (response.data.success) {
      projects.value = response.data.projects || []
      totalCount.value = response.data.total_count || 0
      console.log('✅ 搜索成功:', projects.value.length, '条，总计:', totalCount.value)

      // 只有在有搜索条件时才添加到筛选历史
      if (hasSearchConditions && filterHistoryRef.value) {
        filterHistoryRef.value.addToHistory({
          type: 'simple',
          searchConditions: { ...searchConditions },
          conditions,
          resultCount: totalCount.value
        })
      }
    } else {
      console.error('❌ 搜索失败:', response.data.message)
      projects.value = []
      totalCount.value = 0
      // 可以在这里添加用户提示
    }
  } catch (error) {
    console.error('❌ 搜索请求失败:', error)
    projects.value = []
    totalCount.value = 0
    // 可以在这里添加用户提示
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  console.log('🔄 重置搜索条件...')

  // 清空所有搜索条件
  Object.keys(searchConditions).forEach(key => {
    searchConditions[key] = ''
  })

  // 重置分页
  pagination.page = 1

  // 重置高级筛选
  if (filterMode.value === 'advanced') {
    currentAdvancedFilters.value = {
      filters: [],
      sort: []
    }
  }

  // 重新搜索（这时会显示所有数据）
  if (filterMode.value === 'simple') {
    searchProjects()
  } else {
    searchProjectsAdvanced()
  }
}

const showAllProjects = () => {
  console.log('📋 显示所有项目...')

  // 确保所有搜索条件都为空
  Object.keys(searchConditions).forEach(key => {
    searchConditions[key] = ''
  })

  // 重置分页到第一页
  pagination.page = 1

  // 重置高级筛选
  currentAdvancedFilters.value = {
    filters: [],
    sort: []
  }

  // 切换到简单搜索模式并执行搜索
  filterMode.value = 'simple'
  searchProjects()
}

const onPageChange = (page) => {
  pagination.page = page
  if (filterMode.value === 'simple') {
    searchProjects()
  } else {
    searchProjectsAdvanced()
  }
}

const onItemsPerPageChange = (itemsPerPage) => {
  pagination.itemsPerPage = itemsPerPage
  pagination.page = 1
  if (filterMode.value === 'simple') {
    searchProjects()
  } else {
    searchProjectsAdvanced()
  }
}

const onFilterModeChange = () => {
  // 切换筛选模式时重置搜索
  resetSearch()
}

const onAdvancedFilters = (filterConfig) => {
  currentAdvancedFilters.value = filterConfig
  searchProjectsAdvanced()
}

const onFiltersChanged = (filterConfig) => {
  currentAdvancedFilters.value = filterConfig
}

const searchProjectsAdvanced = async () => {
  try {
    loading.value = true
    console.log('🔍 开始高级搜索...')

    // 转换高级筛选条件为后端格式
    const conditions = convertAdvancedFilters(currentAdvancedFilters.value.filters)
    const sortConfig = currentAdvancedFilters.value.sort

    const offset = (pagination.page - 1) * pagination.itemsPerPage
    console.log('📊 高级搜索参数:', { conditions, sort: sortConfig, limit: pagination.itemsPerPage, offset })

    const response = await axios.post('/api/database/projects/search', {
      conditions,
      sort: sortConfig,
      limit: pagination.itemsPerPage,
      offset
    })

    console.log('📡 高级搜索API响应:', response.data)

    if (response.data.success) {
      projects.value = response.data.projects || []
      totalCount.value = response.data.total_count || 0
      console.log('✅ 高级搜索成功:', projects.value.length, '条，总计:', totalCount.value)

      // 添加到筛选历史
      if (currentAdvancedFilters.value.filters.length > 0 && filterHistoryRef.value) {
        filterHistoryRef.value.addToHistory({
          type: 'advanced',
          filters: [...currentAdvancedFilters.value.filters],
          sort: [...currentAdvancedFilters.value.sort],
          conditions,
          resultCount: totalCount.value
        })
      }
    } else {
      console.error('❌ 高级搜索失败:', response.data.message)
      projects.value = []
      totalCount.value = 0
    }
  } catch (error) {
    console.error('❌ 高级搜索请求失败:', error)
    projects.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

const convertAdvancedFilters = (filters) => {
  const conditions = {}

  filters.forEach(filter => {
    if (!filter.field || !filter.operator || filter.value === '') return

    const field = filter.field
    const operator = filter.operator
    const value = filter.value

    switch (operator) {
      case 'contains':
        conditions[field] = value
        break
      case 'equals':
        conditions[field] = value
        break
      case 'greater_than':
        conditions[`${field}_min`] = value
        break
      case 'greater_equal':
        conditions[`${field}_min`] = value
        break
      case 'less_than':
        conditions[`${field}_max`] = value
        break
      case 'less_equal':
        conditions[`${field}_max`] = value
        break
      case 'not_equals':
        conditions[`${field}_not`] = value
        break
      // 可以根据需要添加更多操作符
    }
  })

  return conditions
}

const onApplyHistoryFilter = (historyItem) => {
  if (historyItem.type === 'simple') {
    // 应用简单搜索历史
    filterMode.value = 'simple'
    Object.assign(searchConditions, historyItem.searchConditions || {})
    searchProjects()
  } else {
    // 应用高级筛选历史
    filterMode.value = 'advanced'
    currentAdvancedFilters.value = {
      filters: historyItem.filters || [],
      sort: historyItem.sort || []
    }
    searchProjectsAdvanced()
  }
}

const viewProject = (project) => {
  selectedProject.value = project
  showDetailDialog.value = true
}

const editProject = (project) => {
  editingProject.value = { ...project }
  showEditDialog.value = true
}

const saveProject = async () => {
  if (!editingProject.value) return

  try {
    saving.value = true

    const response = await axios.put(`/api/database/project/${editingProject.value.id}`, editingProject.value)

    if (response.data.success) {
      showEditDialog.value = false
      await searchProjects()
      alert('项目更新成功')
    } else {
      alert(`更新失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败')
  } finally {
    saving.value = false
  }
}

const deleteProject = async (project) => {
  if (!confirm(`确定要删除项目"${project.project_name}"吗？此操作不可恢复。`)) {
    return
  }

  try {
    const response = await axios.delete(`/api/database/project/${project.id}`)

    if (response.data.success) {
      await searchProjects()
      alert('项目删除成功')
    } else {
      alert(`删除失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败')
  }
}

const batchDelete = async () => {
  if (!selectedItems.value.length) return

  if (!confirm(`确定要删除选中的 ${selectedItems.value.length} 个项目吗？此操作不可恢复。`)) {
    return
  }

  try {
    const response = await axios.delete('/api/database/projects/batch', {
      data: { project_ids: selectedItems.value }
    })

    if (response.data.success) {
      selectedItems.value = []
      await searchProjects()
      alert(`成功删除 ${response.data.deleted_count} 个项目`)
    } else {
      alert(`批量删除失败: ${response.data.message}`)
    }
  } catch (error) {
    console.error('批量删除失败:', error)
    alert('批量删除失败')
  }
}

const exportData = async () => {
  try {
    exporting.value = true
    const url = '/api/database/export'
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

// 工具方法
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('zh-CN').format(num)
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
  const names = {
    'games': '游戏',
    'publishing': '出版',
    'tablegames': '桌游',
    'toys': '潮玩模型',
    'cards': '卡牌',
    'technology': '科技',
    'others': '其他',
    '桌游': '桌游',
    '游戏': '游戏',
    '出版': '出版',
    '潮玩模型': '潮玩模型',
    '卡牌': '卡牌',
    '科技': '科技'
  }
  return names[category] || category || '未知分类'
}

const getStatusColor = (status) => {
  const colors = {
    // 实际网页状态
    '创意': 'info',
    '预热': 'warning',
    '众筹中': 'success',
    '众筹成功': 'primary',
    '项目终止': 'error',
    '众筹失败': 'error',
    '众筹取消': 'warning',
    '未知情况': 'default',
    // 向后兼容旧状态
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

const formatPercentage = (rate) => {
  if (!rate) return '0%'
  return `${parseFloat(rate).toFixed(1)}%`
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

// 生命周期
onMounted(() => {
  searchProjects()
})
</script>

<style scoped>
.v-data-table {
  background: transparent;
}

.v-card-title {
  background: rgba(var(--v-theme-surface-variant), 0.1);
}

/* 表格容器滚动样式 */
.table-container {
  overflow-x: auto;
  width: 100%;
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: rgba(var(--v-theme-primary), 0.3) transparent;
}

.table-container::-webkit-scrollbar {
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.3);
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.5);
}

/* 表格固定最小宽度，防止列压缩 */
.v-data-table :deep(.v-table__wrapper) {
  min-width: 1200px;
}

/* 确保表格列不会被压缩得太小 */
.v-data-table :deep(th),
.v-data-table :deep(td) {
  white-space: nowrap;
  min-width: 60px;
}

/* 项目名称列允许换行 */
.v-data-table :deep(th:first-child),
.v-data-table :deep(td:first-child) {
  white-space: normal;
  min-width: 200px;
}
</style>
