<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { Plus, Clock, Star, TrendCharts, Sunny, Moon, Setting } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'

const router = useRouter()
const route = useRoute()
const settingsStore = useSettingsStore()

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

      <nav class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          :class="['nav-item', { active: isActive(item.name) }]"
        >
          <el-icon :size="16"><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Plus"
          round
          class="add-btn"
          @click="router.push('/record/new')"
        >
          添加记录
        </el-button>
        <el-tooltip :content="settingsStore.darkMode ? '切换亮色' : '切换暗色'" placement="bottom">
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
      </div>
    </div>
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
  transition: background-color 0.3s, border-color 0.3s;
}

.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
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
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s, background-color 0.2s;
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
}

.add-btn {
  flex-shrink: 0;
}
</style>
