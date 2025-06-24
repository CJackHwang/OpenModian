<template>
  <div class="log-viewer-page">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card elevation="2" class="mb-4">
            <v-card-title class="d-flex align-center">
              <v-icon icon="mdi-console-line" class="me-3" />
              实时日志监控
              <v-spacer />


            </v-card-title>

            <v-card-text>
              <v-row>
                <v-col cols="12" md="3">
                  <v-select
                    v-model="selectedLogType"
                    :items="logTypes"
                    item-title="label"
                    item-value="value"
                    label="日志类型"
                    variant="outlined"
                    density="compact"
                    @update:model-value="changeLogType"
                  />
                </v-col>

                <v-col cols="12" md="2">
                  <v-select
                    v-model="selectedLevel"
                    :items="logLevels"
                    item-title="label"
                    item-value="value"
                    label="日志级别"
                    variant="outlined"
                    density="compact"
                    @update:model-value="applyFilters"
                  />
                </v-col>

                <v-col cols="12" md="4">
                  <v-text-field
                    v-model="searchTerm"
                    label="搜索日志内容"
                    variant="outlined"
                    density="compact"
                    prepend-inner-icon="mdi-magnify"
                    clearable
                    @update:model-value="applyFilters"
                  />
                </v-col>

                <v-col cols="12" md="3">
                  <div class="d-flex gap-2">
                    <v-btn
                      color="primary"
                      variant="outlined"
                      @click="refreshLogs"
                      :disabled="!connectionStatus"
                    >
                      <v-icon icon="mdi-refresh" class="me-1" />
                      刷新
                    </v-btn>

                    <v-btn
                      color="warning"
                      variant="outlined"
                      @click="clearLogs"
                      :disabled="!logs.length"
                    >
                      <v-icon icon="mdi-delete" class="me-1" />
                      清空
                    </v-btn>

                    <v-btn
                      color="success"
                      variant="outlined"
                      @click="exportLogs"
                      :disabled="!filteredLogs.length"
                    >
                      <v-icon icon="mdi-download" class="me-1" />
                      导出
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <RealTimeLogViewer
            :height="logViewerHeight"
            :min-height="'400px'"
            :max-height="'calc(100vh - 250px)'"
            :max-logs="1000"
            :auto-scroll="autoScroll"
            :compact="false"
            ref="logViewer"
          />
        </v-col>
      </v-row>

      <!-- 浮动操作按钮 -->
      <v-fab
        v-model="autoScroll"
        :icon="autoScroll ? 'mdi-arrow-down-bold' : 'mdi-pause'"
        location="bottom end"
        size="small"
        :color="autoScroll ? 'success' : 'warning'"
        @click="toggleAutoScroll"
      />

      <!-- 测试日志按钮 -->
      <v-speed-dial
        v-model="testDialOpen"
        location="bottom start"
        transition="slide-y-reverse-transition"
      >
        <template v-slot:activator="{ props: activatorProps }">
          <v-fab
            v-bind="activatorProps"
            icon="mdi-test-tube"
            color="secondary"
            size="small"
          />
        </template>

        <v-fab
          icon="mdi-information"
          size="x-small"
          color="info"
          @click="sendTestLog('info')"
        />

        <v-fab
          icon="mdi-alert"
          size="x-small"
          color="warning"
          @click="sendTestLog('warning')"
        />

        <v-fab
          icon="mdi-close-circle"
          size="x-small"
          color="error"
          @click="sendTestLog('error')"
        />

        <v-fab
          icon="mdi-bug"
          size="x-small"
          color="purple"
          @click="sendTestLog('debug')"
        />
      </v-speed-dial>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useAppStore } from "@/stores/app";
import { useDisplay } from "vuetify";
import RealTimeLogViewer from "@/components/RealTimeLogViewer.vue";

// Store
const appStore = useAppStore();
const display = useDisplay();

// 响应式数据
const connectionStatus = ref(false);
const selectedLogType = ref("all");
const selectedLevel = ref("all");
const searchTerm = ref("");
const autoScroll = ref(true);
const testDialOpen = ref(false);
const logs = ref([]);
const filteredLogs = ref([]);
const logViewer = ref(null);

// 配置选项
const logTypes = [
  { label: "全部日志", value: "all" },
  { label: "系统日志", value: "system" },
  { label: "爬虫日志", value: "spider" },
  { label: "Web界面日志", value: "webui" },
];

const logLevels = [
  { label: "全部级别", value: "all" },
  { label: "DEBUG", value: "debug" },
  { label: "INFO", value: "info" },
  { label: "WARNING", value: "warning" },
  { label: "ERROR", value: "error" },
];

// 计算属性
const totalLogs = computed(() => {
  return filteredLogs.value.length;
});

// 日志查看器高度计算
const logViewerHeight = computed(() => {
  if (display.xs.value) return "400px";
  if (display.sm.value) return "500px";
  return "calc(100vh - 300px)";
});

// 方法
const changeLogType = (newType) => {
  selectedLogType.value = newType;
  if (logViewer.value) {
    logViewer.value.changeLogType(newType);
  }
};

const applyFilters = () => {
  if (logViewer.value) {
    logViewer.value.applyFilters();
  }
};

const refreshLogs = () => {
  if (logViewer.value) {
    logViewer.value.refreshLogs();
  }
};

const clearLogs = () => {
  if (logViewer.value) {
    logViewer.value.clearLogs();
  }
};

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value;
};

const sendTestLog = (level) => {
  if (!appStore.socket || !appStore.socket.connected) {
    return;
  }

  const messages = {
    info: "这是一条测试信息日志",
    warning: "这是一条测试警告日志",
    error: "这是一条测试错误日志",
    debug: "这是一条测试调试日志",
  };

  appStore.socket.emit("log_manual", {
    log_type:
      selectedLogType.value === "all" ? "system" : selectedLogType.value,
    level: level,
    message: `${messages[level]} - ${new Date().toLocaleTimeString()}`,
    source: "log-viewer-test",
  });

  testDialOpen.value = false;
};

const exportLogs = () => {
  if (!filteredLogs.value.length) {
    return;
  }

  // 准备导出数据
  const exportData = filteredLogs.value.map((log) => ({
    时间: log.timestamp,
    级别: log.level,
    来源: log.source || "",
    消息: log.message,
  }));

  // 转换为CSV格式
  const headers = ["时间", "级别", "来源", "消息"];
  const csvContent = [
    headers.join(","),
    ...exportData.map((row) =>
      headers.map((header) => `"${row[header] || ""}"`).join(","),
    ),
  ].join("\n");

  // 下载文件
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute(
    "download",
    `logs_${selectedLogType.value}_${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.csv`,
  );
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 监听连接状态
const setupConnectionMonitor = () => {
  if (appStore.socket) {
    connectionStatus.value = appStore.socket.connected;

    appStore.socket.on("connect", () => {
      connectionStatus.value = true;
    });

    appStore.socket.on("disconnect", () => {
      connectionStatus.value = false;
    });
  }
};

// 生命周期
onMounted(() => {
  setupConnectionMonitor();
});

onUnmounted(() => {
  // 清理监听器
  if (appStore.socket) {
    appStore.socket.off("connect");
    appStore.socket.off("disconnect");
  }
});
</script>

<style scoped>
.log-viewer-page {
  height: 100vh;
  overflow: hidden;
}

.gap-2 {
  gap: 8px;
}
</style>
