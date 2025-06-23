<template>
  <v-card elevation="2" class="mb-6">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-heart" class="me-3" color="primary" />
      项目关注列表
      <v-spacer />
      <v-sheet class="d-flex align-center ga-2" color="transparent">
        <v-chip variant="outlined" color="primary">
          {{ totalCount }} 个项目
        </v-chip>
        <v-chip
          v-if="totalCount > pageSize"
          variant="outlined"
          color="secondary"
          size="small"
        >
          显示 {{ displayRange }}
        </v-chip>
      </v-sheet>
    </v-card-title>

    <v-card-text>
      <!-- 批量导入区域 -->
      <v-expansion-panels v-model="expandedPanels" class="mb-4">
        <v-expansion-panel value="import">
          <v-expansion-panel-title>
            <v-icon icon="mdi-import" class="me-2" />
            批量导入项目ID
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-textarea
              v-model="importText"
              label="项目ID列表（每行一个）"
              placeholder="请输入项目ID，每行一个&#10;例如：&#10;123456&#10;789012&#10;345678"
              rows="6"
              variant="outlined"
              class="mb-3"
            />
            <v-sheet class="d-flex ga-2" color="transparent">
              <v-btn
                color="primary"
                prepend-icon="mdi-import"
                @click="batchImport"
                :loading="importing"
                :disabled="!importText.trim()"
                class="app-button"
              >
                导入项目
              </v-btn>
              <v-btn
                variant="outlined"
                prepend-icon="mdi-content-paste"
                @click="pasteFromClipboard"
                class="app-button"
              >
                从剪贴板粘贴
              </v-btn>
            </v-sheet>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- 关注列表 -->
      <v-sheet v-if="loading" class="text-center py-8" color="transparent">
        <v-progress-circular indeterminate color="primary" />
        <v-card-text class="mt-3 text-medium-emphasis">加载关注列表...</v-card-text>
      </v-sheet>

      <v-sheet v-else-if="!totalCount" class="text-center py-8" color="transparent">
        <v-icon
          icon="mdi-heart-outline"
          size="64"
          color="medium-emphasis"
          class="mb-3"
        />
        <v-card-text class="text-h6 text-medium-emphasis">暂无关注项目</v-card-text>
        <v-card-text class="text-body-2 text-medium-emphasis">
          通过项目详情页面收藏或批量导入项目ID来添加关注项目
        </v-card-text>
      </v-sheet>

      <v-sheet v-else color="transparent">
        <!-- 操作按钮和分页控制 -->
        <v-sheet class="d-flex justify-between align-center mb-3" color="transparent">
          <v-sheet class="d-flex align-center ga-2" color="transparent">
            <!-- 分页控制 -->
            <v-btn
              icon="mdi-chevron-left"
              size="small"
              variant="outlined"
              :disabled="currentPage <= 1"
              @click="previousPage"
              class="app-button"
            />
            <v-chip variant="outlined" size="small">
              {{ currentPage }} / {{ totalPages }}
            </v-chip>
            <v-btn
              icon="mdi-chevron-right"
              size="small"
              variant="outlined"
              :disabled="currentPage >= totalPages"
              @click="nextPage"
              class="app-button"
            />

            <!-- 页面大小选择 -->
            <v-select
              v-model="pageSize"
              :items="pageSizeOptions"
              density="compact"
              variant="outlined"
              style="width: 80px"
              hide-details
              @update:model-value="onPageSizeChange"
            />
          </v-sheet>

          <v-sheet class="d-flex ga-2" color="transparent">
            <!-- 回到顶部按钮 -->
            <v-btn
              v-if="showBackToTop"
              icon="mdi-arrow-up"
              size="small"
              color="primary"
              variant="outlined"
              @click="scrollToTop"
              class="app-button"
            />

            <v-btn
              color="error"
              variant="outlined"
              prepend-icon="mdi-delete-sweep"
              @click="confirmClearAll"
              :disabled="!totalCount"
              class="app-button"
            >
              清空列表
            </v-btn>
          </v-sheet>
        </v-sheet>

        <!-- 项目列表容器 -->
        <v-sheet
          ref="listContainer"
          class="watch-list-container"
          @scroll="onScroll"
          color="surface"
        >
          <v-list class="pa-0">
            <v-list-item
              v-for="project in displayedProjects"
              :key="project.id"
              class="mb-2 app-list-item"
              :style="{ border: '1px solid rgb(var(--v-theme-outline))' }"
            >
              <template #prepend>
                <v-avatar color="primary" class="me-3">
                  <v-icon icon="mdi-folder-heart" />
                </v-avatar>
              </template>

              <v-list-item-title class="font-weight-medium">
                {{ project.project_name || "未知项目" }}
              </v-list-item-title>

              <v-list-item-subtitle class="d-flex flex-column ga-1">
                <v-chip size="x-small" variant="text" color="primary">ID: {{ project.project_id }}</v-chip>
                <v-chip v-if="project.category" size="x-small" variant="tonal" color="primary">{{
                  project.category
                }}</v-chip>
                <v-chip v-if="project.author_name" size="x-small" variant="text" color="medium-emphasis"
                  >作者: {{ project.author_name }}</v-chip
                >
                <v-chip size="x-small" variant="text" color="medium-emphasis"
                  >添加时间: {{ formatTime(project.added_time) }}</v-chip
                >
              </v-list-item-subtitle>

              <template #append>
                <v-sheet class="d-flex ga-1" color="transparent">
                  <v-btn
                    icon
                    size="small"
                    color="primary"
                    :href="project.project_url"
                    target="_blank"
                    class="app-button"
                  >
                    <v-icon icon="mdi-open-in-new" />
                  </v-btn>
                  <v-btn
                    icon
                    size="small"
                    color="error"
                    @click="removeProject(project.project_id)"
                    class="app-button"
                  >
                    <v-icon icon="mdi-delete" />
                  </v-btn>
                </v-sheet>
              </template>
            </v-list-item>
          </v-list>

          <!-- 加载更多指示器 -->
          <v-sheet v-if="loadingMore" class="text-center py-4" color="transparent">
            <v-progress-circular indeterminate color="primary" size="24" />
            <v-card-text class="mt-2 text-caption text-medium-emphasis">加载更多...</v-card-text>
          </v-sheet>
        </v-sheet>
      </v-sheet>
    </v-card-text>

    <!-- 确认清空对话框 -->
    <v-dialog v-model="clearDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon icon="mdi-alert" color="warning" class="me-2" />
          确认清空
        </v-card-title>
        <v-card-text> 确定要清空所有关注项目吗？此操作不可撤销。 </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="clearDialog = false">取消</v-btn>
          <v-btn color="error" @click="clearAllProjects" :loading="clearing"
            >确认清空</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useSnackbar } from "@/composables/useSnackbar";
