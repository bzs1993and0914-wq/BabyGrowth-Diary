import apiClient from './client'
import type {
  ParentWordCreate,
  ParentWordUpdate,
  ParentWordResponse,
  ParentWordListResponse,
  ProfileUpdate,
  AuthUser,
  HighlightCreate,
  HighlightResponse,
} from '@/types/api'

export function getParentWords(params: { page?: number; page_size?: number; author_role?: string }) {
  return apiClient.get<ParentWordListResponse>('/api/parent-words/', { params })
}

export function getParentWord(id: number) {
  return apiClient.get<ParentWordResponse>(`/api/parent-words/${id}`)
}

export function createParentWord(data: ParentWordCreate) {
  return apiClient.post<ParentWordResponse>('/api/parent-words/', data)
}

export function updateParentWord(id: number, data: ParentWordUpdate) {
  return apiClient.put<ParentWordResponse>(`/api/parent-words/${id}`, data)
}

export function deleteParentWord(id: number) {
  return apiClient.delete(`/api/parent-words/${id}`)
}

export function addHighlight(wordId: number, data: HighlightCreate) {
  return apiClient.post<HighlightResponse>(`/api/parent-words/${wordId}/highlights`, data)
}

export function removeHighlight(wordId: number, highlightId: number) {
  return apiClient.delete(`/api/parent-words/${wordId}/highlights/${highlightId}`)
}

export function updateProfile(data: ProfileUpdate) {
  return apiClient.put<AuthUser>('/api/auth/profile', data)
}
