<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { ViewGranularity, LayoutMode } from '@/types/models'

const MOBILE_FILTER_MQ = '(max-width: 767px)'
const isMobileLayout = ref(
  typeof window !== 'undefined' && window.matchMedia(MOBILE_FILTER_MQ).matches
)
let mobileMq: MediaQueryList | undefined

function syncMobileLayout(ev?: MediaQueryListEvent) {
  isMobileLayout.value = ev?.matches ?? mobileMq?.matches ?? false
}

onMounted(() => {
  mobileMq = window.matchMedia(MOBILE_FILTER_MQ)
  syncMobileLayout()
  mobileMq.addEventListener('change', syncMobileLayout)
})

onUnmounted(() => {
  mobileMq?.removeEventListener('change', syncMobileLayout)
})

const allergyOnly = defineModel<boolean>('allergyOnly', { required: true })
const milestoneOnly = defineModel<boolean>('milestoneOnly', { required: true })

const props = defineProps<{
  granularity: ViewGranularity
  layout: LayoutMode
}>()

const emit = defineEmits<{
  'update:granularity': [value: ViewGranularity]
  'update:layout': [value: LayoutMode]
  'update:search': [value: string]
  'update:dateRange': [from: string | null, to: string | null]
}>()

const searchText = ref('')
const dateRange = ref<[string, string] | null>(null)
const mobileDateStart = ref<string | null>(null)
const mobileDateEnd = ref<string | null>(null)
const mobileAdvancedOpen = ref(false)

const granularityOptions = [
  { label: '日', value: 'day' as ViewGranularity },
  { label: '周', value: 'week' as ViewGranularity },
  { label: '月', value: 'month' as ViewGranularity },
  { label: '年', value: 'year' as ViewGranularity },
]

const hasActiveFilters = computed(() => {
  return allergyOnly.value || milestoneOnly.value || !!dateRange.value
})

let searchTimer: ReturnType<typeof setTimeout> | null = null
watch(searchText, (val) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => emit('update:search', val), 300)
})

function onDateRangeChange(val: [string, string] | null) {
  if (val) {
    emit('update:dateRange', val[0], val[1])
  } else {
    emit('update:dateRange', null, null)
  }
}

function syncMobileFieldsFromRange() {
  if (dateRange.value) {
    mobileDateStart.value = dateRange.value[0]
    mobileDateEnd.value = dateRange.value[1]
  } else {
    mobileDateStart.value = null
    mobileDateEnd.value = null
  }
}

watch(
  isMobileLayout,
  (narrow) => {
    if (narrow) syncMobileFieldsFromRange()
  },
  { immediate: true }
)

function onMobileStartChange(val: string | null | undefined) {
  const v = val ?? null
  mobileDateStart.value = v
  if (!v) {
    mobileDateEnd.value = null
    dateRange.value = null
    onDateRangeChange(null)
    return
  }
  const e = mobileDateEnd.value
  if (!e) {
    mobileDateEnd.value = v
    dateRange.value = [v, v]
    onDateRangeChange([v, v])
    return
  }
  const from = v <= e ? v : e
  const to = v <= e ? e : v
  mobileDateStart.value = from
  mobileDateEnd.value = to
  dateRange.value = [from, to]
  onDateRangeChange([from, to])
}

function onMobileEndChange(val: string | null | undefined) {
  const v = val ?? null
  mobileDateEnd.value = v
  if (!v) {
    mobileDateStart.value = null
    dateRange.value = null
    onDateRangeChange(null)
    return
  }
  const s = mobileDateStart.value
  if (!s) {
    mobileDateStart.value = v
    dateRange.value = [v, v]
    onDateRangeChange([v, v])
    return
  }
  const from = s <= v ? s : v
  const to = s <= v ? v : s
  mobileDateStart.value = from
  mobileDateEnd.value = to
  dateRange.value = [from, to]
  onDateRangeChange([from, to])
}

function toggleMobileAdvanced() {
  mobileAdvancedOpen.value = !mobileAdvancedOpen.value
}

function clearAllFilters() {
  allergyOnly.value = false
  milestoneOnly.value = false
  dateRange.value = null
  onDateRangeChange(null)
}
</script>

