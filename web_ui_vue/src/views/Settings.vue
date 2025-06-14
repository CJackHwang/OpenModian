<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-4">
      <v-col>
        <h1 class="text-h4 font-weight-bold text-primary">
          <v-icon class="me-2">mdi-cog</v-icon>
          系统设置
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          配置系统参数和用户偏好
        </p>
      </v-col>
    </v-row>

    <v-row>
      <!-- 外观设置 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon class="me-2">mdi-palette</v-icon>
            外观设置
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-switch
                  v-model="darkMode"
                  label="深色模式"
                  color="primary"
                  @change="toggleTheme"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 系统信息 -->
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-information</v-icon>
            系统信息
          </v-card-title>
          
          <v-card-text>
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
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-spider</v-icon>
            爬虫默认设置
          </v-card-title>
          
          <v-card-text>
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
                >
                  保存设置
                </v-btn>
                
                <v-btn
                  variant="outlined"
                  @click="resetSettings"
                >
                  重置默认
                </v-btn>
              </div>
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

const theme = useTheme()

// 响应式数据
const darkMode = ref(false)

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

const saveSettings = () => {
  localStorage.setItem('defaultSettings', JSON.stringify(defaultSettings))
  // 显示保存成功提示
}

const resetSettings = () => {
  defaultSettings.maxConcurrent = 3
  defaultSettings.delayMin = 1
  defaultSettings.delayMax = 3
  defaultSettings.category = 'all'
}

const loadSettings = () => {
  // 加载主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.global.name.value = savedTheme
    darkMode.value = savedTheme === 'dark'
  }

  // 加载默认设置
  const savedSettings = localStorage.getItem('defaultSettings')
  if (savedSettings) {
    Object.assign(defaultSettings, JSON.parse(savedSettings))
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})
</script>
