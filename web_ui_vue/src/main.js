import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Quasar, Notify, Dialog, Loading } from 'quasar'
import router from './router'
import App from './App.vue'

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/material-icons-outlined/material-icons-outlined.css'
import '@quasar/extras/material-icons-round/material-icons-round.css'
import '@quasar/extras/material-icons-sharp/material-icons-sharp.css'

// Import Quasar css
import 'quasar/src/css/index.sass'

// Custom styles
import './styles/main.scss'

// 初始化应用
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.use(Quasar, {
  plugins: {
    Notify,
    Dialog,
    Loading
  },
  config: {
    brand: {
      primary: '#6750A4',
      secondary: '#625B71',
      accent: '#7D5260',
      dark: '#1C1B1F',
      'dark-page': '#10131C',
      positive: '#4CAF50',
      negative: '#BA1A1A',
      info: '#2196F3',
      warning: '#FF9800'
    }
  }
})

app.mount('#app')
