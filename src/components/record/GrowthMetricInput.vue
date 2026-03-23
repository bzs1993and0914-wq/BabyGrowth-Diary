<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { createGrowthMetric, deleteGrowthMetric } from '@/api/growth-metrics'
import type { GrowthMetricResponse, GrowthMetricCreate } from '@/types/api'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  dailyRecordId: number
  existingMetrics: GrowthMetricResponse[]
}>()

type MetricType = 'height' | 'weight' | 'head_circumference'

const metrics = ref<GrowthMetricResponse[]>([])

const metricLabels: Record<MetricType, { label: string; unit: string }> = {
  height: { label: '身高', unit: 'cm' },
  weight: { label: '体重', unit: 'kg' },
  head_circumference: { label: '头围', unit: 'cm' },
}

const newType = ref<MetricType>('height')
const newValue = ref<number | undefined>(undefined)
const saving = ref(false)

onMounted(() => {
  metrics.value = [...props.existingMetrics]
})

function hasMetric(type: MetricType) {
  return metrics.value.some((m) => m.metric_type === type)
}

async function addMetric() {
  if (newValue.value === undefined || newValue.value <= 0) {
    ElMessage.warning('请输入有效数值')
    return
  }

  saving.value = true
  try {
    const data: GrowthMetricCreate = {
      daily_record_id: props.dailyRecordId,
      metric_type: newType.value,
      value: newValue.value,
      unit: metricLabels[newType.value].unit,
    }
    const created = await createGrowthMetric(data)
    metrics.value.push(created)
    newValue.value = undefined
    ElMessage.success('已添加')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '添加失败')
  } finally {
    saving.value = false
  }
}

async function removeMetric(id: number) {
  try {
    await deleteGrowthMetric(id)
    metrics.value = metrics.value.filter((m) => m.id !== id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}
</script>

<template>
  <div class="growth-input">
    <h4 class="section-title">成长数据</h4>

    <div v-if="metrics.length" class="metric-list">
      <div v-for="m in metrics" :key="m.id" class="metric-row">
        <span class="metric-label">{{ metricLabels[m.metric_type as MetricType]?.label || m.metric_type }}</span>
        <span class="metric-value">{{ m.value }} {{ m.unit }}</span>
        <el-button
          :icon="Delete"
          size="small"
          text
          type="danger"
          @click="removeMetric(m.id)"
        />
      </div>
    </div>

    <div class="add-row">
      <el-select v-model="newType" size="small" style="width: 100px">
        <el-option
          v-for="(info, key) in metricLabels"
          :key="key"
          :label="info.label"
          :value="key"
          :disabled="hasMetric(key as MetricType)"
        />
      </el-select>
      <el-input-number
        v-model="newValue"
        :min="0"
        :precision="1"
        :step="0.1"
        size="small"
        placeholder="数值"
        style="width: 120px"
      />
      <span class="unit-label">{{ metricLabels[newType].unit }}</span>
      <el-button
        :icon="Plus"
        type="primary"
        size="small"
        :loading="saving"
        @click="addMetric"
      >
        添加
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.growth-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.metric-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
}

.metric-label {
  font-size: 14px;
  color: var(--text-secondary);
  width: 60px;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.add-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.unit-label {
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
