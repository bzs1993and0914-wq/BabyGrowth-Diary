import apiClient from './client'
import type {
  MilestoneCreate,
  MilestoneResponse,
  CategoryCreate,
  CategoryResponse,
} from '@/types/api'

export function createMilestone(data: MilestoneCreate) {
  return apiClient.post<MilestoneResponse>('/api/milestones', data)
}

export function deleteMilestone(id: number) {
  return apiClient.delete(`/api/milestones/${id}`)
}

export function getCategories() {
  return apiClient.get<CategoryResponse[]>('/api/milestones/categories')
}

export function createCategory(data: CategoryCreate) {
  return apiClient.post<CategoryResponse>('/api/milestones/categories', data)
}
