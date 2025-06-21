<template>
  <v-app>
    <!-- 顶部应用栏 -->
    <v-app-bar
      elevation="1"
      class="app-bar"
      :height="appBarHeight"
    >
      <template #prepend>
        <v-app-bar-nav-icon
          @click="toggleLeftDrawer"
          class="nav-icon"
          :size="navIconSize"
        />
      </template>

      <v-toolbar-title class="app-title">
        <div class="d-flex align-center">
          <v-avatar color="primary" class="me-3" :size="titleIconSize">
            <v-icon icon="mdi-bug" />
          </v-avatar>
          <div class="title-text">
            <span class="font-weight-medium d-none d-sm-inline">
              摩点爬虫管理系统
            </span>
            <span class="font-weight-medium d-inline d-sm-none">
              摩点爬虫
            </span>
          </div>
        </div>
      </v-toolbar-title>

      <v-spacer />

      <div class="d-flex align-center app-actions">
        <!-- 连接状态 -->
        <v-chip
          :color="connectionStatus ? 'success' : 'error'"
          :prepend-icon="connectionStatus ? 'mdi-wifi' : 'mdi-wifi-off'"
          :text="connectionStatus ? '已连接' : '连接断开'"
          class="me-2 status-chip"
          :size="chipSize"
        />

        <!-- 主题切换 -->
        <v-btn
          @click="toggleTheme"
          variant="text"
          class="me-2 theme-toggle"
          :size="actionButtonSize"
          icon
        >
          <v-icon>{{ isDark ? 'mdi-white-balance-sunny' : 'mdi-weather-night' }}</v-icon>
          <v-tooltip activator="parent" location="bottom">
            {{ isDark ? '切换到浅色主题' : '切换到深色主题' }}
          </v-tooltip>
        </v-btn>

        <!-- 智能刷新按钮 -->
        <v-btn
          @click="smartRefresh"
          :loading="refreshing"
          variant="text"
          class="refresh-button"
          :size="actionButtonSize"
          :color="connectionStatus ? 'primary' : 'error'"
          :disabled="refreshing"
          icon
        >
          <v-icon>{{ connectionStatus ? 'mdi-refresh' : 'mdi-wifi-off' }}</v-icon>
          <v-tooltip activator="parent" location="bottom">
            {{ connectionStatus ? '刷新数据' : '重新连接并刷新' }}
          </v-tooltip>
        </v-btn>
      </div>
    </v-app-bar>

    <!-- 左侧导航抽屉 -->
    <v-navigation-drawer
      v-model="leftDrawerOpen"
      :width="drawerWidth"
      class="navigation-drawer"
      :temporary="isMobile"
      :permanent="!isMobile"
    >
      <!-- 抽屉头部 -->
      <div class="pa-6">
        <div class="d-flex align-center">
          <v-avatar color="primary" class="me-4" :size="drawerIconSize">
            <v-icon icon="mdi-bug" />
          </v-avatar>
          <div class="drawer-title-container">
            <div class="text-h6 font-weight-medium">摩点爬虫</div>
            <div class="text-body-2 opacity-80">管理系统</div>
          </div>
        </div>
      </div>

      <!-- 导航列表 -->
      <v-list class="navigation-list" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          class="nav-item"
          color="primary"
          :height="navItemHeight"
          @click="isMobile && (leftDrawerOpen = false)"
        >
          <template #prepend>
            <v-icon :icon="item.icon" :size="navItemIconSize" />
          </template>
        </v-list-item>
      </v-list>

      <!-- 抽屉底部信息 -->
      <template #append>
        <div class="drawer-footer">
          <v-divider class="mb-4" />
          <div class="px-6 pb-4">
            <div class="text-caption">
              版本 1.0.0
            </div>
            <div class="text-caption">
              © 2024 摩点爬虫系统
            </div>
          </div>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- 主内容区域 -->
    <v-main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </v-main>

    <!-- 全局Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
      min-width="320"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="hideSnackbar"
        >
          关闭
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTheme, useDisplay } from 'vuetify'
import { useAppStore } from '@/stores/app'
import { useSnackbar } from '@/composables/useSnackbar'

const theme = useTheme()
const display = useDisplay()
const appStore = useAppStore()
const { snackbar, hideSnackbar } = useSnackbar()

// 响应式数据
const leftDrawerOpen = ref(false)
const isDark = ref(false)
const refreshing = ref(false)

// 响应式计算属性
const isMobile = computed(() => display.mobile.value)

// 响应式尺寸计算
const appBarHeight = computed(() => {
  if (display.xs.value) return 56
  if (display.sm.value) return 64
  return 72
})

const drawerWidth = computed(() => {
  if (display.xs.value) return 280
  if (display.sm.value) return 300
  return 320
})

const navIconSize = computed(() => {
  if (display.xs.value) return 20
  if (display.sm.value) return 24
  return 28
})

const titleIconSize = computed(() => {
  if (display.xs.value) return 24
  if (display.sm.value) return 28
  return 32
})

const actionButtonSize = computed(() => {
  if (display.xs.value) return 'small'
  if (display.sm.value) return 'default'
  return 'large'
})

const chipSize = computed(() => {
  if (display.xs.value) return 'x-small'
  if (display.sm.value) return 'small'
  return 'small'
})

const drawerIconSize = computed(() => {
  if (display.xs.value) return 32
  if (display.sm.value) return 36
  return 40
})

const navItemHeight = computed(() => {
  if (display.xs.value) return 48
  if (display.sm.value) return 52
  return 56
})

const navItemIconSize = computed(() => {
  if (display.xs.value) return 20
  if (display.sm.value) return 22
  return 24
})

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
    title: '任务管理',
    icon: 'mdi-format-list-bulleted',
    to: '/tasks'
  },
  {
    title: '任务历史',
    icon: 'mdi-history',
    to: '/history'
  },
  {
    title: '实时日志',
    icon: 'mdi-console-line',
    to: '/logs'
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

const smartRefresh = async () => {
  if (refreshing.value) return

  refreshing.value = true
  console.log('🔄 智能刷新开始')

  try {
    if (!connectionStatus.value) {
      // 如果WebSocket未连接，先重连
      console.log('🔄 WebSocket未连接，正在重连...')
      await appStore.initializeSocket()
      console.log('✅ WebSocket重连成功')
    }

    // 刷新数据
    console.log('🔄 正在刷新数据...')
    await appStore.refreshData()
    console.log('✅ 数据刷新成功')

  } catch (error) {
    console.error('❌ 智能刷新失败:', error)
  } finally {
    refreshing.value = false
  }
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
/* 基础布局样式 */
.app-title {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.title-text {
  line-height: 1.2;
}

.app-actions {
  gap: 8px;
}

.drawer-title-container {
  flex: 1;
}

.navigation-list {
  padding: 0 16px;
}

.nav-item {
  margin-bottom: 8px;
}

.drawer-footer {
  margin-top: auto;
}

.main-content {
  min-height: 100vh;
}

.content-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;

  @media (max-width: 960px) {
    padding: 16px;
  }
}

.opacity-80 {
  opacity: 0.8;
}
</style>