import { ref } from 'vue'

// 全局状态
const snackbar = ref({
  show: false,
  message: '',
  color: 'info',
  timeout: 4000
})

export function useSnackbar() {
  const showSnackbar = (message, color = 'info', timeout = 4000) => {
    snackbar.value = {
      show: true,
      message,
      color,
      timeout
    }
  }

  const hideSnackbar = () => {
    snackbar.value.show = false
  }

  return {
    snackbar,
    showSnackbar,
    hideSnackbar
  }
}
