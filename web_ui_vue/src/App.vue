<template>
  <v-app>
    <!-- 顶部应用栏 - M3风格 -->
    <v-app-bar
      elevation="1"
      color="surface-container"
      class="px-6"
      height="72"
    >
      <v-app-bar-nav-icon
        @click="toggleLeftDrawer"
        color="primary"
        class="rounded-lg"
      />

      <v-toolbar-title class="app-title text-primary ms-4">
        <v-icon icon="mdi-bug" class="me-3" size="32" />
        <span class="text-title-large font-weight-medium">摩点爬虫管理系统</span>
      </v-toolbar-title>

      <v-spacer />

      <!-- 连接状态 -->
      <v-chip
        :color="connectionStatus ? 'success' : 'error'"
        :prepend-icon="connectionStatus ? 'mdi-wifi' : 'mdi-wifi-off'"
        :text="connectionStatus ? '已连接' : '连接断开'"
        class="me-4 elevation-1"
        size="small"
        variant="elevated"
      />

      <!-- 主题切换 -->
      <v-btn
        :icon="isDark ? 'mdi-white-balance-sunny' : 'mdi-weather-night'"
        @click="toggleTheme"
        variant="text"
        class="me-2 rounded-lg"
        size="large"
      />

      <!-- 刷新按钮 -->
      <v-btn
        icon="mdi-refresh"
        @click="refreshData"
        variant="text"
        class="rounded-lg"
        size="large"
      />
    </v-app-bar>

    <!-- 左侧导航抽屉 - M3风格 -->
    <v-navigation-drawer
      v-model="leftDrawerOpen"
      :width="320"
      color="surface-container-low"
      class="elevation-0"
      :border="0"
    >
      <!-- 抽屉头部 -->
      <div class="pa-8 bg-primary-container text-on-primary-container rounded-b-xl">
        <div class="d-flex align-center">
          <div class="icon-container me-4">
            <v-icon icon="mdi-bug" size="40" />
          </div>
          <div>
            <div class="text-title-large font-weight-medium">摩点爬虫</div>
            <div class="text-body-medium opacity-80">管理系统</div>
          </div>
        </div>
      </div>

      <!-- 导航列表 -->
      <v-list class="pa-6" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          class="mb-3 nav-item elevation-0"
          rounded="xl"
          color="primary"
          height="56"
        />
      </v-list>
    </v-navigation-drawer>

    <!-- 主内容区域 - M3风格 -->
    <v-main class="bg-background">
      <v-container fluid class="responsive-container">
        <div class="page-content">
          <router-view />
        </div>
      </v-container>
    </v-main>

    <!-- 全局Snackbar - M3风格 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
      variant="elevated"
      class="rounded-xl elevation-3"
      min-width="320"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn
          color="on-surface"
          variant="text"
          @click="hideSnackbar"
          class="rounded-lg"
        >
          关闭
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTheme } from 'vuetify'
import { useAppStore } from '@/stores/app'
import { useSnackbar } from '@/composables/useSnackbar'

const theme = useTheme()
const appStore = useAppStore()
const { snackbar, hideSnackbar } = useSnackbar()

// 响应式数据
const leftDrawerOpen = ref(false)
const isDark = ref(false)

// 菜单项
const menuItems = [
  {
    title: '仪表板',
    icon: 'mdi-view-dashboard',
    to: '/'
  },
  {
    title: '爬虫控制',
    icon: 'mdi-spider',
    to: '/spider'
  },
  {
    title: '数据管理',
    icon: 'mdi-database',
    to: '/data'
  },
  {
    title: '高级数据管理',
    icon: 'mdi-database-edit',
    to: '/data/advanced'
  },
  {
    title: '任务历史',
    icon: 'mdi-history',
    to: '/history'
  },
  {
    title: '系统设置',
    icon: 'mdi-cog',
    to: '/settings'
  }
]

// 计算属性
const connectionStatus = computed(() => appStore.connectionStatus)

// 方法
const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  theme.global.name.value = isDark.value ? 'dark' : 'light'
  // 保存主题设置到localStorage
  localStorage.setItem('theme', theme.global.name.value)
}

const refreshData = () => {
  appStore.refreshData()
}

// 初始化主题
const initializeTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.global.name.value = savedTheme
    isDark.value = savedTheme === 'dark'
  } else {
    // 默认使用浅色主题
    theme.global.name.value = 'light'
    isDark.value = false
    localStorage.setItem('theme', 'light')
  }
}

// 生命周期
onMounted(() => {
  initializeTheme()
  appStore.initializeSocket()
  appStore.refreshData()
})
</script>

<style scoped>
.app-title {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.page-content {
  width: 100%;
  margin: 0 auto;
}

/* 超大屏幕：最大信息密度 */
@media (min-width: 2560px) {
  .page-content {
    max-width: 2400px;
    padding: 0 40px;
  }
}

/* 超大屏幕：高信息密度 */
@media (min-width: 1920px) and (max-width: 2559px) {
  .page-content {
    max-width: 1800px;
    padding: 0 32px;
  }
}

/* 大屏幕：标准信息密度 */
@media (min-width: 1264px) and (max-width: 1919px) {
  .page-content {
    max-width: 1200px;
    padding: 0 24px;
  }
}

/* 中等屏幕：适中信息密度 */
@media (min-width: 960px) and (max-width: 1263px) {
  .page-content {
    max-width: 900px;
    padding: 0 20px;
  }
}

/* 平板：舒适间距 */
@media (min-width: 600px) and (max-width: 959px) {
  .page-content {
    max-width: 100%;
    padding: 0 16px;
  }
}

/* 手机：大间距 */
@media (max-width: 599px) {
  .page-content {
    max-width: 100%;
    padding: 0 12px;
  }
}

.nav-item {
  margin-bottom: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateX(4px);
  }
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

/* 响应式图标容器 */
@media (min-width: 1920px) {
  .icon-container {
    width: 64px;
    height: 64px;
    border-radius: 18px;
  }
}

@media (max-width: 600px) {
  .icon-container {
    width: 48px;
    height: 48px;
    border-radius: 14px;
  }
}

.opacity-80 {
  opacity: 0.8;
}

/* M3 响应式文本 */
@media (min-width: 1920px) {
  .app-title .text-title-large {
    font-size: 1.5rem;
  }
}

@media (max-width: 600px) {
  .app-title .text-title-large {
    font-size: 1.125rem;
  }
}
</style>