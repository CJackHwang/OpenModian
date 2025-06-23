import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      // Vue性能优化
      reactivityTransform: true,
      template: {
        compilerOptions: {
          // 优化编译选项
          hoistStatic: true,
          cacheHandlers: true
        }
      }
    }),
    vuetify({
      autoImport: true,
      theme: {
        defaultTheme: 'light'
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3001,  // 避免与Docker等服务冲突
    host: true,
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://localhost:8080',
        changeOrigin: true,
        secure: false
      },
      '/socket.io': {
        target: process.env.BACKEND_URL || 'http://localhost:8080',
        changeOrigin: true,
        ws: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    target: 'esnext',
    minify: 'esbuild',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          vuetify: ['vuetify'],
          charts: ['chart.js', 'vue-chartjs'],
          utils: ['axios', 'dayjs', 'socket.io-client']
        },
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // 性能优化
    chunkSizeWarningLimit: 1000,
    reportCompressedSize: false
  },

  // 优化依赖预构建 - 最终解决方案
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'vuetify',
      'vuetify/components',
      'vuetify/directives',
      'axios',
      'dayjs',
      'dayjs/plugin/utc',
      'dayjs/plugin/timezone',
      'socket.io-client',
      'chart.js',
      'vue-chartjs'
    ],
    exclude: ['@vueuse/core'],
    // 强制在启动时预构建所有依赖
    force: true,
    // 扫描所有可能的入口点，确保所有组件都被发现
    entries: [
      'src/main.js',
      'src/App.vue',
      'src/views/**/*.vue',
      'src/components/**/*.vue'
    ]
  }
})
