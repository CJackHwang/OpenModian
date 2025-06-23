<template>
  <v-card v-if="showMonitor" class="performance-monitor">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-speedometer" class="me-2" />
      性能监控
      <v-spacer />
      <v-btn
        @click="toggleExpanded"
        :icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
        variant="text"
        size="small"
      />
    </v-card-title>

    <v-expand-transition>
      <v-card-text v-show="expanded" class="pt-0">
        <!-- 性能指标 -->
        <v-row dense>
          <v-col cols="6" sm="3">
            <div class="performance-metric">
              <div class="metric-label">加载时间</div>
              <div class="metric-value" :class="getLoadTimeClass()">
                {{ formatTime(performanceData.loadTime) }}
              </div>
            </div>
          </v-col>

          <v-col cols="6" sm="3">
            <div class="performance-metric">
              <div class="metric-label">渲染时间</div>
              <div class="metric-value" :class="getRenderTimeClass()">
                {{ formatTime(performanceData.renderTime) }}
              </div>
            </div>
          </v-col>

          <v-col cols="6" sm="3">
            <div class="performance-metric">
              <div class="metric-label">内存使用</div>
              <div class="metric-value" :class="getMemoryClass()">
                {{ performanceData.memoryUsage }}%
              </div>
            </div>
          </v-col>

          <v-col cols="6" sm="3">
            <v-sheet class="performance-metric" color="transparent">
              <v-card-text class="metric-label pa-0">FPS</v-card-text>
              <v-card-text class="metric-value pa-0" :class="getFpsClass()">
                {{ performanceData.fps }}
              </v-card-text>
            </v-sheet>
          </v-col>
        </v-row>

        <!-- 性能建议 -->
        <v-sheet v-if="recommendations.length > 0" class="mt-4" color="transparent">
          <v-divider class="mb-3" />
          <v-card-text class="text-subtitle-2 mb-2 pa-0">性能建议</v-card-text>
          <v-alert
            v-for="(recommendation, index) in recommendations"
            :key="index"
            :type="getRecommendationType(recommendation)"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            {{ recommendation }}
          </v-alert>
        </v-sheet>

        <!-- 设备信息 -->
        <v-sheet class="mt-4" color="transparent">
          <v-divider class="mb-3" />
          <v-card-text class="text-subtitle-2 mb-2 pa-0">设备信息</v-card-text>
          <v-chip-group>
            <v-chip
              :color="performanceData.isSlowDevice ? 'warning' : 'success'"
              size="small"
              variant="tonal"
            >
              {{ performanceData.isSlowDevice ? "低性能设备" : "高性能设备" }}
            </v-chip>
            <v-chip size="small" variant="outlined">
              {{ deviceInfo.cores }} 核心
            </v-chip>
            <v-chip size="small" variant="outlined">
              {{ deviceInfo.memory }}GB 内存
            </v-chip>
            <v-chip size="small" variant="outlined">
              {{ deviceInfo.connection }}
            </v-chip>
          </v-chip-group>
        </v-sheet>

        <!-- 操作按钮 -->
        <v-sheet class="mt-4 d-flex justify-end ga-2" color="transparent">
          <v-btn
            @click="clearCache"
            variant="outlined"
            size="small"
            prepend-icon="mdi-cached"
          >
            清理缓存
          </v-btn>
          <v-btn
            @click="optimizePerformance"
            variant="outlined"
            size="small"
            prepend-icon="mdi-tune"
          >
            优化性能
          </v-btn>
        </v-sheet>
      </v-card-text>
    </v-expand-transition>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { usePerformance } from "@/composables/usePerformance";

// Props
const props = defineProps({
  showMonitor: {
    type: Boolean,
    default: false,
  },
  autoOptimize: {
    type: Boolean,
    default: true,
  },
});

// Emits
const emit = defineEmits(["performance-optimized", "cache-cleared"]);

// 响应式数据
const expanded = ref(false);

// 性能监控
const { performanceData, getPerformanceRecommendations, optimizeForDevice } =
  usePerformance();

