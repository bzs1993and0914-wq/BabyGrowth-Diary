/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<
    Record<string, unknown>,
    Record<string, unknown>,
    unknown
  >
  export default component
}

interface Window {
  electronAPI?: {
    apiBaseUrl: string
    platform: string
    /** 主进程在每日例行提醒时派发（US3，时刻见 `DAILY_RECORD_NUDGE_HOUR`） */
    onDailyRecordNudge?: (callback: (message: string) => void) => void
  }
}
