<template>
  <v-card elevation="2" class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-filter-cog" class="me-3" />
      高级筛选构建器
      <v-spacer />
      <v-btn
        icon="mdi-content-save"
        variant="text"
        @click="showSaveDialog = true"
        :disabled="!hasActiveFilters"
        title="保存筛选配置"
      />
      <v-btn
        icon="mdi-folder-open"
        variant="text"
        @click="showLoadDialog = true"
        title="加载筛选配置"
      />
      <v-btn
        icon="mdi-refresh"
        variant="text"
        @click="resetFilters"
        title="重置筛选"
      />
    </v-card-title>

    <v-card-text>
      <!-- 筛选条件列表 -->
      <div v-for="(filter, index) in filters" :key="index" class="mb-3">
        <v-row align="center">
          <v-col cols="12" md="3">
            <v-select
              v-model="filter.field"
              :items="fieldOptions"
              label="字段"
              variant="outlined"
              density="compact"
              @update:model-value="onFieldChange(index)"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-model="filter.operator"
              :items="getOperatorOptions(filter.field)"
              label="操作符"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-if="getFieldType(filter.field) === 'text'"
              v-model="filter.value"
              label="值"
              variant="outlined"
              density="compact"
            />
            <v-text-field
              v-else-if="getFieldType(filter.field) === 'number'"
              v-model.number="filter.value"
              label="值"
              type="number"
              variant="outlined"
              density="compact"
            />
            <v-text-field
              v-else-if="getFieldType(filter.field) === 'date'"
              v-model="filter.value"
              label="值"
              type="date"
              variant="outlined"
              density="compact"
            />
            <v-select
              v-else-if="getFieldType(filter.field) === 'select'"
              v-model="filter.value"
              :items="getSelectOptions(filter.field)"
              label="值"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-select
              v-if="index < filters.length - 1"
              v-model="filter.logic"
              :items="logicOptions"
              label="逻辑"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              icon="mdi-delete"
              variant="text"
              color="error"
              @click="removeFilter(index)"
              :disabled="filters.length === 1"
            />
          </v-col>
        </v-row>
      </div>

      <!-- 添加筛选条件按钮 -->
      <v-btn
        prepend-icon="mdi-plus"
        variant="outlined"
        @click="addFilter"
        class="mb-4"
      >
        添加筛选条件
      </v-btn>

      <!-- 排序配置 -->
      <v-divider class="my-4" />
      
      <h4 class="mb-3">排序配置</h4>
      <div v-for="(sort, index) in sortConfig" :key="`sort-${index}`" class="mb-3">
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-select
              v-model="sort.field"
              :items="sortableFields"
              label="排序字段"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="sort.order"
              :items="sortOrderOptions"
              label="排序方向"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model.number="sort.priority"
              label="优先级"
              type="number"
              variant="outlined"
              density="compact"
              min="1"
            />
          </v-col>
          <v-col cols="12" md="2">
            <v-btn
              icon="mdi-delete"
              variant="text"
              color="error"
              @click="removeSortConfig(index)"
              :disabled="sortConfig.length === 1"
            />
          </v-col>
        </v-row>
      </div>

      <v-btn
        prepend-icon="mdi-plus"
        variant="outlined"
        @click="addSortConfig"
        class="mb-4"
      >
        添加排序字段
      </v-btn>

      <!-- 操作按钮 -->
      <v-divider class="my-4" />
      <v-row>
        <v-col>
          <v-btn
            color="primary"
            prepend-icon="mdi-magnify"
            @click="applyFilters"
            :loading="loading"
            variant="elevated"
          >
            应用筛选
          </v-btn>
          <v-btn
            color="secondary"
            prepend-icon="mdi-eye"
            @click="previewSQL"
            variant="outlined"
            class="ml-2"
          >
            预览SQL
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>

    <!-- 保存筛选配置对话框 -->
    <v-dialog v-model="showSaveDialog" max-width="400px">
      <v-card>
        <v-card-title>保存筛选配置</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="saveConfigName"
            label="配置名称"
            variant="outlined"
            :rules="[v => !!v || '请输入配置名称']"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showSaveDialog = false">取消</v-btn>
          <v-btn color="primary" @click="saveFilterConfig" :disabled="!saveConfigName">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 加载筛选配置对话框 -->
    <v-dialog v-model="showLoadDialog" max-width="600px">
      <v-card>
        <v-card-title>加载筛选配置</v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="config in savedConfigs"
              :key="config.id"
              @click="loadFilterConfig(config)"
            >
              <v-list-item-title>{{ config.name }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ config.description }} - {{ formatDate(config.created_at) }}
              </v-list-item-subtitle>
              <template #append>
                <v-btn
                  icon="mdi-delete"
                  variant="text"
                  size="small"
                  @click.stop="deleteFilterConfig(config.id)"
                />
              </template>
            </v-list-item>
          </v-list>
          <div v-if="!savedConfigs.length" class="text-center pa-4 text-medium-emphasis">
            暂无保存的筛选配置
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showLoadDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- SQL预览对话框 -->
    <v-dialog v-model="showSQLDialog" max-width="800px">
      <v-card>
        <v-card-title>SQL查询预览</v-card-title>
        <v-card-text>
          <v-code class="sql-preview">
            {{ generatedSQL }}
          </v-code>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showSQLDialog = false">关闭</v-btn>
          <v-btn color="primary" @click="copySQL">复制SQL</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['apply-filters', 'filters-changed'])

