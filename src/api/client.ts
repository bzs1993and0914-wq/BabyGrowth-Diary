import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

const apiClient = axios.create({
  baseURL: window.electronAPI?.apiBaseUrl || 'http://localhost:18900',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => config,
  (error: AxiosError) => Promise.reject(error),
)

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
