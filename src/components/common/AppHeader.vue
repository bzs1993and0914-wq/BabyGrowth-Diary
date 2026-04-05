<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Plus,
  Clock,
  Star,
  TrendCharts,
  Sunny,
  Moon,
  Setting,
  User,
  Menu,
} from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const settingsStore = useSettingsStore()
const auth = useAuthStore()

/** ≤767px：主导航收入抽屉，避免中文逐字折行 */
const COMPACT_NAV_MQ = '(max-width: 767px)'
const isCompactNav = ref(false)
const mobileNavOpen = ref(false)
let compactMq: MediaQueryList | undefined

/** 与 variables.css 中 #app.app-scroll-lock 对应；避免使用 EP lockScroll 改写 body 宽度 */
const APP_SCROLL_LOCK_CLASS = 'app-scroll-lock'
let scrollYBeforeAppLock = 0

function setAppScrollLock(locked: boolean) {
  const app = document.getElementById('app')
  if (!app) return
  if (locked) {
    scrollYBeforeAppLock = window.scrollY || document.documentElement.scrollTop
    /* fixed + 负 top 保持当前可视区域，避免仅靠 overflow/100vh 把文档压短导致 scroll 归零跳到顶栏 */
    app.style.top = `-${scrollYBeforeAppLock}px`
    app.classList.add(APP_SCROLL_LOCK_CLASS)
  } else {
    app.classList.remove(APP_SCROLL_LOCK_CLASS)
    app.style.top = ''
    window.scrollTo(0, scrollYBeforeAppLock)
  }
}

function syncCompactNav(ev?: MediaQueryListEvent) {
  isCompactNav.value = ev?.matches ?? compactMq?.matches ?? false
}

onMounted(() => {
  compactMq = window.matchMedia(COMPACT_NAV_MQ)
  syncCompactNav()
  compactMq.addEventListener('change', syncCompactNav)
})

onUnmounted(() => {
  setAppScrollLock(false)
  compactMq?.removeEventListener('change', syncCompactNav)
})

watch(
  () => route.fullPath,
  () => {
    mobileNavOpen.value = false
  }
)

watch(mobileNavOpen, (open) => {
  setAppScrollLock(open)
})

async function logout() {
  try {
    await ElMessageBox.confirm('确定退出当前账号？', '退出登录', {
      type: 'warning',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
    })
    auth.logout()
    router.push('/login')
  } catch {
    /* cancel */
  }
}

function onSheetDarkChange() {
  void settingsStore.toggleDarkMode()
}

function openSettingsFromSheet() {
  mobileNavOpen.value = false
  router.push('/settings')
}

const navItems = [
  { label: '时间轴', path: '/', name: 'timeline', icon: Clock },
  { label: '里程碑', path: '/milestones', name: 'milestones', icon: Star },
  { label: '成长曲线', path: '/growth', name: 'growth', icon: TrendCharts },
]

function isActive(name: string) {
  return route.name === name
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="brand" @click="router.push('/')">
        <span class="brand-icon">👶</span>
        <span class="brand-title">BabyGrow</span>
      </div>

      <nav v-if="!isCompactNav" class="nav-links" aria-label="主导航">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          :class="['nav-item', { active: isActive(item.name) }]"
        >
          <el-icon :size="16"><component :is="item.icon" /></el-icon>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>
      <div v-else class="header-fill" aria-hidden="true" />

      <el-tooltip v-if="isCompactNav" content="打开菜单" placement="bottom">
        <el-button
          class="nav-menu-trigger"
          text
          circle
          aria-label="打开导航菜单"
          @click="mobileNavOpen = true"
        >
          <el-icon :size="22"><Menu /></el-icon>
        </el-button>
      </el-tooltip>

      <div class="header-actions">
        <span v-if="auth.user" class="user-chip" :title="auth.user.username">
          <el-icon><User /></el-icon>
          <span v-if="!isCompactNav" class="user-name">{{
            auth.user.username
          }}</span>
          <el-tag
            v-if="!isCompactNav && auth.user.account_tier === 'vip'"
            size="small"
            type="warning"
          >
            VIP
          </el-tag>
        </span>
        <el-tooltip
          v-if="auth.isAuthenticated && isCompactNav"
          content="添加记录"
          placement="bottom"
        >
          <el-button
            type="primary"
            :icon="Plus"
            circle
            class="add-btn"
            @click="router.push('/record/new')"
          />
        </el-tooltip>
        <el-button
          v-else-if="auth.isAuthenticated"
          type="primary"
          :icon="Plus"
          round
          class="add-btn"
          @click="router.push('/record/new')"
        >
          添加记录
        </el-button>
        <el-button
          v-if="auth.isAuthenticated && !isCompactNav"
          text
          type="danger"
          @click="logout"
        >
          退出
        </el-button>
        <el-button
          v-if="!auth.isAuthenticated"
          type="primary"
          text
          @click="router.push('/login')"
        >
          登录
        </el-button>
        <template v-if="!isCompactNav">
          <el-tooltip
            :content="settingsStore.darkMode ? '切换亮色' : '切换暗色'"
            placement="bottom"
          >
            <el-button circle @click="settingsStore.toggleDarkMode">
              <el-icon>
                <Sunny v-if="settingsStore.darkMode" />
                <Moon v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="设置" placement="bottom">
            <el-button circle @click="router.push('/settings')">
              <el-icon><Setting /></el-icon>
            </el-button>
          </el-tooltip>
        </template>
      </div>
    </div>

    <el-drawer
      v-model="mobileNavOpen"
      direction="btt"
      size="min(78vh, 520px)"
      title="菜单"
      append-to-body
      class="babygrow-mobile-sheet"
      :lock-scroll="false"
    >
      <div class="sheet-handle" aria-hidden="true" />
      <nav class="mobile-nav" aria-label="主导航">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          :class="['mobile-nav-item', { active: isActive(item.name) }]"
        >
          <el-icon :size="18"><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
        <el-button
          v-if="auth.isAuthenticated"
          type="primary"
          class="mobile-nav-record"
          :icon="Plus"
          @click="router.push('/record/new')"
        >
          添加记录
        </el-button>
        <div class="mobile-sheet-divider" role="separator" />
        <div class="mobile-sheet-row">
          <span class="mobile-sheet-row-label">深色模式</span>
          <el-switch
            :model-value="settingsStore.darkMode"
            aria-label="切换深色模式"
            @change="onSheetDarkChange"
          />
        </div>
        <button
          type="button"
          class="mobile-nav-item mobile-nav-item--button"
          @click="openSettingsFromSheet"
        >
          <el-icon :size="18"><Setting /></el-icon>
          <span>设置</span>
        </button>
        <el-button
          v-if="auth.isAuthenticated"
          class="mobile-nav-logout"
          text
          type="danger"
          @click="logout"
        >
          退出登录
        </el-button>
      </nav>
    </el-drawer>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 60px;
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(12px);
  transition:
    background-color 0.3s,
    border-color 0.3s;
}

