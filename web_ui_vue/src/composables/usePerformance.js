import { ref, onMounted, onUnmounted, nextTick } from "vue";

/**
 * 性能监控组合式函数
 * 提供页面性能监控、内存使用情况和渲染性能优化
 */
export function usePerformance() {
  const performanceData = ref({
    loadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    fps: 0,
    isSlowDevice: false,
  });

  const isLoading = ref(false);
  let performanceObserver = null;
  let fpsCounter = null;
  let lastFrameTime = 0;
  let frameCount = 0;

  // 检测设备性能
  const detectDevicePerformance = () => {
    const hardwareConcurrency = navigator.hardwareConcurrency || 1;
    const memory = navigator.deviceMemory || 1;
    const connection = navigator.connection;

    // 基于硬件信息判断设备性能
    const isSlowDevice =
      hardwareConcurrency <= 2 ||
      memory <= 2 ||
      (connection && connection.effectiveType === "slow-2g");

    performanceData.value.isSlowDevice = isSlowDevice;
    return isSlowDevice;
  };

  // 测量页面加载时间
  const measureLoadTime = () => {
    if (performance.timing) {
      const loadTime =
        performance.timing.loadEventEnd - performance.timing.navigationStart;
      performanceData.value.loadTime = loadTime;
    }
  };

  // 测量渲染时间
  const measureRenderTime = async () => {
    const startTime = performance.now();
    await nextTick();
    const endTime = performance.now();
    performanceData.value.renderTime = endTime - startTime;
  };

  // 监控内存使用
  const monitorMemoryUsage = () => {
    if (performance.memory) {
      const memoryUsage =
        (performance.memory.usedJSHeapSize /
          performance.memory.totalJSHeapSize) *
        100;
      performanceData.value.memoryUsage = Math.round(memoryUsage);
    }
  };

  // FPS监控
  const startFPSMonitoring = () => {
    let frames = 0;
    let lastTime = performance.now();

    const countFPS = (currentTime) => {
      frames++;

      if (currentTime >= lastTime + 1000) {
        performanceData.value.fps = Math.round(
          (frames * 1000) / (currentTime - lastTime),
        );
        frames = 0;
        lastTime = currentTime;
      }

      fpsCounter = requestAnimationFrame(countFPS);
    };

    fpsCounter = requestAnimationFrame(countFPS);
  };

  // 停止FPS监控
  const stopFPSMonitoring = () => {
    if (fpsCounter) {
      cancelAnimationFrame(fpsCounter);
      fpsCounter = null;
    }
  };

  // 性能优化建议
  const getPerformanceRecommendations = () => {
    const recommendations = [];

    if (performanceData.value.loadTime > 3000) {
      recommendations.push("页面加载时间较长，建议优化资源加载");
    }

    if (performanceData.value.memoryUsage > 80) {
      recommendations.push("内存使用率较高，建议清理不必要的数据");
    }

    if (performanceData.value.fps < 30) {
      recommendations.push("帧率较低，建议减少动画效果");
    }

    if (performanceData.value.isSlowDevice) {
      recommendations.push("检测到低性能设备，已启用性能优化模式");
    }

    return recommendations;
  };

  // 启动性能监控
  const startMonitoring = () => {
    detectDevicePerformance();
    measureLoadTime();
    measureRenderTime();
    monitorMemoryUsage();
    startFPSMonitoring();

    // 定期更新内存使用情况
    const memoryInterval = setInterval(monitorMemoryUsage, 5000);

    // 清理函数
    return () => {
      clearInterval(memoryInterval);
      stopFPSMonitoring();
    };
  };

  // 性能优化工具函数
  const optimizeForDevice = () => {
    if (performanceData.value.isSlowDevice) {
      // 为低性能设备优化
      return {
        reducedAnimations: true,
        lowerImageQuality: true,
        disableParticles: true,
        simplifiedUI: true,
      };
    }

    return {
      reducedAnimations: false,
      lowerImageQuality: false,
      disableParticles: false,
      simplifiedUI: false,
    };
  };

  // 防抖函数
  const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };

  // 节流函数
  const throttle = (func, limit) => {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  };

  // 生命周期钩子
  onMounted(() => {
    const cleanup = startMonitoring();

    onUnmounted(() => {
      cleanup();
    });
  });

  return {
    performanceData,
    isLoading,
    detectDevicePerformance,
    measureLoadTime,
    measureRenderTime,
    monitorMemoryUsage,
    startFPSMonitoring,
    stopFPSMonitoring,
    getPerformanceRecommendations,
    optimizeForDevice,
    debounce,
    throttle,
  };
}

/**
 * 虚拟滚动优化组合式函数
 */
export function useVirtualScroll(
  items,
  itemHeight = 50,
  containerHeight = 400,
) {
  const scrollTop = ref(0);
  const visibleItems = ref([]);
  const totalHeight = ref(0);
  const offsetY = ref(0);

  const updateVisibleItems = () => {
    const visibleCount = Math.ceil(containerHeight / itemHeight) + 2;
    const startIndex = Math.floor(scrollTop.value / itemHeight);
    const endIndex = Math.min(startIndex + visibleCount, items.value.length);

    visibleItems.value = items.value
      .slice(startIndex, endIndex)
      .map((item, index) => ({
        ...item,
        index: startIndex + index,
      }));

    totalHeight.value = items.value.length * itemHeight;
    offsetY.value = startIndex * itemHeight;
  };

  const handleScroll = (event) => {
    scrollTop.value = event.target.scrollTop;
    updateVisibleItems();
  };

  return {
    scrollTop,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    updateVisibleItems,
  };
}
