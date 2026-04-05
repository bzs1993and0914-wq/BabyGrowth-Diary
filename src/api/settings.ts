import apiClient from './client'
import type { SettingsResponse, SettingsUpdate } from '@/types/api'

/** 获取全量应用设置（主题、暗色模式、缩略图参数等）。 */
export function getSettings() {
  return apiClient.get<SettingsResponse>('/api/settings/')
}

/** 更新应用设置，仅提交需要变更的字段即可（支持部分更新）。 */
export function updateSettings(data: SettingsUpdate) {
  return apiClient.put<SettingsResponse>('/api/settings/', data)
}
