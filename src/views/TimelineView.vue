<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { useRecordsStore } from '@/stores/records'
import type { ViewGranularity, LayoutMode } from '@/types/models'
import type { RecordListItem } from '@/types/api'
import TimelineFilter from '@/components/timeline/TimelineFilter.vue'
import TimelineCard from '@/components/timeline/TimelineCard.vue'
import TimelineGroup from '@/components/timeline/TimelineGroup.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const store = useRecordsStore()

onMounted(() => {
  store.loadRecords()
})

watch(
  () => [
    store.timeline.granularity,
    store.timeline.searchQuery,
    store.timeline.dateFrom,
    store.timeline.dateTo,
    store.timeline.milestoneOnly,
  ],
  () => {
    store.timeline.page = 1
    store.loadRecords()
  },
)

const isGrouped = computed(() => store.timeline.granularity !== 'day')

interface GroupedItems {
  title: string
  items: RecordListItem[]
}

const groupedItems = computed<GroupedItems[]>(() => {
  if (!isGrouped.value) return []
  const groups = new Map<string, RecordListItem[]>()

  for (const item of store.items) {
    const d = new Date(item.date)
    let key: string
    switch (store.timeline.granularity) {
      case 'week': {
        const weekStart = new Date(d)
        weekStart.setDate(d.getDate() - d.getDay())
        key = `${weekStart.getFullYear()}-W${String(Math.ceil((weekStart.getDate()) / 7 + 1)).padStart(2, '0')}`
        break
      }
      case 'month':
        key = `${d.getFullYear()}年${d.getMonth() + 1}月`
        break
      case 'year':
        key = `${d.getFullYear()}年`
        break
      default:
        key = item.date
    }
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(item)
  }

  return Array.from(groups.entries()).map(([title, items]) => ({ title, items }))
})

function handleGranularity(v: ViewGranularity) {
  store.setGranularity(v)
}

function handleLayout(v: LayoutMode) {
  store.setLayout(v)
}

function handleSearch(v: string) {
  store.setSearch(v)
}

function handleDateRange(from: string | null, to: string | null) {
  store.setDateRange(from, to)
}

function handleMilestoneOnly(v: boolean) {
  store.setMilestoneOnly(v)
}

function loadMore() {
  if (store.hasMore && !store.loading) {
    store.nextPage()
    store.loadRecords(true)
  }
}

function handleScroll() {
  const scrollY = window.scrollY + window.innerHeight
  const docHeight = document.documentElement.scrollHeight
  if (docHeight - scrollY < 200) {
    loadMore()
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="timeline-view">
    <div class="home-entry-bar">
      <router-link class="allergy-entry-link" to="/allergy-records">
        ⚠️ 查看过敏记录
      </router-link>
    </div>
    <TimelineFilter
      :granularity="store.timeline.granularity"
      :layout="store.timeline.layout"
      :milestone-only="store.timeline.milestoneOnly"
      @update:granularity="handleGranularity"
      @update:layout="handleLayout"
      @update:search="handleSearch"
      @update:date-range="handleDateRange"
      @update:milestone-only="handleMilestoneOnly"
    />

    <LoadingSkeleton v-if="store.loading && !store.items.length" type="card" :count="4" />

    <template v-else-if="store.items.length">
      <!-- Grouped view (week/month/year) -->
      <template v-if="isGrouped">
        <TimelineGroup
          v-for="group in groupedItems"
          :key="group.title"
          :title="group.title"
          :items="group.items"
          :layout="store.timeline.layout"
        />
      </template>

      <!-- Day (flat) view -->
      <div v-else :class="['day-grid', store.timeline.layout]">
        <TimelineCard
          v-for="item in store.items"
          :key="item.date"
          :item="item"
          :layout="store.timeline.layout"
        />
      </div>

      <div v-if="store.loading" class="loading-more">
        <el-icon class="is-loading" :size="20">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8Z"/>
          </svg>
        </el-icon>
        <span>加载中...</span>
      </div>

      <div v-if="!store.hasMore && store.items.length > 0" class="end-hint">
        已加载全部记录
      </div>
    </template>

    <EmptyState
      v-else
      icon="📷"
      title="还没有记录"
      description="开始记录宝宝成长的每一个瞬间吧"
      action-text="添加第一条记录"
      action-route="/record/new"
    />
  </div>
</template>

<style scoped>
.timeline-view {
  min-height: 60vh;
}

.home-entry-bar {
  margin-bottom: 12px;
}

.allergy-entry-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #bf360c;
  background: linear-gradient(135deg, #ffe0b2, #ffccbc);
  text-decoration: none;
  border: 1px solid #ff8a65;
  transition: transform 0.15s, box-shadow 0.15s;
}

.allergy-entry-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(230, 74, 25, 0.25);
}

.day-grid.flat {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.day-grid.collapsed {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.end-hint {
  text-align: center;
  padding: 24px 0;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
