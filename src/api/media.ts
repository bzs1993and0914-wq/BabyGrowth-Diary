import apiClient from './client'
import type { MediaEntryResponse, MediaUpdate } from '@/types/api'
import { getStoredToken } from '@/utils/authToken'

function tokenParam(): string {
  const t = getStoredToken()
  return t ? `?token=${encodeURIComponent(t)}` : ''
}

/**
 * 上传媒体文件到指定记录，超时时间延长至 120 秒以支持大文件上传。
 * FormData 必须由浏览器自动设置 Content-Type（含 boundary），不能手动指定。
 */
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
    timeout: 120_000,
    transformRequest: [
      (data, headers) => {
        if (data instanceof FormData) {
          delete headers['Content-Type']
        }
        return data
      },
    ],
  })
}

/** 返回媒体原文件的完整 URL（含认证 token），供 <img>/<video> 的 src 属性直接使用。 */
export function getMediaUrl(id: number): string {
  const base = apiClient.defaults.baseURL ?? ''
  return `${base}/api/media/${id}/file${tokenParam()}`
}

/** 返回媒体缩略图的完整 URL（含认证 token），用于列表页快速预览。 */
export function getThumbnailUrl(id: number): string {
  const base = apiClient.defaults.baseURL ?? ''
  return `${base}/api/media/${id}/thumbnail${tokenParam()}`
}

/** 根据后端返回的 API 路径（如 /api/media/1/thumbnail）拼接完整 URL 并附加认证 token。 */
export function buildMediaApiUrl(apiPath: string): string {
  const base = apiClient.defaults.baseURL ?? ''
  return `${base}${apiPath}${tokenParam()}`
}

/** 更新媒体文件的描述或排列顺序。 */
export function updateMedia(id: number, data: MediaUpdate) {
  return apiClient.put<MediaEntryResponse>(`/api/media/${id}`, data)
}

/** 删除媒体文件（同时删除磁盘上的原文件和缩略图）。 */
export function deleteMedia(id: number) {
  return apiClient.delete(`/api/media/${id}`)
}