<template>
  <!-- ═══ 移动端布局 ═══ -->
  <div v-if="isMobileLayout" class="tf-mobile">
    <!-- 顶部：段式控件 + 筛选按钮 -->
    <div class="tf-mobile__top">
      <div class="tf-segment" role="radiogroup" aria-label="时间粒度">
        <button
          v-for="opt in granularityOptions"
          :key="opt.value"
          :class="['tf-segment__item', { 'tf-segment__item--active': props.granularity === opt.value }]"
          role="radio"
          :aria-checked="props.granularity === opt.value"
          @click="emit('update:granularity', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>

      <button
        :class="['tf-mobile__filter-btn', { 'tf-mobile__filter-btn--active': hasActiveFilters }]"
        :aria-expanded="mobileAdvancedOpen"
        aria-label="展开筛选"
        @click="toggleMobileAdvanced"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
        </svg>
        <span v-if="hasActiveFilters" class="tf-mobile__filter-dot" />
      </button>
    </div>

    <!-- 搜索栏 -->
    <div class="tf-mobile__search">
      <el-input
        v-model="searchText"
        placeholder="搜索记录..."
        :prefix-icon="Search"
        clearable
        class="tf-mobile__search-input"
      />
    </div>

    <!-- 可折叠高级筛选区 -->
    <transition name="tf-slide">
      <div v-show="mobileAdvancedOpen" class="tf-mobile__advanced">
        <!-- 日期范围 -->
        <div class="tf-mobile__section">
          <span class="tf-mobile__section-label">日期范围</span>
          <div class="tf-mobile__date-row" role="group" aria-label="按日期范围筛选">
            <el-date-picker
              :model-value="mobileDateStart"
              type="date"
              placeholder="开始日期"
              aria-label="开始日期"
              value-format="YYYY-MM-DD"
              class="tf-mobile__date-picker"
              placement="bottom-start"
              popper-class="timeline-filter-date-popper-mobile"
              clearable
              @update:model-value="onMobileStartChange"
            />
            <span class="tf-mobile__date-sep">至</span>
            <el-date-picker
              :model-value="mobileDateEnd"
              type="date"
              placeholder="结束日期"
              aria-label="结束日期"
              value-format="YYYY-MM-DD"
              class="tf-mobile__date-picker"
              placement="bottom-start"
              popper-class="timeline-filter-date-popper-mobile"
              clearable
              @update:model-value="onMobileEndChange"
            />
          </div>
        </div>

        <!-- 筛选标签 -->
        <div class="tf-mobile__section">
          <span class="tf-mobile__section-label">快捷筛选</span>
          <div class="tf-mobile__chips">
            <button
              :class="['tf-chip', { 'tf-chip--active': allergyOnly }]"
              @click="allergyOnly = !allergyOnly"
            >
              <span class="tf-chip__icon">⚠️</span>
              <span>过敏记录</span>
            </button>
            <button
              :class="['tf-chip', { 'tf-chip--active': milestoneOnly }]"
              @click="milestoneOnly = !milestoneOnly"
            >
              <span class="tf-chip__icon">🏅</span>
              <span>里程碑</span>
            </button>
          </div>
        </div>

        <!-- 布局切换 -->
        <div class="tf-mobile__section">
          <span class="tf-mobile__section-label">视图模式</span>
          <div class="tf-layout-toggle">
            <button
              :class="['tf-layout-toggle__btn', { 'tf-layout-toggle__btn--active': props.layout === 'flat' }]"
              @click="emit('update:layout', 'flat')"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h8v8H3V3zm0 10h8v8H3v-8zm10-10h8v8h-8V3zm0 10h8v8h-8v-8z"/></svg>
              <span>平铺</span>
            </button>
            <button
              :class="['tf-layout-toggle__btn', { 'tf-layout-toggle__btn--active': props.layout === 'collapsed' }]"
              @click="emit('update:layout', 'collapsed')"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z"/></svg>
              <span>列表</span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>

  <!-- ═══ 桌面端布局 ═══ -->
  <div v-else class="tf-desk">
    <!-- 第一行：段式控件 + 搜索 + 布局切换 -->
    <div class="tf-desk__toolbar">
      <div class="tf-segment tf-segment--desk" role="radiogroup" aria-label="时间粒度">
        <button
          v-for="opt in granularityOptions"
          :key="opt.value"
          :class="['tf-segment__item', { 'tf-segment__item--active': props.granularity === opt.value }]"
          role="radio"
          :aria-checked="props.granularity === opt.value"
          @click="emit('update:granularity', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>

      <div class="tf-desk__search-wrap">
        <el-input
          v-model="searchText"
          placeholder="搜索记录..."
          :prefix-icon="Search"
          clearable
          class="tf-desk__search"
        />
      </div>

      <div class="tf-desk__layout">
        <button
          :class="['tf-layout-toggle__btn', { 'tf-layout-toggle__btn--active': props.layout === 'flat' }]"
          title="平铺视图"
          @click="emit('update:layout', 'flat')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h8v8H3V3zm0 10h8v8H3v-8zm10-10h8v8h-8V3zm0 10h8v8h-8v-8z"/></svg>
          <span>平铺</span>
        </button>
        <button
          :class="['tf-layout-toggle__btn', { 'tf-layout-toggle__btn--active': props.layout === 'collapsed' }]"
          title="列表视图"
          @click="emit('update:layout', 'collapsed')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 4h18v2H3V4zm0 7h18v2H3v-2zm0 7h18v2H3v-2z"/></svg>
          <span>列表</span>
        </button>
      </div>
    </div>

    <!-- 第二行：筛选条件 -->
    <div class="tf-desk__filters">
      <span class="tf-desk__filters-label">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
        </svg>
        筛选
      </span>

      <div class="tf-desk__date-wrap">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="default"
          value-format="YYYY-MM-DD"
          class="tf-desk__date-picker"
          @change="onDateRangeChange"
        />
      </div>

      <div class="tf-desk__divider" />

      <button
        :class="['tf-chip', { 'tf-chip--active': allergyOnly }]"
        title="仅显示填写过「宝宝过敏食物」的记录"
        @click="allergyOnly = !allergyOnly"
      >
        <span class="tf-chip__icon">⚠️</span>
        <span>过敏记录</span>
      </button>

      <button
        :class="['tf-chip', { 'tf-chip--active': milestoneOnly }]"
        title="仅显示里程碑记录"
        @click="milestoneOnly = !milestoneOnly"
      >
        <span class="tf-chip__icon">🏅</span>
        <span>里程碑</span>
      </button>

      <button
        v-if="hasActiveFilters"
        class="tf-desk__clear-btn"
        title="清除所有筛选"
        @click="clearAllFilters"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
        </svg>
        清除筛选
      </button>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════
   移动端：全新设计
   ═══════════════════════════════════════════ */

