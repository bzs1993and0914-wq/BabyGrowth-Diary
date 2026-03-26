import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { getStoredToken } from '@/utils/authToken'

// Electron 模式下由主进程注入后端实际端口，开发模式回退到默认端口
const apiClient = axios.create({
  baseURL: window.electronAPI?.apiBaseUrl || 'http://localhost:18900',
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
  (error: AxiosError) => Promise.reject(error),
)

// 响应拦截器：统一提取后端 detail 字段或根据 HTTP 状态码生成友好错误信息并打印日志
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status
    const data = error.response?.data as Record<string, unknown> | undefined

    const message =
      (data?.detail as string) ??
      (status === 404
        ? '请求的资源不存在'
        : status === 422
          ? '请求参数有误'
          : status && status >= 500
            ? '服务器内部错误，请稍后重试'
            : '网络请求失败，请检查连接')

    console.error(`[API ${error.config?.method?.toUpperCase()} ${error.config?.url}]`, message)
    return Promise.reject(error)
  },
)

export default apiClient
