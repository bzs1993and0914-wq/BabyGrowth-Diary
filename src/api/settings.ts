import apiClient from './client'
import type { SettingsResponse, SettingsUpdate } from '@/types/api'

export function getSettings() {
  return apiClient.get<SettingsResponse>('/api/settings')
}

export function updateSettings(data: SettingsUpdate) {
  return apiClient.put<SettingsResponse>('/api/settings', data)
}
