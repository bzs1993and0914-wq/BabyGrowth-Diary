import apiClient from './client'
import type {
  RecordListParams,
  RecordListResponse,
  RecordResponse,
  RecordCreate,
  RecordUpdate,
} from '@/types/api'

export function getRecords(params: RecordListParams) {
  return apiClient.get<RecordListResponse>('/api/records', { params })
}

export function getRecord(date: string) {
  return apiClient.get<RecordResponse>(`/api/records/${date}`)
}

export function createRecord(data: RecordCreate) {
  return apiClient.post<RecordResponse>('/api/records', data)
}

export function updateRecord(date: string, data: RecordUpdate) {
  return apiClient.put<RecordResponse>(`/api/records/${date}`, data)
}

export function deleteRecord(date: string) {
  return apiClient.delete(`/api/records/${date}`)
}
