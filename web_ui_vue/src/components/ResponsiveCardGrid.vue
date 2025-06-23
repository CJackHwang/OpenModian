<template>
  <v-container class="responsive-card-grid" fluid>
    <!-- 网格工具栏 -->
    <v-sheet v-if="showToolbar" class="grid-toolbar mb-4" color="transparent">
      <v-card>
        <v-card-text
          class="d-flex align-center justify-space-between flex-wrap ga-4"
        >
          <!-- 视图切换 -->
          <v-btn-toggle
            v-model="viewMode"
            variant="outlined"
            :size="buttonSize"
            mandatory
          >
            <v-btn value="grid" icon="mdi-view-grid" />
            <v-btn value="list" icon="mdi-view-list" />
            <v-btn value="compact" icon="mdi-view-comfy" />
          </v-btn-toggle>

          <!-- 排序和筛选 -->
          <div class="d-flex align-center ga-2">
            <v-select
              v-if="sortOptions.length > 0"
              v-model="selectedSort"
              :items="sortOptions"
              label="排序"
              variant="outlined"
              density="compact"
              hide-details
              :style="{ minWidth: '120px' }"
            />

            <v-select
              v-if="filterOptions.length > 0"
              v-model="selectedFilter"
              :items="filterOptions"
              label="筛选"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              :style="{ minWidth: '120px' }"
            />
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- 网格容器 -->
    <v-container fluid class="pa-0">
      <v-row :dense="isDense" :class="gridClass">
        <v-col
          v-for="(item, index) in paginatedItems"
          :key="getItemKey(item, index)"
          :cols="gridConfig.cols"
          :sm="gridConfig.sm"
          :md="gridConfig.md"
          :lg="gridConfig.lg"
          :xl="gridConfig.xl"
          :xxl="gridConfig.xxl"
        >
          <!-- 卡片内容插槽 -->
          <slot
            name="card"
            :item="item"
            :index="index"
            :view-mode="viewMode"
            :is-mobile="isMobile"
          >
            <!-- 默认卡片 -->
            <v-card
              :class="cardClass"
              :height="cardHeight"
              @click="handleCardClick(item, index)"
            >
              <v-card-text class="d-flex align-center">
                <v-avatar
                  v-if="item.avatar || item.icon"
                  :color="item.color || 'primary'"
                  class="me-3"
                  :size="avatarSize"
                >
                  <v-img v-if="item.avatar" :src="item.avatar" />
                  <v-icon v-else-if="item.icon" :icon="item.icon" />
                </v-avatar>

                <div class="flex-grow-1">
                  <div class="text-subtitle-1 font-weight-medium">
                    {{ item.title || item.name }}
                  </div>
                  <div
                    v-if="item.subtitle"
                    class="text-body-2 text-medium-emphasis"
                  >
                    {{ item.subtitle }}
                  </div>
                </div>

                <v-chip
                  v-if="item.status"
                  :color="getStatusColor(item.status)"
                  size="small"
                  variant="tonal"
                >
                  {{ item.status }}
                </v-chip>
              </v-card-text>
            </v-card>
          </slot>
        </v-col>
      </v-row>
    </v-container>

    <!-- 分页 -->
    <div
      v-if="showPagination && pageCount > 1"
      class="d-flex justify-center mt-6"
    >
      <v-pagination
        v-model="currentPage"
        :length="pageCount"
        :total-visible="paginationVisible"
        :size="buttonSize"
        @update:model-value="handlePageChange"
      />
    </div>

    <!-- 加载更多 -->
    <div v-if="showLoadMore && hasMore" class="d-flex justify-center mt-4">
      <v-btn
        @click="handleLoadMore"
        :loading="loadingMore"
        variant="outlined"
        :size="buttonSize"
        prepend-icon="mdi-plus"
      >
        加载更多
      </v-btn>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredItems.length === 0 && !loading" class="empty-state">
      <v-icon :icon="emptyIcon" size="64" class="empty-icon" />
      <div class="empty-title">{{ emptyTitle }}</div>
      <div class="empty-subtitle">{{ emptySubtitle }}</div>
    </div>

    <!-- 加载状态 -->
    <v-sheet v-if="loading" class="loading-state" color="transparent">
      <v-row :dense="isDense">
        <v-col
          v-for="n in skeletonCount"
          :key="n"
          :cols="gridConfig.cols"
          :sm="gridConfig.sm"
          :md="gridConfig.md"
          :lg="gridConfig.lg"
          :xl="gridConfig.xl"
          :xxl="gridConfig.xxl"
        >
          <v-skeleton-loader type="card" :height="cardHeight" />
        </v-col>
      </v-row>
    </v-sheet>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useResponsive } from "@/composables/useResponsive";

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  itemsPerPage: {
    type: Number,
    default: 12,
  },
  showToolbar: {
    type: Boolean,
    default: true,
  },
  showPagination: {
    type: Boolean,
    default: true,
  },
  showLoadMore: {
    type: Boolean,
    default: false,
  },
  sortOptions: {
    type: Array,
    default: () => [],
  },
  filterOptions: {
    type: Array,
    default: () => [],
  },
  emptyIcon: {
    type: String,
    default: "mdi-grid-off",
  },
  emptyTitle: {
    type: String,
    default: "暂无内容",
  },
  emptySubtitle: {
    type: String,
    default: "当前没有可显示的内容",
  },
  itemKey: {
    type: String,
    default: "id",
  },
});

