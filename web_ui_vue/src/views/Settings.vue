<template>
  <div>
    <!-- 页面标题 - 统一设计 -->
    <div class="app-section">
      <div class="d-flex align-center">
        <v-avatar
          color="primary"
          class="me-4"
          size="64"
        >
          <v-icon icon="mdi-cog" size="32" />
        </v-avatar>
        <div>
          <h1 class="text-h4 font-weight-medium mb-1">
            系统设置
          </h1>
          <p class="text-subtitle-1 text-medium-emphasis">
            配置系统参数和用户偏好
          </p>
        </div>
      </div>
    </div>

    <v-row>
      <!-- 外观设置 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4 app-card">
          <v-card-title class="p-lg">
            <v-avatar color="tertiary" size="32" class="me-3">
              <v-icon icon="mdi-palette" color="on-tertiary" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">外观设置</div>
              <div class="text-body-2 text-medium-emphasis">自定义界面外观</div>
            </div>
          </v-card-title>

          <v-card-text class="p-lg pt-0">
            <v-row>
              <v-col cols="12">
                <v-switch
                  v-model="darkMode"
                  label="深色模式"
                  color="primary"
                  @change="toggleTheme"
                />
              </v-col>

              <v-col cols="12">
                <!-- 重置按钮 -->
                <v-btn
                  variant="outlined"
                  color="secondary"
                  @click="resetTheme"
                  class="mt-2"
                >
                  <v-icon start>mdi-restore</v-icon>
                  重置为默认主题
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 系统信息 -->
        <v-card class="app-card">
          <v-card-title class="p-lg">
            <v-avatar color="info" size="32" class="me-3">
              <v-icon icon="mdi-information" color="on-info" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">系统信息</div>
              <div class="text-body-2 text-medium-emphasis">查看系统版本信息</div>
            </div>
          </v-card-title>

          <v-card-text class="p-lg pt-0">
            <v-list>
              <v-list-item>
                <v-list-item-title>版本</v-list-item-title>
                <v-list-item-subtitle>v1.0.0</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>前端框架</v-list-item-title>
                <v-list-item-subtitle>Vue 3 + Vuetify 3</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>后端框架</v-list-item-title>
                <v-list-item-subtitle>Flask + SocketIO</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 爬虫设置 -->
      <v-col cols="12" md="6">
        <v-card class="app-card">
          <v-card-title class="p-lg">
            <v-avatar color="warning" size="32" class="me-3">
              <v-icon icon="mdi-spider" color="on-warning" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">爬虫默认设置</div>
              <div class="text-body-2 text-medium-emphasis">配置爬虫默认参数</div>
            </div>
          </v-card-title>

          <v-card-text class="p-lg pt-0">
            <v-form>
              <v-text-field
                v-model.number="defaultSettings.maxConcurrent"
                label="默认并发数"
                type="number"
                min="1"
                max="10"
              />
              
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="defaultSettings.delayMin"
                    label="最小延迟(秒)"
                    type="number"
                    min="0.5"
                    step="0.1"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="defaultSettings.delayMax"
                    label="最大延迟(秒)"
                    type="number"
                    min="0.5"
                    step="0.1"
                  />
                </v-col>
              </v-row>
              
              <v-select
                v-model="defaultSettings.category"
                :items="categories"
                item-title="label"
                item-value="value"
                label="默认分类"
              />
              
              <div class="d-flex ga-2 mt-4">
                <v-btn
                  color="primary"
                  @click="saveSettings"
                  :loading="saveLoading"
                  :disabled="loading"
                  class="app-button"
                >
                  {{ showSaveSuccess ? '已保存' : '保存设置' }}
                </v-btn>

                <v-btn
                  variant="outlined"
                  @click="resetSettings"
                  :loading="loading"
                  :disabled="saveLoading"
                  class="app-button"
                >
                  重置默认
                </v-btn>
              </div>

              <v-alert
                v-if="showSaveSuccess"
                type="success"
                variant="tonal"
                class="mt-4"
                closable
                @click:close="showSaveSuccess = false"
              >
                设置已保存成功！
              </v-alert>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import axios from 'axios'

const theme = useTheme()

// 响应式数据
const darkMode = ref(false)
const showSaveSuccess = ref(false)
const loading = ref(false)
const saveLoading = ref(false)

const defaultSettings = reactive({
  maxConcurrent: 3,
  delayMin: 1,
  delayMax: 3,
  category: 'all'
})

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



// 方法
const toggleTheme = () => {
  theme.global.name.value = darkMode.value ? 'dark' : 'light'
  localStorage.setItem('theme', theme.global.name.value)
}

const resetTheme = () => {
  darkMode.value = false
  theme.global.name.value = 'light'
  localStorage.setItem('theme', 'light')
}

const saveSettings = async () => {
  saveLoading.value = true
  try {
    // 保存爬虫设置到后端
    const spiderSettings = {
      spider_max_concurrent: defaultSettings.maxConcurrent,
      spider_delay_min: defaultSettings.delayMin,
      spider_delay_max: defaultSettings.delayMax,
      spider_category: defaultSettings.category
    }

    const response = await axios.post('/api/settings', {
      settings: spiderSettings
    })

    if (response.data.success) {
      showSaveSuccess.value = true
      setTimeout(() => {
        showSaveSuccess.value = false
      }, 3000)
    } else {
      throw new Error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    // 显示错误提示
    showSaveSuccess.value = false
  } finally {
    saveLoading.value = false
  }
}

const resetSettings = async () => {
  loading.value = true
  try {
    const response = await axios.post('/api/settings/reset')
    if (response.data.success) {
      // 重新加载设置
      await loadSettings()
    } else {
      throw new Error(response.data.message || '重置失败')
    }
  } catch (error) {
    console.error('重置设置失败:', error)
  } finally {
    loading.value = false
  }
}

const loadSettings = async () => {
  loading.value = true
  try {
    // 加载主题设置
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      darkMode.value = savedTheme === 'dark'
    } else {
      darkMode.value = theme.global.name.value === 'dark'
    }

    // 从后端加载爬虫设置
    const response = await axios.get('/api/settings')
    if (response.data.success) {
      const settings = response.data.settings

      // 更新爬虫设置
      defaultSettings.maxConcurrent = settings.spider_max_concurrent || 3
      defaultSettings.delayMin = settings.spider_delay_min || 1
      defaultSettings.delayMax = settings.spider_delay_max || 3
      defaultSettings.category = settings.spider_category || 'all'
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    // 使用默认值
    defaultSettings.maxConcurrent = 3
    defaultSettings.delayMin = 1
    defaultSettings.delayMax = 3
    defaultSettings.category = 'all'
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
/* 样式现在完全由Vuetify defaults配置管理 - 遵循官方文档最佳实践 */
</style>
