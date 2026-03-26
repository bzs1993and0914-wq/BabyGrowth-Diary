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

  /**
   * 根据当前 timeline 筛选条件从后端加载记录列表。
   * append=true 时追加到现有列表（"加载更多"场景），否则替换整个列表。
   */
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

  /** 加载指定日期的完整记录详情，结果保存到 currentRecord。 */
  async function loadRecord(date: string) {
    loading.value = true
    try {
      currentRecord.value = (await getRecord(date)).data
    } finally {
      loading.value = false
    }
  }

  /** 创建新记录并返回完整响应（不自动刷新列表，由调用方决定后续行为）。 */
  async function saveRecord(data: RecordCreate): Promise<RecordResponse> {
    return (await createRecord(data)).data
  }

  /** 更新记录并返回最新数据。 */
  async function editRecord(date: string, data: RecordUpdate): Promise<RecordResponse> {
    return (await updateRecord(date, data)).data
  }

  /** 删除记录后同步从本地列表中移除，避免重新请求接口。 */
  async function removeRecord(date: string) {
    await deleteRecord(date)
    items.value = items.value.filter((i) => i.date !== date)
    total.value -= 1
  }

  /** 切换时间粒度（day/week/month/year），并重置分页到第 1 页。 */
  function setGranularity(g: ViewGranularity) {
    timeline.granularity = g
    timeline.page = 1
  }

  /** 切换时间轴布局模式（flat/grouped）。 */
  function setLayout(l: LayoutMode) {
    timeline.layout = l
  }

  /** 设置全文搜索关键词，并重置分页到第 1 页。 */
  function setSearch(q: string) {
    timeline.searchQuery = q
    timeline.page = 1
  }

  /** 设置日期范围过滤，并重置分页到第 1 页。 */
  function setDateRange(from: string | null, to: string | null) {
    timeline.dateFrom = from
    timeline.dateTo = to
    timeline.page = 1
  }

  /** 切换「仅显示里程碑记录」过滤，并重置分页到第 1 页。 */
  function setMilestoneOnly(v: boolean) {
    timeline.milestoneOnly = v
    timeline.page = 1
  }

  /** 翻到下一页（配合 loadRecords(true) 实现"加载更多"）。 */
  function nextPage() {
    timeline.page += 1
  }

  /** 当前已加载的条数是否少于总数（控制"加载更多"按钮的显隐）。 */
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
