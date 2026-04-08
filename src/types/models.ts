export type ViewGranularity = 'day' | 'week' | 'month' | 'year'

export type LayoutMode = 'flat' | 'collapsed'

export type ThemeName = 'default' | 'warm' | 'night'

export interface TimelineState {
  granularity: ViewGranularity
  layout: LayoutMode
  searchQuery: string
  dateFrom: string | null
  dateTo: string | null
  milestoneOnly: boolean
  /** 仅显示填写过「宝宝过敏食物」的记录（与时间轴同页切换） */
  allergyOnly: boolean
  page: number
  pageSize: number
}
