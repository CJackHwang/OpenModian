<template>
  <div>
    <!-- 页面标题 - 统一设计 -->
    <div class="app-section">
      <div class="d-flex align-center">
        <v-avatar color="primary" class="me-4" size="64">
          <v-icon icon="mdi-spider" size="32" />
        </v-avatar>
        <div>
          <h1 class="text-h4 font-weight-medium mb-1">爬虫控制</h1>
          <p class="text-subtitle-1 text-medium-emphasis">配置和管理爬虫任务</p>
        </div>
      </div>
    </div>

    <v-row>
      <!-- 左侧配置面板 -->
      <v-col cols="12" lg="4">
        <v-card class="mb-4 app-card">
          <v-card-title class="p-lg">
            <v-avatar color="accent" size="32" class="me-3">
              <v-icon icon="mdi-cog" color="on-accent" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">爬虫配置</div>
              <div class="text-body-2 text-medium-emphasis">设置爬取参数</div>
            </div>
          </v-card-title>

          <v-card-text class="p-lg pt-0">
            <v-form ref="configForm" v-model="formValid">
              <!-- 爬取模式选择 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">爬取模式</v-label>
                <v-radio-group
                  v-model="config.crawlMode"
                  inline
                  density="compact"
                  :disabled="isRunning"
                  class="mt-2"
                >
                  <v-radio label="页面范围爬取" value="range" color="primary" />
                  <v-radio
                    label="仅爬取关注列表"
                    value="watchlist"
                    color="primary"
                  />
                </v-radio-group>
              </div>

              <!-- 关注列表模式信息 -->
              <div v-if="config.crawlMode === 'watchlist'" class="mb-4">
                <v-alert
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="text-caption"
                >
                  <v-icon start icon="mdi-heart" />
                  将爬取关注列表中的 {{ watchListCount }} 个项目
                  <template v-if="watchListCount === 0">
                    <br />请先在下方添加项目到关注列表
                  </template>
                </v-alert>
              </div>

              <!-- 页面范围设置（仅在范围模式下显示） -->
              <div v-if="config.crawlMode === 'range'">
                <!-- 页面范围 -->
                <div class="mb-4">
                  <v-label class="text-subtitle-2 mb-2">页面范围</v-label>
                  <v-row>
                    <v-col cols="6">
                      <v-text-field
                        v-model.number="config.startPage"
                        label="起始页"
                        type="number"
                        :min="1"
                        :rules="[(v) => v >= 1 || '起始页必须大于0']"
                        variant="outlined"
                        density="compact"
                        :disabled="isRunning"
                      />
                    </v-col>
                    <v-col cols="6">
                      <v-text-field
                        v-model.number="config.endPage"
                        label="结束页"
                        type="number"
                        :min="config.startPage"
                        :rules="[
                          (v) =>
                            v >= config.startPage || '结束页必须大于等于起始页',
                        ]"
                        variant="outlined"
                        density="compact"
                        :disabled="isRunning"
                      />
                    </v-col>
                  </v-row>
                </div>

                <!-- 项目分类 -->
                <div class="mb-4">
                  <v-label class="text-subtitle-2 mb-2">项目分类</v-label>
                  <v-select
                    v-model="config.category"
                    :items="categories"
                    item-title="label"
                    item-value="value"
                    label="选择分类"
                    variant="outlined"
                    density="compact"
                    :disabled="isRunning"
                  />
                </div>
              </div>

              <!-- 并发设置 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2"
                  >并发请求数: {{ config.maxConcurrent }}</v-label
                >
                <v-slider
                  v-model="config.maxConcurrent"
                  :min="1"
                  :max="10"
                  :step="1"
                  show-ticks
                  tick-size="4"
                  color="primary"
                />
              </div>

              <!-- 延迟设置 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">请求延迟 (秒)</v-label>
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="config.delayMin"
                      label="最小延迟"
                      type="number"
                      :min="0"
                      :step="0.1"
                      variant="outlined"
                      density="compact"
                    />
                  </v-col>
                  <v-col cols="6">
                    <v-text-field
                      v-model.number="config.delayMax"
                      label="最大延迟"
                      type="number"
                      :min="config.delayMin"
                      :step="0.1"
                      variant="outlined"
                      density="compact"
                    />
                  </v-col>
                </v-row>
              </div>

              <!-- 🔧 新增：后台定时任务配置 -->
              <div class="mb-4">
                <v-label class="text-subtitle-2 mb-2">任务类型</v-label>
                <v-switch
                  v-model="config.isScheduled"
                  label="后台定时任务"
                  color="primary"
                  inset
                  hide-details
                />
                <div v-if="config.isScheduled" class="mt-3">
                  <v-text-field
                    v-model.number="config.scheduleInterval"
                    label="执行间隔 (秒)"
                    type="number"
                    :min="5"
                    hint="最小间隔5秒，默认3600秒(1小时)"
                    variant="outlined"
                    density="compact"
                  />
                </div>
              </div>

              <!-- API数据获取说明 -->
              <div class="mb-4">
                <v-alert
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="text-caption"
                >
                  <v-icon start icon="mdi-api"></v-icon>
                  现在使用高性能API获取完整数据，速度提升10倍+，数据更完整
                </v-alert>
              </div>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- 操作按钮 -->
        <v-card class="app-card">
          <v-card-title class="p-lg">
            <v-avatar color="warning" size="32" class="me-3">
              <v-icon icon="mdi-play-circle" color="on-warning" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">任务控制</div>
              <div class="text-body-2 text-medium-emphasis">启动和停止爬虫</div>
            </div>
          </v-card-title>

          <v-card-text class="p-lg pt-0">
            <v-btn
              v-if="!isRunning"
              block
              color="primary"
              size="large"
              prepend-icon="mdi-play"
              @click="startCrawling"
              :disabled="!formValidation"
              :loading="starting"
              class="mb-3 app-button"
            >
              {{
                config.crawlMode === "watchlist"
                  ? "开始爬取关注列表"
                  : "开始爬取"
              }}
            </v-btn>

            <v-btn
              v-else
              block
              color="error"
              size="large"
              prepend-icon="mdi-stop"
              @click="stopCrawling"
              :loading="stopping"
              class="mb-3 app-button"
            >
              停止爬取
            </v-btn>

            <v-btn
              block
              variant="outlined"
              prepend-icon="mdi-refresh"
              @click="loadDefaultConfig"
              :disabled="isRunning"
              class="app-button"
            >
              重置配置
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 右侧状态面板 -->
      <v-col cols="12" lg="8">
        <!-- 当前任务状态 -->
        <v-card class="mb-4 app-card">
          <v-card-title class="p-lg">
            <v-avatar color="primary" size="32" class="me-3">
              <v-icon icon="mdi-information" color="on-primary" size="18" />
            </v-avatar>
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold">当前任务状态</div>
              <div class="text-body-2 text-medium-emphasis">
                实时监控爬虫进度
              </div>
            </div>
            <v-chip
              v-if="currentTask"
              :color="getTaskStatusColor(currentTask.status)"
              class="app-chip"
            >
              {{ getTaskStatusText(currentTask.status) }}
            </v-chip>
          </v-card-title>

          <v-card-text class="p-lg pt-0">
            <v-sheet v-if="currentTask && currentTask.id" color="transparent">
              <!-- 任务信息 -->
              <v-row class="mb-4">
                <v-col cols="12" md="6">
                  <v-card-text class="text-subtitle-2 mb-1 pa-0">任务ID</v-card-text>
                  <v-card-text class="text-body-2 font-mono pa-0">{{ currentTask.id }}</v-card-text>
                </v-col>
                <v-col cols="12" md="6">
                  <v-card-text class="text-subtitle-2 mb-1 pa-0">开始时间</v-card-text>
                  <v-card-text class="text-body-2 pa-0">
                    {{ formatTime(currentTask.startTime) }}
                  </v-card-text>
                </v-col>
              </v-row>

              <!-- 进度条 -->
              <v-sheet class="mb-4" color="transparent">
                <v-sheet class="d-flex justify-space-between mb-2" color="transparent">
                  <v-chip class="text-subtitle-2" variant="text" size="small">爬取进度</v-chip>
                  <v-chip class="text-subtitle-2" variant="text" size="small"
                    >{{ Math.round(currentTask.progress || 0) }}%</v-chip
                  >
                </v-sheet>
                <v-progress-linear
                  :model-value="currentTask.progress || 0"
                  height="12"
                  rounded
                  color="primary"
                  striped
                />
              </v-sheet>

              <!-- 详细进度信息 -->
              <div class="mb-4" v-if="currentTask.stats">
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-1">页面进度</div>
                    <div class="text-body-2">
                      {{ currentTask.stats.current_page || 0 }} /
                      {{ currentTask.stats.total_pages || 0 }} 页
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-subtitle-2 mb-1">项目进度</div>
                    <div class="text-body-2">
                      {{ currentTask.stats.projects_processed || 0 }} /
                      {{ currentTask.stats.total_projects || 0 }} 个项目
                    </div>
                  </v-col>
                </v-row>
              </div>

              <!-- 统计信息 -->
              <v-row class="text-center">
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-primary">
                    {{ currentTask.stats?.pagesCrawled || 0 }}
                  </div>
                  <div class="text-caption">已爬页面</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-success">
                    {{ currentTask.stats?.projectsFound || 0 }}
                  </div>
                  <div class="text-caption">发现项目</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-info">
                    {{ currentTask.stats?.projectsProcessed || 0 }}
                  </div>
                  <div class="text-caption">已处理</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-h6 font-weight-bold text-error">
                    {{ currentTask.stats?.errors || 0 }}
                  </div>
                  <div class="text-caption">错误数</div>
                </v-col>
              </v-row>
            </v-sheet>

            <div v-else class="text-center py-8">
              <v-icon icon="mdi-sleep" size="64" class="mb-4" />
              <div class="text-h6">暂无活跃任务</div>
              <div class="text-subtitle-2">
                配置参数后点击"开始爬取"启动任务
              </div>
            </div>
          </v-card-text>
        </v-card>

        <!-- 实时日志 -->
        <RealTimeLogViewer
          :height="logViewerHeight"
          :min-height="'300px'"
          :max-height="'600px'"
          :max-logs="500"
          :auto-scroll="true"
          :compact="display.xs.value"
        />
      </v-col>
    </v-row>

    <!-- 关注列表管理 -->
    <v-row>
      <v-col cols="12">
        <WatchListManager
          ref="watchListManagerRef"
          @update:count="watchListCount = $event"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import { useAppStore } from "@/stores/app";
