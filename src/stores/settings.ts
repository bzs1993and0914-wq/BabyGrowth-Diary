import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSettings, updateSettings } from '@/api/settings'
import type { SettingsResponse, SettingsUpdate } from '@/types/api'
import type { ThemeName } from '@/types/models'

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref<ThemeName>('default')
  const darkMode = ref(false)
  const thumbnailMaxSize = ref(400)
  const thumbnailQuality = ref(85)
  const loaded = ref(false)

  function applyTheme() {
    const root = document.documentElement
    root.setAttribute('data-theme', theme.value)
    root.classList.toggle('dark', darkMode.value)
  }

  function applyFromResponse(s: SettingsResponse) {
    theme.value = s.theme as ThemeName
    darkMode.value = s.dark_mode
    thumbnailMaxSize.value = s.thumbnail_max_size
    thumbnailQuality.value = s.thumbnail_quality
  }

  async function fetchSettings() {
    const s = (await getSettings()).data
    applyFromResponse(s)
    loaded.value = true
    applyTheme()
  }

  // Alias for backward compatibility
  const load = fetchSettings

  async function update(data: SettingsUpdate) {
    const s = (await updateSettings(data)).data
    applyFromResponse(s)
    applyTheme()
  }

  async function toggleDarkMode() {
    await update({ dark_mode: !darkMode.value })
  }

  return {
    theme,
    darkMode,
    thumbnailMaxSize,
    thumbnailQuality,
    loaded,
    load,
    fetchSettings,
    update,
    applyTheme,
    toggleDarkMode,
  }
})
