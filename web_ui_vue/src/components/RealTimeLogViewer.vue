<template>
  <v-card class="log-viewer d-flex flex-column app-card">
    <!-- 统一设计头部 -->
    <v-card-title class="d-flex align-center p-lg">
      <v-avatar color="primary" size="32" class="me-3">
        <v-icon icon="mdi-console" color="on-primary" size="18" />
      </v-avatar>
      <div class="flex-grow-1">
        <div class="text-h6 font-weight-bold">实时日志</div>
        <div class="text-body-2 text-medium-emphasis">系统运行日志监控</div>
      </div>

      <!-- 简化的控制区域 - 只保留功能按钮 -->
      <div class="d-flex align-center ga-3">
        <!-- 刷新按钮 -->
        <v-btn
          icon="mdi-refresh"
          @click="refreshLogs"
          :disabled="!connectionStatus"
          size="small"
          color="primary"
          variant="outlined"
          class="app-button"
        />

        <!-- 清空按钮 -->
        <v-btn
          icon="mdi-delete"
          @click="clearLogs"
          :disabled="!logs.length"
          size="small"
          color="error"
          variant="outlined"
          class="app-button"
        />
      </div>
    </v-card-title>

    <!-- 日志内容区域 -->
    <v-card-text class="pa-0 flex-grow-1 d-flex flex-column log-content-area">
      <div class="log-container flex-grow-1" ref="logContainer">
        <div v-if="logs.length === 0" class="empty-state">
          <v-icon
            icon="mdi-information-outline"
            size="32"
            class="mb-2 text-medium-emphasis"
          />
          <div class="text-body-2 text-medium-emphasis">
            {{ connectionStatus ? "暂无日志信息" : "等待连接..." }}
          </div>
        </div>

        <div
          v-for="(log, index) in displayedLogs"
          :key="`${log.timestamp}-${index}`"
          :class="['log-entry', `log-${log.level.toLowerCase()}`]"
        >
          <span class="log-timestamp"
            >[{{ formatTimestamp(log.timestamp) }}]</span
          >
          <span :class="['log-level', `log-level-${log.level.toLowerCase()}`]">
            [{{ log.level.toUpperCase() }}]
          </span>
          <span v-if="log.source" class="log-source">[{{ log.source }}]</span>
          <span class="log-message">{{ log.message }}</span>
        </div>

        <!-- 加载更多按钮 -->
        <div v-if="hasMoreLogs" class="text-center pa-2">
          <v-btn
            variant="text"
            size="small"
            color="primary"
            @click="loadMoreLogs"
            :loading="loadingMore"
          >
            加载更多 ({{ logs.length - displayedLogs.length }})
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useAppStore } from "@/stores/app";
import { useDisplay } from "vuetify";

