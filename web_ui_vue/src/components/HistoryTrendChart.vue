<template>
  <v-card class="app-card">
    <v-card-title class="d-flex align-center p-lg">
      <v-avatar color="primary" size="32" class="me-3">
        <v-icon icon="mdi-chart-line" color="on-primary" size="18" />
      </v-avatar>
      <div class="flex-grow-1">
        <div class="text-h6 font-weight-bold">历史数据趋势</div>
        <div class="text-body-2 text-medium-emphasis">项目关键指标变化趋势</div>
      </div>
      <v-chip color="info" size="small" variant="outlined" class="app-chip">
        {{ historyData.length }} 条记录
      </v-chip>
    </v-card-title>

    <v-card-text class="p-lg pt-0">
      <!-- 图表选项控制 -->
      <v-row class="mb-4">
        <v-col cols="12" md="6">
          <v-select
            v-model="selectedMetrics"
            :items="availableMetrics"
            item-title="label"
            item-value="key"
            label="选择显示指标"
            multiple
            chips
            variant="outlined"
            density="compact"
          >
            <template v-slot:chip="{ props, item }">
              <v-chip
                v-bind="props"
                :color="getMetricColor(item.raw.key)"
                size="small"
                variant="flat"
              >
                {{ item.raw.label }}
              </v-chip>
            </template>
          </v-select>
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="timeRange"
            :items="timeRangeOptions"
            item-title="label"
            item-value="value"
            label="时间范围"
            variant="outlined"
            density="compact"
          />
        </v-col>
      </v-row>

      <!-- 图表容器 -->
      <div class="chart-container" :style="{ height: chartHeight + 'px' }">
        <canvas ref="chartCanvas"></canvas>
      </div>

      <!-- 无数据提示 -->
      <div v-if="!historyData.length" class="text-center py-8">
        <v-icon size="64" color="on-surface-variant"
          >mdi-chart-line-variant</v-icon
        >
        <div class="text-h6 mt-2 text-on-surface">暂无历史数据</div>
        <div class="text-caption text-on-surface-variant">
          需要至少2条历史记录才能显示趋势图
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from "vue";
import { useDisplay } from "vuetify";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { formatDateTime } from "@/utils/timeUtils";

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler,
);

// Props
const props = defineProps({
  historyData: {
    type: Array,
    default: () => [],
  },
  height: {
    type: Number,
    default: 400,
  },
});

const display = useDisplay();

// 响应式数据
const chartCanvas = ref(null);
const chart = ref(null);
const selectedMetrics = ref(["raised_amount", "backer_count"]); // 默认只选择两个主要指标
const timeRange = ref("all");
const isUpdating = ref(false); // 防止动画期间重复更新

// 确保至少选择一个指标
watch(
  selectedMetrics,
  (newValue) => {
    if (!newValue || newValue.length === 0) {
      selectedMetrics.value = ["raised_amount"];
    }
    console.log("选择的指标变化:", newValue);
  },
  { immediate: true },
);

// 可用指标配置
const availableMetrics = [
  { key: "raised_amount", label: "筹款金额", color: "primary" },
  { key: "backer_count", label: "支持者数", color: "secondary" },
  { key: "like_count", label: "点赞数", color: "success" },
  { key: "comment_count", label: "评论数", color: "warning" },
  { key: "completion_rate", label: "完成率(%)", color: "info" },
  { key: "update_count", label: "更新数", color: "error" },
];

// 时间范围选项
const timeRangeOptions = [
  { label: "全部", value: "all" },
  { label: "最近7天", value: "7d" },
  { label: "最近30天", value: "30d" },
  { label: "最近90天", value: "90d" },
];

// 计算属性
const chartHeight = computed(() => {
  if (display.xs.value) return 300;
  if (display.sm.value) return 350;
  return props.height;
});

const filteredData = computed(() => {
  if (!props.historyData.length) return [];

  let data = [...props.historyData].reverse(); // 按时间正序排列

  if (timeRange.value !== "all") {
    const days = parseInt(timeRange.value.replace("d", ""));
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    data = data.filter((item) => {
      const itemDate = new Date(item.crawl_time);
      return itemDate >= cutoffDate;
    });
  }

  return data;
});

const chartData = computed(() => {
  if (!filteredData.value.length) {
    console.log("没有过滤后的数据");
    return null;
  }

  console.log("过滤后的数据:", filteredData.value.length, "条");

  const labels = filteredData.value.map((item) =>
    formatDateTime(item.crawl_time, "MM-DD HH:mm"),
  );

  console.log("时间标签:", labels);

  const datasets = selectedMetrics.value.map((metricKey, index) => {
    const metric = availableMetrics.find((m) => m.key === metricKey);
    const color = getMetricColor(metricKey);
    const rawData = filteredData.value.map((item) => item[metricKey] || 0);

    console.log(`指标 ${metricKey} (${metric?.label}) 数据:`, rawData);

    // 处理完成率数据（百分比）
    let data = rawData;
    if (metricKey === "completion_rate") {
      data = rawData.map((val) => Math.min(val, 100)); // 限制在100%以内
    }

    // 使用固定颜色而不是CSS变量
    const colorMap = {
      primary: "#1976d2",
      secondary: "#424242",
      success: "#4caf50",
      warning: "#ff9800",
      info: "#2196f3",
      error: "#f44336",
    };

    // 为每个数据集分配不同颜色
    const colors = [
      "#1976d2",
      "#4caf50",
      "#ff9800",
      "#f44336",
      "#2196f3",
      "#9c27b0",
    ];
    const datasetColor = colors[index % colors.length];

    return {
      label: metric?.label || metricKey,
      data: data,
      borderColor: datasetColor,
      backgroundColor: datasetColor + "20",
      fill: false,
      tension: 0.4,
      pointRadius: 3,
      pointHoverRadius: 5,
      borderWidth: 2,
      yAxisID: metricKey === "completion_rate" ? "y1" : "y", // 完成率使用单独的Y轴
    };
  });

  console.log("图表数据集:", datasets);

  return { labels, datasets };
});