.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
  flex-wrap: nowrap;
  min-width: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex-shrink: 1;
  min-width: 0;
}

.brand-icon {
  font-size: 24px;
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
  min-width: 0;
  flex-wrap: nowrap;
  align-items: center;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scrollbar-width: none;
}

.nav-links::-webkit-scrollbar {
  display: none;
}

.header-fill {
  flex: 1;
  min-width: 0;
}

.nav-menu-trigger {
  flex-shrink: 0;
}

.nav-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  transition:
    color 0.2s,
    background-color 0.2s;
  flex-shrink: 0;
  white-space: nowrap;
}

.nav-label {
  white-space: nowrap;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.nav-item.active {
  color: var(--color-primary);
  background: var(--color-primary-light);
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
  flex-wrap: nowrap;
}

@media (max-width: 767px) {
  .header-inner {
    padding: 0 12px;
    gap: 6px;
  }

  .brand-title {
    font-size: 16px;
    max-width: 28vw;
  }

  .header-actions {
    gap: 4px;
  }

  .header-actions :deep(.el-button.is-circle) {
    padding: 8px;
  }
}

.add-btn {
  flex-shrink: 0;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 140px;
}

.user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 15px;
  color: var(--text-secondary);
  text-decoration: none;
  transition:
    color 0.2s,
    background-color 0.2s;
}

.mobile-nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.mobile-nav-item.active {
  color: var(--color-primary);
  background: var(--color-primary-light);
  font-weight: 600;
}

.mobile-nav-record {
  justify-content: center;
  margin-top: 12px;
  width: 100%;
}

.mobile-nav-logout {
  margin-top: 8px;
  width: 100%;
}

.sheet-handle {
  width: 40px;
  height: 5px;
  border-radius: 3px;
  background: var(--el-border-color, #dcdfe6);
  margin: -4px auto 10px;
  opacity: 0.85;
}

.mobile-sheet-divider {
  height: 1px;
  background: var(--border-color);
  margin: 12px 0 8px;
}

.mobile-sheet-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 10px;
  gap: 12px;
}

.mobile-sheet-row-label {
  font-size: 15px;
  color: var(--text-primary);
}

.mobile-nav-item--button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-family: inherit;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  text-align: left;
  transition:
    color 0.2s,
    background-color 0.2s;
}

.mobile-nav-item--button:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}
</style>

<style>
/**
 * 底部抽屉 teleport 到 body，scoped 选择器无法命中面板节点
 */
.babygrow-mobile-sheet.el-drawer {
  border-radius: 18px 18px 0 0;
  box-shadow: 0 -12px 40px rgba(15, 23, 42, 0.12);
}

.babygrow-mobile-sheet.el-drawer .el-drawer__header {
  margin-bottom: 4px;
  padding: 12px 20px 8px;
}

.babygrow-mobile-sheet.el-drawer .el-drawer__body {
  padding-top: 0;
  padding-bottom: max(20px, env(safe-area-inset-bottom, 0px));
}
</style>
