<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { ViewGranularity, LayoutMode } from '@/types/models'

const props = defineProps<{
  granularity: ViewGranularity
  layout: LayoutMode
  milestoneOnly: boolean
}>()

const emit = defineEmits<{
  'update:granularity': [value: ViewGranularity]
  'update:layout': [value: LayoutMode]
  'update:search': [value: string]
  'update:dateRange': [from: string | null, to: string | null]
  'update:milestoneOnly': [value: boolean]
}>()

const searchText = ref('')
const dateRange = ref<[string, string] | null>(null)

const granularityOptions = [
  { label: '日', value: 'day' as ViewGranularity },
  { label: '周', value: 'week' as ViewGranularity },
  { label: '月', value: 'month' as ViewGranularity },
  { label: '年', value: 'year' as ViewGranularity },
]

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
</script>

<template>
  <div class="timeline-filter">
    <div class="filter-row">
      <el-radio-group
        :model-value="props.granularity"
        size="small"
        @change="emit('update:granularity', $event as ViewGranularity)"
      >
        <el-radio-button
          v-for="opt in granularityOptions"
          :key="opt.value"
          :value="opt.value"
        >
          {{ opt.label }}
        </el-radio-button>
      </el-radio-group>

      <el-input
        v-model="searchText"
        placeholder="搜索记录..."
        :prefix-icon="Search"
        clearable
        size="small"
        class="search-input"
      />

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        size="small"
        value-format="YYYY-MM-DD"
        class="date-picker"
        @change="onDateRangeChange"
      />

      <div class="filter-toggles">
        <el-tooltip content="仅显示里程碑" placement="top">
          <el-switch
            :model-value="props.milestoneOnly"
            active-text="里程碑"
            size="small"
            @change="emit('update:milestoneOnly', $event as boolean)"
          />
        </el-tooltip>

        <el-button-group size="small">
          <el-button
            :type="props.layout === 'flat' ? 'primary' : 'default'"
            @click="emit('update:layout', 'flat')"
          >
            平铺
          </el-button>
          <el-button
            :type="props.layout === 'collapsed' ? 'primary' : 'default'"
            @click="emit('update:layout', 'collapsed')"
          >
            折叠
          </el-button>
        </el-button-group>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-filter {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px var(--shadow-color);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input {
  width: 180px;
}

.date-picker {
  max-width: 260px;
}

.filter-toggles {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}
</style>
