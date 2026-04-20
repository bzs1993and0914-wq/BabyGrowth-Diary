// ── Request / Query params ──────────────────────────────────────────

export interface RecordListParams {
  view?: 'day' | 'week' | 'month' | 'year'
  date?: string
  milestone_only?: boolean
  q?: string
  date_from?: string
  date_to?: string
  page?: number
  page_size?: number
  has_allergy?: boolean
}

export interface TextEntryInput {
  id?: number
  content: string
  sort_order: number
}

export interface RecordCreate {
  date: string
  texts?: TextEntryInput[]
  use_default_media_placeholder?: boolean
  allergy_notes?: string | null
}

export interface RecordUpdate {
  texts?: TextEntryInput[]
  use_default_media_placeholder?: boolean
  allergy_notes?: string | null
}

export interface AuthUser {
  id: number
  username: string
  account_tier: 'normal' | 'vip'
  parent_role?: string | null
}

export interface RegisterPayload {
  username: string
  password: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}

export interface MediaUpdate {
  description?: string
  sort_order?: number
}

export interface MilestoneCreate {
  daily_record_id: number
  category_id: number
  name: string
  description?: string
}

export interface CategoryCreate {
  name: string
  icon?: string
}

export interface ExportRequest {
  date_from?: string
  date_to?: string
}

export interface SettingsUpdate {
  theme?: string
  dark_mode?: boolean
  thumbnail_max_size?: number
  thumbnail_quality?: number
}

export interface GrowthMetricCreate {
  daily_record_id: number
  metric_type: 'height' | 'weight' | 'head_circumference'
  value: number
  unit: string
}

export interface GrowthMetricQuery {
  metric_type?: string
  date_from?: string
  date_to?: string
}

// ── Response types ─────────────────────────────────────────────────

export interface RecordListItem {
  date: string
  media_count: number
  text_count: number
  first_thumbnail: string | null
  use_default_media_placeholder?: boolean
  allergy_notes?: string | null
  has_milestone: boolean
  milestone_name: string | null
  milestone_icon: string | null
  preview_text: string | null
}

export interface RecordListResponse {
  items: RecordListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface MediaEntryResponse {
  id: number
  media_type: 'image' | 'video'
  original_path: string
  thumbnail_path: string | null
  description: string | null
  file_size: number | null
  original_filename: string | null
  exif_date: string | null
  sort_order: number
  created_at: string
}

export interface TextEntryResponse {
  id: number
  content: string
  sort_order: number
  created_at: string
}

export interface MilestoneInfo {
  id: number
  name: string | null
  description: string | null
  category_id: number | null
  category_name: string | null
  category_icon: string | null
}

export interface MilestoneResponse {
  id: number
  daily_record_id: number
  category_id: number | null
  name: string | null
  description: string | null
  category_name: string | null
  category_icon: string | null
  created_at: string
}

export interface GrowthMetricResponse {
  id: number
  daily_record_id: number
  metric_type: string
  value: number
  unit: string | null
  date: string | null
  created_at: string
}

export interface RecordResponse {
  id: number
  date: string
  created_at: string
  updated_at: string
  use_default_media_placeholder?: boolean
  allergy_notes?: string | null
  media_entries: MediaEntryResponse[]
  text_entries: TextEntryResponse[]
  milestone: MilestoneInfo | null
  growth_metrics: GrowthMetricResponse[]
}

export interface CategoryResponse {
  id: number
  name: string
  icon: string | null
  is_preset: boolean
}

export interface ExportStatus {
  export_id: string
  status: 'processing' | 'completed' | 'failed'
  progress: number
  file_path?: string
  file_size?: number
  message?: string
  error?: string
}

export interface StorageStats {
  total_records: number
  total_media: number
  total_images: number
  total_videos: number
  media_size_bytes: number
  thumbnail_size_bytes: number
  database_size_bytes: number
  total_size_bytes: number
}

export interface SettingsResponse {
  theme: string
  dark_mode: boolean
  thumbnail_max_size: number
  thumbnail_quality: number
}

export interface GrowthCurveData {
  dates: string[]
  values: number[]
  metric_type: string
  unit: string | null
}

export interface ParentWordCreate {
  title: string
  content: string
  author_role?: string | null
}

export interface ParentWordUpdate {
  title?: string
  content?: string
  author_role?: string | null
}

export interface ParentWordListItem {
  id: number
  title: string
  content_preview: string
  author_role: string | null
  media_count: number
  first_thumbnail: string | null
  created_at: string
  updated_at: string
}

export interface HighlightCreate {
  start_offset: number
  end_offset: number
  color?: string
}

export interface HighlightResponse {
  id: number
  start_offset: number
  end_offset: number
  color: string | null
  created_at: string
}

export interface ParentWordResponse {
  id: number
  title: string
  content: string
  author_role: string | null
  created_at: string
  updated_at: string
  media_entries: MediaEntryResponse[]
  highlights: HighlightResponse[]
}

export interface ParentWordListResponse {
  items: ParentWordListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ProfileUpdate {
  parent_role: string | null
}
