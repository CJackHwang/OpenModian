<template>
  <v-app>
    <!-- 顶部应用栏 -->
    <v-app-bar
      elevation="2"
      color="surface"
      class="px-4"
    >
      <v-app-bar-nav-icon
        @click="toggleLeftDrawer"
        color="primary"
      />

      <v-toolbar-title class="app-title text-primary">
        <v-icon icon="mdi-bug" class="me-3" size="large" />
        <span class="text-h6 font-weight-medium">摩点爬虫管理系统</span>
      </v-toolbar-title>

      <v-spacer />

      <!-- 连接状态 -->
      <v-chip
        :color="connectionStatus ? 'success' : 'error'"
        :prepend-icon="connectionStatus ? 'mdi-wifi' : 'mdi-wifi-off'"
        :text="connectionStatus ? '已连接' : '连接断开'"
        class="me-4"
        size="small"
        variant="flat"
      />

      <!-- 主题切换 -->
      <v-btn
        :icon="isDark ? 'mdi-white-balance-sunny' : 'mdi-weather-night'"
        @click="toggleTheme"
        variant="text"
        class="me-2"
      />

      <!-- 刷新按钮 -->
      <v-btn
        icon="mdi-refresh"
        @click="refreshData"
        variant="text"
      />
    </v-app-bar>

    <!-- 左侧导航抽屉 -->
    <v-navigation-drawer
      v-model="leftDrawerOpen"
      :width="280"
      color="surface-variant"
      class="elevation-1"
    >
      <!-- 抽屉头部 -->
      <div class="pa-6 bg-primary-container text-on-primary-container">
        <div class="d-flex align-center">
          <v-icon icon="mdi-bug" size="x-large" class="me-4" />
          <div>
            <div class="text-h6 font-weight-medium">摩点爬虫</div>
            <div class="text-caption opacity-70">管理系统</div>
          </div>
        </div>
      </div>

      <!-- 导航列表 -->
      <v-list class="pa-4" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          class="mb-2 nav-item"
          rounded="xl"
          color="primary"
        />
      </v-list>
    </v-navigation-drawer>

    <!-- 主内容区域 -->
    <v-main class="bg-background">
      <v-container fluid class="pa-6">
        <div class="page-content">
          <router-view />
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const theme = useTheme()
const appStore = useAppStore()

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
  max-width: 1200px;
  margin: 0 auto;
}

.nav-item {
  margin-bottom: 8px;
}

.opacity-70 {
  opacity: 0.7;
}
</style>