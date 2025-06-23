<template>
  <v-container class="responsive-layout" :class="layoutClass" fluid>
    <!-- 页面标题区域 -->
    <v-sheet v-if="showHeader" class="layout-header" :class="headerClass" color="transparent">
      <v-sheet class="d-flex align-center" :class="headerContentClass" color="transparent">
        <!-- 图标 -->
        <v-avatar v-if="icon" :color="iconColor" :size="iconSize" class="me-4">
          <v-icon :icon="icon" />
        </v-avatar>

        <!-- 标题内容 -->
        <v-sheet class="flex-grow-1" color="transparent">
          <h1 :class="titleClass">
            {{ title }}
          </h1>
          <v-card-text v-if="subtitle" :class="subtitleClass" class="pa-0">
            {{ subtitle }}
          </v-card-text>
        </v-sheet>

        <!-- 头部操作 -->
        <v-sheet v-if="$slots.actions" class="header-actions" color="transparent">
          <slot name="actions" />
        </v-sheet>

        <!-- 状态指示器 -->
        <v-chip
          v-if="status"
          :color="statusColor"
          :prepend-icon="statusIcon"
          :size="chipSize"
          :class="statusChipClass"
        >
          {{ status }}
        </v-chip>
      </v-sheet>
    </v-sheet>

    <!-- 工具栏区域 -->
    <v-sheet v-if="$slots.toolbar" class="layout-toolbar" :class="toolbarClass" color="transparent">
      <slot name="toolbar" />
    </v-sheet>

    <!-- 主要内容区域 -->
    <v-sheet class="layout-content" :class="contentClass" color="transparent">
      <!-- 侧边栏 -->
      <v-sheet
        v-if="$slots.sidebar && showSidebar"
        class="layout-sidebar"
        :class="sidebarClass"
        color="transparent"
      >
        <slot name="sidebar" />
      </v-sheet>

      <!-- 主内容 -->
      <v-sheet class="layout-main" :class="mainClass" color="transparent">
        <slot />
      </v-sheet>

      <!-- 右侧栏 -->
      <v-sheet
        v-if="$slots.aside && showAside"
        class="layout-aside"
        :class="asideClass"
        color="transparent"
      >
        <slot name="aside" />
      </v-sheet>
    </v-sheet>

    <!-- 底部区域 -->
    <v-sheet v-if="$slots.footer" class="layout-footer" :class="footerClass" color="transparent">
      <slot name="footer" />
    </v-sheet>
  </v-container>
</template>

<script setup>
import { computed } from "vue";
import { useResponsive } from "@/composables/useResponsive";

// Props
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: "",
  },
  icon: {
    type: String,
    default: "",
  },
  iconColor: {
    type: String,
    default: "primary",
  },
  status: {
    type: String,
    default: "",
  },
  statusColor: {
    type: String,
    default: "success",
  },
  statusIcon: {
    type: String,
    default: "mdi-check-circle",
  },
  showHeader: {
    type: Boolean,
    default: true,
  },
  showSidebar: {
    type: Boolean,
    default: true,
  },
  showAside: {
    type: Boolean,
    default: true,
  },
  layout: {
    type: String,
    default: "default", // default, centered, full-width, sidebar-left, sidebar-right
    validator: (value) =>
      [
        "default",
        "centered",
        "full-width",
        "sidebar-left",
        "sidebar-right",
      ].includes(value),
  },
  spacing: {
    type: String,
    default: "normal", // compact, normal, comfortable, spacious
    validator: (value) =>
      ["compact", "normal", "comfortable", "spacious"].includes(value),
  },
  maxWidth: {
    type: String,
    default: "1200px",
  },
});

// 响应式组合函数
const { display, getResponsiveSize, getResponsiveSpacing } = useResponsive();

// 响应式尺寸
const iconSize = getResponsiveSize({
  xs: 24,
  sm: 28,
  md: 32,
  lg: 32,
  xl: 32,
  xxl: 32,
});

const chipSize = getResponsiveSize({
  xs: "small",
  sm: "small",
  md: "default",
  lg: "default",
  xl: "default",
  xxl: "default",
});

const responsiveSpacing = getResponsiveSpacing({
  xs: 2,
  sm: 3,
  md: 4,
  lg: 6,
  xl: 8,
  xxl: 10,
});

// 计算属性
const isMobile = computed(() => display.mobile.value);
const isTablet = computed(() => display.sm.value);
const isDesktop = computed(() => display.mdAndUp.value);

// 布局类
const layoutClass = computed(() => ({
  [`layout-${props.layout}`]: true,
  [`spacing-${props.spacing}`]: true,
  "is-mobile": isMobile.value,
  "is-tablet": isTablet.value,
  "is-desktop": isDesktop.value,
}));