// 方法
const getMetricColor = (metricKey) => {
  const metric = availableMetrics.find((m) => m.key === metricKey);
  return metric?.color || "primary";
};

const createChart = () => {
  if (isUpdating.value) {
    console.log("图表正在更新中，跳过创建");
    return;
  }

  if (!chartCanvas.value || !chartData.value) {
    console.log("图表创建失败: 缺少canvas或数据", {
      hasCanvas: !!chartCanvas.value,
      hasData: !!chartData.value,
      dataLength: chartData.value?.datasets?.length || 0,
    });
    return;
  }

  isUpdating.value = true;
  console.log("开始创建图表", chartData.value);

  // 销毁现有图表
  if (chart.value) {
    chart.value.destroy();
    chart.value = null;
  }

  const ctx = chartCanvas.value.getContext("2d");

  if (!ctx) {
    console.error("无法获取canvas上下文");
    isUpdating.value = false;
    return;
  }

  try {
    chart.value = new ChartJS(ctx, {
      type: "line",
      data: chartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 750,
          onComplete: () => {
            // 确保在Vue的响应式系统中更新
            nextTick(() => {
              isUpdating.value = false;
              console.log("图表动画完成");
            });
          },
        },
        plugins: {
          title: {
            display: false,
          },
          legend: {
            position: "bottom",
            labels: {
              usePointStyle: true,
              padding: 20,
              color: "#666",
              font: {
                size: 12,
              },
            },
          },
          tooltip: {
            mode: "index",
            intersect: false,
            backgroundColor: "#fff",
            titleColor: "#333",
            bodyColor: "#333",
            borderColor: "#ddd",
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12,
          },
        },
        scales: {
          x: {
            display: true,
            title: {
              display: true,
              text: "时间",
              color: "#666",
            },
            grid: {
              color: "#e0e0e0",
            },
            ticks: {
              color: "#666",
              maxTicksLimit: 8,
            },
          },
          y: {
            display: true,
            type: "linear",
            position: "left",
            title: {
              display: true,
              text: "数值",
              color: "#666",
            },
            grid: {
              color: "#e0e0e0",
            },
            ticks: {
              color: "#666",
              callback: function (value) {
                // 格式化Y轴标签，处理大数值
                if (value >= 1000000) {
                  return (value / 1000000).toFixed(1) + "M";
                } else if (value >= 1000) {
                  return (value / 1000).toFixed(1) + "K";
                }
                return value;
              },
            },
          },
          y1: {
            display: selectedMetrics.value.includes("completion_rate"),
            type: "linear",
            position: "right",
            title: {
              display: true,
              text: "完成率(%)",
              color: "#666",
            },
            grid: {
              drawOnChartArea: false,
            },
            ticks: {
              color: "#666",
              min: 0,
              max: 100,
              callback: function (value) {
                return value + "%";
              },
            },
          },
        },
        interaction: {
          mode: "nearest",
          axis: "x",
          intersect: false,
        },
      },
    });

    console.log("图表创建成功", chart.value);
  } catch (error) {
    console.error("图表创建失败:", error);
    isUpdating.value = false;
  }
};

const updateChart = () => {
  if (!chart.value || !chartData.value) {
    console.log("无法更新图表:", {
      hasChart: !!chart.value,
      hasData: !!chartData.value,
    });
    return;
  }

  console.log("更新图表数据");
  chart.value.data = chartData.value;
  chart.value.update("active");
};

// 防抖定时器
let updateTimer = null;

// 监听器
watch(
  [selectedMetrics, timeRange],
  () => {
    console.log("指标或时间范围变化，重新创建图表", {
      selectedMetrics: selectedMetrics.value,
      timeRange: timeRange.value,
    });

    // 清除之前的定时器
    if (updateTimer) {
      clearTimeout(updateTimer);
    }

    // 防抖：延迟执行，避免快速连续变化
    updateTimer = setTimeout(() => {
      if (!isUpdating.value) {
        nextTick(() => {
          createChart();
        });
      }
    }, 300); // 300ms防抖
  },
  { deep: true },
);

watch(
  () => props.historyData,
  () => {
    console.log("历史数据变化，重新创建图表");

    // 清除防抖定时器
    if (updateTimer) {
      clearTimeout(updateTimer);
    }

    // 数据变化立即更新，但也要检查动画状态
    if (!isUpdating.value) {
      nextTick(() => {
        createChart();
      });
    }
  },
  { deep: true },
);

// 生命周期
onMounted(() => {
  console.log("组件挂载，历史数据长度:", props.historyData.length);
  nextTick(() => {
    setTimeout(() => {
      createChart();
    }, 100); // 延迟创建图表，确保DOM完全渲染
  });
});

onUnmounted(() => {
  // 清除防抖定时器
  if (updateTimer) {
    clearTimeout(updateTimer);
    updateTimer = null;
  }

  // 销毁图表
  if (chart.value) {
    try {
      chart.value.destroy();
    } catch (error) {
      console.warn("图表销毁时出现错误:", error);
    }
    chart.value = null;
  }

  isUpdating.value = false;
});
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
}

.chart-container canvas {
  max-width: 100%;
  height: auto;
}

/* MD3 选择器样式优化 */
.v-select {
  --v-field-border-radius: 12px;
}

/* 响应式优化 */
@media (max-width: 599px) {
  .chart-container {
    height: 300px !important;
  }
}
</style>