import { useDisplay } from "vuetify";
import { useSnackbar } from "@/composables/useSnackbar";
import axios from "axios";
import RealTimeLogViewer from "@/components/RealTimeLogViewer.vue";
import WatchListManager from "@/components/WatchListManager.vue";
import { pageCache } from "@/utils/pageCache";

const appStore = useAppStore();
const display = useDisplay();
const { showSnackbar } = useSnackbar();

// 响应式数据
const formValid = ref(false);
const starting = ref(false);
const stopping = ref(false);
const categories = ref([]);
const currentTask = ref(null);

// 配置数据
const config = reactive({
  crawlMode: "range", // 'range' 或 'watchlist'
  startPage: 1,
  endPage: 10,
  category: "all",
  maxConcurrent: 3,
  delayMin: 1.0,
  delayMax: 3.0,
  isScheduled: false,
  scheduleInterval: 3600,
});

// 关注列表管理
const watchListManagerRef = ref(null);
const watchListCount = ref(0);

// 计算属性
const isRunning = computed(() => {
  return (
    currentTask.value &&
    ["starting", "running"].includes(currentTask.value.status)
  );
});

// 表单验证
const formValidation = computed(() => {
  if (config.crawlMode === "watchlist") {
    // 关注列表模式：只需要有关注项目
    return watchListCount.value > 0;
  } else {
    // 页面范围模式：需要有效的页面范围
    return (
      config.startPage >= 1 &&
      config.endPage >= config.startPage &&
      config.category
    );
  }
});

