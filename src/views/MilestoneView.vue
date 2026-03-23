<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordsStore } from '@/stores/records'
import { useMilestonesStore } from '@/stores/milestones'
import apiClient from '@/api/client'
import MilestoneMarker from '@/components/timeline/MilestoneMarker.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const recordsStore = useRecordsStore()
const milestonesStore = useMilestonesStore()
const loading = ref(true)

const baseUrl = apiClient.defaults.baseURL ?? ''

interface MilestoneItem {
  date: string
  name: string
  icon: string
  categoryName: string
  thumbnail: string | null
}

const milestoneItems = ref<MilestoneItem[]>([])

onMounted(async () => {
  try {
    await Promise.all([
      milestonesStore.loadCategories(),
      recordsStore.loadRecords(),
    ])

    milestoneItems.value = recordsStore.items
      .filter((i) => i.has_milestone)
      .map((i) => ({
        date: i.date,
        name: i.milestone_name || '',
        icon: i.milestone_icon || 'Star',
        categoryName: '',
        thumbnail: i.first_thumbnail
          ? i.first_thumbnail.startsWith('http')
            ? i.first_thumbnail
            : `${baseUrl}${i.first_thumbnail}`
          : null,
      }))
  } finally {
    loading.value = false
  }
})

function formattedDate(d: string) {
  const dt = new Date(d)
  return `${dt.getFullYear()}年${dt.getMonth() + 1}月${dt.getDate()}日`
}

function goDetail(date: string) {
  router.push(`/record/${date}`)
}
</script>

<template>
  <div class="milestone-view">
    <h2 class="page-title">里程碑</h2>

    <LoadingSkeleton v-if="loading" type="list" :count="5" />

    <template v-else-if="milestoneItems.length">
      <div class="milestone-timeline">
        <div
          v-for="item in milestoneItems"
          :key="item.date + item.name"
          class="milestone-card"
          @click="goDetail(item.date)"
        >
          <div class="card-left">
            <div class="timeline-dot" />
            <div class="timeline-line" />
          </div>
          <div class="card-content">
            <div class="card-date">{{ formattedDate(item.date) }}</div>
            <MilestoneMarker :name="item.name" :icon="item.icon" :category-name="item.categoryName" />
            <img
              v-if="item.thumbnail"
              :src="item.thumbnail"
              class="card-thumb"
              @error="($event.target as HTMLImageElement).style.display = 'none'"
            />
          </div>
        </div>
      </div>
    </template>

    <EmptyState
      v-else
      icon="🏆"
      title="还没有里程碑"
      description="在记录详情中标记宝宝的成长里程碑"
      action-text="去看看时间轴"
      action-route="/"
    />
  </div>
</template>

<style scoped>
.milestone-view {
  min-height: 60vh;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.milestone-timeline {
  display: flex;
  flex-direction: column;
}

.milestone-card {
  display: flex;
  gap: 16px;
  cursor: pointer;
  padding-bottom: 4px;
}

.card-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-primary);
  flex-shrink: 0;
  margin-top: 4px;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: var(--timeline-line);
  margin-top: 4px;
}

.card-content {
  flex: 1;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px var(--shadow-color);
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform 0.15s;
}

.card-content:hover {
  transform: translateX(4px);
}

.card-date {
  font-size: 13px;
  color: var(--text-secondary);
}

.card-thumb {
  width: 100%;
  max-height: 160px;
  object-fit: cover;
  border-radius: 8px;
  margin-top: 4px;
}
</style>
