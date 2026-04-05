import apiClient from './client'
import type {
  RecordListParams,
  RecordListResponse,
  RecordResponse,
  RecordCreate,
  RecordUpdate,
} from '@/types/api'

/** 分页查询记录列表，支持时间粒度、日期范围、关键词、里程碑过滤等参数。 */
export function getRecords(params: RecordListParams) {
  return apiClient.get<RecordListResponse>('/api/records/', { params })
}

/** 获取指定日期的完整记录（含媒体、文字、里程碑、生长指标）。 */
export function getRecord(date: string) {
  return apiClient.get<RecordResponse>(`/api/records/${date}`)
}

/** 创建新的每日记录。 */
export function createRecord(data: RecordCreate) {
  return apiClient.post<RecordResponse>('/api/records/', data)
}

/** 更新指定日期的记录内容（全量替换文字列表）。 */
export function updateRecord(date: string, data: RecordUpdate) {
  return apiClient.put<RecordResponse>(`/api/records/${date}`, data)
}

/** 删除指定日期的记录及其关联的所有媒体文件。 */
export function deleteRecord(date: string) {
  return apiClient.delete(`/api/records/${date}`)
}
