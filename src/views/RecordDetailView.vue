<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Edit, Delete } from '@element-plus/icons-vue'
import { useRecordsStore } from '@/stores/records'
import DiaryView from '@/components/record/DiaryView.vue'
import MilestoneMarker from '@/components/timeline/MilestoneMarker.vue'
import MilestonePicker from '@/components/record/MilestonePicker.vue'
import GrowthMetricInput from '@/components/record/GrowthMetricInput.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { updateMedia } from '@/api/media'

const route = useRoute()
const router = useRouter()
const store = useRecordsStore()
const showMilestonePicker = ref(false)
const reorderBusy = ref(false)

const date = computed(() => route.params.date as string)

const record = computed(() => store.currentRecord)

const formattedDate = computed(() => {
  if (!record.value) return ''
  const d = new Date(record.value.date)
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 周${weekDays[d.getDay()]}`
})

const metricLabels: Record<string, string> = {
  height: '身高',
  weight: '体重',
  head_circumference: '头围',
}

onMounted(async () => {
  try {
    await store.loadRecord(date.value)
  } catch {
    ElMessage.error('记录不存在')
    router.replace('/')
  }
})

function goEdit() {
  router.push(`/record/${date.value}/edit`)
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除这天的记录吗？删除后无法恢复。', '删除记录', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await store.removeRecord(date.value)
    ElMessage.success('已删除')
    router.replace('/')
  } catch {
    // cancelled
  }
}

function onMilestoneSaved() {
  store.loadRecord(date.value)
}

function syncListThumbnailForCurrentDate() {
  const r = store.currentRecord
  const d = date.value
  if (!r || r.date !== d) return
  const item = store.items.find((i) => i.date === d)
  if (!item) return
  let firstThumb: string | null = null
  for (const m of r.media_entries) {
    if (m.thumbnail_path) {
      firstThumb = `/api/media/${m.id}/thumbnail`
      break
    }
  }
  item.first_thumbnail = firstThumb
  item.use_default_media_placeholder =
    r.media_entries.length === 0 ||
    !r.media_entries.some((m) => m.thumbnail_path)
}

async function onReorderMedia(orderedIds: number[]) {
  if (!record.value || orderedIds.length < 2) return
  reorderBusy.value = true
  try {
    await Promise.all(
      orderedIds.map((id, i) => updateMedia(id, { sort_order: i }))
    )
    await store.loadRecord(date.value)
    syncListThumbnailForCurrentDate()
    ElMessage.success('排序已保存')
  } catch {
    ElMessage.error('保存排序失败，请重试')
    await store.loadRecord(date.value)
  } finally {
    reorderBusy.value = false
  }
}
</script>

<template>
  <div class="record-detail">
    <div class="detail-nav">
      <el-button text :icon="ArrowLeft" @click="router.push('/')">返回时间轴</el-button>
    </div>

    <LoadingSkeleton v-if="store.loading" type="detail" />

    <template v-else-if="record">
      <div class="detail-header">
        <h1 class="detail-date">{{ formattedDate }}</h1>
        <div class="detail-actions">
          <el-button :icon="Edit" @click="goEdit">编辑</el-button>
          <el-button type="danger" text :icon="Delete" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <div v-if="record.allergy_notes" class="allergy-alert">
        <strong>⚠️ 宝宝过敏食物</strong>
        <p>{{ record.allergy_notes }}</p>
      </div>

      <div v-if="record.milestone" class="milestone-section">
        <MilestoneMarker
          :name="record.milestone.name || ''"
          :icon="record.milestone.category_icon || 'Star'"
          :category-name="record.milestone.category_name || ''"
        />
        <p v-if="record.milestone.description" class="milestone-desc">
          {{ record.milestone.description }}
        </p>
      </div>

      <div v-if="record.growth_metrics.length" class="metrics-section">
        <div class="metrics-row">
          <div v-for="m in record.growth_metrics" :key="m.id" class="metric-chip">
            <span class="chip-label">{{ metricLabels[m.metric_type] || m.metric_type }}</span>
            <span class="chip-value">{{ m.value }} {{ m.unit }}</span>
          </div>
        </div>
      </div>

      <p v-if="record.media_entries.length > 1" class="reorder-hint">
        电脑端可直接拖动格子排序；手机和平板请先长按某一格，感到轻微震动后再拖到目标位置松手。保存后时间轴首张缩略图会与新顺序一致。
      </p>

      <DiaryView
        :media-entries="record.media_entries"
        :text-entries="record.text_entries"
        :use-default-media-placeholder="record.use_default_media_placeholder ?? false"
        :reorderable="record.media_entries.length > 1"
        :reorder-busy="reorderBusy"
        @reorder-media="onReorderMedia"
      />

      <div v-if="!record.milestone" class="milestone-action">
        <el-button round @click="showMilestonePicker = true">
          标记为里程碑
        </el-button>
      </div>

      <MilestonePicker
        v-model="showMilestonePicker"
        :daily-record-id="record.id"
        @saved="onMilestoneSaved"
      />
    </template>
  </div>
</template>

<style scoped>
.record-detail {
  max-width: 700px;
  margin: 0 auto;
}

.detail-nav {
  margin-bottom: 16px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-date {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.allergy-alert {
  background: linear-gradient(135deg, #ffe0b2, #ffccbc);
  border: 1px solid #ff8a65;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.allergy-alert strong {
  display: block;
  font-size: 15px;
  color: #bf360c;
  margin-bottom: 8px;
}

.allergy-alert p {
  margin: 0;
  font-size: 14px;
  color: #5d4037;
  line-height: 1.5;
  white-space: pre-wrap;
}

.milestone-section {
  background: linear-gradient(135deg, #fff8e1, #fff3e0);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.milestone-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.metrics-section {
  margin-bottom: 24px;
}

.metrics-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.metric-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 20px;
  border-radius: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
}

.reorder-hint {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.chip-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.chip-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

.milestone-action {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 20px;
}
</style>
