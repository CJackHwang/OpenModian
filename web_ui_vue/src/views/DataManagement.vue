<template>
  <div>
    <!-- 页面标题 -->
    <v-row class="mb-8">
      <v-col>
        <div class="d-flex align-center mb-4">
          <v-avatar color="primary" class="me-4" size="64">
            <v-icon icon="mdi-database" size="32" />
          </v-avatar>
          <div>
            <h1 class="text-h4 font-weight-medium mb-1">数据管理</h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              查看、搜索和管理爬取的项目数据
            </p>
          </div>
        </div>
      </v-col>
      <v-col cols="auto" class="d-flex align-center ga-3">
        <v-chip color="info" prepend-icon="mdi-database" class="app-chip">
          {{ projects.length }} 个项目
        </v-chip>
        <v-btn
          color="primary"
          prepend-icon="mdi-download"
          @click="exportData"
          :loading="exporting"
          size="large"
          class="app-button"
        >
          导出数据
        </v-btn>
        <v-btn
          color="secondary"
          prepend-icon="mdi-refresh"
          @click="refreshData"
          :loading="loading"
          size="large"
          class="app-button"
        >
          刷新
        </v-btn>
      </v-col>
    </v-row>

    <!-- 数据统计 -->
    <v-row class="mb-8">
      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center stats-card app-card"
          color="primary-container"
        >
          <v-card-text class="p-lg">
            <v-avatar color="primary" size="80" class="mb-4">
              <v-icon icon="mdi-database" size="40" color="on-primary" />
            </v-avatar>
            <div
              class="text-h3 font-weight-medium text-on-primary-container mb-2"
            >
              {{ stats.total }}
            </div>
            <div
              class="text-subtitle-1 text-on-primary-container font-weight-medium"
            >
              总项目数
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center stats-card app-card"
          color="secondary-container"
        >
          <v-card-text class="p-lg">
            <v-avatar color="secondary" size="80" class="mb-4">
              <v-icon
                icon="mdi-calendar-today"
                size="40"
                color="on-secondary"
              />
            </v-avatar>
            <div
              class="text-h3 font-weight-medium text-on-secondary-container mb-2"
            >
              {{ stats.today }}
            </div>
            <div
              class="text-subtitle-1 text-on-secondary-container font-weight-medium"
            >
              今日新增
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card
          class="text-center stats-card app-card"
          color="success-container"
        >
          <v-card-text class="p-lg">
            <v-avatar color="success" size="80" class="mb-4">
              <v-icon icon="mdi-calendar-week" size="40" color="on-success" />
            </v-avatar>
            <div
              class="text-h3 font-weight-medium text-on-success-container mb-2"
            >
              {{ stats.week }}
            </div>
            <div
              class="text-subtitle-1 text-on-success-container font-weight-medium"
            >
              本周新增
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center stats-card app-card" color="info-container">
          <v-card-text class="p-lg">
            <v-avatar color="info" size="80" class="mb-4">
              <v-icon icon="mdi-currency-cny" size="40" color="on-info" />
            </v-avatar>
            <div class="text-h3 font-weight-medium text-on-info-container mb-2">
              {{ formatCurrency(stats.totalAmount) }}
            </div>
            <div
              class="text-subtitle-1 text-on-info-container font-weight-medium"
            >
              总筹款金额
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 选项卡导航 - MD3优化 -->
    <v-card elevation="0" class="mb-6" rounded="xl">
      <v-tabs
        v-model="activeTab"
        color="primary"
        align-tabs="start"
        height="64"
      >
        <v-tab value="data" class="text-none">
          <v-icon icon="mdi-table" class="me-2" />
          数据查看
        </v-tab>
        <v-tab value="backup" class="text-none">
          <v-icon icon="mdi-backup-restore" class="me-2" />
          备份管理
        </v-tab>
      </v-tabs>
    </v-card>

    <!-- 选项卡内容 -->
    <v-window v-model="activeTab">
      <!-- 数据查看选项卡 -->
      <v-window-item value="data">
        <!-- 筛选和搜索 - MD3优化 -->
        <v-card elevation="0" class="mb-6" rounded="xl">
          <v-card-title class="pa-6">
            <v-avatar color="tertiary" size="32" class="me-3">
              <v-icon icon="mdi-filter" color="on-tertiary" size="18" />
            </v-avatar>
            <div>
              <div class="text-h6 font-weight-bold">数据筛选</div>
              <div class="text-body-2 text-medium-emphasis">
                快速筛选和搜索项目数据
              </div>
            </div>
          </v-card-title>

          <v-card-text class="pa-6 pt-0">
            <v-row>
              <v-col cols="12" md="2">
                <v-select
                  v-model="filters.period"
                  :items="periodOptions"
                  label="时间范围"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-calendar"
                  @update:model-value="applyFilters"
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-select
                  v-model="filters.category"
                  :items="categoryOptions"
                  label="项目分类"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-tag"
                  @update:model-value="applyFilters"
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field
                  v-model="filters.projectId"
                  label="项目ID"
                  prepend-inner-icon="mdi-identifier"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="debounceSearch"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="filters.search"
                  label="搜索项目名称"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  @update:model-value="debounceSearch"
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-btn
                  block
                  color="primary"
                  @click="applyFilters"
                  :loading="loading"
                  variant="elevated"
                  size="large"
                >
                  搜索
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 数据表格 - MD3优化 -->
        <v-card elevation="0" rounded="xl">
          <v-card-title class="pa-6">
            <v-avatar color="primary" size="32" class="me-3">
              <v-icon icon="mdi-table" color="on-primary" size="18" />
            </v-avatar>
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold">项目数据</div>
              <div class="text-body-2 text-medium-emphasis">
                详细的项目信息列表
              </div>
            </div>
            <div class="d-flex align-center ga-2">
              <v-chip variant="tonal" color="info" prepend-icon="mdi-database">
                共 {{ totalCount }} 条记录
              </v-chip>
              <v-chip
                variant="outlined"
                color="warning"
                size="small"
                prepend-icon="mdi-information"
              >
                每页最多100条
              </v-chip>
            </div>
          </v-card-title>

          <v-data-table-server
            :headers="headers"
            :items="projects"
            :loading="loading"
            :items-per-page="itemsPerPage"
            :page="currentPage"
            :items-length="totalCount"
            :items-per-page-options="itemsPerPageOptions"
            class="data-table elevation-0"
            item-value="id"
            density="default"
            :mobile-breakpoint="0"
            show-current-page
            @update:options="onTableOptionsUpdate"
          >
            <!-- 项目名称列 -->
            <template #item.project_name="{ item }">
              <div class="d-flex align-center">
                <div>
                  <v-btn
                    variant="text"
                    color="primary"
                    class="text-left pa-0 font-weight-medium"
                    style="text-transform: none; justify-content: flex-start"
                    @click="goToProjectDetail(item.project_id)"
                  >
                    {{ item.project_name || "未知项目" }}
                  </v-btn>
                  <div class="text-caption text-medium-emphasis">
                    ID: {{ item.project_id || "-" }}
                  </div>
                </div>
              </div>
            </template>

            <!-- 分类列 -->
            <template #item.category="{ item }">
              <v-chip
                size="small"
                variant="tonal"
                :color="getCategoryColor(item.category)"
              >
                {{ getCategoryDisplayName(item.category) }}
              </v-chip>
            </template>

            <!-- 作者列 -->
            <template #item.author_name="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="24" class="me-2">
                  <v-img
                    v-if="isValidImageUrl(item.author_image)"
                    :src="item.author_image"
                    :alt="item.author_name"
                  >
                    <template v-slot:error>
                      <v-icon icon="mdi-account" size="16" />
                    </template>
                  </v-img>
                  <v-icon v-else icon="mdi-account" size="16" />
                </v-avatar>
                <span class="text-truncate">{{
                  item.author_name || "未知作者"
                }}</span>
              </div>
            </template>

            <!-- 金额列 -->
            <template #item.raised_amount="{ item }">
              <div class="text-right">
                <div class="font-weight-bold text-success">
                  ¥{{ formatNumber(item.raised_amount || 0) }}
                </div>
                <div class="text-caption text-medium-emphasis">
                  目标: ¥{{ formatNumber(item.target_amount || 0) }}
                </div>
                <div
                  class="text-caption"
                  :class="getCompletionColor(item.completion_rate)"
                >
                  {{ formatPercentage(item.completion_rate) }}
                </div>
              </div>
            </template>

            <!-- 支持者数列 -->
            <template #item.backer_count="{ item }">
              <div class="text-center">
                <v-chip size="small" color="primary" variant="tonal">
                  {{ formatNumber(item.backer_count || 0) }}
                </v-chip>
              </div>
            </template>

            <!-- 评论数列 -->
            <template #item.comment_count="{ item }">
              <div class="text-center">
                <v-chip size="small" color="info" variant="tonal">
                  {{ formatNumber(item.comment_count || 0) }}
                </v-chip>
              </div>
            </template>

            <!-- 看好数列 -->
            <template #item.supporter_count="{ item }">
              <div class="text-center">
                <v-chip size="small" color="success" variant="tonal">
                  {{ formatNumber(item.supporter_count || 0) }}
                </v-chip>
              </div>
            </template>

            <!-- 状态列 -->
            <template #item.project_status="{ item }">
              <v-chip
                size="small"
                :color="getStatusColor(item.project_status)"
                variant="tonal"
              >
                {{ getStatusText(item.project_status) }}
              </v-chip>
            </template>

            <!-- 爬取时间列 -->
            <template #item.crawl_time="{ item }">
              <div class="text-caption">
                {{ formatDateTime(item.crawl_time) }}
              </div>
            </template>

            <!-- 无数据状态 -->
            <template #no-data>
              <div class="text-center pa-8">
                <v-icon size="64" class="mb-4 icon-medium-emphasis"
                  >mdi-database-off</v-icon
                >
                <div class="text-h6 text-medium-emphasis">暂无数据</div>
                <div class="text-subtitle-2 text-medium-emphasis mb-4">
                  请先运行爬虫任务获取数据
                </div>
                <v-btn
                  color="primary"
                  prepend-icon="mdi-spider"
                  @click="$router.push('/spider')"
                >
                  开始爬取
                </v-btn>
              </div>
            </template>
          </v-data-table-server>

          <!-- 自定义分页控制 -->
          <v-card-actions v-if="totalCount > 0" class="justify-center">
            <div class="d-flex align-center ga-4">
              <v-btn
                icon="mdi-chevron-left"
                variant="outlined"
                size="small"
                :disabled="currentPage <= 1"
                @click="goToPage(currentPage - 1)"
              />

              <div class="d-flex align-center ga-2">
                <span class="text-body-2">第</span>
                <v-text-field
                  v-model.number="currentPageInput"
                  type="number"
                  :min="1"
                  :max="totalPages"
                  variant="outlined"
                  density="compact"
                  style="width: 80px"
                  @keyup.enter="goToPage(currentPageInput)"
                  @blur="goToPage(currentPageInput)"
                />
                <span class="text-body-2">页，共 {{ totalPages }} 页</span>
              </div>

              <v-btn
                icon="mdi-chevron-right"
                variant="outlined"
                size="small"
                :disabled="currentPage >= totalPages"
                @click="goToPage(currentPage + 1)"
              />

              <v-divider vertical />

              <div class="text-caption text-medium-emphasis">
                共 {{ totalCount }} 条记录
              </div>
            </div>
          </v-card-actions>
        </v-card>
      </v-window-item>

      <!-- 备份管理选项卡 -->
      <v-window-item value="backup">
        <BackupManager />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import BackupManager from "@/components/BackupManager.vue";
