import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  login as loginApi,
  register as registerApi,
  fetchMe,
  changePassword as changePasswordApi,
  devSetTier,
} from '@/api/auth'
import { updateProfile as updateProfileApi } from '@/api/parentWords'
import { getStoredToken, setStoredToken } from '@/utils/authToken'
import type {
  AuthUser,
  LoginPayload,
  RegisterPayload,
  ChangePasswordPayload,
  ProfileUpdate,
} from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getStoredToken())
  const user = ref<AuthUser | null>(null)
  const initialized = ref(false)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  /**
   * 应用启动时调用：若 localStorage 中有缓存 Token，则请求 /auth/me 恢复登录状态；
   * Token 失效时自动清除，避免进入需鉴权页面时报错。
   */
  async function init() {
    if (!getStoredToken()) {
      initialized.value = true
      return
    }
    token.value = getStoredToken()
    try {
      loading.value = true
      const res = await fetchMe()
      user.value = res.data
    } catch {
      setToken(null)
      user.value = null
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  /** 同步更新内存中的 token 响应式变量并持久化到 localStorage。 */
  function setToken(t: string | null) {
    token.value = t
    setStoredToken(t)
  }

  /** 调用登录接口，成功后保存 Token 和用户信息。 */
  async function login(payload: LoginPayload) {
    const res = await loginApi(payload)
    setToken(res.data.access_token)
    user.value = res.data.user
    initialized.value = true
  }

  /** 调用注册接口，成功后保存 Token 和用户信息（与登录行为一致）。 */
  async function register(payload: RegisterPayload) {
    const res = await registerApi(payload)
    setToken(res.data.access_token)
    user.value = res.data.user
    initialized.value = true
  }

  /** 清除本地 Token 和用户信息，路由守卫会将未登录用户重定向到登录页。 */
  function logout() {
    setToken(null)
    user.value = null
  }

  /** 修改当前用户密码（需提供旧密码）。 */
  async function changePassword(payload: ChangePasswordPayload) {
    await changePasswordApi(payload)
  }

  /** 开发调试用：切换账号等级，并更新 store 中的用户信息。 */
  async function setAccountTier(tier: 'normal' | 'vip') {
    const res = await devSetTier(tier)
    user.value = res.data
  }

  async function updateProfile(payload: ProfileUpdate) {
    const res = await updateProfileApi(payload)
    user.value = res.data
  }

  return {
    token,
    user,
    initialized,
    loading,
    isAuthenticated,
    init,
    login,
    register,
    logout,
    changePassword,
    setAccountTier,
    updateProfile,
    setToken,
  }
})
