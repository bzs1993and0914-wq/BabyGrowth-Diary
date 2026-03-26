const STORAGE_KEY = 'babygrow_auth_token'

/** 从 localStorage 读取持久化的 JWT；localStorage 不可用时返回 null。 */
export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

/** 将 JWT 持久化写入 localStorage；传入 null 时删除已存储的 Token（即登出）。 */
export function setStoredToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(STORAGE_KEY, token)
    else localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* ignore */
  }
}