import { isValidImageUrl } from "@/utils/imageUtils";

const router = useRouter();

// 响应式数据
const loading = ref(false);
const exporting = ref(false);
const projects = ref([]);
const itemsPerPage = ref(25);
const activeTab = ref("data");
const totalCount = ref(0);

// 分页相关的响应式数据
const currentPageInput = ref(1);
const currentPage = ref(1);

// 每页显示数量选项 - 限制最大100条防止浏览器卡死
const itemsPerPageOptions = [
  { value: 10, title: "10" },
  { value: 25, title: "25" },
  { value: 50, title: "50" },
  { value: 100, title: "100" },
];

const stats = reactive({
  total: 0,
  today: 0,
  week: 0,
  totalAmount: 0,
});

const filters = reactive({
  period: "all",
  category: "all",
  projectId: "",
  search: "",
});

// 选项数据
const periodOptions = [
  { value: "all", title: "全部时间" },
  { value: "today", title: "今天" },
  { value: "week", title: "本周" },
  { value: "month", title: "本月" },
];

const categoryOptions = [
  { value: "all", title: "全部分类" },
  { value: "games", title: "游戏" },
  { value: "publishing", title: "出版" },
  { value: "tablegames", title: "桌游" },
  { value: "toys", title: "潮玩模型" },
  { value: "cards", title: "卡牌" },
  { value: "technology", title: "科技" },
  { value: "film-video", title: "影视" },
  { value: "music", title: "音乐" },
  { value: "activities", title: "活动" },
  { value: "design", title: "设计" },
  { value: "curio", title: "文玩" },
  { value: "home", title: "家居" },
  { value: "food", title: "食品" },
  { value: "comics", title: "动漫" },
  { value: "charity", title: "爱心通道" },
  { value: "animals", title: "动物救助" },
  { value: "wishes", title: "个人愿望" },
  { value: "others", title: "其他" },
];

