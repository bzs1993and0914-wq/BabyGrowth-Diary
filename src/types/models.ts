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
  page: number
  pageSize: number
}