// 日志查看器高度计算
const logViewerHeight = computed(() => {
  if (display.xs.value) return "300px";
  if (display.sm.value) return "350px";
  if (display.md.value) return "400px";
  return "450px";
});

// 方法
const loadDefaultConfig = async () => {
  try {
    // 优先使用包含用户设置的配置API
    const response = await axios.get("/api/config/with_user_settings");
    if (response.data.success) {
      const defaultConfig = response.data.config;
      config.startPage = defaultConfig.start_page;
      config.endPage = defaultConfig.end_page;
      config.category = defaultConfig.category;
      config.maxConcurrent = defaultConfig.max_concurrent;
      config.delayMin = defaultConfig.delay_min;
      config.delayMax = defaultConfig.delay_max;
      categories.value = defaultConfig.categories;

      console.log("✅ 已加载用户设置配置:", defaultConfig);
    } else {
      // 如果新API失败，回退到原API
      const fallbackResponse = await axios.get("/api/config");
      if (fallbackResponse.data.success) {
        const defaultConfig = fallbackResponse.data.config;
        config.startPage = defaultConfig.start_page;
        config.endPage = defaultConfig.end_page;
        config.category = defaultConfig.category;
        config.maxConcurrent = defaultConfig.max_concurrent;
        config.delayMin = defaultConfig.delay_min;
        config.delayMax = defaultConfig.delay_max;
        categories.value = defaultConfig.categories;

        console.log("⚠️ 使用默认配置（用户设置API不可用）");
      }
    }
  } catch (error) {
    console.error("加载默认配置失败:", error);
  }
};

