import { onUnmounted, watch } from 'vue'
import { ElNotification } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { hasRecordForDate } from '@/api/records'
import { DAILY_RECORD_NUDGE_HOUR } from '@/constants/dailyRecordNudge'

const NUDGE_MESSAGE = '该给宝宝创建新的记录啦'

function localDateKey(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** 当日已处理过「无需再提醒」或「已弹出」则跳过，避免每分钟打接口 */
function handledStorageKey(dateKey: string): string {
  return `babygrow-daily-nudge-handled-${dateKey}`
}

function markHandled(dateKey: string): void {
  try {
    localStorage.setItem(handledStorageKey(dateKey), '1')
  } catch {
    /* ignore */
  }
}

function isHandled(dateKey: string): boolean {
  try {
    return localStorage.getItem(handledStorageKey(dateKey)) === '1'
  } catch {
    return false
  }
}

/**
 * US3：每个自然日上午 10:00 起至多提示一次；仅当当日尚无记录时提示。
 * 10:00 之后才打开应用时，首次满足条件时补提示（避免错过准点）。
 */
export function useDailyRecordNudge(): void {
  const auth = useAuthStore()
  let timer: ReturnType<typeof setInterval> | null = null

  const tick = async (): Promise<void> => {
    if (!auth.isAuthenticated) return

    const now = new Date()
    if (now.getHours() < DAILY_RECORD_NUDGE_HOUR) return

    const dateKey = localDateKey(now)
    if (isHandled(dateKey)) return

    try {
      if (await hasRecordForDate(dateKey)) {
        markHandled(dateKey)
        return
      }
    } catch {
      return
    }

    markHandled(dateKey)

    ElNotification({
      title: 'BabyGrow',
      message: NUDGE_MESSAGE,
      type: 'info',
      duration: 10_000,
    })

    // 上面已用 ElNotification 做了 UI 提示，这段是用浏览器的原生 Notification API 触发系统级通知，
    // 在 Electron生产环境下，ElNotification/系统通知通常有主进程支持，并不依赖于此逻辑。
    // 如果只在 Electron 环境发布，可以去掉这部分；如需在纯网页环境触发系统通知，可保留。

    // 仅在网页(浏览器)环境且获得 Notification 权限时，额外发系统通知
    if (
      typeof window !== 'undefined' &&
      'Notification' in window &&
      Notification.permission === 'granted'
    ) {
      try {
        new Notification('BabyGrow', { body: NUDGE_MESSAGE })
      } catch {
        /* ignore */
      }
    }
  }

  const startInterval = (): void => {
    if (timer) return
    void tick()
    timer = setInterval(() => void tick(), 60_000)
  }

  const stopInterval = (): void => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  watch(
    () => auth.isAuthenticated,
    (ok) => {
      if (ok) startInterval()
      else stopInterval()
    },
    { immediate: true }
  )

  onUnmounted(stopInterval)
}