// 响应式数据
const filters = ref([
  { field: '', operator: '', value: '', logic: 'AND' }
])

const sortConfig = ref([
  { field: '', order: 'desc', priority: 1 }
])

const showSaveDialog = ref(false)
const showLoadDialog = ref(false)
const showSQLDialog = ref(false)
const saveConfigName = ref('')
const savedConfigs = ref([])
const generatedSQL = ref('')

// 字段选项
const fieldOptions = [
  { value: 'project_name', title: '项目名称' },
  { value: 'category', title: '分类' },
  { value: 'author_name', title: '作者' },
  { value: 'raised_amount', title: '已筹金额' },
  { value: 'target_amount', title: '目标金额' },
  { value: 'completion_rate', title: '完成度' },
  { value: 'backer_count', title: '支持者数' },
  { value: 'comment_count', title: '评论数' },
  { value: 'supporter_count', title: '点赞数' },
  { value: 'project_status', title: '项目状态' },
  { value: 'crawl_time', title: '爬取时间' }
]

const sortableFields = fieldOptions

const logicOptions = [
  { value: 'AND', title: '并且 (AND)' },
  { value: 'OR', title: '或者 (OR)' }
]

const sortOrderOptions = [
  { value: 'asc', title: '升序 (ASC)' },
  { value: 'desc', title: '降序 (DESC)' }
]

// 计算属性
const hasActiveFilters = computed(() => {
  return filters.value.some(f => f.field && f.operator && f.value !== '')
})

// 方法
const getFieldType = (field) => {
  const types = {
    'project_name': 'text',
    'author_name': 'text',
    'category': 'select',
    'project_status': 'select',
    'raised_amount': 'number',
    'target_amount': 'number',
    'completion_rate': 'number',
    'backer_count': 'number',
    'comment_count': 'number',
    'supporter_count': 'number',
    'crawl_time': 'date'
  }
  return types[field] || 'text'
}

const getOperatorOptions = (field) => {
  const type = getFieldType(field)

  if (type === 'text') {
    return [
      { value: 'contains', title: '包含' },
      { value: 'not_contains', title: '不包含' },
      { value: 'equals', title: '等于' },
      { value: 'not_equals', title: '不等于' },
      { value: 'starts_with', title: '开始于' },
      { value: 'ends_with', title: '结束于' }
    ]
  } else if (type === 'number') {
    return [
      { value: 'equals', title: '等于' },
      { value: 'not_equals', title: '不等于' },
      { value: 'greater_than', title: '大于' },
      { value: 'greater_equal', title: '大于等于' },
      { value: 'less_than', title: '小于' },
      { value: 'less_equal', title: '小于等于' },
      { value: 'between', title: '介于' }
    ]
  } else if (type === 'date') {
    return [
      { value: 'equals', title: '等于' },
      { value: 'not_equals', title: '不等于' },
      { value: 'after', title: '晚于' },
      { value: 'before', title: '早于' },
      { value: 'between', title: '介于' }
    ]
  } else if (type === 'select') {
    return [
      { value: 'equals', title: '等于' },
      { value: 'not_equals', title: '不等于' },
      { value: 'in', title: '包含于' },
      { value: 'not_in', title: '不包含于' }
    ]
  }

  return []
}

const getSelectOptions = (field) => {
  if (field === 'category') {
    return [
      { value: 'games', title: '游戏' },
      { value: 'publishing', title: '出版' },
      { value: 'tablegames', title: '桌游' },
      { value: 'toys', title: '潮玩模型' },
      { value: 'cards', title: '卡牌' },
      { value: 'technology', title: '科技' },
      { value: 'others', title: '其他' }
    ]
  } else if (field === 'project_status') {
    return [
      { value: 'active', title: '进行中' },
      { value: 'completed', title: '已完成' },
      { value: 'failed', title: '失败' },
      { value: 'cancelled', title: '已取消' }
    ]
  }
  return []
}

const onFieldChange = (index) => {
  // 重置操作符和值
  filters.value[index].operator = ''
  filters.value[index].value = ''
}