const startCrawling = async () => {
  if (!formValidation.value) return;

  starting.value = true;
  try {
    const requestData = {
      max_concurrent: config.maxConcurrent,
      delay_min: config.delayMin,
      delay_max: config.delayMax,
      is_scheduled: config.isScheduled,
      schedule_interval: config.scheduleInterval,
      crawl_mode: config.crawlMode,
    };

    if (config.crawlMode === "range") {
      // 页面范围模式
      requestData.start_page = config.startPage;
      requestData.end_page = config.endPage;
      requestData.category = config.category;
      requestData.include_watch_list = false;
    } else if (config.crawlMode === "watchlist") {
      // 关注列表模式
      if (watchListManagerRef.value) {
        const watchedProjectIds =
          watchListManagerRef.value.getWatchedProjectIds();
        if (watchedProjectIds.length > 0) {
          requestData.watched_project_ids = watchedProjectIds;
          requestData.include_watch_list = true;
          requestData.watch_list_only = true;  // 新增：仅爬取关注列表标识
          // 关注列表模式不需要页面范围
          requestData.start_page = 1;
          requestData.end_page = 1;
          requestData.category = "all";
        } else {
          throw new Error("关注列表为空，无法启动爬取");
        }
      }
    }

    const response = await axios.post("/api/start_crawl", requestData);

    if (response.data.success) {
      if (config.isScheduled) {
        console.log(`✅ 定时任务已创建: ${response.data.task_id}`);

        // 显示成功提示
        showSnackbar(
          `定时任务创建成功！任务ID: ${response.data.task_id}，执行间隔: ${config.scheduleInterval}秒`,
          "success",
          6000
        );

        // 通过WebSocket发送日志
        if (appStore.socket && appStore.socket.connected) {
          appStore.socket.emit("log_manual", {
            log_type: "webui",
            level: "info",
            message: `定时任务已创建: ${response.data.task_id}`,
            source: "spider-control",
          });
          appStore.socket.emit("log_manual", {
            log_type: "webui",
            level: "info",
            message: `执行间隔: ${config.scheduleInterval}秒`,
            source: "spider-control",
          });
        }
      } else {
        console.log(`✅ 任务已启动: ${response.data.task_id}`);

        // 设置当前任务状态
        currentTask.value = {
          id: response.data.task_id,
          status: "starting",
          progress: 0,
          startTime: new Date().toISOString(),
          stats: {
            status: "starting",
            progress: 0,
            pages_crawled: 0,
            projects_found: 0,
            projects_processed: 0,
            errors: 0,
          },
        };

        // 通过WebSocket发送日志
        if (appStore.socket && appStore.socket.connected) {
          appStore.socket.emit("log_manual", {
            log_type: "webui",
            level: "info",
            message: `爬虫任务已启动: ${response.data.task_id}`,
            source: "spider-control",
          });
        }

        // 开始轮询任务状态
        startPolling();

        // 缓存任务状态
        pageCache.cacheSpiderTask("current", currentTask.value);
      }
    } else {
      console.error(`❌ 启动失败: ${response.data.message}`);
      // 通过WebSocket发送错误日志
      if (appStore.socket && appStore.socket.connected) {
        appStore.socket.emit("log_manual", {
          log_type: "webui",
          level: "error",
          message: `启动失败: ${response.data.message}`,
          source: "spider-control",
        });
      }
    }
  } catch (error) {
    console.error(`❌ 启动失败: ${error.message}`);
    // 通过WebSocket发送错误日志
    if (appStore.socket && appStore.socket.connected) {
      appStore.socket.emit("log_manual", {
        log_type: "webui",
        level: "error",
        message: `启动失败: ${error.message}`,
        source: "spider-control",
      });
    }
  } finally {
    starting.value = false;
  }
};

