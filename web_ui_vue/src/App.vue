<template>
  <q-layout view="lHh Lpr lFf">
    <!-- 顶部工具栏 -->
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title class="app-title">
          <q-icon name="bug_report" class="q-mr-sm" />
          摩点爬虫管理系统
        </q-toolbar-title>

        <!-- 连接状态 -->
        <q-chip
          :color="connectionStatus ? 'positive' : 'negative'"
          text-color="white"
          :icon="connectionStatus ? 'wifi' : 'wifi_off'"
          :label="connectionStatus ? '已连接' : '连接断开'"
          class="q-mr-sm"
        />

        <!-- 主题切换 -->
        <q-btn
          flat
          dense
          round
          :icon="isDark ? 'light_mode' : 'dark_mode'"
          @click="toggleTheme"
          class="q-mr-sm"
        />

        <!-- 刷新按钮 -->
        <q-btn
          flat
          dense
          round
          icon="refresh"
          @click="refreshData"
        />
      </q-toolbar>
    </q-header>

    <!-- 左侧抽屉 -->
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      class="bg-grey-1"
    >
      <q-list>
        <q-item-label header class="text-grey-8">
          <q-icon name="bug_report" class="q-mr-sm" />
          导航菜单
        </q-item-label>

        <q-item
          v-for="item in menuItems"
          :key="item.title"
          clickable
          v-ripple
          :active="$route.path === item.to"
          @click="navigateTo(item.to)"
        >
          <q-item-section avatar>
            <q-icon :name="item.icon" />
          </q-item-section>

          <q-item-section>
            <q-item-label>{{ item.title }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <!-- 主内容区域 -->
    <q-page-container>
      <q-page padding>
        <router-view />
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

// 计算连接状态
const connectionStatus = computed(() => appStore.connectionStatus)

// 响应式数据
const leftDrawerOpen = ref(false)
const isDark = ref(false)

// 菜单项
const menuItems = [
  {
    title: '仪表板',
    icon: 'dashboard',
    to: '/'
  },
  {
    title: '爬虫控制',
    icon: 'bug_report',
    to: '/spider'
  },
  {
    title: '数据管理',
    icon: 'storage',
    to: '/data'
  },
  {
    title: '任务历史',
    icon: 'history',
    to: '/history'
  },
  {
    title: '系统设置',
    icon: 'settings',
    to: '/settings'
  }
]

// 方法
const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  // 使用Quasar的主题切换
  import('quasar').then(({ Dark }) => {
    Dark.set(isDark.value)
  })
}

const navigateTo = (path) => {
  router.push(path)
  leftDrawerOpen.value = false
}

const refreshData = () => {
  // 刷新数据逻辑
  import('quasar').then(({ Notify }) => {
    Notify.create({
      message: '数据已刷新',
      color: 'positive',
      position: 'top'
    })
  })
}

// 生命周期
onMounted(() => {
  // 初始化应用
  appStore.initialize()
})
</script>

<style scoped>
.app-title {
  display: flex;
  align-items: center;
  font-weight: 500;
}
</style>
