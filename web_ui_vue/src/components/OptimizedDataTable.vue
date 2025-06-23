<template>
  <div class="optimized-data-table">
    <!-- 表格工具栏 -->
    <v-card class="mb-4" v-if="showToolbar">
      <v-card-text
        class="d-flex align-center justify-space-between flex-wrap ga-4"
      >
        <!-- 搜索框 -->
        <v-text-field
          v-model="searchQuery"
          :placeholder="searchPlaceholder"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          hide-details
          clearable
          :style="{ maxWidth: searchFieldWidth }"
          @input="handleSearch"
        />

        <!-- 操作按钮 -->
        <div class="d-flex align-center ga-2">
          <v-btn
            v-if="showRefresh"
            @click="handleRefresh"
            :loading="refreshing"
            variant="outlined"
            :size="buttonSize"
            icon="mdi-refresh"
          >
            <v-tooltip activator="parent" location="bottom">刷新数据</v-tooltip>
          </v-btn>

          <v-btn
            v-if="showExport"
            @click="handleExport"
            variant="outlined"
            :size="buttonSize"
            prepend-icon="mdi-download"
          >
            导出
          </v-btn>

          <slot name="toolbar-actions" />
        </div>
      </v-card-text>
    </v-card>

    <!-- 数据表格 -->
    <v-data-table
      v-model:items-per-page="itemsPerPage"
      v-model:page="currentPage"
      v-model:sort-by="sortBy"
      :headers="computedHeaders"
      :items="filteredItems"
      :loading="loading"
      :items-per-page-options="itemsPerPageOptions"
      :density="tableDensity"
      :hover="hover"
      :show-current-page="showCurrentPage"
      :mobile-breakpoint="mobileBreakpoint"
      class="app-table"
      @update:options="handleOptionsUpdate"
    >
      <!-- 自定义列内容 -->
      <template v-for="(_, slot) in $slots" v-slot:[slot]="scope">
        <slot :name="slot" v-bind="scope" />
      </template>

      <!-- 加载状态 -->
      <template #loading>
        <v-skeleton-loader
          v-for="n in skeletonRows"
          :key="n"
          type="table-row"
          class="mx-auto"
        />
      </template>

      <!-- 空状态 -->
      <template #no-data>
        <div class="empty-state py-8">
          <v-icon :icon="emptyIcon" size="64" class="empty-icon" />
          <div class="empty-title">{{ emptyTitle }}</div>
          <div class="empty-subtitle">{{ emptySubtitle }}</div>
          <v-btn
            v-if="showEmptyAction"
            @click="handleEmptyAction"
            color="primary"
            class="mt-4"
            :size="buttonSize"
          >
            {{ emptyActionText }}
          </v-btn>
        </div>
      </template>

      <!-- 底部分页 -->
      <template #bottom>
        <div
          class="d-flex align-center justify-space-between pa-4 flex-wrap ga-4"
        >
          <div class="text-body-2 text-medium-emphasis">
            共 {{ totalItems }} 条记录
          </div>

          <v-pagination
            v-model="currentPage"
            :length="pageCount"
            :total-visible="paginationVisible"
            :size="buttonSize"
            density="comfortable"
            @update:model-value="handlePageChange"
          />
        </div>
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { useResponsive } from "@/composables/useResponsive";
import { usePerformance } from "@/composables/usePerformance";

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  headers: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  searchPlaceholder: {
    type: String,
    default: "搜索...",
  },
  showToolbar: {
    type: Boolean,
    default: true,
  },
  showRefresh: {
    type: Boolean,
    default: true,
  },
  showExport: {
    type: Boolean,
    default: true,
  },
  hover: {
    type: Boolean,
    default: true,
  },
  emptyIcon: {
    type: String,
    default: "mdi-database-off",
  },
  emptyTitle: {
    type: String,
    default: "暂无数据",
  },
  emptySubtitle: {
    type: String,
    default: "当前没有可显示的数据",
  },
  showEmptyAction: {
    type: Boolean,
    default: false,
  },
  emptyActionText: {
    type: String,
    default: "刷新",
  },
});

// Emits
const emit = defineEmits([
  "refresh",
  "export",
  "empty-action",
  "options-update",
]);

// 响应式组合函数
const { getResponsiveSize, getResponsiveTableConfig } = useResponsive();
const { debounce } = usePerformance();

// 响应式数据
const searchQuery = ref("");
const currentPage = ref(1);
const sortBy = ref([]);
const refreshing = ref(false);

// 响应式配置
const tableConfig = getResponsiveTableConfig();
const buttonSize = getResponsiveSize();

// 计算属性
const itemsPerPage = computed(() => tableConfig.value.itemsPerPage);
const tableDensity = computed(() => tableConfig.value.density);
const showCurrentPage = computed(() => !tableConfig.value.hideHeaders);
const mobileBreakpoint = computed(() => tableConfig.value.mobileBreakpoint);

const searchFieldWidth = computed(() => {
  return tableConfig.value.density === "compact" ? "200px" : "300px";
});

const skeletonRows = computed(() => {
  return itemsPerPage.value || 5;
});

const paginationVisible = computed(() => {
  return tableDensity.value === "compact" ? 5 : 7;
});

const itemsPerPageOptions = computed(() => {
  const base = [5, 10, 25, 50];
  if (tableDensity.value === "compact") {
    return base.slice(0, 3);
  }
  return [...base, 100];
});

// 响应式表头
const computedHeaders = computed(() => {
  if (tableConfig.value.hideHeaders) {
    // 移动端简化表头
    return props.headers.filter((header) => header.mobile !== false);
  }
  return props.headers;
});

// 过滤后的数据
const filteredItems = computed(() => {
  if (!searchQuery.value || !props.searchable) {
    return props.items;
  }

  const query = searchQuery.value.toLowerCase();
  return props.items.filter((item) => {
    return Object.values(item).some((value) => {
      return String(value).toLowerCase().includes(query);
    });
  });
});

const totalItems = computed(() => filteredItems.value.length);
const pageCount = computed(() =>
  Math.ceil(totalItems.value / itemsPerPage.value),
);

// 方法
const handleSearch = debounce((value) => {
  currentPage.value = 1;
}, 300);

const handleRefresh = async () => {
  refreshing.value = true;
  try {
    await emit("refresh");
  } finally {
    refreshing.value = false;
  }
};

const handleExport = () => {
  emit("export", filteredItems.value);
};

const handleEmptyAction = () => {
  emit("empty-action");
};

const handlePageChange = (page) => {
  currentPage.value = page;
};

const handleOptionsUpdate = (options) => {
  emit("options-update", options);
};

// 监听器
watch(
  () => props.items,
  () => {
    // 当数据变化时重置到第一页
    if (currentPage.value > pageCount.value) {
      currentPage.value = 1;
    }
  },
);

// 生命周期
onMounted(() => {
  // 初始化时可以执行一些优化操作
});
</script>

<style scoped>
.optimized-data-table {
  width: 100%;
}

.app-table {
  border-radius: var(--md3-radius-xl);
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  opacity: 0.6;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-subtitle {
  font-size: 0.875rem;
  opacity: 0.7;
  max-width: 400px;
  margin: 0 auto;
}
</style>
