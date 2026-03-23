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

const route = useRoute()
const router = useRouter()
const store = useRecordsStore()
const showMilestonePicker = ref(false)

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

      <DiaryView
        :media-entries="record.media_entries"
        :text-entries="record.text_entries"
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
