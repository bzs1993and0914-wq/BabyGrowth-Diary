import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './themes/variables.css'
import 'element-plus/dist/index.css'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// 先初始化认证状态（尝试用本地缓存 Token 刷新用户信息），
// 确保路由守卫在 auth.initialized 为 true 后才做重定向判断，
// 避免登录页面闪烁。
const auth = useAuthStore()
auth.init().finally(() => {
  app.use(router)
  app.use(ElementPlus, { locale: zhCn })

  // 批量注册所有 Element Plus 图标为全局组件，模板中可直接使用 <IconName /> 调用
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.mount('#app')
})
