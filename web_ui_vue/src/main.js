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

// 创建Vuetify实例
const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#6750A4',
          secondary: '#625B71',
          accent: '#7D5260',
          error: '#BA1A1A',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FF9800',
          surface: '#FFFBFE',
          'surface-variant': '#E7E0EC',
          'on-surface': '#1C1B1F',
          'on-surface-variant': '#49454F',
          'primary-container': '#EADDFF',
          'on-primary-container': '#21005D',
          'secondary-container': '#E8DEF8',
          'on-secondary-container': '#1D192B',
          'tertiary-container': '#FFD8E4',
          'on-tertiary-container': '#31111D'
        }
      },
      dark: {
        colors: {
          primary: '#D0BCFF',
          secondary: '#CCC2DC',
          accent: '#EFB8C8',
          error: '#FFB4AB',
          info: '#64B5F6',
          success: '#81C784',
          warning: '#FFB74D',
          surface: '#10131C',
          'surface-variant': '#49454F',
          'on-surface': '#E6E1E5',
          'on-surface-variant': '#CAC4D0'
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
  }
})

// 初始化应用
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')