const addFilter = () => {
  filters.value.push({ field: '', operator: '', value: '', logic: 'AND' })
}

const removeFilter = (index) => {
  if (filters.value.length > 1) {
    filters.value.splice(index, 1)
  }
}

const addSortConfig = () => {
  const nextPriority = Math.max(...sortConfig.value.map(s => s.priority)) + 1
  sortConfig.value.push({ field: '', order: 'desc', priority: nextPriority })
}

const removeSortConfig = (index) => {
  if (sortConfig.value.length > 1) {
    sortConfig.value.splice(index, 1)
  }
}

const resetFilters = () => {
  filters.value = [{ field: '', operator: '', value: '', logic: 'AND' }]
  sortConfig.value = [{ field: '', order: 'desc', priority: 1 }]
  emit('filters-changed', { filters: [], sort: [] })
}

const applyFilters = () => {
  const activeFilters = filters.value.filter(f => f.field && f.operator && f.value !== '')
  const activeSort = sortConfig.value.filter(s => s.field).sort((a, b) => a.priority - b.priority)

  emit('apply-filters', { filters: activeFilters, sort: activeSort })
  emit('filters-changed', { filters: activeFilters, sort: activeSort })
}

const previewSQL = () => {
  generatedSQL.value = generateSQL()
  showSQLDialog.value = true
}

const generateSQL = () => {
  let sql = 'SELECT * FROM projects'

  // WHERE条件
  const activeFilters = filters.value.filter(f => f.field && f.operator && f.value !== '')
  if (activeFilters.length > 0) {
    const whereConditions = activeFilters.map((filter, index) => {
      let condition = ''

      switch (filter.operator) {
        case 'contains':
          condition = `${filter.field} LIKE '%${filter.value}%'`
          break
        case 'not_contains':
          condition = `${filter.field} NOT LIKE '%${filter.value}%'`
          break
        case 'equals':
          condition = `${filter.field} = '${filter.value}'`
          break
        case 'not_equals':
          condition = `${filter.field} != '${filter.value}'`
          break
        case 'greater_than':
          condition = `${filter.field} > ${filter.value}`
          break
        case 'greater_equal':
          condition = `${filter.field} >= ${filter.value}`
          break
        case 'less_than':
          condition = `${filter.field} < ${filter.value}`
          break
        case 'less_equal':
          condition = `${filter.field} <= ${filter.value}`
          break
        case 'starts_with':
          condition = `${filter.field} LIKE '${filter.value}%'`
          break
        case 'ends_with':
          condition = `${filter.field} LIKE '%${filter.value}'`
          break
        default:
          condition = `${filter.field} = '${filter.value}'`
      }

      if (index > 0) {
        condition = ` ${activeFilters[index - 1].logic} ${condition}`
      }

      return condition
    })

    sql += '\nWHERE ' + whereConditions.join('')
  }

  // ORDER BY
  const activeSort = sortConfig.value.filter(s => s.field).sort((a, b) => a.priority - b.priority)
  if (activeSort.length > 0) {
    const orderConditions = activeSort.map(sort => `${sort.field} ${sort.order.toUpperCase()}`)
    sql += '\nORDER BY ' + orderConditions.join(', ')
  }

  return sql
}

const saveFilterConfig = async () => {
  const config = {
    name: saveConfigName.value,
    filters: filters.value,
    sort: sortConfig.value,
    description: `${filters.value.filter(f => f.field).length} 个筛选条件`,
    created_at: new Date().toISOString()
  }

  // 保存到localStorage
  const saved = JSON.parse(localStorage.getItem('filterConfigs') || '[]')
  config.id = Date.now()
  saved.push(config)
  localStorage.setItem('filterConfigs', JSON.stringify(saved))

  savedConfigs.value = saved
  showSaveDialog.value = false
  saveConfigName.value = ''
}

const loadFilterConfig = (config) => {
  filters.value = [...config.filters]
  sortConfig.value = [...config.sort]
  showLoadDialog.value = false

  // 自动应用筛选
  applyFilters()
}

const deleteFilterConfig = (configId) => {
  const saved = JSON.parse(localStorage.getItem('filterConfigs') || '[]')
  const filtered = saved.filter(c => c.id !== configId)
  localStorage.setItem('filterConfigs', JSON.stringify(filtered))
  savedConfigs.value = filtered
}

const copySQL = () => {
  navigator.clipboard.writeText(generatedSQL.value)
  // 这里可以添加复制成功的提示
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadSavedConfigs = () => {
  savedConfigs.value = JSON.parse(localStorage.getItem('filterConfigs') || '[]')
}

// 生命周期
onMounted(() => {
  loadSavedConfigs()
})
</script>

<style scoped>
.sql-preview {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
