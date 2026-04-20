<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Plus, Sunny, Moon, Setting, User, MoreFilled } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import { useMediaQuery } from '@/composables/useMediaQuery'

const router = useRouter()
const route = useRoute()
const settingsStore = useSettingsStore()
const auth = useAuthStore()

const isCompactNav = useMediaQuery('(max-width: 767px)')
const mobileMenuOpen = ref(false)

const APP_SCROLL_LOCK_CLASS = 'app-scroll-lock'
let scrollYBeforeAppLock = 0

function setAppScrollLock(locked: boolean) {
  const app = document.getElementById('app')
  if (!app) return
  if (locked) {
    scrollYBeforeAppLock = window.scrollY || document.documentElement.scrollTop
    app.style.top = `-${scrollYBeforeAppLock}px`
    app.classList.add(APP_SCROLL_LOCK_CLASS)
  } else {
    app.classList.remove(APP_SCROLL_LOCK_CLASS)
    app.style.top = ''
    window.scrollTo(0, scrollYBeforeAppLock)
  }
}

onUnmounted(() => {
  setAppScrollLock(false)
})

watch(
  () => route.fullPath,
  () => { mobileMenuOpen.value = false },
)

watch(mobileMenuOpen, (open) => {
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
  mobileMenuOpen.value = false
  router.push('/settings')
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="brand" @click="router.push('/')">
        <span class="brand-icon">👶</span>
        <span class="brand-title">BabyGrow</span>
      </div>

      <div class="header-fill" />

      <div class="header-actions">
        <span v-if="auth.user && !isCompactNav" class="user-chip" :title="auth.user.username">
          <el-icon><User /></el-icon>
          <span class="user-name">{{ auth.user.username }}</span>
          <el-tag
            v-if="auth.user.account_tier === 'vip'"
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
          <el-button
            v-if="auth.isAuthenticated"
            text
            type="danger"
            @click="logout"
          >
            退出
          </el-button>
        </template>

        <el-button
          v-if="isCompactNav"
          class="more-trigger"
          text
          circle
          aria-label="更多选项"
          @click="mobileMenuOpen = true"
        >
          <el-icon :size="20"><MoreFilled /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Mobile bottom sheet: settings & account only -->
    <el-drawer
      v-model="mobileMenuOpen"
      direction="btt"
      size="min(50vh, 340px)"
      title="更多"
      append-to-body
      class="babygrow-mobile-sheet"
      :lock-scroll="false"
    >
      <div class="sheet-handle" aria-hidden="true" />

      <div v-if="auth.user" class="sheet-user-row">
        <el-icon :size="18"><User /></el-icon>
        <span class="sheet-user-name">{{ auth.user.username }}</span>
        <el-tag
          v-if="auth.user.account_tier === 'vip'"
          size="small"
          type="warning"
        >
          VIP
        </el-tag>
      </div>

      <div class="sheet-divider" role="separator" />

      <div class="sheet-row">
        <span class="sheet-row-label">深色模式</span>
        <el-switch
          :model-value="settingsStore.darkMode"
          aria-label="切换深色模式"
          @change="onSheetDarkChange"
        />
      </div>

      <button
        type="button"
        class="sheet-action-item"
        @click="openSettingsFromSheet"
      >
        <el-icon :size="18"><Setting /></el-icon>
        <span>设置</span>
      </button>

      <el-button
        v-if="auth.isAuthenticated"
        class="sheet-logout"
        text
        type="danger"
        @click="logout"
      >
        退出登录
      </el-button>
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
  height: var(--header-height, 60px);
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  transition:
    background-color 0.3s;
}

.header-inner {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
  flex-wrap: nowrap;
  min-width: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex-shrink: 0;
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
}

.header-fill {
  flex: 1;
  min-width: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
  flex-wrap: nowrap;
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

.more-trigger {
  flex-shrink: 0;
}

/* ─── Mobile ─────────────────────────────────── */
@media (max-width: 767px) {
  .app-header {
    height: var(--header-height-mobile, 54px);
  }

  .header-inner {
    padding: 0 14px;
    gap: 8px;
  }

  .brand-title {
    font-size: 16px;
  }

  .brand-icon {
    font-size: 22px;
  }

  .header-actions {
    gap: 6px;
  }

  .header-actions :deep(.el-button.is-circle) {
    padding: 7px;
  }
}

/* ─── Bottom sheet content ────────────────────── */
.sheet-handle {
  width: 40px;
  height: 5px;
  border-radius: 3px;
  background: var(--el-border-color, #dcdfe6);
  margin: -4px auto 10px;
  opacity: 0.85;
}

.sheet-user-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px 12px;
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 500;
}

.sheet-user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sheet-divider {
  height: 1px;
  background: var(--border-color);
  margin: 4px 0 8px;
}

.sheet-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 10px;
  gap: 12px;
}

.sheet-row-label {
  font-size: 15px;
  color: var(--text-primary);
}

.sheet-action-item {
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

.sheet-action-item:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.sheet-logout {
  margin-top: 8px;
  width: 100%;
}
</style>

<style>
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