// 分类显示名称映射
const categoryDisplayNames = {
  games: "游戏",
  publishing: "出版",
  tablegames: "桌游",
  toys: "潮玩模型",
  cards: "卡牌",
  technology: "科技",
  "film-video": "影视",
  music: "音乐",
  activities: "活动",
  design: "设计",
  curio: "文玩",
  home: "家居",
  food: "食品",
  comics: "动漫",
  charity: "爱心通道",
  animals: "动物救助",
  wishes: "个人愿望",
  others: "其他",
  // 支持中文分类（向后兼容）
  桌游: "桌游",
  游戏: "游戏",
  出版: "出版",
  潮玩模型: "潮玩模型",
  卡牌: "卡牌",
  科技: "科技",
  影视: "影视",
  音乐: "音乐",
  活动: "活动",
  设计: "设计",
  文玩: "文玩",
  家居: "家居",
  食品: "食品",
  动漫: "动漫",
  爱心通道: "爱心通道",
  动物救助: "动物救助",
  个人愿望: "个人愿望",
};

// 表格列定义 - 响应式
const headers = [
  {
    title: "项目名称",
    key: "project_name",
    sortable: true,
    width: "250px",
    class: "text-left",
  },
  {
    title: "分类",
    key: "category",
    sortable: true,
    width: "100px",
    class: "d-none d-md-table-cell",
  },
  {
    title: "作者",
    key: "author_name",
    sortable: true,
    width: "120px",
    class: "d-none d-lg-table-cell",
  },
  {
    title: "筹款金额",
    key: "raised_amount",
    sortable: true,
    width: "130px",
    class: "text-right",
  },
  {
    title: "支持者",
    key: "backer_count",
    sortable: true,
    width: "80px",
    class: "d-none d-sm-table-cell text-center",
  },
  {
    title: "评论数",
    key: "comment_count",
    sortable: true,
    width: "80px",
    class: "d-none d-md-table-cell text-center",
  },
  {
    title: "看好数",
    key: "supporter_count",
    sortable: true,
    width: "80px",
    class: "d-none d-lg-table-cell text-center",
  },
  {
    title: "状态",
    key: "project_status",
    sortable: true,
    width: "100px",
    class: "d-none d-md-table-cell text-center",
  },
  {
    title: "爬取时间",
    key: "crawl_time",
    sortable: true,
    width: "150px",
    class: "d-none d-xl-table-cell text-center",
  },
];