// 头部样式
const headerClass = computed(() => ({
  "app-section": true,
  "mb-4": props.spacing === "compact",
  "mb-6": props.spacing === "normal",
  "mb-8": props.spacing === "comfortable",
  "mb-12": props.spacing === "spacious",
}));

const headerContentClass = computed(() => ({
  "flex-column": isMobile.value && props.status,
  "align-start": isMobile.value && props.status,
}));

const titleClass = computed(() => {
  const baseClass = "font-weight-medium mb-1";
  if (isMobile.value) return `text-h5 ${baseClass}`;
  if (isTablet.value) return `text-h4 ${baseClass}`;
  return `text-h4 ${baseClass}`;
});

const subtitleClass = computed(() => {
  const baseClass = "text-medium-emphasis";
  if (isMobile.value) return `text-body-1 ${baseClass}`;
  return `text-subtitle-1 ${baseClass}`;
});

const statusChipClass = computed(() => ({
  "d-none": isMobile.value && !props.status,
  "d-md-flex": !isMobile.value,
  "mt-2": isMobile.value && props.status,
  "align-self-start": isMobile.value && props.status,
}));

// 工具栏样式
const toolbarClass = computed(() => ({
  "mb-4": props.spacing === "compact",
  "mb-6": props.spacing === "normal",
  "mb-8": props.spacing === "comfortable",
  "mb-12": props.spacing === "spacious",
}));

// 内容区域样式
const contentClass = computed(() => {
  const baseClass = "d-flex";

  if (props.layout === "centered") {
    return `${baseClass} justify-center`;
  }

  if (isMobile.value) {
    return `${baseClass} flex-column`;
  }

  return baseClass;
});

const sidebarClass = computed(() => ({
  "layout-sidebar-mobile": isMobile.value,
  "layout-sidebar-desktop": !isMobile.value,
  "mb-4": isMobile.value,
  "me-6": !isMobile.value && props.spacing !== "compact",
  "me-4": !isMobile.value && props.spacing === "compact",
}));

const mainClass = computed(() => {
  const baseClass = "flex-grow-1";

  if (props.layout === "centered") {
    return `${baseClass} d-flex flex-column align-center`;
  }

  if (props.layout === "full-width") {
    return `${baseClass} w-100`;
  }

  return baseClass;
});

const asideClass = computed(() => ({
  "layout-aside-mobile": isMobile.value,
  "layout-aside-desktop": !isMobile.value,
  "mt-4": isMobile.value,
  "ms-6": !isMobile.value && props.spacing !== "compact",
  "ms-4": !isMobile.value && props.spacing === "compact",
}));

// 底部样式
const footerClass = computed(() => ({
  "mt-4": props.spacing === "compact",
  "mt-6": props.spacing === "normal",
  "mt-8": props.spacing === "comfortable",
  "mt-12": props.spacing === "spacious",
}));
</script>

<style scoped>
.responsive-layout {
  width: 100%;
  min-height: 100%;
}

/* 布局变体 */
.layout-default {
  max-width: v-bind(maxWidth);
  margin: 0 auto;
  padding: 0 16px;
}

.layout-centered {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px;
}

.layout-full-width {
  width: 100%;
  padding: 0 16px;
}

.layout-sidebar-left .layout-content {
  flex-direction: row;
}

.layout-sidebar-right .layout-content {
  flex-direction: row-reverse;
}

/* 间距变体 */
.spacing-compact {
  --layout-spacing: 8px;
}

.spacing-normal {
  --layout-spacing: 16px;
}

.spacing-comfortable {
  --layout-spacing: 24px;
}

.spacing-spacious {
  --layout-spacing: 32px;
}

/* 响应式调整 */
@media (min-width: 600px) {
  .layout-default,
  .layout-centered {
    padding: 0 24px;
  }
}

@media (min-width: 1280px) {
  .layout-default {
    max-width: 1400px;
    padding: 0 32px;
  }

  .layout-centered {
    max-width: 1000px;
    padding: 0 32px;
  }
}

@media (min-width: 1920px) {
  .layout-default {
    max-width: 1600px;
  }

  .layout-centered {
    max-width: 1200px;
  }
}

/* 侧边栏和辅助栏 */
.layout-sidebar-desktop {
  width: 280px;
  flex-shrink: 0;
}

.layout-aside-desktop {
  width: 320px;
  flex-shrink: 0;
}

.layout-sidebar-mobile,
.layout-aside-mobile {
  width: 100%;
}

/* 头部操作区域 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 移动端优化 */
.is-mobile .header-actions {
  width: 100%;
  justify-content: flex-start;
  margin-top: 12px;
}

.is-mobile .layout-content {
  flex-direction: column;
}

/* 动画效果 */
.layout-content {
  transition: all var(--md3-motion-duration-medium)
    var(--md3-motion-easing-standard);
}

.layout-sidebar,
.layout-aside {
  transition: all var(--md3-motion-duration-medium)
    var(--md3-motion-easing-standard);
}
</style>
