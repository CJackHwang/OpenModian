<template>
  <v-container fluid class="fill-height pa-0">
    <v-row no-gutters class="fill-height">
      <v-col cols="12" class="d-flex flex-column">
        <!-- 控制面板 -->
        <v-card elevation="2" class="mb-4 flex-shrink-0">
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
                  <v-row no-gutters class="ga-2">
                    <v-col cols="4" md="12" lg="4">
                      <v-btn
                        color="primary"
                        variant="outlined"
                        @click="refreshLogs"
                        :disabled="!connectionStatus"
                        :size="display.xs.value ? 'small' : 'default'"
                        :block="display.mdAndDown.value"
                        class="log-action-btn"
                      >
                        <v-icon icon="mdi-refresh" :class="display.xs.value ? '' : 'me-1'" />
                        <span v-if="!display.xs.value">刷新</span>
                      </v-btn>
                    </v-col>

                    <v-col cols="4" md="12" lg="4">
                      <v-btn
                        color="warning"
                        variant="outlined"
                        @click="clearLogs"
                        :disabled="!logs.length"
                        :size="display.xs.value ? 'small' : 'default'"
                        :block="display.mdAndDown.value"
                        class="log-action-btn"
                      >
                        <v-icon icon="mdi-delete" :class="display.xs.value ? '' : 'me-1'" />
                        <span v-if="!display.xs.value">清空</span>
                      </v-btn>
                    </v-col>

                    <v-col cols="4" md="12" lg="4">
                      <v-btn
                        color="success"
                        variant="outlined"
                        @click="exportLogs"
                        :disabled="!filteredLogs.length"
                        :size="display.xs.value ? 'small' : 'default'"
                        :block="display.mdAndDown.value"
                        class="log-action-btn"
                      >
                        <v-icon icon="mdi-download" :class="display.xs.value ? '' : 'me-1'" />
                        <span v-if="!display.xs.value">导出</span>
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

        <!-- 日志查看器 - 使用flex-grow-1自动填充剩余空间 -->
        <div class="flex-grow-1 d-flex flex-column">
          <RealTimeLogViewer
            height="auto"
            min-height="200px"
            max-height="none"
            :max-logs="1000"
            :auto-scroll="true"
            :compact="display.xs.value"
            ref="logViewer"
          />
        </div>
      </v-col>
    </v-row>


  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
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

// 方法
const changeLogType = (newType) => {
  selectedLogType.value = newType;
  if (logViewer.value) {
    logViewer.value.changeLogType(newType);
  }
};

const applyFilters = () => {
  if (logViewer.value) {
    // 将过滤参数传递给子组件
    logViewer.value.applyFilters(selectedLevel.value, searchTerm.value);
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
/* 按钮样式优化 */
.log-action-btn {
  /* 确保按钮文字不会被截断 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 确保容器使用全部可用高度 */
.fill-height {
  height: 100%;
}
</style>
