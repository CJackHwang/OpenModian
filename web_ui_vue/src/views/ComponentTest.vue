<template>
  <div class="component-test-page">
    <v-container fluid>
      <!-- 页面标题 -->
      <v-row class="mb-4">
        <v-col>
          <div class="d-flex align-center">
            <v-avatar color="primary" class="me-4" size="48">
              <v-icon icon="mdi-test-tube" />
            </v-avatar>
            <div>
              <h1 class="text-h4 font-weight-bold">组件测试</h1>
              <p class="text-subtitle-1 text-medium-emphasis">
                测试RealTimeLogViewer组件的响应式布局和功能
              </p>
            </div>
          </div>
        </v-col>
      </v-row>

      <!-- 测试控制面板 -->
      <v-row class="mb-4">
        <v-col cols="12">
          <v-card elevation="2">
            <v-card-title>
              <v-icon icon="mdi-cog" class="me-2" />
              测试控制
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" sm="6" md="3">
                  <v-select
                    v-model="testHeight"
                    :items="heightOptions"
                    label="组件高度"
                    variant="outlined"
                    density="compact"
                  />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-switch
                    v-model="compactMode"
                    label="紧凑模式"
                    color="primary"
                    hide-details
                  />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-switch
                    v-model="autoScroll"
                    label="自动滚动"
                    color="primary"
                    hide-details
                  />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-btn
                    color="primary"
                    variant="outlined"
                    @click="sendTestLog"
                    block
                  >
                    发送测试日志
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 单个组件测试 -->
      <v-row class="mb-4">
        <v-col cols="12">
          <v-card elevation="2">
            <v-card-title>
              单个组件测试 - 高度: {{ testHeight }}
            </v-card-title>
            <v-card-text class="pa-2">
              <RealTimeLogViewer
                :height="testHeight"
                :min-height="'200px'"
                :max-height="'800px'"
                :max-logs="200"
                :auto-scroll="autoScroll"
                :compact="compactMode"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 多组件布局测试 -->
      <v-row>
        <v-col cols="12" md="6">
          <v-card elevation="2">
            <v-card-title>
              左侧组件 - 自适应高度
            </v-card-title>
            <v-card-text class="pa-2">
              <RealTimeLogViewer
                height="auto"
                :min-height="'250px'"
                :max-height="'400px'"
                :max-logs="100"
                :auto-scroll="true"
                :compact="display.xs.value"
              />
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card elevation="2">
            <v-card-title>
              右侧组件 - 固定高度
            </v-card-title>
            <v-card-text class="pa-2">
              <RealTimeLogViewer
                height="350px"
                :max-logs="100"
                :auto-scroll="true"
                :compact="display.xs.value"
              />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 屏幕尺寸信息 -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card elevation="1">
            <v-card-text>
              <div class="text-caption">
                <strong>当前屏幕信息:</strong>
                宽度: {{ display.width.value }}px |
                高度: {{ display.height.value }}px |
                断点: {{ currentBreakpoint }} |
                移动设备: {{ display.mobile.value ? '是' : '否' }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useAppStore } from '@/stores/app'
import RealTimeLogViewer from '@/components/RealTimeLogViewer.vue'

const display = useDisplay()
const appStore = useAppStore()

// 响应式数据
const testHeight = ref('400px')
const compactMode = ref(false)
const autoScroll = ref(true)

// 配置选项
const heightOptions = [
  { title: '自适应', value: 'auto' },
  { title: '300px', value: '300px' },
  { title: '400px', value: '400px' },
  { title: '500px', value: '500px' },
  { title: '600px', value: '600px' },
  { title: '50vh', value: '50vh' },
  { title: '70vh', value: '70vh' }
]

// 计算属性
const currentBreakpoint = computed(() => {
  if (display.xs.value) return 'xs (< 600px)'
  if (display.sm.value) return 'sm (600-960px)'
  if (display.md.value) return 'md (960-1264px)'
  if (display.lg.value) return 'lg (1264-1904px)'
  if (display.xl.value) return 'xl (1904-2560px)'
  return 'xxl (> 2560px)'
})

// 方法
const sendTestLog = () => {
  if (!appStore.socket || !appStore.socket.connected) {
    console.warn('WebSocket未连接，无法发送测试日志')
    return
  }

  const levels = ['info', 'warning', 'error', 'debug']
  const level = levels[Math.floor(Math.random() * levels.length)]
  const messages = [
    '这是一条测试日志消息',
    '组件响应式测试进行中',
    '检查布局是否正常显示',
    '验证高度设置是否生效',
    '测试多组件组合布局'
  ]
  const message = messages[Math.floor(Math.random() * messages.length)]

  appStore.socket.emit('log_manual', {
    log_type: 'system',
    level: level,
    message: `[测试] ${message} - ${new Date().toLocaleTimeString()}`,
    source: 'component-test'
  })
}
</script>

<style scoped>
.component-test-page {
  min-height: 100vh;
}
</style>
