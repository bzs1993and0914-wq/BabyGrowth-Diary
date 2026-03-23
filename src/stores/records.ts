import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { getRecords, getRecord, createRecord, updateRecord, deleteRecord } from '@/api/records'
import type { RecordListItem, RecordResponse, RecordListParams, RecordCreate, RecordUpdate } from '@/types/api'
import type { TimelineState, ViewGranularity, LayoutMode } from '@/types/models'

export const useRecordsStore = defineStore('records', () => {
  const items = ref<RecordListItem[]>([])
  const total = ref(0)
  const loading = ref(false)
  const currentRecord = ref<RecordResponse | null>(null)

  const timeline = reactive<TimelineState>({
    granularity: 'day',
    layout: 'flat',
    searchQuery: '',
    dateFrom: null,
    dateTo: null,
    milestoneOnly: false,
    page: 1,
    pageSize: 20,
  })

  async function loadRecords(append = false) {
    loading.value = true
    try {
      const params: RecordListParams = {
        view: timeline.granularity,
        milestone_only: timeline.milestoneOnly || undefined,
        q: timeline.searchQuery || undefined,
        date_from: timeline.dateFrom ?? undefined,
        date_to: timeline.dateTo ?? undefined,
        page: timeline.page,
        page_size: timeline.pageSize,
      }
      const res = (await getRecords(params)).data
      items.value = append ? [...items.value, ...res.items] : res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function loadRecord(date: string) {
    loading.value = true
    try {
      currentRecord.value = (await getRecord(date)).data
    } finally {
      loading.value = false
    }
  }

  async function saveRecord(data: RecordCreate): Promise<RecordResponse> {
    return (await createRecord(data)).data
  }

  async function editRecord(date: string, data: RecordUpdate): Promise<RecordResponse> {
    return (await updateRecord(date, data)).data
  }

  async function removeRecord(date: string) {
    await deleteRecord(date)
    items.value = items.value.filter((i) => i.date !== date)
    total.value -= 1
  }

  function setGranularity(g: ViewGranularity) {
    timeline.granularity = g
    timeline.page = 1
  }

  function setLayout(l: LayoutMode) {
    timeline.layout = l
  }

  function setSearch(q: string) {
    timeline.searchQuery = q
    timeline.page = 1
  }

  function setDateRange(from: string | null, to: string | null) {
    timeline.dateFrom = from
    timeline.dateTo = to
    timeline.page = 1
  }

  function setMilestoneOnly(v: boolean) {
    timeline.milestoneOnly = v
    timeline.page = 1
  }

  function nextPage() {
    timeline.page += 1
  }

  const hasMore = computed(() => items.value.length < total.value)

  return {
    items,
    total,
    loading,
    currentRecord,
    timeline,
    hasMore,
    loadRecords,
    loadRecord,
    saveRecord,
    editRecord,
    removeRecord,
    setGranularity,
    setLayout,
    setSearch,
    setDateRange,
    setMilestoneOnly,
    nextPage,
  }
})
