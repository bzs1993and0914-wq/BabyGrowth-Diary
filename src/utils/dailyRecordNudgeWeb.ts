import { ElNotification } from 'element-plus'
import { DAILY_RECORD_NUDGE_HOUR } from '@/constants/dailyRecordNudge'

const LS_KEY = 'babygrow-last-daily-nudge-date'

function localDateKey(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/**
 * 纯浏览器（如 `vite` 无 Electron）下的 US3：本地 10:00 至多一次 Element通知。
 * Electron 内由主进程调度，此处跳过以免重复。
 */
export function startWebDailyRecordNudge(): void {
  if (typeof window === 'undefined') return
  if (window.electronAPI) return

  const tick = (): void => {
    const now = new Date()
    if (now.getHours() !== DAILY_RECORD_NUDGE_HOUR) return
    const key = localDateKey(now)
    try {
      if (localStorage.getItem(LS_KEY) === key) return
      localStorage.setItem(LS_KEY, key)
    } catch {
      return
    }
    ElNotification({
      title: 'BabyGrow',
      message: '该给宝宝创建新的记录啦',
      type: 'info',
      duration: 10_000,
    })
  }

  tick()
  setInterval(tick, 60_000)
}