const stopCrawling = async () => {
  if (!currentTask.value?.id) return;

  stopping.value = true;
  try {
    const response = await axios.post(
      `/api/stop_crawl/${currentTask.value.id}`,
    );

    if (response.data.success) {
      console.log("⚠️ 任务已停止");

      // 更新任务状态
      if (currentTask.value) {
        currentTask.value.status = "stopped";
        currentTask.value.stats.status = "stopped";

        // 缓存更新后的状态
        pageCache.cacheSpiderTask("current", currentTask.value);
      }

      // 停止轮询
      stopPolling();

      // 通过WebSocket发送日志
      if (appStore.socket && appStore.socket.connected) {
        appStore.socket.emit("log_manual", {
          log_type: "webui",
          level: "warning",
          message: "爬虫任务已停止",
          source: "spider-control",
        });
      }
    } else {
      console.error(`❌ 停止失败: ${response.data.message}`);
      // 通过WebSocket发送错误日志
      if (appStore.socket && appStore.socket.connected) {
        appStore.socket.emit("log_manual", {
          log_type: "webui",
          level: "error",
          message: `停止失败: ${response.data.message}`,
          source: "spider-control",
        });
      }
    }
  } catch (error) {
    console.error(`❌ 停止失败: ${error.message}`);
    // 通过WebSocket发送错误日志
    if (appStore.socket && appStore.socket.connected) {
      appStore.socket.emit("log_manual", {
        log_type: "webui",
        level: "error",
        message: `停止失败: ${error.message}`,
        source: "spider-control",
      });
    }
  } finally {
    stopping.value = false;
  }
};

// 日志功能现在由RealTimeLogViewer组件处理

const getTaskStatusColor = (status) => {
  const colors = {
    idle: "grey",
    starting: "warning",
    running: "success",
    completed: "primary",
    failed: "error",
    stopped: "secondary",
  };
  return colors[status] || "grey";
};

const getTaskStatusText = (status) => {
  const texts = {
    idle: "空闲",
    starting: "启动中",
    running: "运行中",
    completed: "已完成",
    failed: "失败",
    stopped: "已停止",
  };
  return texts[status] || "未知";
};

const formatTime = (timeStr) => {
  if (!timeStr) return "-";
  return new Date(timeStr).toLocaleString();
};

// 轮询任务状态
let pollingInterval = null;

