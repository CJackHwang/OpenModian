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

// 创建Vuetify实例 - Material Design 3 配置
const vuetify = createVuetify({
  display: {
    mobileBreakpoint: 'sm',
    thresholds: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1264,
      xl: 1920,
      xxl: 2560
    }
  },
  theme: {
    defaultTheme: 'light',
    variations: {
      colors: ['primary', 'secondary', 'tertiary'],
      lighten: 5,
      darken: 5
    },
    themes: {
      light: {
        dark: false,
        colors: {
          // M3 Primary Colors
          primary: '#6750A4',
          'on-primary': '#FFFFFF',
          'primary-container': '#EADDFF',
          'on-primary-container': '#21005D',

          // M3 Secondary Colors
          secondary: '#625B71',
          'on-secondary': '#FFFFFF',
          'secondary-container': '#E8DEF8',
          'on-secondary-container': '#1D192B',

          // M3 Tertiary Colors
          tertiary: '#7D5260',
          'on-tertiary': '#FFFFFF',
          'tertiary-container': '#FFD8E4',
          'on-tertiary-container': '#31111D',

          // M3 Error Colors
          error: '#BA1A1A',
          'on-error': '#FFFFFF',
          'error-container': '#FFDAD6',
          'on-error-container': '#410002',

          // M3 Surface Colors
          background: '#FFFBFE',
          'on-background': '#1C1B1F',
          surface: '#FFFBFE',
          'on-surface': '#1C1B1F',
          'surface-variant': '#E7E0EC',
          'on-surface-variant': '#49454F',
          'surface-container-lowest': '#FFFFFF',
          'surface-container-low': '#F7F2FA',
          'surface-container': '#F3EDF7',
          'surface-container-high': '#ECE6F0',
          'surface-container-highest': '#E6E0E9',

          // M3 Outline Colors
          outline: '#79747E',
          'outline-variant': '#CAC4D0',

          // M3 Other Colors
          shadow: '#000000',
          scrim: '#000000',
          'inverse-surface': '#313033',
          'inverse-on-surface': '#F4EFF4',
          'inverse-primary': '#D0BCFF',

          // System Colors
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FF9800'
        }
      },
      dark: {
        dark: true,
        colors: {
          // M3 Primary Colors (Dark)
          primary: '#D0BCFF',
          'on-primary': '#381E72',
          'primary-container': '#4F378B',
          'on-primary-container': '#EADDFF',

          // M3 Secondary Colors (Dark)
          secondary: '#CCC2DC',
          'on-secondary': '#332D41',
          'secondary-container': '#4A4458',
          'on-secondary-container': '#E8DEF8',

          // M3 Tertiary Colors (Dark)
          tertiary: '#EFB8C8',
          'on-tertiary': '#492532',
          'tertiary-container': '#633B48',
          'on-tertiary-container': '#FFD8E4',

          // M3 Error Colors (Dark)
          error: '#FFB4AB',
          'on-error': '#690005',
          'error-container': '#93000A',
          'on-error-container': '#FFDAD6',

          // M3 Surface Colors (Dark)
          background: '#10131C',
          'on-background': '#E6E1E5',
          surface: '#10131C',
          'on-surface': '#E6E1E5',
          'surface-variant': '#49454F',
          'on-surface-variant': '#CAC4D0',
          'surface-container-lowest': '#0B0E17',
          'surface-container-low': '#1D1B20',
          'surface-container': '#211F26',
          'surface-container-high': '#2B2930',
          'surface-container-highest': '#36343B',

          // M3 Outline Colors (Dark)
          outline: '#938F99',
          'outline-variant': '#49454F',

          // M3 Other Colors (Dark)
          shadow: '#000000',
          scrim: '#000000',
          'inverse-surface': '#E6E1E5',
          'inverse-on-surface': '#313033',
          'inverse-primary': '#6750A4',

          // System Colors (Dark)
          info: '#64B5F6',
          success: '#81C784',
          warning: '#FFB74D'
        }
      }
    }
  },
  defaults: {
    VCard: {
      elevation: 2,
      rounded: 'lg'
    },
    VBtn: {
      rounded: 'xl',
      style: 'text-transform: none; font-weight: 500;'
    },
    VChip: {
      rounded: 'lg'
    },
    VTextField: {
      rounded: 'lg',
      variant: 'outlined'
    },
    VSelect: {
      rounded: 'lg',
      variant: 'outlined'
    },
    VDialog: {
      VCard: {
        rounded: 'xxl'
      }
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  }
})

// 初始化应用
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')