// 分页相关计算属性 - 基于服务器端总数
const totalPages = computed(() => {
  return Math.ceil(totalCount.value / itemsPerPage.value);
});

// 监听分页变化，同步输入框
watch(
  () => currentPage.value,
  (newPage) => {
    currentPageInput.value = newPage;
  },
);

// 方法
const refreshData = async () => {
  try {
    loading.value = true;

    // 构建搜索条件
    const conditions = {};

    // 添加分类筛选
    if (filters.category !== "all") {
      conditions.category = filters.category;
    }

    // 添加时间筛选
    if (filters.period !== "all") {
      conditions.time_period = filters.period;
    }

    // 添加项目ID搜索
    if (filters.projectId && filters.projectId.trim()) {
      conditions.project_id = filters.projectId.trim();
    }

    // 添加项目名称搜索
    if (filters.search && filters.search.trim()) {
      conditions.project_name = filters.search.trim();
    }

    // 计算分页参数
    const offset = (currentPage.value - 1) * itemsPerPage.value;

    // 使用搜索API获取分页数据
    const projectsResponse = await axios.post("/api/database/projects/search", {
      conditions,
      limit: itemsPerPage.value,
      offset,
    });

    if (projectsResponse.data.success) {
      projects.value = projectsResponse.data.projects || [];
      totalCount.value = projectsResponse.data.total_count || 0;
      console.log(
        `📊 加载项目数据: ${projects.value.length} 条，总计: ${totalCount.value}，分类筛选: ${filters.category}`,
      );
    }

    // 加载统计数据
    const statsResponse = await axios.get("/api/database/stats");
    if (statsResponse.data.success) {
      const data = statsResponse.data.stats;
      stats.total = data.total_projects || 0;
      stats.today = data.today_projects || 0;
      stats.week = data.week_projects || 0;
      stats.totalAmount = data.total_amount || 0;
    }
  } catch (error) {
    console.error("加载数据失败:", error);
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => {
  // 重新加载数据以应用筛选条件
  refreshData();
};

const debounceSearch = (() => {
  let timeout;
  return () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      applyFilters();
    }, 300);
  };
})();

