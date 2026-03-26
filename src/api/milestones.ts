import apiClient from './client'
import type {
  MilestoneCreate,
  MilestoneResponse,
  CategoryCreate,
  CategoryResponse,
} from '@/types/api'

/** 为指定每日记录创建里程碑（每条记录只能有一个）。 */
export function createMilestone(data: MilestoneCreate) {
  return apiClient.post<MilestoneResponse>('/api/milestones', data)
}

/** 删除里程碑记录。 */
export function deleteMilestone(id: number) {
  return apiClient.delete(`/api/milestones/${id}`)
}

/** 获取所有里程碑分类（系统预置 + 用户自定义）。 */
export function getCategories() {
  return apiClient.get<CategoryResponse[]>('/api/milestones/categories')
}

/** 创建自定义里程碑分类。 */
export function createCategory(data: CategoryCreate) {
  return apiClient.post<CategoryResponse>('/api/milestones/categories', data)
}
