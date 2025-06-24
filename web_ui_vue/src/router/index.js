import { createRouter, createWebHistory } from "vue-router";

// 路由懒加载优化
const lazyLoad = (view) => () => import(`@/views/${view}.vue`);

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // 滚动行为优化
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: "smooth",
      };
    } else {
      return { top: 0, behavior: "smooth" };
    }
  },
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: lazyLoad("Dashboard"),
      meta: {
        title: "仪表板",
        icon: "mdi-view-dashboard",
        requiresAuth: false,
        keepAlive: true,
      },
    },
    {
      path: "/spider",
      name: "spider",
      component: lazyLoad("SpiderControl"),
      meta: {
        title: "爬虫控制",
        icon: "mdi-spider",
        requiresAuth: false,
        keepAlive: false,
      },
    },
    {
      path: "/data",
      name: "data",
      component: lazyLoad("DataManagement"),
      meta: {
        title: "数据管理",
        icon: "mdi-database",
        requiresAuth: false,
        keepAlive: true,
      },
    },
    {
      path: "/data/advanced",
      name: "advanced-data",
      component: lazyLoad("AdvancedDataManagement"),
      meta: {
        title: "高级数据管理",
        icon: "mdi-database-edit",
        requiresAuth: false,
        keepAlive: true,
      },
    },
    {
      path: "/projects/:id",
      name: "project-detail",
      component: lazyLoad("ProjectDetail"),
      meta: {
        title: "项目详情",
        icon: "mdi-file-document",
        requiresAuth: false,
        keepAlive: false,
      },
    },
    {
      path: "/tasks",
      name: "tasks",
      component: lazyLoad("TaskManagement"),
      meta: {
        title: "任务管理",
        icon: "mdi-format-list-bulleted",
        requiresAuth: false,
        keepAlive: true,
      },
    },
    {
      path: "/history",
      name: "history",
      component: lazyLoad("TaskHistory"),
      meta: {
        title: "任务历史",
        icon: "mdi-history",
        requiresAuth: false,
        keepAlive: true,
      },
    },
    {
      path: "/logs",
      name: "logs",
      component: lazyLoad("LogViewer"),
      meta: {
        title: "实时日志",
        icon: "mdi-console-line",
        requiresAuth: false,
        keepAlive: false,
      },
    },
    {
      path: "/settings",
      name: "settings",
      component: lazyLoad("Settings"),
      meta: {
        title: "系统设置",
        icon: "mdi-cog",
        requiresAuth: false,
        keepAlive: true,
      },
    },

    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: lazyLoad("NotFound"),
      meta: {
        title: "页面未找到",
        icon: "mdi-alert-circle",
        requiresAuth: false,
        keepAlive: false,
      },
    },
  ],
});

// 路由守卫优化
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 摩点爬虫管理系统`;
  }

  // 权限检查（如果需要）
  if (to.meta.requiresAuth) {
    // 这里可以添加认证逻辑
    // const isAuthenticated = await checkAuth()
    // if (!isAuthenticated) {
    //   return next('/login')
    // }
  }

  // 页面加载进度指示
  if (to.name !== from.name) {
    // 可以在这里显示加载指示器
    console.log(`导航到: ${to.meta.title}`);
  }

  next();
});

// 路由后置守卫
router.afterEach((to, from) => {
  // 页面访问统计
  if (typeof window !== "undefined" && typeof window.gtag !== "undefined") {
    window.gtag("config", "GA_MEASUREMENT_ID", {
      page_title: to.meta.title,
      page_location: to.fullPath,
    });
  }

  // 滚动到顶部（如果不是同一页面）
  if (to.name !== from.name) {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

export default router;
