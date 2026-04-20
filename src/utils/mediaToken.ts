import apiClient from '@/api/client'

/**
 * 媒体访问 Token 缓存：
 * - 后端 `POST /api/auth/media-token` 颁发的是 scope=media、TTL 较短（默认 15min）的 JWT，
 *   仅可用于媒体文件端点 (`/api/media/*`) 的 URL 查询参数鉴权；
 * - 本模块在内存中缓存当前 media token，并提供 `ensureMediaToken()` 在过期前自动刷新；
 * - `<img>/<video>` 的 src 拼接是同步的，因此 `getMediaTokenSync()` 提供只读快照，
 *   首次使用前调用方需先 `await ensureMediaToken()` 预热（通常在登录/init 时完成）。
 */

interface MediaTokenCache {
  token: string
  expiresAt: number
}

let cache: MediaTokenCache | null = null
let inflight: Promise<string> | null = null

const REFRESH_LEEWAY_SECONDS = 60

function nowSeconds(): number {
  return Math.floor(Date.now() / 1000)
}

async function requestNewToken(): Promise<string> {
  const res = await apiClient.post<{ token: string; expires_at: number }>(
    '/api/auth/media-token',
  )
  cache = { token: res.data.token, expiresAt: res.data.expires_at }
  return cache.token
}

/**
 * 保证当前有可用的 media token；必要时向后端换取新 token。
 * 并发调用共用同一个 in-flight Promise，避免重复请求。
 */
export async function ensureMediaToken(): Promise<string> {
  if (cache && cache.expiresAt - nowSeconds() > REFRESH_LEEWAY_SECONDS) {
    return cache.token
  }
  if (!inflight) {
    inflight = requestNewToken().finally(() => {
      inflight = null
    })
  }
  return inflight
}

/**
 * 同步读取当前缓存的 media token；已过期或尚未初始化时返回 null。
 * 用于 `<img>`/`<video>` 的 URL 拼接，调用前应已通过 `ensureMediaToken()` 预热。
 */
export function getMediaTokenSync(): string | null {
  if (!cache) return null
  if (cache.expiresAt - nowSeconds() <= REFRESH_LEEWAY_SECONDS) return null
  return cache.token
}

/** 退出登录或鉴权失败时调用，立即清空缓存防止继续使用已泄漏的 token。 */
export function clearMediaToken(): void {
  cache = null
}