const exportData = async () => {
  try {
    exporting.value = true;
    const url = `/api/database/export?period=${filters.period}&category=${filters.category}`;
    const link = document.createElement("a");
    link.href = url;
    link.download = `modian_data_${new Date().toISOString().split("T")[0]}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error("导出失败:", error);
  } finally {
    exporting.value = false;
  }
};

const formatNumber = (num) => {
  if (!num) return "0";
  return new Intl.NumberFormat("zh-CN").format(num);
};

const formatCurrency = (num) => {
  if (!num) return "¥0";
  return "¥" + new Intl.NumberFormat("zh-CN").format(num);
};

const getCategoryColor = (category) => {
  const colors = {
    games: "purple",
    publishing: "blue",
    tablegames: "green",
    toys: "orange",
    cards: "red",
    technology: "cyan",
    桌游: "green",
    游戏: "purple",
    出版: "blue",
    潮玩模型: "orange",
    卡牌: "red",
    科技: "cyan",
  };
  return colors[category] || "grey";
};

const getCategoryDisplayName = (category) => {
  return categoryDisplayNames[category] || category || "未知分类";
};

const getStatusColor = (status) => {
  const colors = {
    active: "success",
    completed: "primary",
    failed: "error",
    cancelled: "warning",
    进行中: "success",
    已完成: "primary",
    失败: "error",
    已取消: "warning",
  };
  return colors[status] || "grey";
};

const getStatusText = (status) => {
  const texts = {
    active: "进行中",
    completed: "已完成",
    failed: "失败",
    cancelled: "已取消",
  };
  return texts[status] || status || "未知";
};

const getCompletionColor = (rate) => {
  if (!rate) return "text-medium-emphasis";
  const percentage = parseFloat(rate);
  if (percentage >= 100) return "text-success";
  if (percentage >= 50) return "text-warning";
  return "text-error";
};

const formatPercentage = (rate) => {
  if (!rate) return "0%";
  return `${parseFloat(rate).toFixed(1)}%`;
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return "";
  try {
    const date = new Date(dateStr);
    // 确保显示本地时间（GMT+8北京时间）
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Shanghai", // 明确指定北京时区
    });
  } catch {
    return dateStr;
  }
};

const goToProjectDetail = (projectId) => {
  if (projectId) {
    router.push(`/projects/${projectId}`);
  }
};

// 表格选项更新处理（服务器端分页）
const onTableOptionsUpdate = (options) => {
  console.log("📊 表格选项更新:", options);

  // 限制每页最大显示数量为100，防止浏览器卡死
  const maxItemsPerPage = 100;
  const safeItemsPerPage = Math.min(options.itemsPerPage, maxItemsPerPage);

  if (options.itemsPerPage > maxItemsPerPage) {
    console.warn(`⚠️ 每页显示数量限制为${maxItemsPerPage}条，防止浏览器卡死`);
  }

  // 更新分页状态
  currentPage.value = options.page;
  itemsPerPage.value = safeItemsPerPage;
  currentPageInput.value = options.page;

  // 重新加载数据
  refreshData();
};

// 分页跳转方法
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return;

  currentPage.value = page;
  currentPageInput.value = page;

  // 重新加载数据
  refreshData();
};

// 监听筛选条件变化
watch([() => filters.category, () => filters.period], () => {
  console.log(
    `🔄 筛选条件变化: 分类=${filters.category}, 时间=${filters.period}`,
  );
  applyFilters();
});

// 生命周期
onMounted(() => {
  refreshData();
});
</script>

<style scoped>
/* DataManagement MD3 标准样式 */
/* 样式现在完全由Vuetify defaults配置管理 - 遵循官方文档最佳实践 */
.stats-card {
  transition: background-color var(--md3-motion-duration-short)
    var(--md3-motion-easing-standard);
}

.stats-card .v-avatar {
  transition: none;
}

.v-avatar .v-img {
  border-radius: 50%;
}

/* 按钮文本对齐现在通过内联样式处理，避免覆盖VBtn默认样式 */

/* 响应式优化现在通过Vuetify defaults配置管理 */
</style>
