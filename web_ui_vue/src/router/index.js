import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: {
        title: '仪表板'
      }
    },
    {
      path: '/spider',
      name: 'spider',
      component: () => import('@/views/SpiderControl.vue'),
      meta: {
        title: '爬虫控制'
      }
    },
    {
      path: '/data',
      name: 'data',
      component: () => import('@/views/DataManagement.vue'),
      meta: {
        title: '数据管理'
      }
    },
    {
      path: '/data/advanced',
      name: 'advanced-data',
      component: () => import('@/views/AdvancedDataManagement.vue'),
      meta: {
        title: '高级数据管理'
      }
    },
    {
      path: '/projects/:id',
      name: 'project-detail',
      component: () => import('@/views/ProjectDetail.vue'),
      meta: {
        title: '项目详情'
      }
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('@/views/TaskManagement.vue'),
      meta: {
        title: '任务管理'
      }
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/TaskHistory.vue'),
      meta: {
        title: '任务历史'
      }
    },
    {
      path: '/logs',
      name: 'logs',
      component: () => import('@/views/LogViewer.vue'),
      meta: {
        title: '实时日志'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/Settings.vue'),
      meta: {
        title: '系统设置'
      }
    },
    {
      path: '/test',
      name: 'component-test',
      component: () => import('@/views/ComponentTest.vue'),
      meta: {
        title: '组件测试'
      }
    },
    {
      path: '/button-test',
      name: 'button-test',
      component: () => import('@/views/ButtonTest.vue'),
      meta: {
        title: '按钮测试'
      }
    },
    {
      path: '/md3-test',
      name: 'md3-test',
      component: () => import('@/views/MD3Test.vue'),
      meta: {
        title: 'MD3设计测试'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue'),
      meta: {
        title: '页面未找到'
      }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 摩点爬虫管理系统`
  }
  next()
})

export default router