.tf-mobile {
  margin-bottom: 16px;
}

/* ── 顶栏：段式控件 + 筛选按钮 ── */
.tf-mobile__top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.tf-segment {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 3px;
  background: var(--bg-secondary);
  border-radius: 10px;
  gap: 2px;
}

.tf-segment__item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 36px;
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.tf-segment__item--active {
  color: var(--color-primary);
  background: var(--bg-card);
  box-shadow: 0 1px 3px var(--shadow-color), 0 0 0 1px rgba(var(--color-primary-rgb), 0.08);
  font-weight: 600;
}

.tf-segment__item:hover:not(.tf-segment__item--active) {
  color: var(--text-primary);
  background: rgba(var(--color-primary-rgb), 0.04);
}

.tf-segment__item:active:not(.tf-segment__item--active) {
  background: rgba(var(--color-primary-rgb), 0.06);
}

.tf-mobile__filter-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: 1.5px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.tf-mobile__filter-btn--active {
  color: var(--color-primary);
  border-color: rgba(var(--color-primary-rgb), 0.3);
  background: rgba(var(--color-primary-rgb), 0.06);
}

.tf-mobile__filter-btn:active {
  transform: scale(0.95);
}

.tf-mobile__filter-dot {
  position: absolute;
  top: 7px;
  right: 7px;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-primary);
}

/* ── 搜索栏 ── */
.tf-mobile__search {
  margin-bottom: 2px;
}

.tf-mobile__search-input :deep(.el-input__wrapper) {
  height: 40px;
  border-radius: 10px;
  background: var(--bg-secondary);
  box-shadow: none !important;
  border: 1.5px solid transparent;
  transition: border-color 0.2s, background-color 0.2s;
}

.tf-mobile__search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
  background: var(--bg-card);
}

.tf-mobile__search-input :deep(.el-input__inner) {
  font-size: 14px;
}

.tf-mobile__search-input :deep(.el-input__prefix) {
  color: var(--text-secondary);
}

/* ── 高级筛选区 ── */
.tf-mobile__advanced {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 14px;
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tf-mobile__section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tf-mobile__section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 日期行 */
.tf-mobile__date-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tf-mobile__date-picker {
  flex: 1;
  min-width: 0;
  width: auto !important;
}

.tf-mobile__date-picker :deep(.el-input__wrapper) {
  height: 38px;
  border-radius: 10px;
  box-shadow: none !important;
  background: var(--bg-secondary);
  border: 1.5px solid transparent;
  transition: border-color 0.2s;
}

.tf-mobile__date-picker :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
}

.tf-mobile__date-picker :deep(.el-input__inner) {
  font-size: 13px;
}

.tf-mobile__date-sep {
  font-size: 13px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

/* 筛选芯片 */
.tf-mobile__chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tf-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 34px;
  padding: 0 14px;
  border-radius: 17px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.tf-chip:hover:not(.tf-chip--active) {
  color: var(--text-primary);
  border-color: var(--border-color);
}

.tf-chip--active {
  color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.08);
  border-color: rgba(var(--color-primary-rgb), 0.25);
}

