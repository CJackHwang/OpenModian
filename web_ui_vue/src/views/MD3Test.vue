<template>
  <v-container class="pa-6" fluid>
    <!-- 页面标题 -->
    <div class="mb-8">
      <h1 class="text-h3 font-weight-medium mb-2">
        Material Design 3 测试页面
      </h1>
      <p class="text-subtitle-1 text-medium-emphasis">
        验证MD3大圆角扁平化设计 - 无阴影 + 描边效果
      </p>
    </div>

    <!-- 主题切换 -->
    <v-row class="mb-8">
      <v-col cols="12">
        <v-card>
          <v-card-title>主题切换</v-card-title>
          <v-card-text>
            <v-btn-toggle
              v-model="currentTheme"
              mandatory
              @update:model-value="toggleTheme"
            >
              <v-btn value="light" prepend-icon="mdi-white-balance-sunny">
                浅色模式
              </v-btn>
              <v-btn value="dark" prepend-icon="mdi-moon-waning-crescent">
                深色模式
              </v-btn>
            </v-btn-toggle>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 按钮系统测试 -->
    <v-row class="mb-8">
      <v-col cols="12">
        <v-card>
          <v-card-title>MD3 扁平化按钮系统 - 无阴影描边设计</v-card-title>
          <v-card-text>
            <p class="mb-4">所有按钮都采用扁平化设计，无阴影，使用描边效果：</p>
            <div class="d-flex flex-wrap ga-4 mb-4">
              <v-btn color="primary">Primary Button</v-btn>
              <v-btn variant="tonal" color="primary">Tonal Button</v-btn>
              <v-btn variant="outlined" color="primary">Outlined Button</v-btn>
              <v-btn variant="text" color="primary">Text Button</v-btn>
            </div>
            <div class="d-flex flex-wrap ga-4 mb-4">
              <v-btn color="secondary">Secondary</v-btn>
              <v-btn color="tertiary">Tertiary</v-btn>
              <v-btn color="success">Success</v-btn>
              <v-btn color="error">Error</v-btn>
            </div>
            <div class="d-flex flex-wrap ga-4">
              <v-btn-group>
                <v-btn>Group 1</v-btn>
                <v-btn>Group 2</v-btn>
                <v-btn>Group 3</v-btn>
              </v-btn-group>
              <v-btn-toggle>
                <v-btn>Toggle 1</v-btn>
                <v-btn>Toggle 2</v-btn>
              </v-btn-toggle>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 卡片系统测试 -->
    <v-row class="mb-8">
      <v-col cols="12" md="4">
        <v-card color="primary-container" variant="flat">
          <v-card-title>Primary Container</v-card-title>
          <v-card-text>
            这是使用primary-container颜色的卡片，展示MD3的tonal elevation效果。
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card color="secondary-container" variant="flat">
          <v-card-title>Secondary Container</v-card-title>
          <v-card-text> 这是使用secondary-container颜色的卡片。 </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card color="surface-container-high" variant="flat">
          <v-card-title>Surface Container High</v-card-title>
          <v-card-text>
            这是使用surface-container-high的卡片，展示表面层次。
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 表单系统测试 -->
    <v-row class="mb-8">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>MD3 表单组件</v-card-title>
          <v-card-text>
            <v-text-field
              label="文本输入"
              placeholder="请输入文本"
              class="mb-4"
            />
            <v-select
              label="选择框"
              :items="['选项1', '选项2', '选项3']"
              class="mb-4"
            />
            <v-textarea
              label="文本区域"
              placeholder="请输入多行文本"
              rows="3"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>MD3 控制组件 - 现代化开关样式</v-card-title>
          <v-card-text>
            <h4 class="mb-3">现代化开关组件</h4>
            <p class="text-caption mb-4">应用了完整的现代化样式规范</p>

            <v-switch label="主要开关" color="primary" class="mb-3" />
            <v-switch
              label="次要开关"
              color="secondary"
              :model-value="true"
              class="mb-3"
            />
            <v-switch label="成功开关" color="success" class="mb-3" />
            <v-switch label="禁用开关" disabled class="mb-4" />

            <v-divider class="my-4" />

            <h4 class="mb-3">其他控制组件</h4>
            <v-checkbox label="复选框" color="primary" class="mb-4" />
            <v-radio-group>
              <v-radio label="单选项1" value="1" color="primary" />
              <v-radio label="单选项2" value="2" color="primary" />
            </v-radio-group>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 芯片和徽章测试 -->
    <v-row class="mb-8">
      <v-col cols="12">
        <v-card>
          <v-card-title>MD3 芯片和徽章</v-card-title>
          <v-card-text>
            <div class="d-flex flex-wrap ga-2 mb-4">
              <v-chip color="primary">Primary Chip</v-chip>
              <v-chip variant="tonal" color="secondary">Tonal Chip</v-chip>
              <v-chip variant="outlined" color="tertiary">Outlined Chip</v-chip>
              <v-chip closable>Closable Chip</v-chip>
            </div>
            <div class="d-flex ga-4">
              <v-badge content="99+" color="error">
                <v-btn>带徽章的按钮</v-btn>
              </v-badge>
              <v-badge dot color="success">
                <v-icon>mdi-bell</v-icon>
              </v-badge>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 警告和消息测试 -->
    <v-row class="mb-8">
      <v-col cols="12">
        <v-card>
          <v-card-title>MD3 警告和消息</v-card-title>
          <v-card-text>
            <v-alert type="success" class="mb-4">
              这是一个成功消息，使用MD3的tonal variant。
            </v-alert>
            <v-alert type="warning" class="mb-4">
              这是一个警告消息，展示MD3的颜色系统。
            </v-alert>
            <v-alert type="error" class="mb-4">
              这是一个错误消息，符合WCAG 2.1 AA对比度标准。
            </v-alert>
            <v-alert type="info"> 这是一个信息消息，使用扁平化设计。 </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 大组件扁平化设计展示 -->
    <v-row class="mb-8">
      <v-col cols="12">
        <v-card>
          <v-card-title>大组件扁平化设计展示</v-card-title>
          <v-card-text>
            <p class="mb-4">所有大组件都采用大圆角 + 描边设计，无阴影效果：</p>

            <!-- 扩展面板示例 -->
            <v-expansion-panels class="mb-4">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  扩展面板 - 大圆角扁平化
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  这是一个扩展面板的内容，展示大圆角和描边效果，无阴影设计。
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- 数据表格示例 -->
            <v-data-table
              :headers="[
                { title: '名称', key: 'name' },
                { title: '类型', key: 'type' },
                { title: '状态', key: 'status' },
              ]"
              :items="[
                { name: '项目A', type: '大组件', status: '扁平化' },
                { name: '项目B', type: '大圆角', status: '无阴影' },
                { name: '项目C', type: '描边设计', status: '现代化' },
              ]"
              class="mb-4"
            />

            <!-- 横幅示例 -->
            <v-banner
              text="这是一个横幅组件，展示大圆角扁平化设计效果"
              icon="mdi-information"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 对比度测试 -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>WCAG 2.1 AA 对比度测试</v-card-title>
          <v-card-text>
            <v-sheet class="d-flex flex-wrap ga-4" color="transparent">
              <v-sheet
                class="pa-4 rounded-xl"
                style="background-color: rgb(var(--v-theme-primary))"
              >
                <v-chip style="color: rgb(var(--v-theme-on-primary))" variant="text"
                  >Primary背景上的文字</v-chip
                >
              </v-sheet>
              <v-sheet
                class="pa-4 rounded-xl"
                style="background-color: rgb(var(--v-theme-primary-container))"
              >
                <v-chip style="color: rgb(var(--v-theme-on-primary-container))" variant="text"
                  >Primary Container背景上的文字</v-chip
                >
              </v-sheet>
              <v-sheet
                class="pa-4 rounded-xl"
                style="background-color: rgb(var(--v-theme-surface-container))"
              >
                <v-chip style="color: rgb(var(--v-theme-on-surface))" variant="text"
                  >Surface Container背景上的文字</v-chip
                >
              </v-sheet>
            </v-sheet>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from "vue";
import { useTheme } from "vuetify";

const theme = useTheme();
const currentTheme = ref(theme.global.name.value);

const toggleTheme = (value) => {
  theme.global.name.value = value;
};
</script>

<style scoped>
/* MD3测试页面样式 - 完全依赖Vuetify3 defaults配置 */
</style>
