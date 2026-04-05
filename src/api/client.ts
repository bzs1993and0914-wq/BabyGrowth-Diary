import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { getStoredToken } from '@/utils/authToken'

// Electron 开发时窗口加载 http://localhost:5173，但渲染进程里 import.meta.env.DEV 可能为 false，
// 若仍用 18900 会直接跨域，浏览器会报 Network Error 且无 response（表现为「请检查连接」）。
function resolveApiBaseURL(): string {
  if (typeof window === 'undefined') {
    return import.meta.env.DEV ? '' : 'http://localhost:18900'
  }
  const { hostname, port } = window.location
  const local = hostname === 'localhost' || hostname === '127.0.0.1'
  if (local && port === '5173') {
    return ''
  }
  if (import.meta.env.DEV && local) {
    return ''
  }
  return (
    window.electronAPI?.apiBaseUrl ||
    (import.meta.env.VITE_API_BASE as string | undefined) ||
    'http://localhost:18900'
  )
}

const apiClient = axios.create({
  baseURL: resolveApiBaseURL(),
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：从 localStorage 读取 JWT，自动附加到每个请求的 Authorization 头
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken()
    if (token) {
      config.headers = config.headers ?? {}
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

function detailMessage(
  data: Record<string, unknown> | undefined
): string | undefined {
  const d = data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    try {
      return JSON.stringify(d)
    } catch {
      return '请求参数校验失败'
    }
  }
  return undefined
}

// 响应拦截器：统一提取后端 detail 字段或根据 HTTP 状态码生成友好错误信息并打印日志
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status
    const data = error.response?.data as Record<string, unknown> | undefined
    const fromDetail = detailMessage(data)

    const message =
      fromDetail ??
      (status === 404
        ? '请求的资源不存在'
        : status === 401
          ? '未登录或登录已过期'
          : status === 422
            ? '请求参数有误'
            : status && status >= 500
              ? '服务器内部错误，请稍后重试'
              : !error.response
                ? `无法连接接口（${error.message || error.code || '无响应'}）。请确认后端已在 18900 运行，且当前页面走 localhost:5173 同源代理。`
                : '网络请求失败，请检查连接')

    const fullUrl = (error.config?.baseURL ?? '') + (error.config?.url ?? '')
    console.error(
      `[API ${error.config?.method?.toUpperCase()} ${fullUrl}]`,
      message
    )
    return Promise.reject(error)
  }
)

export default apiClient