// Emits
const emit = defineEmits([
  "card-click",
  "load-more",
  "sort-change",
  "filter-change",
]);

// 响应式组合函数
const { getResponsiveSize, display } = useResponsive();

// 响应式数据
const viewMode = ref("grid");
const currentPage = ref(1);
const selectedSort = ref(null);
const selectedFilter = ref(null);
const loadingMore = ref(false);

// 响应式配置
const isMobile = computed(() => display.mobile.value);
const buttonSize = getResponsiveSize();

// 网格配置
const gridConfig = computed(() => {
  const baseConfig = {
    grid: { xs: 1, sm: 2, md: 3, lg: 4, xl: 5, xxl: 6 },
    list: { xs: 1, sm: 1, md: 1, lg: 1, xl: 1, xxl: 1 },
    compact: { xs: 1, sm: 2, md: 4, lg: 6, xl: 8, xxl: 10 },
  };

  const config = baseConfig[viewMode.value] || baseConfig.grid;
  return {
    cols: 12,
    sm: Math.floor(12 / config.sm),
    md: Math.floor(12 / config.md),
    lg: Math.floor(12 / config.lg),
    xl: Math.floor(12 / config.xl),
    xxl: Math.floor(12 / config.xxl),
  };
});

// 样式配置
const isDense = computed(() => viewMode.value === "compact" || isMobile.value);
const cardHeight = computed(() => {
  switch (viewMode.value) {
    case "list":
      return "auto";
    case "compact":
      return "120px";
    default:
      return "160px";
  }
});

const avatarSize = computed(() => {
  switch (viewMode.value) {
    case "compact":
      return 32;
    case "list":
      return 40;
    default:
      return 48;
  }
});

const gridClass = computed(() => ({
  "grid-view": viewMode.value === "grid",
  "list-view": viewMode.value === "list",
  "compact-view": viewMode.value === "compact",
}));

const cardClass = computed(() => ({
  "cursor-pointer": true,
  "hover-card": !isMobile.value,
}));

const paginationVisible = computed(() => (isMobile.value ? 5 : 7));
const skeletonCount = computed(() => props.itemsPerPage);

// 数据处理
const filteredItems = computed(() => {
  let items = [...props.items];

  // 筛选
  if (selectedFilter.value) {
    items = items.filter((item) => {
      const filter = props.filterOptions.find(
        (f) => f.value === selectedFilter.value,
      );
      return filter ? filter.filter(item) : true;
    });
  }

  // 排序
  if (selectedSort.value) {
    const sort = props.sortOptions.find((s) => s.value === selectedSort.value);
    if (sort && sort.sort) {
      items.sort(sort.sort);
    }
  }

  return items;
});

const paginatedItems = computed(() => {
  if (props.showLoadMore) {
    return filteredItems.value.slice(0, currentPage.value * props.itemsPerPage);
  }

  const start = (currentPage.value - 1) * props.itemsPerPage;
  const end = start + props.itemsPerPage;
  return filteredItems.value.slice(start, end);
});

const pageCount = computed(() => {
  return Math.ceil(filteredItems.value.length / props.itemsPerPage);
});

const hasMore = computed(() => {
  return paginatedItems.value.length < filteredItems.value.length;
});

// 方法
const getItemKey = (item, index) => {
  return item[props.itemKey] || index;
};

const getStatusColor = (status) => {
  const colorMap = {
    active: "success",
    inactive: "error",
    pending: "warning",
    completed: "primary",
  };
  return colorMap[status] || "secondary";
};

const handleCardClick = (item, index) => {
  emit("card-click", { item, index });
};

const handlePageChange = (page) => {
  currentPage.value = page;
};

const handleLoadMore = async () => {
  loadingMore.value = true;
  try {
    currentPage.value++;
    await emit("load-more");
  } finally {
    loadingMore.value = false;
  }
};

// 监听器
watch(selectedSort, (newSort) => {
  emit("sort-change", newSort);
});

watch(selectedFilter, (newFilter) => {
  emit("filter-change", newFilter);
});

watch(viewMode, () => {
  currentPage.value = 1;
});
</script>

<style scoped>
.responsive-card-grid {
  width: 100%;
}

.grid-toolbar {
  position: sticky;
  top: 0;
  z-index: 1;
}

.hover-card {
  transition: transform var(--md3-motion-duration-short)
    var(--md3-motion-easing-standard);
}

.hover-card:hover {
  transform: translateY(-2px);
}

.empty-state {
  text-align: center;
  padding: 64px 24px;
}

.empty-icon {
  opacity: 0.6;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-subtitle {
  font-size: 0.875rem;
  opacity: 0.7;
  max-width: 400px;
  margin: 0 auto;
}

.loading-state {
  width: 100%;
}

/* 视图模式特定样式 */
.list-view .v-card {
  border-radius: var(--md3-radius-lg);
}

.compact-view .v-card {
  border-radius: var(--md3-radius-md);
}

.grid-view .v-card {
  border-radius: var(--md3-radius-xl);
}
</style>
