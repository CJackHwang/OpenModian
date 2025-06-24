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

  // 优化依赖预构建 - 禁用动态构建，实现一次性完整构建
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
    // 禁用强制重新构建，避免页面导航时重载
    force: false,
    // 移除动态扫描，避免触发重新构建
    entries: ['src/main.js']
  },

  // 开发服务器优化 - 减少热重载触发
  server: {
    port: 3001,
    host: true,
    // 禁用文件系统监听优化，减少不必要的重载
    watch: {
      ignored: ['**/node_modules/**', '**/dist/**']
    },
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
  }
})
