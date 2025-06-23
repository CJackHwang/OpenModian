<template>
  <v-container class="pa-6">
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon icon="mdi-test-tube" class="me-2" />
            按钮样式测试页面
          </v-card-title>
          <v-card-text>
            <v-card-text class="text-body-1 mb-4 pa-0">
              此页面用于测试按钮的显示效果，特别是filled按钮的背景色问题。
            </v-card-text>

            <!-- 默认按钮测试 -->
            <v-row class="mb-6">
              <v-col cols="12">
                <h3 class="text-h6 mb-3">默认按钮（使用main.js配置）</h3>
                <v-sheet class="d-flex flex-wrap gap-3" color="transparent">
                  <!-- 这些按钮应该使用main.js中的默认filled配置 -->
                  <v-btn>默认按钮1</v-btn>
                  <v-btn color="primary">Primary按钮</v-btn>
                  <v-btn color="secondary">Secondary按钮</v-btn>
                  <v-btn color="success">Success按钮</v-btn>
                  <v-btn color="error">Error按钮</v-btn>
                  <v-btn color="warning">Warning按钮</v-btn>
                </v-sheet>
              </v-col>
            </v-row>

            <!-- 明确指定filled的按钮 -->
            <v-row class="mb-6">
              <v-col cols="12">
                <h3 class="text-h6 mb-3">明确指定filled的按钮</h3>
                <div class="d-flex flex-wrap gap-3">
                  <v-btn variant="filled">默认Filled</v-btn>
                  <v-btn variant="filled" color="primary">Primary Filled</v-btn>
                  <v-btn variant="filled" color="secondary"
                    >Secondary Filled</v-btn
                  >
                  <v-btn variant="filled" color="success">Success Filled</v-btn>
                  <v-btn variant="filled" color="error">Error Filled</v-btn>
                  <v-btn variant="filled" color="warning">Warning Filled</v-btn>
                </div>
              </v-col>
            </v-row>

            <!-- 其他variant对比 -->
            <v-row class="mb-6">
              <v-col cols="12">
                <h3 class="text-h6 mb-3">其他variant对比</h3>
                <div class="d-flex flex-wrap gap-3 mb-3">
                  <v-btn variant="outlined" color="primary">Outlined</v-btn>
                  <v-btn variant="text" color="primary">Text</v-btn>
                  <v-btn variant="tonal" color="primary">Tonal</v-btn>
                  <v-btn variant="flat" color="primary">Flat</v-btn>
                </div>
              </v-col>
            </v-row>

            <!-- 强制样式测试 -->
            <v-row class="mb-6">
              <v-col cols="12">
                <h3 class="text-h6 mb-3">强制样式测试</h3>
                <div class="d-flex flex-wrap gap-3">
                  <v-btn style="background-color: red; color: white"
                    >强制红色背景</v-btn
                  >
                  <v-btn style="background-color: #1976d2; color: white"
                    >强制Primary色背景</v-btn
                  >
                </div>
                <p class="text-caption mt-2">
                  如果上面的强制样式按钮显示正常，说明CSS没有被完全阻止。
                </p>
              </v-col>
            </v-row>

            <!-- 主题信息 -->
            <v-row>
              <v-col cols="12">
                <h3 class="text-h6 mb-3">当前主题信息</h3>
                <v-card variant="outlined" class="pa-3">
                  <p><strong>当前主题:</strong> {{ currentTheme }}</p>
                  <p><strong>Primary颜色:</strong> {{ primaryColor }}</p>
                  <p><strong>On-Primary颜色:</strong> {{ onPrimaryColor }}</p>
                  <p><strong>Surface颜色:</strong> {{ surfaceColor }}</p>
                </v-card>
              </v-col>
            </v-row>

            <!-- 调试信息 -->
            <v-row class="mt-6">
              <v-col cols="12">
                <v-expansion-panels>
                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <v-icon icon="mdi-bug" class="me-2" />
                      调试信息
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <pre class="text-caption">{{ debugInfo }}</pre>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed } from "vue";
import { useTheme } from "vuetify";

const theme = useTheme();

// 计算属性
const currentTheme = computed(() => theme.global.name.value);

const primaryColor = computed(() => {
  const colors = theme.current.value.colors;
  return colors.primary;
});

const onPrimaryColor = computed(() => {
  const colors = theme.current.value.colors;
  return colors["on-primary"];
});

const surfaceColor = computed(() => {
  const colors = theme.current.value.colors;
  return colors.surface;
});

const debugInfo = computed(() => {
  return JSON.stringify(
    {
      themeName: theme.global.name.value,
      colors: {
        primary: theme.current.value.colors.primary,
        "on-primary": theme.current.value.colors["on-primary"],
        surface: theme.current.value.colors.surface,
        "on-surface": theme.current.value.colors["on-surface"],
      },
      variables: theme.current.value.variables,
    },
    null,
    2,
  );
});
</script>

<style scoped>
/* 测试页面样式 */
.gap-3 {
  gap: 12px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}
</style>
