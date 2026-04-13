<script setup lang="ts">
import { onMounted, onUnmounted, computed, watch } from 'vue'
import { useRecordsStore } from '@/stores/records'
import type { ViewGranularity, LayoutMode } from '@/types/models'
import type { RecordListItem } from '@/types/api'
import TimelineFilter from '@/components/timeline/TimelineFilter.vue'
import TimelineCard from '@/components/timeline/TimelineCard.vue'
import TimelineGroup from '@/components/timeline/TimelineGroup.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import {
  formatIsoWeekTitle,
  getISOWeekData,
  parseLocalYmd,
} from '@/utils/timelineGrouping'

const store = useRecordsStore()

watch(
  () => [
    store.timeline.granularity,
    store.timeline.searchQuery,
    store.timeline.dateFrom,
    store.timeline.dateTo,
    store.timeline.milestoneOnly,
    store.timeline.allergyOnly,
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

interface GroupBucket {
  sortKey: number
  title: string
  items: RecordListItem[]
}

const groupedItems = computed<GroupedItems[]>(() => {
  if (!isGrouped.value) return []
  const groups = new Map<string, GroupBucket>()

  for (const item of store.items) {
    const d = parseLocalYmd(item.date)
    let mapKey: string
    let title: string
    let sortKey: number

    switch (store.timeline.granularity) {
      case 'week': {
        const { isoYear, isoWeek } = getISOWeekData(d)
        title = formatIsoWeekTitle(isoYear, isoWeek)
        mapKey = title
        sortKey = isoYear * 100 + isoWeek
        break
      }
      case 'month': {
        const y = d.getFullYear()
        const m = d.getMonth() + 1
        title = `${y}年${m}月`
        mapKey = `${y}-${String(m).padStart(2, '0')}`
        sortKey = y * 100 + m
        break
      }
      case 'year': {
        const y = d.getFullYear()
        title = `${y}年`
        mapKey = String(y)
        sortKey = y
        break
      }
      default:
        mapKey = item.date
        title = item.date
        sortKey = 0
    }

    if (!groups.has(mapKey)) {
      groups.set(mapKey, { sortKey, title, items: [] })
    }
    groups.get(mapKey)!.items.push(item)
  }

  return Array.from(groups.values())
    .sort((a, b) => b.sortKey - a.sortKey)
    .map(({ title, items }) => ({ title, items }))
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
  store.loadRecords()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="timeline-view">
    <TimelineFilter
      v-model:allergy-only="store.timeline.allergyOnly"
      v-model:milestone-only="store.timeline.milestoneOnly"
      :granularity="store.timeline.granularity"
      :layout="store.timeline.layout"
      @update:granularity="handleGranularity"
      @update:layout="handleLayout"
      @update:search="handleSearch"
      @update:date-range="handleDateRange"
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
      v-else-if="store.timeline.allergyOnly"
      icon="⚠️"
      title="暂无过敏相关记录"
      description="在新建或编辑记录时填写「宝宝过敏食物」后，打开「查看过敏记录」即可在此集中浏览"
      action-text="新建记录"
      action-route="/record/new"
    />

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

@media (max-width: 767px) {
  .day-grid.flat {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .day-grid.collapsed {
    gap: 6px;
  }

  .loading-more {
    padding: 20px 0;
    font-size: 13px;
  }

  .end-hint {
    padding: 20px 0;
    font-size: 12px;
  }
}
</style>
