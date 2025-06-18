<template>
  <v-card elevation="2" class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-history" class="me-3" />
      筛选历史
      <v-spacer />
      <v-btn
        icon="mdi-delete-sweep"
        variant="text"
        @click="clearHistory"
        :disabled="!filterHistory.length"
        title="清空历史"
      />
    </v-card-title>

    <v-card-text>
      <div v-if="!filterHistory.length" class="text-center pa-4 text-medium-emphasis">
        暂无筛选历史记录
      </div>
      
      <v-list v-else density="compact">
        <v-list-item
          v-for="(item, index) in filterHistory"
          :key="index"
          @click="applyHistoryFilter(item)"
          class="history-item"
        >
          <template #prepend>
            <v-icon 
              :icon="item.type === 'simple' ? 'mdi-magnify' : 'mdi-filter-cog'" 
              :color="item.type === 'simple' ? 'primary' : 'secondary'"
            />
          </template>
          
          <v-list-item-title>
            {{ getHistoryTitle(item) }}
          </v-list-item-title>
          
          <v-list-item-subtitle>
            {{ formatDateTime(item.timestamp) }} - {{ getHistoryDescription(item) }}
          </v-list-item-subtitle>
          
          <template #append>
            <v-btn
              icon="mdi-star-outline"
              variant="text"
              size="small"
              @click.stop="saveAsFavorite(item)"
              title="保存为收藏"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              size="small"
              @click.stop="removeHistoryItem(index)"
              title="删除"
            />
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Props
const props = defineProps({
  maxItems: {
    type: Number,
    default: 20
  }
})

// Emits
const emit = defineEmits(['apply-filter'])

// 响应式数据
const filterHistory = ref([])

// 方法
const addToHistory = (filterData) => {
  const historyItem = {
    ...filterData,
    timestamp: new Date().toISOString(),
    id: Date.now()
  }
  
  // 避免重复添加相同的筛选条件
  const isDuplicate = filterHistory.value.some(item => 
    JSON.stringify(item.conditions || item.searchConditions) === 
    JSON.stringify(filterData.conditions || filterData.searchConditions)
  )
  
  if (!isDuplicate) {
    filterHistory.value.unshift(historyItem)
    
    // 限制历史记录数量
    if (filterHistory.value.length > props.maxItems) {
      filterHistory.value = filterHistory.value.slice(0, props.maxItems)
    }
    
    saveToLocalStorage()
  }
}

const applyHistoryFilter = (item) => {
  emit('apply-filter', item)
}

const removeHistoryItem = (index) => {
  filterHistory.value.splice(index, 1)
  saveToLocalStorage()
}

const clearHistory = () => {
  if (confirm('确定要清空所有筛选历史吗？')) {
    filterHistory.value = []
    saveToLocalStorage()
  }
}

const saveAsFavorite = (item) => {
  // 保存到收藏配置中
  const favorites = JSON.parse(localStorage.getItem('filterConfigs') || '[]')
  const favoriteItem = {
    name: `历史筛选 - ${getHistoryTitle(item)}`,
    filters: item.filters || [],
    sort: item.sort || [],
    searchConditions: item.searchConditions || {},
    type: item.type,
    description: getHistoryDescription(item),
    created_at: new Date().toISOString(),
    id: Date.now()
  }
  
  favorites.push(favoriteItem)
  localStorage.setItem('filterConfigs', JSON.stringify(favorites))
  
  // 可以添加成功提示
  console.log('已保存为收藏配置')
}

const getHistoryTitle = (item) => {
  if (item.type === 'simple') {
    const conditions = item.searchConditions || {}
    const parts = []
    
    if (conditions.project_name) parts.push(`项目: ${conditions.project_name}`)
    if (conditions.author_name) parts.push(`作者: ${conditions.author_name}`)
    if (conditions.category) parts.push(`分类: ${conditions.category}`)
    if (conditions.min_amount || conditions.max_amount) {
      parts.push(`金额: ${conditions.min_amount || 0}-${conditions.max_amount || '∞'}`)
    }
    
    return parts.length > 0 ? parts.join(', ') : '简单搜索'
  } else {
    const filterCount = (item.filters || []).filter(f => f.field && f.value).length
    const sortCount = (item.sort || []).filter(s => s.field).length
    return `高级筛选 (${filterCount}个条件, ${sortCount}个排序)`
  }
}

const getHistoryDescription = (item) => {
  if (item.type === 'simple') {
    const conditions = item.searchConditions || {}
    const conditionCount = Object.keys(conditions).filter(key => conditions[key]).length
    return `${conditionCount} 个搜索条件`
  } else {
    const filterCount = (item.filters || []).filter(f => f.field && f.value).length
    const sortCount = (item.sort || []).filter(s => s.field).length
    return `${filterCount} 个筛选条件, ${sortCount} 个排序字段`
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`

  // 确保显示本地时间（GMT+8北京时间）
  return date.toLocaleDateString('zh-CN', {
    timeZone: 'Asia/Shanghai'
  })
}

const saveToLocalStorage = () => {
  localStorage.setItem('filterHistory', JSON.stringify(filterHistory.value))
}

const loadFromLocalStorage = () => {
  const saved = localStorage.getItem('filterHistory')
  if (saved) {
    try {
      filterHistory.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载筛选历史失败:', e)
      filterHistory.value = []
    }
  }
}

// 暴露方法给父组件
defineExpose({
  addToHistory
})

// 生命周期
onMounted(() => {
  loadFromLocalStorage()
})
</script>

<style scoped>
.history-item {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.history-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}
</style>
