import { computed, ref, onMounted, onUnmounted } from "vue";
import { useDisplay } from "vuetify";

/**
 * 响应式设计组合式函数
 * 提供高级响应式布局和组件适配功能
 */
export function useResponsive() {
  const display = useDisplay();
  const windowWidth = ref(window.innerWidth);
  const windowHeight = ref(window.innerHeight);

  // 更新窗口尺寸
  const updateWindowSize = () => {
    windowWidth.value = window.innerWidth;
    windowHeight.value = window.innerHeight;
  };

  // 监听窗口大小变化
  const handleResize = () => {
    updateWindowSize();
  };

  // 设备类型检测
  const deviceType = computed(() => {
    if (display.xs.value) return "mobile";
    if (display.sm.value) return "tablet";
    if (display.md.value) return "laptop";
    if (display.lg.value) return "desktop";
    return "large-desktop";
  });

  // 屏幕方向
  const orientation = computed(() => {
    return windowWidth.value > windowHeight.value ? "landscape" : "portrait";
  });

  // 是否为触摸设备
  const isTouchDevice = computed(() => {
    return "ontouchstart" in window || navigator.maxTouchPoints > 0;
  });

  // 响应式列数计算
  const getResponsiveColumns = (config = {}) => {
    const defaultConfig = {
      xs: 1,
      sm: 2,
      md: 3,
      lg: 4,
      xl: 5,
      xxl: 6,
    };

    const finalConfig = { ...defaultConfig, ...config };

    return computed(() => {
      if (display.xs.value) return finalConfig.xs;
      if (display.sm.value) return finalConfig.sm;
      if (display.md.value) return finalConfig.md;
      if (display.lg.value) return finalConfig.lg;
      if (display.xl.value) return finalConfig.xl;
      return finalConfig.xxl;
    });
  };

  // 响应式间距计算
  const getResponsiveSpacing = (config = {}) => {
    const defaultConfig = {
      xs: 2,
      sm: 3,
      md: 4,
      lg: 6,
      xl: 8,
      xxl: 10,
    };

    const finalConfig = { ...defaultConfig, ...config };

    return computed(() => {
      if (display.xs.value) return finalConfig.xs;
      if (display.sm.value) return finalConfig.sm;
      if (display.md.value) return finalConfig.md;
      if (display.lg.value) return finalConfig.lg;
      if (display.xl.value) return finalConfig.xl;
      return finalConfig.xxl;
    });
  };

  // 响应式字体大小
  const getResponsiveFontSize = (config = {}) => {
    const defaultConfig = {
      xs: "0.875rem",
      sm: "1rem",
      md: "1.125rem",
      lg: "1.25rem",
      xl: "1.375rem",
      xxl: "1.5rem",
    };

    const finalConfig = { ...defaultConfig, ...config };

    return computed(() => {
      if (display.xs.value) return finalConfig.xs;
      if (display.sm.value) return finalConfig.sm;
      if (display.md.value) return finalConfig.md;
      if (display.lg.value) return finalConfig.lg;
      if (display.xl.value) return finalConfig.xl;
      return finalConfig.xxl;
    });
  };

  // 响应式组件尺寸
  const getResponsiveSize = (config = {}) => {
    const defaultConfig = {
      xs: "small",
      sm: "small",
      md: "default",
      lg: "default",
      xl: "large",
      xxl: "large",
    };

    const finalConfig = { ...defaultConfig, ...config };

    return computed(() => {
      if (display.xs.value) return finalConfig.xs;
      if (display.sm.value) return finalConfig.sm;
      if (display.md.value) return finalConfig.md;
      if (display.lg.value) return finalConfig.lg;
      if (display.xl.value) return finalConfig.xl;
      return finalConfig.xxl;
    });
  };

  // 响应式密度
  const getResponsiveDensity = (config = {}) => {
    const defaultConfig = {
      xs: "compact",
      sm: "compact",
      md: "comfortable",
      lg: "comfortable",
      xl: "default",
      xxl: "default",
    };

    const finalConfig = { ...defaultConfig, ...config };

    return computed(() => {
      if (display.xs.value) return finalConfig.xs;
      if (display.sm.value) return finalConfig.sm;
      if (display.md.value) return finalConfig.md;
      if (display.lg.value) return finalConfig.lg;
      if (display.xl.value) return finalConfig.xl;
      return finalConfig.xxl;
    });
  };

  // 响应式容器宽度
  const getResponsiveContainerWidth = () => {
    return computed(() => {
      if (display.xs.value) return "100%";
      if (display.sm.value) return "540px";
      if (display.md.value) return "720px";
      if (display.lg.value) return "960px";
      if (display.xl.value) return "1140px";
      return "1320px";
    });
  };

  // 响应式网格配置
  const getResponsiveGridConfig = (itemsPerRow = {}) => {
    const defaultItemsPerRow = {
      xs: 1,
      sm: 2,
      md: 3,
      lg: 4,
      xl: 5,
      xxl: 6,
    };

    const finalConfig = { ...defaultItemsPerRow, ...itemsPerRow };

    return computed(() => {
      const cols = 12;
      let itemsInRow;

      if (display.xs.value) itemsInRow = finalConfig.xs;
      else if (display.sm.value) itemsInRow = finalConfig.sm;
      else if (display.md.value) itemsInRow = finalConfig.md;
      else if (display.lg.value) itemsInRow = finalConfig.lg;
      else if (display.xl.value) itemsInRow = finalConfig.xl;
      else itemsInRow = finalConfig.xxl;

      return {
        cols: Math.floor(cols / itemsInRow),
        itemsPerRow: itemsInRow,
      };
    });
  };

  // 响应式表格配置
  const getResponsiveTableConfig = () => {
    return computed(() => {
      return {
        itemsPerPage: display.xs.value ? 5 : display.sm.value ? 10 : 25,
        density: display.xs.value ? "compact" : "comfortable",
        hideHeaders: display.xs.value,
        mobileBreakpoint: "sm",
      };
    });
  };

  // 响应式对话框配置
  const getResponsiveDialogConfig = () => {
    return computed(() => {
      return {
        fullscreen: display.xs.value,
        maxWidth: display.xs.value
          ? "100%"
          : display.sm.value
            ? "600px"
            : "800px",
        persistent: display.xs.value,
      };
    });
  };

  // 响应式导航配置
  const getResponsiveNavigationConfig = () => {
    return computed(() => {
      return {
        rail: display.lg.value && !display.xl.value,
        temporary: display.mobile.value,
        permanent: !display.mobile.value,
        width: display.xs.value ? 280 : display.sm.value ? 300 : 320,
      };
    });
  };

  // 生命周期
  onMounted(() => {
    window.addEventListener("resize", handleResize);
    updateWindowSize();
  });

  onUnmounted(() => {
    window.removeEventListener("resize", handleResize);
  });

  return {
    // 基础响应式数据
    display,
    windowWidth,
    windowHeight,
    deviceType,
    orientation,
    isTouchDevice,

    // 响应式计算函数
    getResponsiveColumns,
    getResponsiveSpacing,
    getResponsiveFontSize,
    getResponsiveSize,
    getResponsiveDensity,
    getResponsiveContainerWidth,
    getResponsiveGridConfig,
    getResponsiveTableConfig,
    getResponsiveDialogConfig,
    getResponsiveNavigationConfig,

    // 工具函数
    updateWindowSize,
  };
}