// Props
const props = defineProps({
  height: {
    type: [String, Number],
    default: "auto",
  },
  minHeight: {
    type: [String, Number],
    default: "300px",
  },
  maxHeight: {
    type: [String, Number],
    default: "600px",
  },
  maxLogs: {
    type: Number,
    default: 500,
  },
  autoScroll: {
    type: Boolean,
    default: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
});

// Composables
const appStore = useAppStore();
const display = useDisplay();

// 响应式数据
const logs = ref([]);
const displayedLogs = ref([]);
const connectionStatus = ref(false);
const loadingMore = ref(false);
const displayLimit = ref(100);

// 日志容器引用
const logContainer = ref(null);

// 计算属性
const hasMoreLogs = computed(() => {
  return logs.value.length > displayedLogs.value.length;
});

// 响应式高度计算
const containerHeight = computed(() => {
  if (props.height === "auto") {
    // 自动高度模式：根据屏幕尺寸和内容调整
    if (display.xs.value) {
      return "250px";
    } else if (display.sm.value) {
      return "300px";
    } else if (display.md.value) {
      return "350px";
    } else {
      return "400px";
    }
  }

  // 固定高度模式
  return typeof props.height === "number" ? `${props.height}px` : props.height;
});

// 响应式显示限制
const responsiveDisplayLimit = computed(() => {
  if (display.xs.value) return 50;
  if (display.sm.value) return 75;
  return 100;
});

// 本地存储键名
const STORAGE_KEY = "realtime_logs_cache";

// 方法
const initializeLogViewer = () => {
  // 加载缓存的日志
  loadCachedLogs();

  // 设置WebSocket监听
  setupWebSocketListeners();

  // 订阅日志更新
  subscribeToLogs();
};

const loadCachedLogs = () => {
  try {
    const cached = localStorage.getItem(STORAGE_KEY);
    if (cached) {
      const parsedLogs = JSON.parse(cached);
      logs.value = parsedLogs.slice(-props.maxLogs); // 只保留最新的日志
      updateDisplayedLogs();
      console.log(`📝 加载缓存日志: ${logs.value.length} 条`);
    }
  } catch (error) {
    console.error("加载缓存日志失败:", error);
    logs.value = [];
  }
};

const saveCachedLogs = () => {
  try {
    // 只缓存最新的日志，避免存储过大
    const logsToCache = logs.value.slice(-props.maxLogs);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(logsToCache));
  } catch (error) {
    console.error("保存日志缓存失败:", error);
    // 如果存储失败，可能是因为存储空间不足，清理旧数据
    try {
      localStorage.removeItem(STORAGE_KEY);
      const reducedLogs = logs.value.slice(-Math.floor(props.maxLogs / 2));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(reducedLogs));
    } catch (retryError) {
      console.error("重试保存日志缓存也失败:", retryError);
    }
  }
};

const setupWebSocketListeners = () => {
  if (!appStore.socket) {
    console.warn("WebSocket未初始化");
    return;
  }

  // 连接状态监听
  appStore.socket.on("connect", () => {
    connectionStatus.value = true;
    console.log("✅ 日志查看器WebSocket已连接");
    subscribeToLogs();
  });

  appStore.socket.on("disconnect", () => {
    connectionStatus.value = false;
    console.log("❌ 日志查看器WebSocket已断开");
  });

  // 日志更新监听
  appStore.socket.on("log_update", (data) => {
    console.log("📡 日志查看器收到log_update:", data);
    handleLogUpdate(data);
  });

  // 日志历史监听
  appStore.socket.on("log_history", (data) => {
    console.log("📝 日志查看器收到log_history:", data);
    handleLogHistory(data);
  });

  // 日志清空监听
  appStore.socket.on("log_cleared", (data) => {
    if (data.log_type === "all") {
      logs.value = [];
      updateDisplayedLogs();
      saveCachedLogs();
    }
  });

  // 设置初始连接状态
  connectionStatus.value = appStore.socket.connected;
};

const subscribeToLogs = () => {
  if (!appStore.socket || !appStore.socket.connected) {
    return;
  }

  // 订阅所有日志更新
  appStore.socket.emit("log_subscribe", {
    log_type: "all",
  });

  console.log("📡 订阅所有日志类型");
};

const handleLogUpdate = (data) => {
  if (data.entry) {
    console.log(
      `📡 收到实时日志: [${data.entry.level}] ${data.entry.message.substring(0, 50)}...`,
    );
    addLogEntry(data.entry);
  }
};

const handleLogHistory = (data) => {
  if (data.logs && Array.isArray(data.logs)) {
    // 合并历史日志，避免重复
    const existingTimestamps = new Set(
      logs.value.map((log) => `${log.timestamp}-${log.message}`),
    );
    const newLogs = data.logs.filter(
      (log) => !existingTimestamps.has(`${log.timestamp}-${log.message}`),
    );

    logs.value = [...newLogs, ...logs.value].slice(-props.maxLogs);
    updateDisplayedLogs();
    saveCachedLogs();

    console.log(`📝 接收历史日志: ${newLogs.length} 条新日志`);
  }
};

const addLogEntry = (entry) => {
  // 检查是否已存在相同的日志条目
  const exists = logs.value.some(
    (log) =>
      log.timestamp === entry.timestamp &&
      log.message === entry.message &&
      log.level === entry.level,
  );

  if (!exists) {
    logs.value.push(entry);

    // 限制日志数量
    if (logs.value.length > props.maxLogs) {
      logs.value = logs.value.slice(-props.maxLogs);
    }

    updateDisplayedLogs();
    saveCachedLogs();

    // 自动滚动到底部
    if (props.autoScroll) {
      // 使用双重 nextTick 确保 DOM 完全更新
      nextTick(() => {
        nextTick(() => {
          scrollToBottom();
        });
      });
    }
  }
};

