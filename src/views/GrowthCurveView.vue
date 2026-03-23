<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import { fetchGrowthCurve } from '@/api/growth-metrics'
import type { GrowthCurveData } from '@/types/api'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

type MetricType = 'height' | 'weight' | 'head_circumference'

const metricOptions: { label: string; value: MetricType; unit: string; color: string }[] = [
  { label: '身高', value: 'height', unit: 'cm', color: '#409eff' },
  { label: '体重', value: 'weight', unit: 'kg', color: '#f0883e' },
  { label: '头围', value: 'head_circumference', unit: 'cm', color: '#67c23a' },
]

const selectedMetric = ref<MetricType>('height')
const dateRange = ref<[string, string] | null>(null)
const curveData = ref<GrowthCurveData | null>(null)
const loading = ref(true)

const currentOption = computed(() => metricOptions.find((o) => o.value === selectedMetric.value)!)

async function loadData() {
  loading.value = true
  try {
    curveData.value = await fetchGrowthCurve({
      metric_type: selectedMetric.value,
      date_from: dateRange.value?.[0],
      date_to: dateRange.value?.[1],
    })
  } catch {
    curveData.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch([selectedMetric, dateRange], loadData)

const chartOption = computed(() => {
  if (!curveData.value || !curveData.value.dates.length) return null

  const opt = currentOption.value
  return {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        return `${p.axisValue}<br/>${opt.label}: <b>${p.value} ${opt.unit}</b>`
      },
    },
    grid: {
      left: 60,
      right: 24,
      top: 40,
      bottom: 40,
    },
    xAxis: {
      type: 'category',
      data: curveData.value.dates,
      axisLabel: {
        rotate: 30,
        fontSize: 11,
        color: 'var(--text-secondary)',
      },
      axisLine: { lineStyle: { color: 'var(--border-color)' } },
    },
    yAxis: {
      type: 'value',
      name: `${opt.label} (${opt.unit})`,
      nameTextStyle: { fontSize: 12, color: 'var(--text-secondary)' },
      axisLabel: { fontSize: 11, color: 'var(--text-secondary)' },
      splitLine: { lineStyle: { color: 'var(--border-color)', type: 'dashed' } },
    },
    series: [
      {
        type: 'line',
        data: curveData.value.values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: opt.color },
        itemStyle: { color: opt.color },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: opt.color + '30' },
              { offset: 1, color: opt.color + '05' },
            ],
          },
        },
      },
    ],
  }
})

const hasData = computed(() => curveData.value && curveData.value.dates.length > 0)
</script>

<template>
  <div class="growth-curve-view">
    <h2 class="page-title">成长曲线</h2>

    <div class="controls">
      <el-radio-group v-model="selectedMetric" size="small">
        <el-radio-button
          v-for="opt in metricOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </el-radio-button>
      </el-radio-group>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        size="small"
        value-format="YYYY-MM-DD"
        clearable
      />
    </div>

    <LoadingSkeleton v-if="loading" type="detail" />

    <div v-else-if="hasData && chartOption" class="chart-container">
      <v-chart :option="chartOption" autoresize class="chart" />
    </div>

    <EmptyState
      v-else
      icon="📈"
      title="暂无数据"
      description="在记录中添加身高、体重等成长数据后，这里会展示成长曲线"
      action-text="添加记录"
      action-route="/record/new"
    />
  </div>
</template>

<style scoped>
.growth-curve-view {
  min-height: 60vh;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.chart-container {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.chart {
  width: 100%;
  height: 400px;
}
</style>
