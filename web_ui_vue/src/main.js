import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import router from './router'
import App from './App.vue'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

// Custom styles
import './styles/main.scss'

// 创建基础Vuetify配置
const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          // MD3 主色调系统 - 修复filled按钮背景色问题
          primary: '#1976D2',
          'primary-container': '#D3E3FD',
          'on-primary': '#FFFFFF',
          'on-primary-container': '#001C38',

          // MD3 次要色系统
          secondary: '#546E7A',
          'secondary-container': '#D7E3F7',
          'on-secondary': '#FFFFFF',
          'on-secondary-container': '#101C2B',

          // MD3 第三色系统 - 优化对比度
          tertiary: '#006064',
          'tertiary-container': '#B8EEFF',
          'on-tertiary': '#FFFFFF',
          'on-tertiary-container': '#001F24',

          // MD3 语义色系统
          error: '#BA1A1A',
          'error-container': '#FFDAD6',
          'on-error': '#FFFFFF',
          'on-error-container': '#410002',

          warning: '#D32F2F',
          'warning-container': '#FFDBCC',
          'on-warning': '#FFFFFF',
          'on-warning-container': '#2D1600',

          success: '#2E7D32',
          'success-container': '#C8E6C9',
          'on-success': '#FFFFFF',
          'on-success-container': '#0D2818',

          info: '#1976D2',
          'info-container': '#D3E3FD',
          'on-info': '#FFFFFF',
          'on-info-container': '#001C38',

          // MD3 表面色系统
          surface: '#FEFBFF',
          'surface-dim': '#DDD8E1',
          'surface-bright': '#FEFBFF',
          'surface-container-lowest': '#FFFFFF',
          'surface-container-low': '#F7F2FA',
          'surface-container': '#F1ECF4',
          'surface-container-high': '#ECE6F0',
          'surface-container-highest': '#E6E0E9',
          'surface-variant': '#E7E0EC',
          'on-surface': '#1D1B20',
          'on-surface-variant': '#49454F',

          // MD3 轮廓色系统 - 优化对比度
          outline: '#6F6B76', // 增强对比度
          'outline-variant': '#C4C7C5', // 优化边框可见性

          // MD3 背景色系统
          background: '#FEFBFF',
          'on-background': '#1D1B20',

          // MD3 反色表面
          'inverse-surface': '#322F35',
          'inverse-on-surface': '#F5EFF7',
          'inverse-primary': '#A8C8EC'
        },
        variables: {
          // MD3 文字透明度变量
          'high-emphasis-opacity': 0.87,
          'medium-emphasis-opacity': 0.60,
          'disabled-opacity': 0.38,
          // MD3 状态层透明度
          'hover-opacity': 0.08,
          'focus-opacity': 0.12,
          'selected-opacity': 0.12,
          'activated-opacity': 0.12,
          'pressed-opacity': 0.16,
          'dragged-opacity': 0.16
        },
        variables: {
          // MD3 按钮系统CSS变量 - 确保filled按钮正确显示背景色
          'btn-filled-background-opacity': 1,
          'btn-filled-color-opacity': 1
        }
      },
      dark: {
        dark: true,
        colors: {
          // MD3 主色调系统 - 深色模式（修正对比度）
          primary: '#A8C8EC',
          'primary-container': '#004A77',
          'on-primary': '#000000', // 修正：在浅色primary背景上使用黑色文字
          'on-primary-container': '#D3E3FD',

          // MD3 次要色系统 - 深色模式（修正对比度）
          secondary: '#BCC7DB',
          'secondary-container': '#3C4858',
          'on-secondary': '#000000', // 修正：在浅色secondary背景上使用黑色文字
          'on-secondary-container': '#D7E3F7',

          // MD3 第三色系统 - 深色模式
          tertiary: '#86D2FF',
          'tertiary-container': '#004F5C',
          'on-tertiary': '#003640',
          'on-tertiary-container': '#B8EEFF',

          // MD3 语义色系统 - 深色模式
          error: '#FFB4AB',
          'error-container': '#93000A',
          'on-error': '#690005',
          'on-error-container': '#FFDAD6',

          warning: '#FFB951',
          'warning-container': '#D32F2F',
          'on-warning': '#000000',
          'on-warning-container': '#FFFFFF',

          success: '#A6CF70',
          'success-container': '#1B5E20',
          'on-success': '#0D2818',
          'on-success-container': '#C8E6C9',

          info: '#A8C8EC',
          'info-container': '#004A77',
          'on-info': '#003258',
          'on-info-container': '#D3E3FD',

          // MD3 表面色系统 - 深色模式
          surface: '#141218',
          'surface-dim': '#141218',
          'surface-bright': '#3A3740',
          'surface-container-lowest': '#0F0D13',
          'surface-container-low': '#1D1B20',
          'surface-container': '#211F26',
          'surface-container-high': '#2B2930',
          'surface-container-highest': '#36343B',
          'surface-variant': '#49454F',
          'on-surface': '#E6E0E9',
          'on-surface-variant': '#CAC4D0',

          // MD3 轮廓色系统 - 深色模式优化对比度
          outline: '#9A96A1', // 增强深色模式下的对比度
          'outline-variant': '#524F5A', // 优化深色模式边框可见性

          // MD3 背景色系统 - 深色模式
          background: '#141218',
          'on-background': '#E6E0E9',

          // MD3 反色表面 - 深色模式
          'inverse-surface': '#E6E0E9',
          'inverse-on-surface': '#322F35',
          'inverse-primary': '#1976D2'
        },
        variables: {
          // MD3 文字透明度变量
          'high-emphasis-opacity': 0.87,
          'medium-emphasis-opacity': 0.60,
          'disabled-opacity': 0.38,
          // MD3 状态层透明度
          'hover-opacity': 0.08,
          'focus-opacity': 0.12,
          'selected-opacity': 0.12,
          'activated-opacity': 0.12,
          'pressed-opacity': 0.16,
          'dragged-opacity': 0.16
        },
        variables: {
          // MD3 按钮系统CSS变量 - 确保filled按钮正确显示背景色
          'btn-filled-background-opacity': 1,
          'btn-filled-color-opacity': 1
        }
      }
    }
  },

  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  },

  display: {
    mobileBreakpoint: 'sm',
    thresholds: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
      xxl: 2560
    }
  },

  defaults: {
    // MD3 基础布局系统 - 完整配置
    VApp: {
      // 移除固定theme属性，让Vuetify自动管理主题切换
    },
    VMain: {
      // 主内容区域，无需特殊配置
    },
    VContainer: {
      fluid: false // 默认固定宽度容器
    },
    VRow: {
      dense: false,
      noGutters: false
    },
    VCol: {
      // 响应式列，根据需要设置
    },
    VSpacer: {
      // 间距组件，无需配置
    },

    // MD3 按钮系统 - 统一使用elevated variant确保背景色显示
    VBtn: {
      rounded: 'lg',
      elevation: 2, // elevated按钮需要elevation
      size: 'default',
      density: 'default',
      variant: 'elevated', // 使用elevated variant确保有背景色和阴影
      color: 'primary' // 默认primary颜色
    },

    // MD3 按钮组系统
    VBtnGroup: {
      rounded: 'lg',
      elevation: 0,
      variant: 'outlined', // 按钮组默认使用outlined
      color: 'primary',
      density: 'default'
    },
    VBtnToggle: {
      variant: 'outlined',
      color: 'primary',
      density: 'default'
    },

    // MD3 卡片系统 - 优化视觉层次和对比度
    VCard: {
      elevation: 1, // 确保与背景有明显区分
      rounded: 'xl',
      variant: 'outlined' // 使用outlined variant确保边框可见性
      // ✅ 修复：移除color属性，让Vuetify自动管理背景色和文字颜色
    },

    // MD3 卡片标题系统 - 文字颜色由Vuetify自动管理
    VCardTitle: {
      // Vuetify3自动处理文字颜色
    },

    // MD3 卡片文本系统 - 文字颜色由Vuetify自动管理
    VCardText: {
      // Vuetify3自动处理文字颜色
    },

    // MD3 卡片操作系统
    VCardActions: {
      // 操作按钮样式通过VBtn defaults管理
    },

    // MD3 芯片系统 - 基于官方文档的完整配置
    VChip: {
      rounded: 'lg',
      elevation: 0,
      variant: 'tonal',
      size: 'default',
      density: 'default'
    },

    // MD3 表单系统 - 现代输入样式
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'xl'
      // 文字颜色由Vuetify3自动管理
    },

    // MD3 选择框系统 - 修复下拉菜单背景透明问题
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'xl',
      menuProps: {
        contentClass: 'v-select-menu'
      }
    },

    // MD3 自动完成系统
    VAutocomplete: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'xl',
      menuProps: {
        contentClass: 'v-select-menu'
      }
    },

    // MD3 组合框系统
    VCombobox: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'xl',
      menuProps: {
        contentClass: 'v-select-menu'
      }
    },

    // MD3 文件输入系统
    VFileInput: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'xl',
      color: 'primary'
    },

    // MD3 文本区域系统
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'xl',
      color: 'primary'
    },
    // 重复配置已在上方统一配置，移除重复

    // 重复配置已在下方统一配置，移除重复

    // MD3 列表系统 - 修复选中状态颜色对比度
    VList: {
      density: 'comfortable',
      nav: true // 启用导航模式
    },
    VListItem: {
      rounded: 'xl',
      activeColor: 'primary', // 激活状态使用primary颜色
      variant: 'text' // 使用text变体，文字颜色由Vuetify自动管理
    },

    // MD3 列表项标题系统 - 文字颜色由Vuetify自动管理
    VListItemTitle: {
      // Vuetify3自动处理文字颜色
    },

    // MD3 列表项副标题系统 - 文字颜色由Vuetify自动管理
    VListItemSubtitle: {
      // Vuetify3自动处理文字颜色
    },

    // 重复配置已在下方统一配置，移除重复

    // MD3 头像系统
    VAvatar: {
      rounded: 'lg'
    },

    // MD3 工具提示
    VTooltip: {
      location: 'top'
    },

    // MD3 底部导航
    VBottomNavigation: {
      elevation: 0,
      color: 'surface-container'
    },

    // MD3 时间线系统 - 修复颜色问题
    VTimeline: {
      density: 'comfortable'
    },
    VTimelineItem: {
      dotColor: 'primary',
      size: 'small'
    },

    // MD3 应用栏系统 - 优化对比度
    VAppBar: {
      elevation: 1, // ✅ 修复：添加轻微elevation增强视觉层次
      flat: false,
      color: 'surface-container-low', // ✅ 修复：使用更高对比度的背景
      border: 'b-thin opacity-20' // ✅ 修复：增强边框可见性
    },

    // MD3 导航抽屉系统 - 优化对比度
    VNavigationDrawer: {
      elevation: 1, // ✅ 修复：添加轻微elevation增强视觉层次
      color: 'surface-container', // ✅ 修复：使用更高对比度的背景
      border: 'e-thin opacity-20' // ✅ 修复：增强边框可见性
    },

    // MD3 图标系统 - 移除默认颜色配置以避免对比度问题
    VIcon: {
      // 移除默认color配置，让图标根据上下文自动选择颜色
    },

    // MD3 进度条系统
    VProgressLinear: {
      rounded: true,
      height: 8,
      color: 'primary' // ✅ 修复：添加了缺失的color配置
    },
    VProgressCircular: {
      size: 'default',
      color: 'primary' // ✅ 修复：添加了缺失的color配置
    },

    // MD3 分隔线系统 - 优化对比度
    VDivider: {
      color: 'outline', // ✅ 修复：使用outline而非outline-variant提高对比度
      thickness: 1
    },

    // MD3 对话框系统
    VDialog: {
      rounded: 'xl', // ✅ 修复：添加了缺失的rounded配置
      maxWidth: '500px',
      persistent: false,
      scrollable: true
    },

    // MD3 底部表单系统
    VBottomSheet: {
      rounded: 'xl' // ✅ 修复：添加了缺失的rounded配置
    },

    // MD3 消息条系统
    VSnackbar: {
      timeout: 4000,
      location: 'top right',
      variant: 'tonal', // ✅ 修复：使用MD3推荐的tonal variant
      rounded: 'lg',
      elevation: 2
    },

    // MD3 警告系统 - 确保正确的颜色对比度
    VAlert: {
      variant: 'tonal',
      rounded: 'lg',
      elevation: 0,
      density: 'default'
      // VAlert的文字颜色由variant自动管理，确保正确的对比度
    },

    // MD3 菜单系统 - 修复背景透明问题
    VMenu: {
      rounded: 'lg',
      elevation: 2,
      offset: 8,
      contentClass: 'v-menu-content'
    },

    // MD3 工具栏系统
    VToolbar: {
      elevation: 0,
      flat: true,
      color: 'surface-container'
    },

    // MD3 标签页系统
    VTabs: {
      color: 'primary',
      alignTabs: 'start',
      density: 'default'
    },
    VTab: {
      rounded: 'lg' // ✅ 修复：添加了缺失的rounded配置
    },

    // MD3 滑块系统
    VSlider: {
      color: 'primary',
      thumbColor: 'primary',
      trackColor: 'outline',
      density: 'default'
    },

    // MD3 范围滑块系统
    VRangeSlider: {
      color: 'primary',
      thumbColor: 'primary',
      trackColor: 'outline',
      density: 'default'
    },

    // MD3 开关系统
    VSwitch: {
      color: 'primary',
      density: 'default'
    },

    // MD3 复选框系统
    VCheckbox: {
      color: 'primary',
      density: 'default'
    },

    // MD3 单选框系统
    VRadio: {
      color: 'primary',
      density: 'default'
    },
    VRadioGroup: {
      color: 'primary',
      density: 'default'
    },

    // MD3 数据表格系统 - 完整配置
    VDataTable: {
      density: 'comfortable',
      hover: true,
      elevation: 0,
      rounded: 'xl',
      itemsPerPage: 25,
      showCurrentPage: true
    },

    // MD3 徽章系统
    VBadge: {
      color: 'primary',
      location: 'top end',
      content: ''
    },

    // MD3 扩展面板系统
    VExpansionPanels: {
      variant: 'accordion',
      color: 'primary'
    },
    VExpansionPanel: {
      // 扩展面板项，使用默认配置
    },

    // MD3 图片系统
    VImg: {
      rounded: 'lg'
    },

    // MD3 响应式图片系统
    VResponsive: {
      // 响应式容器，使用默认配置
    },

    // MD3 懒加载系统
    VLazy: {
      // 懒加载，使用默认配置
    },

    // MD3 并行组系统
    VParallax: {
      // 视差滚动，使用默认配置
    },

    // VDivider配置已在上方统一配置，移除重复

    // MD3 步进器系统
    VStepper: {
      elevation: 0,
      rounded: 'xl',
      color: 'primary'
    },
    VStepperHeader: {
      elevation: 0
    },
    VStepperItem: {
      color: 'primary'
    },

    // MD3 轮播图系统
    VCarousel: {
      rounded: 'xl',
      showArrows: 'hover',
      hideDelimiters: false,
      cycle: false
    },
    VCarouselItem: {
      // 轮播项，使用默认配置
    },

    // MD3 横幅系统
    VBanner: {
      rounded: 'lg',
      elevation: 0,
      color: 'surface-container'
    },

    // MD3 面包屑系统
    VBreadcrumbs: {
      density: 'comfortable',
      divider: '/'
    },
    VBreadcrumbsItem: {
      // 面包屑项，使用默认配置
    },

    // MD3 分页系统
    VPagination: {
      rounded: 'lg',
      color: 'primary',
      variant: 'outlined',
      density: 'comfortable'
    },

    // MD3 评分系统
    VRating: {
      color: 'warning',
      emptyIcon: 'mdi-star-outline',
      fullIcon: 'mdi-star',
      halfIcon: 'mdi-star-half-full',
      density: 'comfortable'
    },

    // MD3 虚拟滚动系统
    VVirtualScroll: {
      height: 400,
      itemHeight: 48
    },

    // MD3 数据迭代器系统
    VDataIterator: {
      itemsPerPage: 12,
      showCurrentPage: true
    },

    // MD3 表单系统扩展
    VForm: {
      // 表单容器，使用默认配置
    },
    VInput: {
      density: 'comfortable',
      color: 'primary'
    },
    VLabel: {
      // 标签，使用默认配置
    },

    // MD3 覆盖层系统
    VOverlay: {
      // 覆盖层，使用默认配置
    },

    // MD3 骨架加载器系统
    VSkeletonLoader: {
      type: 'card',
      elevation: 0
    },

    // MD3 无限滚动系统
    VInfiniteScroll: {
      // 无限滚动，使用默认配置
    },

    // MD3 OTP输入系统
    VOtpInput: {
      variant: 'outlined',
      color: 'primary',
      density: 'comfortable'
    },

    // MD3 颜色选择器系统
    VColorPicker: {
      mode: 'hexa',
      showSwatches: true
    },

    // MD3 日期选择器系统
    VDatePicker: {
      color: 'primary',
      elevation: 2,
      rounded: 'lg'
    },

    // MD3 时间选择器系统
    VTimePicker: {
      color: 'primary',
      elevation: 2,
      rounded: 'lg'
    },

    // MD3 窗口系统
    VWindow: {
      // 窗口容器，使用默认配置
    },
    VWindowItem: {
      // 窗口项，使用默认配置
    },

    // MD3 代码显示系统
    VCode: {
      // 代码显示，使用默认配置
    },

    // MD3 键盘按键系统
    VKbd: {
      // 键盘按键，使用默认配置
    },

    // MD3 系统栏系统
    VSystemBar: {
      color: 'surface-container',
      height: 24
    },

    // MD3 速度拨号系统
    VSpeedDial: {
      // 速度拨号，使用默认配置
    },

    // MD3 悬浮操作按钮系统
    VFab: {
      color: 'primary',
      size: 'default',
      elevation: 6
    },

    // MD3 表格系统扩展
    VTable: {
      density: 'comfortable',
      hover: true
    },

    // MD3 虚拟表格系统
    VDataTableVirtual: {
      density: 'comfortable',
      hover: true,
      itemHeight: 48
    },

    // MD3 服务器端表格系统
    VDataTableServer: {
      density: 'comfortable',
      hover: true,
      itemsPerPage: 25,
      showCurrentPage: true
    },

    // MD3 数据表格行系统
    VDataTableRow: {
      // 表格行，使用默认配置
    },

    // MD3 数据表格头部系统
    VDataTableHeaders: {
      // 表格头部，使用默认配置
    },

    // MD3 列表子组件系统
    VListGroup: {
      // 列表组，使用默认配置
    },
    VListSubheader: {
      // 列表子标题，使用默认配置
    },

    // MD3 卡片子组件系统
    VCardItem: {
      // 卡片项，使用默认配置
    },
    VCardSubtitle: {
      // 卡片副标题，使用默认配置
    },

    // MD3 应用栏子组件系统
    VAppBarTitle: {
      // 应用栏标题，使用默认配置
    },
    VAppBarNavIcon: {
      // 应用栏导航图标，使用默认配置
    },

    // MD3 工具栏子组件系统
    VToolbarTitle: {
      // 工具栏标题，使用默认配置
    },
    VToolbarItems: {
      // 工具栏项，使用默认配置
    },

    // MD3 标签页窗口系统
    VTabsWindow: {
      // 标签页窗口，使用默认配置
    },
    VTabsWindowItem: {
      // 标签页窗口项，使用默认配置
    },

    // MD3 扩展面板子组件系统
    VExpansionPanelTitle: {
      // 扩展面板标题，使用默认配置
    },
    VExpansionPanelText: {
      // 扩展面板文本，使用默认配置
    },

    // MD3 时间线子组件系统
    VTimelineItem: {
      dotColor: 'primary',
      size: 'small'
    },

    // 其他组件配置已在上方统一配置，避免重复
  }
})

// 初始化应用
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')