import axios from "axios";

// 定义事件
const emit = defineEmits(["update:count"]);

// 响应式数据
const loading = ref(false);
const importing = ref(false);
const clearing = ref(false);
const loadingMore = ref(false);
const watchedProjects = ref([]);
const importText = ref("");
const expandedPanels = ref([]);
const clearDialog = ref(false);

// 分页相关
const currentPage = ref(1);
const pageSize = ref(20);
const totalCount = ref(0);
const pageSizeOptions = [10, 20, 50, 100];
const showBackToTop = ref(false);
const listContainer = ref(null);

// 使用snackbar
const { showSnackbar } = useSnackbar();

// 计算属性
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));

const displayedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return watchedProjects.value.slice(start, end);
});

const displayRange = computed(() => {
  if (totalCount.value === 0) return "0";
  const start = (currentPage.value - 1) * pageSize.value + 1;
  const end = Math.min(currentPage.value * pageSize.value, totalCount.value);
  return `${start}-${end}`;
});

// 监听总数变化，通知父组件
watch(
  totalCount,
  (newCount) => {
    emit("update:count", newCount);
  },
  { immediate: true },
);

// 组件挂载时加载数据
onMounted(() => {
  loadWatchedProjects();
});

// 加载关注项目列表
async function loadWatchedProjects() {
  try {
    loading.value = true;
    const response = await axios.get("/api/watch/list");

    if (response.data.success) {
      watchedProjects.value = response.data.projects;
      totalCount.value = response.data.count;

      // 如果当前页超出范围，重置到第一页
      if (currentPage.value > totalPages.value && totalPages.value > 0) {
        currentPage.value = 1;
      }
    } else {
      showSnackbar(response.data.message || "加载关注列表失败", "error");
    }
  } catch (error) {
    console.error("加载关注列表失败:", error);
    showSnackbar("网络错误，请稍后重试", "error");
  } finally {
    loading.value = false;
  }
}