// 计算属性
const recommendations = computed(() => getPerformanceRecommendations());

const deviceInfo = computed(() => ({
  cores: navigator.hardwareConcurrency || "Unknown",
  memory: navigator.deviceMemory || "Unknown",
  connection: navigator.connection?.effectiveType || "Unknown",
}));

// 方法
const toggleExpanded = () => {
  expanded.value = !expanded.value;
};

const formatTime = (time) => {
  if (time < 1000) {
    return `${Math.round(time)}ms`;
  }
  return `${(time / 1000).toFixed(1)}s`;
};

const getLoadTimeClass = () => {
  const time = performanceData.value.loadTime;
  if (time > 3000) return "text-error";
  if (time > 1500) return "text-warning";
  return "text-success";
};

const getRenderTimeClass = () => {
  const time = performanceData.value.renderTime;
  if (time > 100) return "text-error";
  if (time > 50) return "text-warning";
  return "text-success";
};

const getMemoryClass = () => {
  const usage = performanceData.value.memoryUsage;
  if (usage > 80) return "text-error";
  if (usage > 60) return "text-warning";
  return "text-success";
};

const getFpsClass = () => {
  const fps = performanceData.value.fps;
  if (fps < 30) return "text-error";
  if (fps < 50) return "text-warning";
  return "text-success";
};

const getRecommendationType = (recommendation) => {
  if (
    recommendation.includes("较长") ||
    recommendation.includes("较高") ||
    recommendation.includes("较低")
  ) {
    return "warning";
  }
  if (recommendation.includes("低性能设备")) {
    return "info";
  }
  return "success";
};

const clearCache = () => {
  try {
    // 清理各种缓存
    if ("caches" in window) {
      caches.keys().then((names) => {
        names.forEach((name) => {
          caches.delete(name);
        });
      });
    }

    // 清理localStorage中的缓存数据
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (key.includes("cache") || key.includes("temp"))) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach((key) => localStorage.removeItem(key));

    // 触发垃圾回收（如果支持）
    if (window.gc) {
      window.gc();
    }

    emit("cache-cleared");

    // 显示成功消息
    console.log("缓存清理完成");
  } catch (error) {
    console.error("清理缓存失败:", error);
  }
};

const optimizePerformance = () => {
  try {
    const optimizations = optimizeForDevice();

    // 应用性能优化
    if (optimizations.reducedAnimations) {
      document.documentElement.style.setProperty(
        "--md3-motion-duration-short",
        "0ms",
      );
      document.documentElement.style.setProperty(
        "--md3-motion-duration-medium",
        "0ms",
      );
      document.documentElement.style.setProperty(
        "--md3-motion-duration-long",
        "0ms",
      );
    }

    if (optimizations.simplifiedUI) {
      document.documentElement.classList.add("simplified-ui");
    }

    emit("performance-optimized", optimizations);

    console.log("性能优化已应用:", optimizations);
  } catch (error) {
    console.error("性能优化失败:", error);
  }
};

// 生命周期
onMounted(() => {
  if (props.autoOptimize && performanceData.value.isSlowDevice) {
    optimizePerformance();
  }
});
</script>

<style scoped>
.performance-monitor {
  position: fixed;
  top: 80px;
  right: 16px;
  width: 320px;
  z-index: 1000;
  max-height: 80vh;
  overflow-y: auto;
}

.performance-metric {
  text-align: center;
  padding: 8px;
  border-radius: 8px;
  background-color: rgba(var(--v-theme-surface-variant), 0.1);
}

.metric-label {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 600;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .performance-monitor {
    position: relative;
    top: auto;
    right: auto;
    width: 100%;
    margin-bottom: 16px;
  }
}

/* 简化UI模式 */
:global(.simplified-ui) .v-card {
  box-shadow: none !important;
  border: 1px solid rgba(var(--v-theme-outline), 0.2);
}

:global(.simplified-ui) .v-btn {
  box-shadow: none !important;
}

:global(.simplified-ui) .v-chip {
  box-shadow: none !important;
}
</style>
