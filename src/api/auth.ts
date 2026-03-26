import apiClient from './client'
import type { AuthUser, LoginPayload, RegisterPayload, ChangePasswordPayload } from '@/types/api'

/** 注册新用户，成功后返回 JWT 和用户信息。 */
export function register(payload: RegisterPayload) {
  return apiClient.post<{ access_token: string; token_type: string; user: AuthUser }>(
    '/api/auth/register',
    payload,
  )
}

/** 用户名密码登录，成功后返回 JWT 和用户信息。 */
export function login(payload: LoginPayload) {
  return apiClient.post<{ access_token: string; token_type: string; user: AuthUser }>(
    '/api/auth/login',
    payload,
  )
}

/** 用当前 Token 获取最新用户信息（用于页面刷新时恢复登录状态）。 */
export function fetchMe() {
  return apiClient.get<AuthUser>('/api/auth/me')
}

/** 修改当前用户密码，需提供旧密码进行验证。 */
export function changePassword(payload: ChangePasswordPayload) {
  return apiClient.post<{ message: string }>('/api/auth/change-password', payload)
}

/** 开发调试用：切换账号等级（normal/vip）以测试媒体上传上限等差异功能。 */
export function devSetTier(tier: 'normal' | 'vip') {
  return apiClient.post<AuthUser>(`/api/auth/dev/set-tier?tier=${encodeURIComponent(tier)}`)
}