const startPolling = () => {
  if (pollingInterval) return;

  pollingInterval = setInterval(async () => {
    try {
      const response = await axios.get("/api/tasks");
      if (response.data.success && response.data.tasks.length > 0) {
        const task = response.data.tasks[0]; // 获取最新任务
        currentTask.value = {
          id: task.task_id,
          status: task.stats.status,
          progress: task.stats.progress,
          startTime: task.stats.start_time,
          stats: task.stats,
        };

        // 缓存任务状态
        pageCache.cacheSpiderTask("current", currentTask.value);

        // 如果任务完成或失败，停止轮询并清理缓存
        if (["completed", "failed", "stopped"].includes(task.stats.status)) {
          stopPolling();
          // 延迟清理缓存，让用户能看到最终状态
          setTimeout(() => {
            pageCache.removeSpiderTask("current");
          }, 30000); // 30秒后清理
        }
      }
    } catch (error) {
      console.error("轮询任务状态失败:", error);
    }
  }, 2000); // 每2秒轮询一次
};

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
};

// 恢复任务状态
const restoreTaskState = async () => {
  try {
    // 1. 尝试从缓存恢复
    const cachedTask = pageCache.getSpiderTask("current");
    if (cachedTask && cachedTask.taskData) {
      console.log("📋 从缓存恢复任务状态:", cachedTask.taskData);
      currentTask.value = cachedTask.taskData;
    }

    // 2. 查询服务器当前活跃任务
    const response = await axios.get("/api/tasks");
    if (response.data.success && response.data.tasks.length > 0) {
      // 查找正在运行的任务
      const runningTask = response.data.tasks.find((task) =>
        ["running", "starting"].includes(task.stats.status),
      );

      if (runningTask) {
        console.log("🔄 发现正在运行的任务:", runningTask);
        currentTask.value = {
          id: runningTask.task_id,
          status: runningTask.stats.status,
          progress: runningTask.stats.progress,
          startTime: runningTask.stats.start_time,
          stats: runningTask.stats,
        };

        // 开始轮询
        startPolling();

        // 缓存任务状态
        pageCache.cacheSpiderTask("current", currentTask.value);
      } else {
        // 没有运行中的任务，清理缓存
        pageCache.removeSpiderTask("current");
        currentTask.value = null;
      }
    }
  } catch (error) {
    console.error("恢复任务状态失败:", error);
  }
};

// 更新关注列表数量
const updateWatchListCount = () => {
  if (watchListManagerRef.value) {
    watchListCount.value = watchListManagerRef.value.getTotalCount() || 0;
  }
};

// 生命周期
onMounted(() => {
  loadDefaultConfig();

  // 恢复任务状态
  restoreTaskState();

  // 监听WebSocket消息
  const setupWebSocketListeners = () => {
    if (appStore.socket) {
      console.log("🔌 设置WebSocket监听器");

      appStore.socket.on("task_update", (data) => {
        console.log("📊 收到任务更新:", data);

        if (data.task_id && data.stats) {
          currentTask.value = {
            id: data.task_id,
            status: data.stats.status,
            progress: data.stats.progress,
            startTime: data.stats.start_time,
            stats: data.stats,
          };

          // 缓存最新任务状态
          pageCache.cacheSpiderTask("current", currentTask.value);

          // 日志更新现在由RealTimeLogViewer组件处理
        }
      });

      appStore.socket.on("connect", () => {
        console.log("✅ WebSocket已连接，重新设置监听器");
        // WebSocket重连后重新查询任务状态
        restoreTaskState();
      });
    } else {
      console.log("⚠️ WebSocket未初始化，1秒后重试");
      setTimeout(setupWebSocketListeners, 1000);
    }
  };

  setupWebSocketListeners();

  // 初始化关注列表数量
  setTimeout(() => {
    updateWatchListCount();
  }, 1000);
});

onUnmounted(() => {
  stopPolling();
});
</script>

<style scoped>
.font-mono {
  font-family: "Courier New", monospace;
}
</style>
