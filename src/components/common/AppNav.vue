<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { NavLinkItem, NavGroupItem } from '@/types/nav'
import { isNavGroup } from '@/types/nav'
import { navItems } from '@/config/nav'

const emit = defineEmits<{
  (e: 'navigate', path: string): void
}>()

const router = useRouter()
const route = useRoute()

interface FlatNavItem {
  label: string
  path: string
  name: string
  icon?: NavLinkItem['icon']
}

const flatItems = computed<FlatNavItem[]>(() => {
  const result: FlatNavItem[] = []
  for (const item of navItems) {
    if (isNavGroup(item)) {
      for (const child of (item as NavGroupItem).children) {
        result.push(child)
      }
    } else {
      result.push(item as NavLinkItem)
    }
  }
  return result
})

function isActive(name: string) {
  return route.name === name
}

function navHref(path: string) {
  return router.resolve({ path }).href
}

function goNav(e: MouseEvent, path: string) {
  if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return
  e.preventDefault()
  emit('navigate', path)
  void router.push(path)
}
</script>

<template>
  <nav class="app-tab-bar" aria-label="主导航">
    <div class="tab-bar-track">
      <a
        v-for="item in flatItems"
        :key="item.name"
        :href="navHref(item.path)"
        :class="['tab-item', { active: isActive(item.name) }]"
        :aria-current="isActive(item.name) ? 'page' : undefined"
        @click="goNav($event, item.path)"
      >
        <el-icon v-if="item.icon" class="tab-icon"><component :is="item.icon" /></el-icon>
        <span class="tab-label">{{ item.label }}</span>
      </a>
    </div>
  </nav>
</template>

<style scoped>
.app-tab-bar {
  position: sticky;
  top: var(--header-height, 60px);
  z-index: 95;
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 1px 3px var(--shadow-color);
  transition:
    background-color 0.3s,
    box-shadow 0.3s;
}

.tab-bar-track {
  display: flex;
  align-items: stretch;
  gap: 4px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}

.tab-bar-track::-webkit-scrollbar {
  display: none;
}

.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 12px 18px;
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
  flex-shrink: 0;
  transition:
    color 0.2s,
    background-color 0.2s;
}

.tab-item:hover {
  color: var(--text-primary);
}

.tab-item.active {
  color: var(--color-primary);
  font-weight: 600;
}

.tab-icon {
  font-size: 17px;
}

.tab-label {
  position: relative;
  padding-bottom: 2px;
}

.tab-label::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  width: 0;
  height: 2.5px;
  background: var(--color-primary);
  border-radius: 2px 2px 0 0;
  transform: translateX(-50%);
  transition:
    width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-item:hover .tab-label::after {
  width: 60%;
}

.tab-item.active .tab-label::after {
  width: 80%;
}

@media (max-width: 767px) {
  .app-tab-bar {
    top: var(--header-height-mobile, 54px);
  }

  .tab-bar-track {
    padding: 0 8px;
    gap: 0;
  }

  .tab-item {
    padding: 10px 14px;
    font-size: 13px;
    gap: 5px;
  }

  .tab-icon {
    font-size: 16px;
  }
}
</style>
