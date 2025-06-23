<template>
  <v-app>
    <!-- 顶部应用栏 - 统一设计 -->
    <v-app-bar class="app-bar" :height="appBarHeight">
      <template #prepend>
        <v-app-bar-nav-icon
          @click="toggleLeftDrawer"
          class="nav-icon app-button"
          :size="navIconSize"
        />
      </template>

      <v-toolbar-title class="app-title">
        <v-sheet class="d-flex align-center" color="transparent">
          <v-avatar color="primary" class="me-3" :size="titleIconSize">
            <v-icon icon="mdi-spider" />
          </v-avatar>
          <v-sheet class="title-text" color="transparent">
            <v-chip class="text-h6 font-weight-medium d-none d-sm-inline" variant="text" color="on-surface">
              摩点网爬虫管理系统
            </v-chip>
            <v-chip class="text-h6 font-weight-medium d-inline d-sm-none" variant="text" color="on-surface">
              摩点爬虫
            </v-chip>
          </v-sheet>
        </v-sheet>
      </v-toolbar-title>

      <v-spacer />

      <v-sheet class="d-flex align-center app-actions ga-2" color="transparent">
        <!-- 连接状态 -->
        <v-chip
          :color="connectionStatus ? 'success' : 'error'"
          :prepend-icon="connectionStatus ? 'mdi-wifi' : 'mdi-wifi-off'"
          :text="connectionStatus ? '已连接' : '连接断开'"
          class="app-chip"
          :size="chipSize"
        />

        <!-- 主题切换 -->
        <v-btn
          @click="toggleTheme"
          variant="text"
          color="primary"
          class="theme-toggle app-button"
          :size="actionButtonSize"
          icon
        >
          <v-icon>{{
            isDark ? "mdi-white-balance-sunny" : "mdi-weather-night"
          }}</v-icon>
          <v-tooltip activator="parent" location="bottom">
            {{ isDark ? "切换到浅色主题" : "切换到深色主题" }}
          </v-tooltip>
        </v-btn>

        <!-- 智能刷新按钮 -->
        <v-btn
          @click="smartRefresh"
          :loading="refreshing"
          variant="text"
          color="secondary"
          class="refresh-button app-button"
          :size="actionButtonSize"
          :disabled="refreshing"
          icon
        >
          <v-icon>{{
            connectionStatus ? "mdi-refresh" : "mdi-wifi-off"
          }}</v-icon>
          <v-tooltip activator="parent" location="bottom">
            {{ connectionStatus ? "刷新数据" : "重新连接并刷新" }}
          </v-tooltip>
        </v-btn>
      </v-sheet>
    </v-app-bar>

    <!-- 左侧导航抽屉 - 统一设计 -->
    <v-navigation-drawer
      v-model="leftDrawerOpen"
      :width="drawerWidth"
      class="navigation-drawer"
      :temporary="isMobile"
      :permanent="!isMobile"
    >
      <!-- 抽屉头部 -->
      <v-sheet class="p-lg" color="transparent">
        <v-sheet class="d-flex align-center" color="transparent">
          <v-avatar color="primary" class="me-4" :size="drawerIconSize">
            <v-icon icon="mdi-spider" />
          </v-avatar>
          <v-sheet class="drawer-title-container" color="transparent">
            <v-card-text class="text-h6 font-weight-medium pa-0">外星武器</v-card-text>
            <v-card-text class="text-body-2 text-medium-emphasis pa-0">
              摩点酱，你也不想你交易的数据让别人知道吧~
            </v-card-text>
          </v-sheet>
        </v-sheet>
      </v-sheet>

      <!-- 导航列表 -->
      <v-list class="navigation-list px-2" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          class="nav-item mb-1"
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
        <v-sheet class="drawer-footer" color="transparent">
          <v-divider class="mb-4" />
          <v-sheet class="p-lg" color="transparent">
            <v-chip variant="outlined" size="small" class="mb-2 app-chip">
              版本 1.0.0
            </v-chip>
            <v-card-text class="text-caption text-medium-emphasis pa-0">
              © 2025 CJackHwang 数据已经完全变成开发者的形状了 ❤️
            </v-card-text>
          </v-sheet>
        </v-sheet>
      </template>
    </v-navigation-drawer>

    <!-- 主内容区域 - 统一设计 -->
    <v-main class="main-content">
      <v-container class="app-container" fluid>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" class="fade-in-up" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <!-- 全局Snackbar - 统一设计 -->
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
          color="secondary"
          @click="hideSnackbar"
          size="small"
          class="app-button"
        >
          关闭
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useTheme, useDisplay } from "vuetify";
import { useAppStore } from "@/stores/app";
import { useSnackbar } from "@/composables/useSnackbar";
import { useResponsive } from "@/composables/useResponsive";
import { usePerformance } from "@/composables/usePerformance";
import { cleanupMonetThemeData } from "@/utils/themeCleanup";

const theme = useTheme();
const display = useDisplay();
const appStore = useAppStore();
const { snackbar, hideSnackbar } = useSnackbar();
const { getResponsiveSize } = useResponsive();
const { optimizeForDevice } = usePerformance();

// 响应式数据
const leftDrawerOpen = ref(false);
const isDark = ref(false);
const refreshing = ref(false);

// 响应式计算属性
const isMobile = computed(() => display.mobile.value);

