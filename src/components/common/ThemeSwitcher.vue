<script setup lang="ts">
import { computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import type { ThemeName } from '@/types/models'

const settings = useSettingsStore()

const themes: { name: ThemeName; label: string; color: string }[] = [
  { name: 'default', label: '简约白', color: '#409eff' },
  { name: 'warm', label: '暖阳橙', color: '#f0883e' },
  { name: 'night', label: '夜空蓝', color: '#6c8cff' },
]

const selectedTheme = computed(() => settings.theme)

async function selectTheme(name: ThemeName) {
  await settings.update({ theme: name })
}

async function toggleDark(val: boolean) {
  await settings.update({ dark_mode: val })
}
</script>

<template>
  <div class="theme-switcher">
    <h4 class="section-label">主题风格</h4>
    <div class="theme-options">
      <div
        v-for="t in themes"
        :key="t.name"
        :class="['theme-swatch', { active: selectedTheme === t.name }]"
        @click="selectTheme(t.name)"
      >
        <span class="swatch-circle" :style="{ background: t.color }" />
        <span class="swatch-label">{{ t.label }}</span>
      </div>
    </div>

    <div class="dark-toggle">
      <span class="dark-label">深色模式</span>
      <el-switch
        :model-value="settings.darkMode"
        @change="toggleDark($event as boolean)"
      />
    </div>
  </div>
</template>

<style scoped>
.theme-switcher {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-options {
  display: flex;
  gap: 16px;
}

.theme-swatch {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-secondary);
}

.theme-swatch:hover {
  border-color: var(--border-color);
}

.theme-swatch.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.swatch-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.swatch-label {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.dark-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 1px solid var(--border-color);
}

.dark-label {
  font-size: 14px;
  color: var(--text-primary);
}
</style>