.tf-chip--active:hover {
  background: rgba(var(--color-primary-rgb), 0.12);
}

.tf-chip:active {
  transform: scale(0.96);
}

.tf-chip__icon {
  font-size: 14px;
  line-height: 1;
}

/* 布局切换 */
.tf-layout-toggle {
  display: flex;
  gap: 8px;
}

.tf-layout-toggle__btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.tf-layout-toggle__btn:hover:not(.tf-layout-toggle__btn--active) {
  color: var(--text-primary);
  border-color: var(--border-color);
}

.tf-layout-toggle__btn--active {
  color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.08);
  border-color: rgba(var(--color-primary-rgb), 0.25);
}

.tf-layout-toggle__btn--active:hover {
  background: rgba(var(--color-primary-rgb), 0.12);
}

.tf-layout-toggle__btn:active {
  transform: scale(0.97);
}

/* 折叠动画 */
.tf-slide-enter-active,
.tf-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  max-height: 300px;
  opacity: 1;
}

.tf-slide-enter-from,
.tf-slide-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* ═══════════════════════════════════════════
   桌面端：Toolbar + Filter Chips
   ═══════════════════════════════════════════ */

.tf-desk {
  background: var(--bg-card);
  border-radius: 14px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
  overflow: hidden;
}

/* ── 第一行：工具栏 ── */
.tf-desk__toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
}

.tf-segment--desk {
  flex: 0 0 auto;
}

.tf-segment--desk .tf-segment__item {
  padding: 0 18px;
  height: 34px;
  font-size: 13px;
}

.tf-desk__search-wrap {
  flex: 1;
  min-width: 0;
  max-width: 320px;
}

.tf-desk__search :deep(.el-input__wrapper) {
  height: 34px;
  border-radius: 8px;
  background: var(--bg-secondary);
  box-shadow: none !important;
  border: 1.5px solid transparent;
  transition: border-color 0.2s, background-color 0.2s;
}

.tf-desk__search :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
  background: var(--bg-card);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1) !important;
}

.tf-desk__search :deep(.el-input__inner) {
  font-size: 13px;
}

.tf-desk__search :deep(.el-input__prefix) {
  color: var(--text-secondary);
}

.tf-desk__layout {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  margin-left: auto;
}

.tf-desk__layout .tf-layout-toggle__btn {
  height: 34px;
  padding: 0 14px;
  border-radius: 8px;
  font-size: 13px;
}

/* ── 第二行：筛选条件 ── */
.tf-desk__filters {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px 10px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.tf-desk__filters-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
  user-select: none;
}

.tf-desk__date-wrap {
  flex-shrink: 0;
}

.tf-desk__date-picker {
  width: 240px !important;
}

.tf-desk__date-picker :deep(.el-input__wrapper),
.tf-desk__date-picker :deep(.el-range-editor.el-input__wrapper) {
  height: 30px;
  border-radius: 15px;
  background: var(--bg-card);
  box-shadow: none !important;
  border: 1.5px solid var(--border-color);
  transition: border-color 0.2s;
}

.tf-desk__date-picker :deep(.el-input__wrapper:hover),
.tf-desk__date-picker :deep(.el-range-editor.el-input__wrapper:hover) {
  border-color: var(--color-primary);
}

.tf-desk__date-picker :deep(.el-range-input) {
  font-size: 12px;
}

.tf-desk__date-picker :deep(.el-range-separator) {
  font-size: 12px;
  padding: 0 4px;
  color: var(--text-secondary);
}

.tf-desk__divider {
  width: 1px;
  height: 18px;
  background: var(--border-color);
  flex-shrink: 0;
}

.tf-desk__filters .tf-chip {
  height: 30px;
  padding: 0 12px;
  border-radius: 15px;
  font-size: 12px;
}

.tf-desk__filters .tf-chip__icon {
  font-size: 13px;
}

.tf-desk__clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 30px;
  padding: 0 10px;
  border: none;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 500;
  font-family: inherit;
  color: var(--text-secondary);
  background: transparent;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  margin-left: auto;
  flex-shrink: 0;
}

.tf-desk__clear-btn:hover {
  color: #e53935;
  background: rgba(229, 57, 53, 0.06);
}
</style>

<style>
@media (max-width: 767px) {
  .timeline-filter-date-popper-mobile.el-popper {
    max-width: min(calc(100vw - 24px), 360px) !important;
  }

  .timeline-filter-date-popper-mobile .el-picker-panel {
    width: 100% !important;
  }
}
</style>
