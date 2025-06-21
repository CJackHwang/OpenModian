<template>
  <v-container fluid class="pa-6">
    <!-- 加载状态 -->
    <v-row v-if="loading" justify="center">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
        <div class="mt-4 text-h6">加载项目详情中...</div>
      </v-col>
    </v-row>

    <!-- 错误状态 -->
    <v-row v-else-if="error" justify="center">
      <v-col cols="12" md="8">
        <v-alert type="error" prominent>
          <v-alert-title>加载失败</v-alert-title>
          {{ error }}
        </v-alert>
        <div class="text-center mt-4">
          <v-btn color="primary" @click="loadProjectDetail">重试</v-btn>
          <v-btn color="secondary" @click="$router.go(-1)" class="ml-2">返回</v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 项目详情内容 -->
    <div v-else-if="project">
      <!-- 页面标题和操作按钮 -->
      <v-row class="mb-6">
        <v-col cols="12" md="8">
          <div class="d-flex align-center mb-2">
            <v-btn icon @click="$router.go(-1)" class="mr-2">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <h1 class="text-h4 font-weight-bold">{{ project.project_name }}</h1>
          </div>
          <v-chip color="primary" class="mr-2">{{ project.category }}</v-chip>
          <v-chip :color="getStatusColor(project.project_status)" class="mr-2">
            {{ project.project_status || '进行中' }}
          </v-chip>
        </v-col>
        <v-col cols="12" md="4" class="text-right">
          <v-btn 
            color="primary" 
            :href="project.project_url" 
            target="_blank"
            prepend-icon="mdi-open-in-new"
            class="mr-2"
          >
            访问原始项目
          </v-btn>
          <v-btn 
            color="secondary" 
            @click="exportProjectData"
            prepend-icon="mdi-download"
            :loading="exporting"
          >
            导出数据
          </v-btn>
        </v-col>
      </v-row>

      <!-- 项目基本信息卡片 -->
      <v-row class="mb-6">
        <v-col cols="12" md="4">
          <v-card class="h-100">
            <v-img
              :src="isValidImageUrl(project.project_image) ? project.project_image : '/placeholder-image.jpg'"
              height="200"
              cover
              class="white--text"
            >
              <template v-slot:placeholder>
                <v-row class="fill-height ma-0" align="center" justify="center">
                  <v-progress-circular indeterminate color="grey lighten-5"></v-progress-circular>
                </v-row>
              </template>
              <template v-slot:error>
                <v-row class="fill-height ma-0" align="center" justify="center">
                  <v-icon size="64" color="grey">mdi-image-off</v-icon>
                </v-row>
              </template>
            </v-img>
            <v-card-text>
              <div class="text-h6 mb-2">作者信息</div>
              <div class="d-flex align-center mb-2">
                <v-avatar size="32" class="mr-2">
                  <v-img
                    v-if="isValidImageUrl(project.author_image)"
                    :src="project.author_image"
                  >
                    <template v-slot:error>
                      <v-icon icon="mdi-account" size="20" />
                    </template>
                  </v-img>
                  <v-icon v-else icon="mdi-account" size="20" />
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ project.author_name || '未知作者' }}</div>
                  <a 
                    v-if="project.author_link" 
                    :href="project.author_link" 
                    target="_blank"
                    class="text-caption text-primary"
                  >
                    查看作者主页
                  </a>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="8">
          <v-card class="h-100">
            <v-card-title>项目数据</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" md="3">
                  <div class="text-center">
                    <div class="text-h4 font-weight-bold text-primary">
                      ¥{{ formatNumber(project.raised_amount) }}
                    </div>
                    <div class="text-caption">已筹金额</div>
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-center">
                    <div class="text-h4 font-weight-bold">
                      ¥{{ formatNumber(project.target_amount) }}
                    </div>
                    <div class="text-caption">目标金额</div>
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-center">
                    <div class="text-h4 font-weight-bold text-success">
                      {{ project.completion_rate?.toFixed(1) || 0 }}%
                    </div>
                    <div class="text-caption">完成率</div>
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-center">
                    <div class="text-h4 font-weight-bold">
                      {{ project.backer_count || 0 }}
                    </div>
                    <div class="text-caption">支持者</div>
                  </div>
                </v-col>
              </v-row>

              <v-progress-linear 
                :model-value="project.completion_rate || 0" 
                height="8" 
                color="primary"
                class="my-4"
              ></v-progress-linear>

              <v-row>
                <v-col cols="4">
                  <div class="text-center">
                    <v-icon color="red" class="mb-1">mdi-heart</v-icon>
                    <div class="font-weight-medium">{{ project.supporter_count || 0 }}</div>
                    <div class="text-caption">点赞数</div>
                  </div>
                </v-col>
                <v-col cols="4">
                  <div class="text-center">
                    <v-icon color="blue" class="mb-1">mdi-comment</v-icon>
                    <div class="font-weight-medium">{{ project.comment_count || 0 }}</div>
                    <div class="text-caption">评论数</div>
                  </div>
                </v-col>

              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 项目时间信息 -->
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card>
            <v-card-title>时间信息</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="3">
                  <div class="text-subtitle-2 mb-1">开始时间</div>
                  <div>{{ formatDate(project.start_time) }}</div>
                </v-col>
                <v-col cols="12" md="3">
                  <div class="text-subtitle-2 mb-1">结束时间</div>
                  <div>{{ formatDate(project.end_time) }}</div>
                </v-col>
                <v-col cols="12" md="3">
                  <div class="text-subtitle-2 mb-1">最后爬取</div>
                  <div>{{ formatDate(project.crawl_time) }}</div>
                </v-col>
                <v-col cols="12" md="3">
                  <div class="text-subtitle-2 mb-1">项目ID</div>
                  <div class="font-family-monospace">{{ project.project_id }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 回报列表 -->
      <v-row v-if="rewards && rewards.length > 0" class="mb-6">
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-gift</v-icon>
              回报列表
              <v-chip class="ml-2" size="small" color="primary">{{ rewards.length }}个档位</v-chip>
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col v-for="(reward, index) in rewards" :key="index" cols="12" md="6" lg="4">
                  <v-card variant="outlined" class="h-100">
                    <v-card-title class="d-flex justify-space-between align-center">
                      <div>¥{{ formatNumber(reward.price || 0) }}</div>
                      <v-chip
                        size="small"
                        :color="reward.is_sold_out ? 'error' : 'success'"
                        variant="tonal"
                      >
                        {{ reward.is_sold_out ? '已售罄' : '可支持' }}
                      </v-chip>
                    </v-card-title>
                    <v-card-text>
                      <div class="font-weight-medium mb-2">{{ reward.title || '未命名档位' }}</div>
                      <div class="text-caption text-medium-emphasis mb-2">{{ reward.content || '无详细描述' }}</div>
                      <div class="d-flex justify-space-between text-caption">
                        <span>
                          <v-icon size="small" color="primary">mdi-account-multiple</v-icon>
                          {{ reward.backer_count || 0 }}人支持
                        </span>
                        <span v-if="reward.is_limited">
                          <v-icon size="small" color="warning">mdi-timer-sand</v-icon>
                          剩余{{ reward.remaining_count || 0 }}个
                        </span>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 历史数据追踪 -->
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-chart-timeline-variant</v-icon>
              历史数据追踪
              <v-spacer></v-spacer>
              <v-btn 
                size="small" 
                @click="loadProjectHistory" 
                :loading="historyLoading"
                prepend-icon="mdi-refresh"
              >
                刷新
              </v-btn>
            </v-card-title>
            <v-card-text>
              <!-- 统计信息 -->
              <div v-if="statistics && statistics.trends" class="mb-4">
                <v-row>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <div class="text-h6 font-weight-bold" 
                           :class="getTrendColor(statistics.trends.raised_amount_growth)">
                        {{ formatGrowth(statistics.trends.raised_amount_growth) }}
                      </div>
                      <div class="text-caption">资金增长率</div>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <div class="text-h6 font-weight-bold"
                           :class="getTrendColor(statistics.trends.backer_count_growth)">
                        {{ formatGrowth(statistics.trends.backer_count_growth) }}
                      </div>
                      <div class="text-caption">支持者增长率</div>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <div class="text-h6 font-weight-bold"
                           :class="getTrendColor(statistics.trends.supporter_count_growth)">
                        {{ formatGrowth(statistics.trends.supporter_count_growth) }}
                      </div>
                      <div class="text-caption">点赞增长率</div>
                    </v-card>
                  </v-col>
                  <v-col cols="6" md="3">
                    <v-card variant="outlined" class="text-center pa-3">
                      <div class="text-h6 font-weight-bold">{{ statistics.total_records || 0 }}</div>
                      <div class="text-caption">历史记录数</div>
                    </v-card>
                  </v-col>
                </v-row>
              </div>

              <!-- 历史记录时间线 -->
              <div v-if="history.length > 0">
                <v-timeline density="compact">
                  <v-timeline-item
                    v-for="(record, index) in history"
                    :key="index"
                    :dot-color="index === 0 ? 'primary' : 'grey'"
                    size="small"
                  >
                    <template v-slot:opposite>
                      <div class="text-caption">
                        {{ formatDate(record.crawl_time) }}
                      </div>
                    </template>
                    
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="py-2">
                        <div class="d-flex justify-space-between align-center">
                          <div>
                            <div class="font-weight-medium">
                              ¥{{ formatNumber(record.raised_amount) }} 
                              <span class="text-caption text-medium-emphasis">
                                ({{ record.completion_rate?.toFixed(1) || 0 }}%)
                              </span>
                            </div>
                            <div class="text-caption">
                              支持者: {{ record.backer_count || 0 }} | 
                              点赞: {{ record.supporter_count || 0 }} | 
                              评论: {{ record.comment_count || 0 }}
                            </div>
                          </div>
                          <div v-if="index < history.length - 1" class="text-right">
                            <div class="text-caption" 
                                 :class="getChangeColor(record.raised_amount - history[index + 1].raised_amount)">
                              {{ formatChange(record.raised_amount - history[index + 1].raised_amount, '¥') }}
                            </div>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-timeline-item>
                </v-timeline>

                <!-- 加载更多按钮 -->
                <div v-if="history.length < totalHistoryCount" class="text-center mt-4">
                  <v-btn 
                    @click="loadMoreHistory" 
                    :loading="historyLoading"
                    variant="outlined"
                  >
                    加载更多历史记录
                  </v-btn>
                </div>
              </div>

              <!-- 无历史数据 -->
              <div v-else-if="!historyLoading" class="text-center py-8">
                <v-icon size="64" color="grey">mdi-history</v-icon>
                <div class="text-h6 mt-2">暂无历史数据</div>
                <div class="text-caption">该项目还没有历史爬取记录</div>
              </div>

              <!-- 历史数据加载状态 -->
              <div v-if="historyLoading" class="text-center py-4">
                <v-progress-circular indeterminate size="32"></v-progress-circular>
                <div class="mt-2">加载历史数据中...</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSnackbar } from '@/composables/useSnackbar'