const updateDisplayedLogs = () => {
  // 简化版本：直接显示所有日志，不进行过滤
  displayedLogs.value = logs.value.slice(0, displayLimit.value);
};

const loadMoreLogs = () => {
  loadingMore.value = true;

  setTimeout(() => {
    const currentLength = displayedLogs.value.length;
    const nextBatch = logs.value.slice(currentLength, currentLength + 50);
    displayedLogs.value = [...displayedLogs.value, ...nextBatch];
    loadingMore.value = false;
  }, 300);
};

const refreshLogs = () => {
  if (!appStore.socket || !appStore.socket.connected) {
    return;
  }

  // 请求最新日志
  appStore.socket.emit("log_request", {
    log_type: "all",
    limit: 100,
  });
};

const clearLogs = () => {
  logs.value = [];
  displayedLogs.value = [];
  saveCachedLogs();

  // 通知服务器清空缓存
  if (appStore.socket && appStore.socket.connected) {
    appStore.socket.emit("log_clear", {
      log_type: "all",
    });
  }
};

const scrollToBottom = () => {
  if (logContainer.value) {
    // 使用 requestAnimationFrame 确保 DOM 更新完成后再滚动
    requestAnimationFrame(() => {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    });
  }
};

const formatTimestamp = (timestamp) => {
  if (!timestamp) return "";
  try {
    // 如果是完整的时间戳，只显示时分秒
    const date = new Date(timestamp);
    return date.toLocaleTimeString("zh-CN", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return timestamp;
  }
};

const initializeResponsiveSettings = () => {
  // 根据屏幕尺寸调整初始设置
  displayLimit.value = responsiveDisplayLimit.value;
};

// 监听器
watch(
  () => appStore.connectionStatus,
  (newStatus) => {
    connectionStatus.value = newStatus;
    if (newStatus) {
      subscribeToLogs();
    }
  },
);

// 监听器
watch(
  () => display.xs.value,
  (isXs) => {
    // 屏幕尺寸变化时调整设置
    if (isXs) {
      displayLimit.value = 50;
    } else {
      displayLimit.value = responsiveDisplayLimit.value;
    }
  },
);

// 生命周期
onMounted(() => {
  initializeResponsiveSettings();
  initializeLogViewer();
});

onUnmounted(() => {
  // 保存最终状态
  saveCachedLogs();
});
</script>

<style scoped>
.log-viewer {
  /* 使用固定高度，避免与内层容器冲突 */
  height: v-bind(containerHeight);
  min-height: v-bind(minHeight);
  max-height: v-bind(maxHeight);
  /* 确保日志查看器有正确的定位 */
  position: relative;
  z-index: 1;
  /* 防止内容溢出 */
  overflow: hidden;
  /* 使用flex布局确保内容区域正确分配空间 */
  display: flex;
  flex-direction: column;
}

/* 确保内容区域有正确的高度计算 */
.log-content-area {
  /* 确保内容区域能够正确伸缩 */
  min-height: 0;
  flex: 1;
}

.log-container {
  /* 使用flex-grow-1让容器自适应剩余空间 */
  flex: 1;
  overflow-y: auto;
  font-family:
    "JetBrains Mono", "Fira Code", "Consolas", "Monaco", "Courier New",
    monospace;
  font-size: 13px;
  line-height: 1.4;
  padding: 12px 16px;
  background-color: rgb(var(--v-theme-surface-container));
  border: 1px solid rgba(var(--v-theme-outline-variant), 0.3);
  border-radius: 8px;
  /* 使用标准的margin */
  margin: 0 16px 16px 16px;
  scroll-behavior: smooth;
  /* 确保容器有正确的定位 */
  position: relative;
  z-index: auto;
  /* 防止容器内容溢出到其他元素 */
  contain: layout style;
  /* 确保容器高度计算正确 */
  min-height: 0;
}

.log-entry {
  padding: 4px 8px;
  margin: 2px 0;
  word-wrap: break-word;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  border-radius: 4px;
  transition:
    background-color var(--md3-motion-duration-short)
      var(--md3-motion-easing-standard),
    border-left-color var(--md3-motion-duration-short)
      var(--md3-motion-easing-standard);
  border-left: 2px solid transparent;
  background-color: rgb(var(--v-theme-surface-container-low));
  color: rgb(var(--v-theme-on-surface));
}

.log-entry:hover {
  background-color: rgb(var(--v-theme-surface-container));
  border-left-color: rgba(var(--v-theme-primary), 0.3);
}

/* 不同级别的左边框颜色 */
.log-debug:hover {
  border-left-color: rgba(var(--v-theme-secondary), 0.5);
}

.log-info:hover {
  border-left-color: rgba(var(--v-theme-info), 0.5);
}

.log-warning:hover {
  border-left-color: rgba(var(--v-theme-warning), 0.7);
}

.log-error:hover {
  border-left-color: rgba(var(--v-theme-error), 0.7);
}

.log-timestamp {
  font-size: 11px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  flex-shrink: 0;
  min-width: 60px;
  font-weight: 500;
}

.log-level {
  font-weight: 600;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 2px;
  flex-shrink: 0;
  min-width: 50px;
  text-align: center;
}

.log-level-debug {
  background-color: rgba(var(--v-theme-secondary), 0.12);
  color: rgb(var(--v-theme-secondary));
  font-weight: 500;
  border: 1px solid rgba(var(--v-theme-secondary), 0.2);
}

.log-level-info {
  background-color: rgba(var(--v-theme-info), 0.12);
  color: rgb(var(--v-theme-info));
  font-weight: 600;
  border: 1px solid rgba(var(--v-theme-info), 0.2);
}

.log-level-warning {
  background-color: rgba(var(--v-theme-warning), 0.15);
  color: rgb(var(--v-theme-warning));
  font-weight: 600;
  border: 1px solid rgba(var(--v-theme-warning), 0.3);
}

.log-level-error {
  background-color: rgba(var(--v-theme-error), 0.15);
  color: rgb(var(--v-theme-error));
  font-weight: 700;
  border: 1px solid rgba(var(--v-theme-error), 0.3);
}

.log-source {
  font-size: 11px;
  font-weight: 500;
  color: rgb(var(--v-theme-primary));
  flex-shrink: 0;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.log-message {
  flex: 1;
  word-break: break-word;
  color: rgba(var(--v-theme-on-surface), 0.87);
  font-size: 12px;
  line-height: 1.4;
  font-weight: 400;
}

/* 不同级别日志的消息颜色 */
.log-debug .log-message {
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.log-info .log-message {
  color: rgba(var(--v-theme-on-surface), 0.87);
}

.log-warning .log-message {
  color: rgba(var(--v-theme-warning), 0.9);
  font-weight: 500;
}

.log-error .log-message {
  color: rgba(var(--v-theme-error), 0.9);
  font-weight: 600;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 120px;
}

.log-level-select {
  min-width: 80px;
  max-width: 100px;
}

/* 响应式优化 */
@media (max-width: 600px) {
  .log-container {
    font-size: 12px;
    padding: 6px 8px;
    margin: 0 8px 8px 8px;
  }

  .log-entry {
    gap: 4px;
    flex-wrap: wrap;
  }

  .log-timestamp {
    font-size: 10px;
    min-width: 50px;
  }

  .log-level {
    font-size: 9px;
    min-width: 40px;
  }

  .log-source {
    max-width: 60px;
    font-size: 10px;
  }

  .log-message {
    font-size: 11px;
    flex-basis: 100%;
  }

  .log-level-select {
    min-width: 70px;
    max-width: 80px;
  }
}

@media (max-width: 960px) {
  .log-container {
    margin: 0 12px 12px 12px;
  }
}

/* 滚动条优化 */
.log-container::-webkit-scrollbar {
  width: 6px;
}

.log-container::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-on-surface), 0.05);
  border-radius: 3px;
}

.log-container::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 3px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.3);
}
</style>
