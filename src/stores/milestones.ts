import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories, createMilestone, deleteMilestone, createCategory } from '@/api/milestones'
import type { CategoryResponse, MilestoneCreate, MilestoneResponse, CategoryCreate } from '@/types/api'

export const useMilestonesStore = defineStore('milestones', () => {
  const categories = ref<CategoryResponse[]>([])
  const loading = ref(false)

  async function loadCategories() {
    loading.value = true
    try {
      categories.value = (await getCategories()).data
    } finally {
      loading.value = false
    }
  }

  async function addMilestone(data: MilestoneCreate): Promise<MilestoneResponse> {
    return (await createMilestone(data)).data
  }

  async function removeMilestone(id: number) {
    await deleteMilestone(id)
  }

  async function addCategory(data: CategoryCreate): Promise<CategoryResponse> {
    const cat = (await createCategory(data)).data
    categories.value.push(cat)
    return cat
  }

  return { categories, loading, loadCategories, addMilestone, removeMilestone, addCategory }
})