import axios from 'axios'
import { isValidImageUrl } from '@/utils/imageUtils'

const route = useRoute()
const router = useRouter()
const { showSnackbar } = useSnackbar()

// 响应式数据
const loading = ref(true)
const historyLoading = ref(false)
const exporting = ref(false)
const error = ref('')
const project = ref(null)
const statistics = ref(null)
const history = ref([])
const rewards = ref([])
const totalHistoryCount = ref(0)
const historyOffset = ref(0)
const historyLimit = ref(10)

// 计算属性
const projectId = computed(() => route.params.id)

// 生命周期
onMounted(() => {
  loadProjectDetail()
})

// 方法
async function loadProjectDetail() {
  try {
    loading.value = true
    error.value = ''

    const response = await axios.get(`/api/projects/${projectId.value}/detail`)

    if (response.data.success) {
      project.value = response.data.project
      statistics.value = response.data.statistics

      // 解析回报数据
      parseRewardsData(response.data.project.rewards_data)

      // 加载历史数据
      await loadProjectHistory()
    } else {
      error.value = response.data.message || '加载项目详情失败'
    }
  } catch (err) {
    console.error('加载项目详情失败:', err)
    error.value = err.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function loadProjectHistory() {
  try {
    historyLoading.value = true

    const response = await axios.get(`/api/projects/${projectId.value}/history`, {
      params: {
        limit: historyLimit.value,
        offset: historyOffset.value
      }
    })

    if (response.data.success) {
      if (historyOffset.value === 0) {
        history.value = response.data.history
      } else {
        history.value.push(...response.data.history)
      }
      totalHistoryCount.value = response.data.total_count
    } else {
      showSnackbar(response.data.message || '加载历史数据失败', 'error')
    }
  } catch (err) {
    console.error('加载历史数据失败:', err)
    showSnackbar('加载历史数据失败', 'error')
  } finally {
    historyLoading.value = false
  }
}

async function loadMoreHistory() {
  historyOffset.value += historyLimit.value
  await loadProjectHistory()
}

async function exportProjectData() {
  try {
    exporting.value = true

    const response = await axios.get(`/api/projects/${projectId.value}/export`, {
      responseType: 'blob'
    })

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `project_${projectId.value}_history.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    showSnackbar('数据导出成功', 'success')
  } catch (err) {
    console.error('导出数据失败:', err)
    showSnackbar('导出数据失败', 'error')
  } finally {
    exporting.value = false
  }
}

function parseRewardsData(rewardsDataStr) {
  try {
    rewards.value = []

    if (!rewardsDataStr || rewardsDataStr === 'none' || rewardsDataStr === '[]' || rewardsDataStr === '') {
      return
    }

    // 根据爬虫代码分析，rewards_data实际存储的是回报数量，不是具体的回报数据
    // 爬虫存储格式：[str(rewards_list), len(rewards_list)]
    // 其中rewards_list包含的是字符串化的回报数据

    // 如果只是数字，说明这是回报数量，而不是具体的回报数据
    if (/^\d+$/.test(rewardsDataStr.toString().trim())) {
      const rewardCount = parseInt(rewardsDataStr)
      if (rewardCount > 0) {
        // 创建占位符回报数据
        rewards.value = Array.from({ length: Math.min(rewardCount, 10) }, (_, index) => ({
          id: index,
          price: 0,
          backer_count: 0,
          title: `回报档位 ${index + 1}`,
          content: '回报详情需要重新爬取获取',
          time_info: '',
          is_limited: false,
          remaining_count: 0,
          is_sold_out: false
        }))
        console.log(`发现 ${rewardCount} 个回报档位，但详细数据需要重新爬取`)
        return
      }
    }

    // 尝试解析复杂的回报数据格式
    let rewardsData

    if (typeof rewardsDataStr === 'string') {
      // 处理字符串化的数组格式
      if (rewardsDataStr.startsWith('[') && rewardsDataStr.endsWith(']')) {
        try {
          rewardsData = JSON.parse(rewardsDataStr)
        } catch {
          // 如果JSON解析失败，尝试其他方式
          const matches = rewardsDataStr.match(/\[([^\]]+)\]/g)
          if (matches) {
            rewardsData = matches.map(match => {
              try {
                return JSON.parse(match)
              } catch {
                return match.slice(1, -1).split(',').map(s => s.trim().replace(/['"]/g, ''))
              }
            })
          }
        }
      }
    } else if (Array.isArray(rewardsDataStr)) {
      rewardsData = rewardsDataStr
    }

    if (rewardsData && Array.isArray(rewardsData)) {
      rewards.value = rewardsData.map((reward, index) => {
        if (Array.isArray(reward) && reward.length >= 6) {
          // 处理爬虫格式：[title, sign_logo, back_money, backers, time_info, detail]
          const [title, sign_logo, back_money, backers, time_info, detail] = reward
          return {
            id: index,
            title: title !== 'none' ? title : `回报档位 ${index + 1}`,
            price: parseFloat(back_money) || 0,
            backer_count: backers === '已满' ? '已满' : (parseInt(backers) || 0),
            content: detail !== 'none' ? detail : '无详细描述',
            time_info: time_info !== 'none' ? time_info : '',
            is_limited: sign_logo.includes('限量'),
            remaining_count: 0,
            is_sold_out: backers === '已满'
          }
        } else if (typeof reward === 'object') {
          // 处理对象格式的回报数据
          return {
            id: reward.id || index,
            price: parseFloat(reward.price || reward.money || 0),
            backer_count: parseInt(reward.backer_count || reward.back_count || 0),
            title: reward.title || reward.name || `回报档位 ${index + 1}`,
            content: reward.content || reward.description || '无详细描述',
            is_limited: reward.max_total > 0,
            remaining_count: Math.max(0, (reward.max_total || 0) - (reward.backer_count || 0)),
            is_sold_out: reward.status === 'sold_out' || reward.backer_count >= reward.max_total
          }
        }
        return null
      }).filter(Boolean)
    }

    console.log('解析回报数据:', rewards.value)
  } catch (error) {
    console.warn('解析回报数据失败:', error, rewardsDataStr)
    rewards.value = []
  }
}

// 工具函数
function formatNumber(num) {
  if (!num) return '0'
  return new Intl.NumberFormat('zh-CN').format(num)
}

function formatDate(dateStr) {
  if (!dateStr) return '未知'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

function formatGrowth(growth) {
  if (growth === undefined || growth === null) return '0%'
  const sign = growth >= 0 ? '+' : ''
  return `${sign}${growth.toFixed(1)}%`
}

function formatChange(change, prefix = '') {
  if (!change) return '无变化'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${prefix}${formatNumber(Math.abs(change))}`
}

function getTrendColor(value) {
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-error'
  return 'text-medium-emphasis'
}

function getChangeColor(value) {
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-error'
  return 'text-medium-emphasis'
}

function getStatusColor(status) {
  switch (status) {
    case '成功': return 'success'
    case '失败': return 'error'
    case '进行中': return 'primary'
    default: return 'grey'
  }
}


</script>

<style scoped>
.font-family-monospace {
  font-family: 'Courier New', monospace;
}

.v-timeline-item {
  padding-bottom: 8px;
}
</style>
