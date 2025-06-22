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

// 创建基础Vuetify配置 - 基于Material Design 3官方规范
const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          // MD3 主色调系统 - 优化浅色模式对比度
          primary: '#1976D2', // 标准蓝色，确保良好对比度
          'primary-container': '#BBDEFB', // 更明显的容器色
          'on-primary': '#FFFFFF',
          'on-primary-container': '#0D47A1', // 深色文字确保对比度

          // MD3 次要色系统 - 优化浅色模式对比度
          secondary: '#546E7A', // 灰蓝色
          'secondary-container': '#CFD8DC', // 更明显的容器色
          'on-secondary': '#FFFFFF',
          'on-secondary-container': '#263238', // 深色文字

          // MD3 第三色系统 - 优化浅色模式
          tertiary: '#00796B', // 青色
          'tertiary-container': '#B2DFDB', // 更明显的容器色
          'on-tertiary': '#FFFFFF',
          'on-tertiary-container': '#004D40', // 深色文字

          // MD3 语义色系统 - 优化对比度
          error: '#D32F2F', // 红色
          'error-container': '#FFCDD2', // 更明显的容器色
          'on-error': '#FFFFFF',
          'on-error-container': '#B71C1C', // 深色文字

          warning: '#F57C00', // 橙色
          'warning-container': '#FFE0B2', // 更明显的容器色
          'on-warning': '#FFFFFF',
          'on-warning-container': '#E65100', // 深色文字

          success: '#388E3C', // 绿色
          'success-container': '#C8E6C9', // 更明显的容器色
          'on-success': '#FFFFFF',
          'on-success-container': '#1B5E20', // 深色文字

          info: '#1976D2', // 与primary保持一致
          'info-container': '#BBDEFB',
          'on-info': '#FFFFFF',
          'on-info-container': '#0D47A1',

          // MD3 表面色系统 - 优化层次和对比度
          surface: '#FEFBFF', // MD3标准表面色
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

          // MD3 轮廓色系统 - 优化边框可见性
          outline: '#79747E', // MD3标准轮廓色
          'outline-variant': '#CAC4D0', // MD3标准轮廓变体色

          // MD3 背景色系统
          background: '#FEFBFF',
          'on-background': '#1D1B20',

          // MD3 反色表面
          'inverse-surface': '#322F35',
          'inverse-on-surface': '#F5EFF7',
          'inverse-primary': '#A8C8EC'
        },
        variables: {
          // MD3 文字透明度变量 - 符合官方规范
          'high-emphasis-opacity': 0.87,
          'medium-emphasis-opacity': 0.60,
          'disabled-opacity': 0.38,
          // MD3 状态层透明度 - 官方标准
          'hover-opacity': 0.08,
          'focus-opacity': 0.12,
          'selected-opacity': 0.12,
          'activated-opacity': 0.12,
          'pressed-opacity': 0.16,
          'dragged-opacity': 0.16,
          // MD3 elevation系统 - 使用tonal elevation
          'surface-tint-color': 'var(--v-theme-primary)',
          'surface-tint-opacity': 0.05
        }
      },
      dark: {
        dark: true,
        colors: {
          // MD3 主色调系统 - 深色模式（保持用户满意的配色）
          primary: '#90CAF9', // 更亮的蓝色，适合深色背景
          'primary-container': '#1565C0', // 深蓝容器
          'on-primary': '#0D47A1', // 深色文字在浅色primary上
          'on-primary-container': '#E3F2FD', // 浅色文字在深色容器上

          // MD3 次要色系统 - 深色模式
          secondary: '#B0BEC5', // 浅灰蓝
          'secondary-container': '#455A64', // 深灰蓝容器
          'on-secondary': '#263238', // 深色文字在浅色secondary上
          'on-secondary-container': '#ECEFF1', // 浅色文字在深色容器上

          // MD3 第三色系统 - 深色模式
          tertiary: '#80CBC4', // 浅青色
          'tertiary-container': '#00695C', // 深青容器
          'on-tertiary': '#004D40', // 深色文字在浅色tertiary上
          'on-tertiary-container': '#E0F2F1', // 浅色文字在深色容器上

          // MD3 语义色系统 - 深色模式
          error: '#EF9A9A', // 浅红色
          'error-container': '#C62828', // 深红容器
          'on-error': '#B71C1C', // 深红文字
          'on-error-container': '#FFEBEE', // 浅色文字在深色容器上

          warning: '#FFCC80', // 浅橙色
          'warning-container': '#E65100', // 深橙容器
          'on-warning': '#BF360C', // 深橙文字
          'on-warning-container': '#FFF3E0', // 浅色文字在深色容器上

          success: '#A5D6A7', // 浅绿色
          'success-container': '#2E7D32', // 深绿容器
          'on-success': '#1B5E20', // 深绿文字
          'on-success-container': '#E8F5E8', // 浅色文字在深色容器上

          info: '#90CAF9', // 与primary保持一致
          'info-container': '#1565C0',
          'on-info': '#0D47A1',
          'on-info-container': '#E3F2FD',

          // MD3 表面色系统 - 深色模式（保持用户满意的层次）
          surface: '#121212', // 标准深色背景
          'surface-dim': '#0F0F0F', // 更暗的表面
          'surface-bright': '#2C2C2C', // 更亮的表面
          'surface-container-lowest': '#0A0A0A',
          'surface-container-low': '#1A1A1A',
          'surface-container': '#1F1F1F',
          'surface-container-high': '#252525',
          'surface-container-highest': '#2A2A2A',
          'surface-variant': '#424242',
          'on-surface': '#E0E0E0', // 高对比度文字
          'on-surface-variant': '#BDBDBD', // 中等强调文字

          // MD3 轮廓色系统 - 深色模式
          outline: '#757575', // 中等灰色边框
          'outline-variant': '#424242', // 深灰边框

          // MD3 背景色系统 - 深色模式
          background: '#121212',
          'on-background': '#E0E0E0',

          // MD3 反色表面 - 深色模式
          'inverse-surface': '#E0E0E0',
          'inverse-on-surface': '#121212',
          'inverse-primary': '#1565C0'
        },
        variables: {
          // MD3 文字透明度变量 - 符合官方规范
          'high-emphasis-opacity': 0.87,
          'medium-emphasis-opacity': 0.60,
          'disabled-opacity': 0.38,
          // MD3 状态层透明度 - 官方标准
          'hover-opacity': 0.08,
          'focus-opacity': 0.12,
          'selected-opacity': 0.12,
          'activated-opacity': 0.12,
          'pressed-opacity': 0.16,
          'dragged-opacity': 0.16,
          // MD3 elevation系统 - 使用tonal elevation
          'surface-tint-color': 'var(--v-theme-primary)',
          'surface-tint-opacity': 0.08
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

    // MD3 按钮系统 - 完全扁平化设计，无阴影
    VBtn: {
      rounded: 'xl', // 大圆角
      elevation: 0, // 完全无阴影
      size: 'default',
      density: 'default',
      variant: 'outlined', // 使用outlined获得描边效果
      color: 'primary'
    },

    // MD3 按钮组系统 - 完全扁平化设计
    VBtnGroup: {
      rounded: 'xl', // 大圆角
      elevation: 0, // 无阴影
      variant: 'outlined', // 描边设计
      color: 'primary',
      density: 'default'
    },
    VBtnToggle: {
      variant: 'outlined', // 描边设计
      color: 'primary',
      density: 'default',
      rounded: 'xl', // 大圆角
      elevation: 0 // 无阴影
    },

    // MD3 卡片系统 - 大圆角扁平化设计
    VCard: {
      elevation: 0, // 移除阴影
      rounded: 'xl', // 大圆角
      variant: 'outlined' // 使用描边而非阴影，保持原来的描边颜色
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

    // MD3 芯片系统 - 基于官方MD3规范，大圆角
    VChip: {
      rounded: 'xl', // 大圆角芯片
      elevation: 0,
      variant: 'tonal', // MD3推荐的tonal variant
      size: 'default',
      density: 'default'
    },

    // MD3 表单系统 - 基于官方MD3规范，使用大圆角和更明显的边框
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'lg', // 大圆角输入框
      baseColor: 'primary' // 使用primary颜色让边框更明显
    },

    // MD3 选择框系统 - 统一大圆角样式和更明显的边框
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'lg', // 大圆角输入框
      baseColor: 'primary', // 使用primary颜色让边框更明显
      menuProps: {
        contentClass: 'v-select-menu',
        elevation: 1 // 轻微elevation确保可见性
      }
    },

    // MD3 自动完成系统 - 大圆角和更明显的边框
    VAutocomplete: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'lg', // 大圆角输入框
      baseColor: 'primary', // 使用primary颜色让边框更明显
      menuProps: {
        contentClass: 'v-select-menu',
        elevation: 1
      }
    },

    // MD3 组合框系统 - 大圆角和更明显的边框
    VCombobox: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
      rounded: 'lg', // 大圆角输入框
      baseColor: 'primary', // 使用primary颜色让边框更明显
      menuProps: {
        contentClass: 'v-select-menu',
        elevation: 1
      }
    },

    // MD3 文件输入系统 - 大圆角和更明显的边框
    VFileInput: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg', // 大圆角输入框
      color: 'primary',
      baseColor: 'primary' // 使用primary颜色让边框更明显
    },

    // MD3 文本区域系统 - 大圆角和更明显的边框
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg', // 大圆角文本区域
      color: 'primary',
      baseColor: 'primary' // 使用primary颜色让边框更明显
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

    // MD3 头像系统 - 大圆角
    VAvatar: {
      rounded: 'xl' // 大圆角头像
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

    // MD3 应用栏系统 - 扁平化设计，仅使用Vuetify支持的属性
    VAppBar: {
      elevation: 0, // 完全无阴影
      flat: true, // 完全扁平
      color: 'surface-container', // 使用MD3表面容器色
      border: 'b-thin' // 底部边框分隔
    },

    // MD3 导航抽屉系统 - 扁平化设计，仅使用Vuetify支持的属性
    VNavigationDrawer: {
      elevation: 0, // 完全无阴影
      color: 'surface-container-low', // 使用MD3表面容器色
      border: 'e-thin' // 右侧边框分隔
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

    // MD3 对话框系统 - 大圆角扁平化设计
    VDialog: {
      rounded: 'xl', // 大圆角
      maxWidth: '500px',
      persistent: false,
      scrollable: true,
      elevation: 0 // 移除阴影，使用描边
    },

    // MD3 底部表单系统 - 大圆角扁平化设计
    VBottomSheet: {
      rounded: 'xl', // 大圆角
      elevation: 0 // 移除阴影，使用描边
    },

    // MD3 消息条系统 - 基于官方MD3规范，大圆角
    VSnackbar: {
      timeout: 4000,
      location: 'top right',
      variant: 'tonal',
      rounded: 'lg', // 大圆角消息条
      elevation: 0 // 无阴影，使用tonal colors
    },

    // MD3 警告系统 - 大圆角扁平化设计
    VAlert: {
      variant: 'outlined', // 使用outlined获得描边效果
      rounded: 'xl', // 大圆角
      elevation: 0, // 无阴影
      density: 'default',
      border: true // 使用完整描边
    },

    // MD3 菜单系统 - 大圆角扁平化设计
    VMenu: {
      rounded: 'lg', // 大圆角
      elevation: 0, // 移除阴影
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

    // MD3 数据表格系统 - 大圆角扁平化设计
    VDataTable: {
      density: 'comfortable',
      hover: true,
      elevation: 0, // 无阴影
      rounded: 'xl', // 大圆角
      itemsPerPage: 25,
      showCurrentPage: true
    },

    // MD3 徽章系统 - 符合MD3规范
    VBadge: {
      color: 'primary',
      location: 'top end',
      content: '',
      rounded: 'xl' // 更圆润的边角
    },

    // MD3 扩展面板系统 - 大圆角扁平化设计
    VExpansionPanels: {
      variant: 'accordion',
      color: 'primary',
      elevation: 0, // 无阴影
      rounded: 'xl' // 大圆角
    },
    VExpansionPanel: {
      elevation: 0, // 无阴影
      rounded: 'xl' // 大圆角
    },

    // MD3 图片系统 - 大圆角
    VImg: {
      rounded: 'xl' // 大圆角图片
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

    // MD3 步进器系统 - 大圆角扁平化设计
    VStepper: {
      elevation: 0, // 无阴影
      rounded: 'xl', // 大圆角
      variant: 'outlined' // 使用描边而非阴影
    },
    VStepperHeader: {
      elevation: 0 // 无阴影
    },
    VStepperItem: {
      color: 'primary'
    },

    // MD3 轮播图系统 - 大圆角扁平化设计
    VCarousel: {
      rounded: 'xl', // 大圆角
      showArrows: 'hover',
      hideDelimiters: false,
      cycle: false,
      elevation: 0 // 无阴影
    },
    VCarouselItem: {
      rounded: 'xl' // 大圆角
    },

    // MD3 横幅系统 - 大圆角扁平化设计
    VBanner: {
      rounded: 'xl', // 大圆角
      elevation: 0, // 无阴影
      variant: 'outlined' // 使用描边而非阴影
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

    // MD3 OTP输入系统 - 大圆角和更明显的边框
    VOtpInput: {
      variant: 'outlined',
      color: 'primary',
      density: 'comfortable',
      rounded: 'lg', // 大圆角OTP输入框
      baseColor: 'primary' // 使用primary颜色让边框更明显
    },

    // MD3 颜色选择器系统
    VColorPicker: {
      mode: 'hexa',
      showSwatches: true
    },

    // MD3 日期选择器系统 - 大圆角扁平化设计
    VDatePicker: {
      color: 'primary',
      elevation: 0, // 无阴影
      rounded: 'xl', // 大圆角
      variant: 'outlined' // 使用描边而非阴影
    },

    // MD3 时间选择器系统 - 大圆角扁平化设计
    VTimePicker: {
      color: 'primary',
      elevation: 0, // 无阴影
      rounded: 'xl', // 大圆角
      variant: 'outlined' // 使用描边而非阴影
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

    // MD3 悬浮操作按钮系统 - 扁平化设计，与整体风格一致
    VFab: {
      color: 'primary',
      size: 'default',
      elevation: 0, // 无阴影，与整体扁平化风格一致
      rounded: 'xl', // 大圆角
      variant: 'outlined' // 描边设计
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

    // MD3 时间线子组件系统 - 已在上方配置，移除重复

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
