import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { hideHeader: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { hideHeader: true },
    },
    {
      path: '/',
      name: 'timeline',
      component: () => import('@/views/TimelineView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/record/new',
      name: 'record-new',
      component: () => import('@/views/RecordEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/record/:date/edit',
      name: 'record-edit',
      component: () => import('@/views/RecordEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/record/:date',
      name: 'record-detail',
      component: () => import('@/views/RecordDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/milestones',
      name: 'milestones',
      component: () => import('@/views/MilestoneView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/growth',
      name: 'growth',
      component: () => import('@/views/GrowthCurveView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

/**
 * 全局路由守卫：
 * 1. 确保 auth store 已初始化（防止首屏刷新时状态丢失）
 * 2. 需鉴权页面：未登录时重定向到登录页，并携带原目标路径便于登录后回跳
 * 3. 已登录用户：访问登录/注册页时自动重定向到首页
 */
router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized) {
    await auth.init()
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (auth.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    return '/'
  }
  return true
})

export default router