// 批量导入项目
async function batchImport() {
  if (!importText.value.trim()) {
    showSnackbar("请输入项目ID", "warning");
    return;
  }

  try {
    importing.value = true;

    // 解析项目ID列表
    const projectIds = importText.value
      .split("\n")
      .map((id) => id.trim())
      .filter((id) => id && /^\d+$/.test(id));

    if (!projectIds.length) {
      showSnackbar("未找到有效的项目ID", "warning");
      return;
    }

    const response = await axios.post("/api/watch/batch_import", {
      project_ids: projectIds,
    });

    if (response.data.success) {
      showSnackbar(response.data.message, "success");
      importText.value = "";
      expandedPanels.value = [];
      await loadWatchedProjects();

      // 如果有无效ID，显示详细信息
      if (response.data.invalid_ids && response.data.invalid_ids.length > 0) {
        console.warn("无效的项目ID:", response.data.invalid_ids);
      }
    } else {
      showSnackbar(response.data.message || "导入失败", "error");
    }
  } catch (error) {
    console.error("批量导入失败:", error);
    showSnackbar("导入失败，请稍后重试", "error");
  } finally {
    importing.value = false;
  }
}

// 从剪贴板粘贴
async function pasteFromClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) {
      importText.value = text;
      showSnackbar("已从剪贴板粘贴内容", "success");
    }
  } catch (error) {
    console.error("读取剪贴板失败:", error);
    showSnackbar("无法读取剪贴板内容", "warning");
  }
}

// 移除单个项目
async function removeProject(projectId) {
  try {
    const response = await axios.post("/api/watch/remove", {
      project_id: projectId,
    });

    if (response.data.success) {
      showSnackbar("项目已从关注列表移除", "success");
      await loadWatchedProjects();
    } else {
      showSnackbar(response.data.message || "移除失败", "error");
    }
  } catch (error) {
    console.error("移除项目失败:", error);
    showSnackbar("移除失败，请稍后重试", "error");
  }
}

// 确认清空所有项目
function confirmClearAll() {
  clearDialog.value = true;
}

// 清空所有项目
async function clearAllProjects() {
  try {
    clearing.value = true;
    const response = await axios.post("/api/watch/clear");

    if (response.data.success) {
      showSnackbar("关注列表已清空", "success");
      clearDialog.value = false;
      await loadWatchedProjects();
    } else {
      showSnackbar(response.data.message || "清空失败", "error");
    }
  } catch (error) {
    console.error("清空关注列表失败:", error);
    showSnackbar("清空失败，请稍后重试", "error");
  } finally {
    clearing.value = false;
  }
}

// 分页相关方法
function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
    scrollToTop();
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    scrollToTop();
  }
}

function onPageSizeChange() {
  currentPage.value = 1;
  scrollToTop();
}

// 滚动相关方法
function onScroll(event) {
  const { scrollTop } = event.target;
  showBackToTop.value = scrollTop > 200;
}

function scrollToTop() {
  if (listContainer.value) {
    listContainer.value.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }
}

// 格式化时间
function formatTime(timeStr) {
  if (!timeStr) return "-";
  try {
    return new Date(timeStr).toLocaleString("zh-CN");
  } catch {
    return timeStr;
  }
}

// 暴露方法给父组件
defineExpose({
  loadWatchedProjects,
  getWatchedProjectIds: () => watchedProjects.value.map((p) => p.project_id),
  getTotalCount: () => totalCount.value,
});
</script>

<style scoped>
.app-list-item {
  border-radius: 12px;
  background: rgb(var(--v-theme-surface));
}

.app-list-item:hover {
  background: rgb(var(--v-theme-surface-variant));
}

.watch-list-container {
  max-height: 450px;
  overflow-y: auto;
  border-radius: 12px;
  border: 1px solid rgb(var(--v-theme-outline));
  background: rgb(var(--v-theme-surface));
}

.watch-list-container::-webkit-scrollbar {
  width: 8px;
}

.watch-list-container::-webkit-scrollbar-track {
  background: rgb(var(--v-theme-surface-variant));
  border-radius: 4px;
}

.watch-list-container::-webkit-scrollbar-thumb {
  background: rgb(var(--v-theme-outline));
  border-radius: 4px;
}

.watch-list-container::-webkit-scrollbar-thumb:hover {
  background: rgb(var(--v-theme-primary));
}

/* 移动端优化 */
@media (max-width: 768px) {
  .watch-list-container {
    max-height: 350px;
  }

  .d-flex.justify-between {
    flex-direction: column;
    gap: 12px;
  }

  .d-flex.justify-between > div {
    justify-content: center;
  }
}
</style>
