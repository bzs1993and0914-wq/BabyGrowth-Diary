import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getParentWords,
  getParentWord,
  createParentWord,
  updateParentWord,
  deleteParentWord,
} from '@/api/parentWords'
import type {
  ParentWordListItem,
  ParentWordResponse,
  ParentWordCreate,
  ParentWordUpdate,
} from '@/types/api'

export const useParentWordsStore = defineStore('parentWords', () => {
  const items = ref<ParentWordListItem[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentWord = ref<ParentWordResponse | null>(null)
  const page = ref(1)
  const pageSize = ref(20)

  const hasMore = computed(() => items.value.length < total.value)

  async function loadList(append = false) {
    loading.value = true
    try {
      const res = (await getParentWords({ page: page.value, page_size: pageSize.value })).data
      items.value = append ? [...items.value, ...res.items] : res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function loadDetail(id: number) {
    loading.value = true
    try {
      currentWord.value = (await getParentWord(id)).data
    } finally {
      loading.value = false
    }
  }

  async function create(data: ParentWordCreate): Promise<ParentWordResponse> {
    return (await createParentWord(data)).data
  }

  async function update(id: number, data: ParentWordUpdate): Promise<ParentWordResponse> {
    return (await updateParentWord(id, data)).data
  }

  async function remove(id: number) {
    await deleteParentWord(id)
    items.value = items.value.filter((i) => i.id !== id)
    total.value -= 1
  }

  function nextPage() {
    page.value += 1
  }

  function resetList() {
    items.value = []
    total.value = 0
    page.value = 1
  }

  return {
    items,
    total,
    loading,
    currentWord,
    page,
    pageSize,
    hasMore,
    loadList,
    loadDetail,
    create,
    update,
    remove,
    nextPage,
    resetList,
  }
})
