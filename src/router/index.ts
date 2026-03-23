import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'timeline',
      component: () => import('@/views/TimelineView.vue'),
    },
    {
      path: '/record/new',
      name: 'record-new',
      component: () => import('@/views/RecordEditView.vue'),
    },
    {
      path: '/record/:date/edit',
      name: 'record-edit',
      component: () => import('@/views/RecordEditView.vue'),
    },
    {
      path: '/record/:date',
      name: 'record-detail',
      component: () => import('@/views/RecordDetailView.vue'),
    },
    {
      path: '/milestones',
      name: 'milestones',
      component: () => import('@/views/MilestoneView.vue'),
    },
    {
      path: '/growth',
      name: 'growth',
      component: () => import('@/views/GrowthCurveView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
    },
  ],
})

export default router
