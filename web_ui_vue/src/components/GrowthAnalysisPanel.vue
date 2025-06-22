<template>
  <v-card class="app-card">
    <v-card-title class="d-flex align-center p-lg">
      <v-avatar color="secondary" size="32" class="me-3">
        <v-icon icon="mdi-trending-up" color="on-secondary" size="18" />
      </v-avatar>
      <div class="flex-grow-1">
        <div class="text-h6 font-weight-bold">增长率分析</div>
        <div class="text-body-2 text-medium-emphasis">不同时间周期的数据增长趋势</div>
      </div>
      <v-select
        v-model="selectedMetric"
        :items="availableMetrics"
        item-title="label"
        item-value="key"
        variant="outlined"
        density="compact"
        style="max-width: 200px;"
        hide-details
      />
    </v-card-title>
    
    <v-card-text class="p-lg pt-0">
      <v-row>
        <!-- 日增长率 -->
        <v-col cols="12" md="4">
          <v-card variant="outlined" class="text-center pa-4">
            <div class="d-flex align-center justify-center mb-2">
              <v-icon 
                :color="getTrendIconColor(dailyGrowth.trend)" 
                :icon="getTrendIcon(dailyGrowth.trend)"
                size="20"
                class="me-2"
              />
              <span class="text-subtitle-2 text-on-surface-variant">日增长率</span>
            </div>
            <div 
              class="text-h5 font-weight-bold mb-1"
              :class="getTrendColorClass(dailyGrowth.trend)"
            >
              {{ formatGrowthRate(dailyGrowth.rate) }}
            </div>
            <div class="text-caption text-on-surface-variant">
              {{ getTrendDescription(dailyGrowth.trend) }}
            </div>
            <div v-if="dailyGrowth.latest" class="text-caption text-on-surface-variant mt-2">
              最近变化: {{ formatChange(dailyGrowth.latest.change) }}
            </div>
          </v-card>
        </v-col>
        
        <!-- 周增长率 -->
        <v-col cols="12" md="4">
          <v-card variant="outlined" class="text-center pa-4">
            <div class="d-flex align-center justify-center mb-2">
              <v-icon 
                :color="getTrendIconColor(weeklyGrowth.trend)" 
                :icon="getTrendIcon(weeklyGrowth.trend)"
                size="20"
                class="me-2"
              />
              <span class="text-subtitle-2 text-on-surface-variant">周增长率</span>
            </div>
            <div 
              class="text-h5 font-weight-bold mb-1"
              :class="getTrendColorClass(weeklyGrowth.trend)"
            >
              {{ formatGrowthRate(weeklyGrowth.rate) }}
            </div>
            <div class="text-caption text-on-surface-variant">
              {{ getTrendDescription(weeklyGrowth.trend) }}
            </div>
            <div v-if="weeklyGrowth.latest" class="text-caption text-on-surface-variant mt-2">
              最近变化: {{ formatChange(weeklyGrowth.latest.change) }}
            </div>
          </v-card>
        </v-col>
        
        <!-- 月增长率 -->
        <v-col cols="12" md="4">
          <v-card variant="outlined" class="text-center pa-4">
            <div class="d-flex align-center justify-center mb-2">
              <v-icon 
                :color="getTrendIconColor(monthlyGrowth.trend)" 
                :icon="getTrendIcon(monthlyGrowth.trend)"
                size="20"
                class="me-2"
              />
              <span class="text-subtitle-2 text-on-surface-variant">月增长率</span>
            </div>
            <div 
              class="text-h5 font-weight-bold mb-1"
              :class="getTrendColorClass(monthlyGrowth.trend)"
            >
              {{ formatGrowthRate(monthlyGrowth.rate) }}
            </div>
            <div class="text-caption text-on-surface-variant">
              {{ getTrendDescription(monthlyGrowth.trend) }}
            </div>
            <div v-if="monthlyGrowth.latest" class="text-caption text-on-surface-variant mt-2">
              最近变化: {{ formatChange(monthlyGrowth.latest.change) }}
            </div>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- 详细分析 -->
      <v-row v-if="selectedAnalysis.data.length > 0" class="mt-4">
        <v-col cols="12">
          <v-card variant="outlined">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              {{ selectedMetricLabel }} - {{ selectedPeriodLabel }}详细分析
            </v-card-title>
            <v-card-text>
              <div class="analysis-timeline">
                <div 
                  v-for="(item, index) in selectedAnalysis.data.slice(-5)" 
                  :key="index"
                  class="timeline-item d-flex align-center justify-space-between py-2"
                  :class="{ 'border-bottom': index < selectedAnalysis.data.slice(-5).length - 1 }"
                >
                  <div class="flex-grow-1">
                    <div class="text-body-2 font-weight-medium">
                      {{ formatPeriodLabel(item) }}
                    </div>
                    <div class="text-caption text-on-surface-variant">
                      {{ formatValue(item.value) }} 
                      <span v-if="item.previousValue">(前期: {{ formatValue(item.previousValue) }})</span>
                    </div>
                  </div>
                  <div class="text-right">
                    <div 
                      class="text-body-2 font-weight-bold"
                      :class="item.rate >= 0 ? 'text-success' : 'text-error'"
                    >
                      {{ formatGrowthRate(item.rate) }}
                    </div>
                    <div class="text-caption text-on-surface-variant">
                      {{ formatChange(item.change) }}
                    </div>
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- 无数据提示 -->
      <div v-if="!historyData.length" class="text-center py-8">
        <v-icon size="64" color="on-surface-variant">mdi-chart-timeline-variant</v-icon>
        <div class="text-h6 mt-2 text-on-surface">暂无历史数据</div>
        <div class="text-caption text-on-surface-variant">需要至少2条历史记录才能进行增长率分析</div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  calculateDailyGrowth, 
  calculateWeeklyGrowth, 
  calculateMonthlyGrowth,
  getTrendDescription,
  getTrendColorClass,
  formatGrowthRate
} from '@/utils/growthAnalysis'

