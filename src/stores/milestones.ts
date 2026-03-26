import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories, createMilestone, deleteMilestone, createCategory } from '@/api/milestones'
import type { CategoryResponse, MilestoneCreate, MilestoneResponse, CategoryCreate } from '@/types/api'

export const useMilestonesStore = defineStore('milestones', () => {
  const categories = ref<CategoryResponse[]>([])
  const loading = ref(false)

  /** 从后端拉取所有里程碑分类并缓存到 store。 */
  async function loadCategories() {
    loading.value = true
    try {
      categories.value = (await getCategories()).data
    } finally {
      loading.value = false
    }
  }

  /** 创建里程碑并返回新建结果（不自动关联到列表，由调用方处理）。 */
  async function addMilestone(data: MilestoneCreate): Promise<MilestoneResponse> {
    return (await createMilestone(data)).data
  }

  /** 删除里程碑（无需更新本地 categories，因里程碑不存储在分类列表中）。 */
  async function removeMilestone(id: number) {
    await deleteMilestone(id)
  }

  /** 创建自定义分类并立即追加到本地 categories 列表，无需重新请求。 */
  async function addCategory(data: CategoryCreate): Promise<CategoryResponse> {
    const cat = (await createCategory(data)).data
    categories.value.push(cat)
    return cat
  }

  return { categories, loading, loadCategories, addMilestone, removeMilestone, addCategory }
})
