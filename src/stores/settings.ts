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

  /** 将当前主题和暗色模式应用到 document.documentElement，驱动 CSS 变量切换。 */
  function applyTheme() {
    const root = document.documentElement
    root.setAttribute('data-theme', theme.value)
    root.classList.toggle('dark', darkMode.value)
  }

  /** 将接口返回的设置对象同步到 store 各响应式变量。 */
  function applyFromResponse(s: SettingsResponse) {
    theme.value = s.theme as ThemeName
    darkMode.value = s.dark_mode
    thumbnailMaxSize.value = s.thumbnail_max_size
    thumbnailQuality.value = s.thumbnail_quality
  }

  /** 从后端拉取最新设置，写入 store 并立即应用主题。 */
  async function fetchSettings() {
    const s = (await getSettings()).data
    applyFromResponse(s)
    loaded.value = true
    applyTheme()
  }

  // 向后兼容的别名，组件中可使用 store.load() 代替 store.fetchSettings()
  const load = fetchSettings

  /** 提交设置变更，后端返回全量最新设置后更新 store 并重新应用主题。 */
  async function update(data: SettingsUpdate) {
    const s = (await updateSettings(data)).data
    applyFromResponse(s)
    applyTheme()
  }

  /** 切换暗色/亮色模式，等同于 update({ dark_mode: !darkMode }) 的便捷方法。 */
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