// Props
const props = defineProps({
  historyData: {
    type: Array,
    default: () => []
  }
})

// 响应式数据
const selectedMetric = ref('raised_amount')
const selectedPeriod = ref('daily')

// 可用指标
const availableMetrics = [
  { key: 'raised_amount', label: '筹款金额' },
  { key: 'backer_count', label: '支持者数' },
  { key: 'supporter_count', label: '点赞数' },
  { key: 'comment_count', label: '评论数' },
  { key: 'completion_rate', label: '完成率' },
  { key: 'update_count', label: '更新数' }
]

// 计算属性
const selectedMetricLabel = computed(() => {
  const metric = availableMetrics.find(m => m.key === selectedMetric.value)
  return metric?.label || '未知指标'
})

const selectedPeriodLabel = computed(() => {
  const labels = {
    daily: '日',
    weekly: '周',
    monthly: '月'
  }
  return labels[selectedPeriod.value] || '未知周期'
})

const dailyGrowth = computed(() => {
  return calculateDailyGrowth(props.historyData, selectedMetric.value)
})

const weeklyGrowth = computed(() => {
  return calculateWeeklyGrowth(props.historyData, selectedMetric.value)
})

const monthlyGrowth = computed(() => {
  return calculateMonthlyGrowth(props.historyData, selectedMetric.value)
})

const selectedAnalysis = computed(() => {
  switch (selectedPeriod.value) {
    case 'weekly':
      return weeklyGrowth.value
    case 'monthly':
      return monthlyGrowth.value
    default:
      return dailyGrowth.value
  }
})

// 方法
const getTrendIcon = (trend) => {
  const icons = {
    rising: 'mdi-trending-up',
    falling: 'mdi-trending-down',
    stable: 'mdi-trending-neutral'
  }
  return icons[trend] || 'mdi-trending-neutral'
}

const getTrendIconColor = (trend) => {
  const colors = {
    rising: 'success',
    falling: 'error',
    stable: 'on-surface-variant'
  }
  return colors[trend] || 'on-surface-variant'
}

const formatChange = (change) => {
  if (!change) return '无变化'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${Math.abs(change).toLocaleString()}`
}

const formatValue = (value) => {
  if (selectedMetric.value === 'raised_amount') {
    return `¥${value.toLocaleString()}`
  }
  if (selectedMetric.value === 'completion_rate') {
    return `${value.toFixed(1)}%`
  }
  return value.toLocaleString()
}

const formatPeriodLabel = (item) => {
  if (item.date) return item.date
  if (item.week) return item.week
  if (item.month) return item.month
  return '未知时期'
}

// 监听指标变化，自动选择最佳周期
watch(selectedMetric, () => {
  // 根据数据量自动选择合适的分析周期
  if (props.historyData.length > 30) {
    selectedPeriod.value = 'weekly'
  } else if (props.historyData.length > 7) {
    selectedPeriod.value = 'daily'
  } else {
    selectedPeriod.value = 'daily'
  }
})
</script>

<style scoped>
.analysis-timeline {
  max-height: 300px;
  overflow-y: auto;
}

.timeline-item {
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.12);
}

.timeline-item:last-child {
  border-bottom: none !important;
}

/* MD3 卡片悬停效果 */
.v-card[variant="outlined"]:hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
  transition: background-color 0.2s ease;
}
</style>