// 响应式尺寸计算 - 使用优化的响应式函数
const appBarHeight = computed(() => {
  const config = { xs: 56, sm: 64, md: 72, lg: 72, xl: 72, xxl: 72 };
  if (display.xs.value) return config.xs;
  if (display.sm.value) return config.sm;
  return config.md;
});

const drawerWidth = computed(() => {
  const config = { xs: 280, sm: 300, md: 320, lg: 320, xl: 320, xxl: 320 };
  if (display.xs.value) return config.xs;
  if (display.sm.value) return config.sm;
  return config.md;
});

// 使用响应式组合函数优化图标和按钮尺寸
const navIconSize = getResponsiveSize({
  xs: 20,
  sm: 24,
  md: 28,
  lg: 28,
  xl: 28,
  xxl: 28,
});

const titleIconSize = getResponsiveSize({
  xs: 24,
  sm: 28,
  md: 32,
  lg: 32,
  xl: 32,
  xxl: 32,
});

const actionButtonSize = getResponsiveSize({
  xs: "small",
  sm: "default",
  md: "large",
  lg: "large",
  xl: "large",
  xxl: "large",
});

const chipSize = getResponsiveSize({
  xs: "x-small",
  sm: "small",
  md: "small",
  lg: "small",
  xl: "small",
  xxl: "small",
});

const drawerIconSize = getResponsiveSize({
  xs: 32,
  sm: 36,
  md: 40,
  lg: 40,
  xl: 40,
  xxl: 40,
});

const navItemHeight = getResponsiveSize({
  xs: 48,
  sm: 52,
  md: 56,
  lg: 56,
  xl: 56,
  xxl: 56,
});

const navItemIconSize = getResponsiveSize({
  xs: 20,
  sm: 22,
  md: 24,
  lg: 24,
  xl: 24,
  xxl: 24,
});

// 性能优化配置
const optimizationConfig = computed(() => optimizeForDevice());

// 菜单项
const menuItems = [
  {
    title: "仪表板",
    icon: "mdi-view-dashboard",
    to: "/",
  },
  {
    title: "爬虫控制",
    icon: "mdi-spider",
    to: "/spider",
  },
  {
    title: "数据管理",
    icon: "mdi-database",
    to: "/data",
  },
  {
    title: "高级数据管理",
    icon: "mdi-database-edit",
    to: "/data/advanced",
  },
  {
    title: "任务管理",
    icon: "mdi-format-list-bulleted",
    to: "/tasks",
  },
  {
    title: "任务历史",
    icon: "mdi-history",
    to: "/history",
  },
  {
    title: "实时日志",
    icon: "mdi-console-line",
    to: "/logs",
  },
  {
    title: "系统设置",
    icon: "mdi-cog",
    to: "/settings",
  },
  {
    title: "组件测试",
    icon: "mdi-test-tube",
    to: "/test",
  },
];

// 计算属性
const connectionStatus = computed(() => appStore.connectionStatus);

// 方法
const toggleLeftDrawer = () => {
  leftDrawerOpen.value = !leftDrawerOpen.value;
};

const toggleTheme = () => {
  isDark.value = !isDark.value;
  theme.global.name.value = isDark.value ? "dark" : "light";
  // 保存主题设置到localStorage
  localStorage.setItem("theme", theme.global.name.value);
};

const smartRefresh = async () => {
  if (refreshing.value) return;

  refreshing.value = true;
  console.log("🔄 智能刷新开始");

  try {
    if (!connectionStatus.value) {
      // 如果WebSocket未连接，先重连
      console.log("🔄 WebSocket未连接，正在重连...");
      await appStore.initializeSocket();
      console.log("✅ WebSocket重连成功");
    }

    // 刷新数据
    console.log("🔄 正在刷新数据...");
    await appStore.refreshData();
    console.log("✅ 数据刷新成功");
  } catch (error) {
    console.error("❌ 智能刷新失败:", error);
  } finally {
    refreshing.value = false;
  }
};

// 初始化主题
const initializeTheme = () => {
  // 清理Monet相关的localStorage数据
  cleanupMonetThemeData();

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    theme.global.name.value = savedTheme;
    isDark.value = savedTheme === "dark";
  } else {
    // 默认使用浅色主题
    theme.global.name.value = "light";
    isDark.value = false;
    localStorage.setItem("theme", "light");
  }
};

// 生命周期
onMounted(() => {
  initializeTheme();
  appStore.initializeSocket();
  appStore.refreshData();
});
</script>

<style scoped>
/* MD3 应用布局样式 - 简洁现代 */
.app-title {
  display: flex;
  align-items: center;
}

.title-text {
  line-height: 1.2;
}

.app-actions {
  gap: var(--md3-spacing-sm);
}

.drawer-title-container {
  flex: 1;
}

/* nav-item样式现在由VListItem的defaults配置管理 */

.drawer-footer {
  margin-top: auto;
}

.main-content {
  min-height: 100vh;
}

/* MD3 页面过渡动画 - 更自然 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--md3-motion-duration-medium)
    var(--md3-motion-easing-standard);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* MD3 按钮交互 - 移除旋转效果 */
.theme-toggle {
  transition: var(--md3-motion-duration-short) var(--md3-motion-easing-standard);
}

.refresh-button {
  transition: var(--md3-motion-duration-short) var(--md3-motion-easing-standard);
}

/* 样式现在完全由Vuetify defaults配置管理 - 遵循官方文档最佳实践 */
</style>
