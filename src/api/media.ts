import apiClient from './client'
import type { MediaEntryResponse, MediaUpdate } from '@/types/api'

export function uploadMedia(
  file: File,
  dailyRecordId: number,
  description?: string,
  sortOrder?: number,
) {
  const form = new FormData()
  form.append('file', file)
  form.append('daily_record_id', String(dailyRecordId))
  if (description) form.append('description', description)
  if (sortOrder !== undefined) form.append('sort_order', String(sortOrder))

  return apiClient.post<MediaEntryResponse>('/api/media/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120_000,
  })
}

export function getMediaUrl(id: number): string {
  const base = apiClient.defaults.baseURL ?? ''
  return `${base}/api/media/${id}/file`
}

export function getThumbnailUrl(id: number): string {
  const base = apiClient.defaults.baseURL ?? ''
  return `${base}/api/media/${id}/thumbnail`
}

export function updateMedia(id: number, data: MediaUpdate) {
  return apiClient.put<MediaEntryResponse>(`/api/media/${id}`, data)
}

export function deleteMedia(id: number) {
  return apiClient.delete(`/api/media/${id}`)
}
