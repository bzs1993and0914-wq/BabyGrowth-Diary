<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import type { ViewGranularity, LayoutMode } from '@/types/models'

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

function toggleAllergyLabel() {
  allergyOnly.value = !allergyOnly.value
}

function toggleMilestoneLabel() {
  milestoneOnly.value = !milestoneOnly.value
}
</script>

<template>
  <div class="timeline-filter">
    <div class="filter-row">
      <el-radio-group
        class="granularity-group"
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
        start-placeholder="开始"
        end-placeholder="结束"
        size="small"
        value-format="YYYY-MM-DD"
        class="date-picker"
        @change="onDateRangeChange"
      />

      <div class="filter-toggles">
        <div class="switch-pair-row">
          <div
            class="toggle-with-label filter-switch-wrap"
            title="仅显示填写过「宝宝过敏食物」的记录"
          >
            <el-switch v-model="allergyOnly" size="small" />
            <span
              class="toggle-label toggle-label--clickable"
              role="button"
              tabindex="0"
              @click="toggleAllergyLabel"
              @keydown.enter.prevent="toggleAllergyLabel"
              @keydown.space.prevent="toggleAllergyLabel"
            >
              查看过敏记录
            </span>
          </div>

          <div class="toggle-with-label filter-switch-wrap" title="仅显示里程碑记录">
            <el-switch v-model="milestoneOnly" size="small" />
            <span
              class="toggle-label toggle-label--clickable"
              role="button"
              tabindex="0"
              @click="toggleMilestoneLabel"
              @keydown.enter.prevent="toggleMilestoneLabel"
              @keydown.space.prevent="toggleMilestoneLabel"
            >
              里程碑
            </span>
          </div>
        </div>

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
  gap: 8px;
  flex-wrap: nowrap;
  min-width: 0;
  /* 极窄时横向滚动，避免折成两行 */
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  /* 预留横向滚动条槽位，避免出现时顶高一行造成上下抖动 */
  scrollbar-gutter: stable;
}

.granularity-group {
  flex-shrink: 0;
}

.search-input {
  width: 148px;
  min-width: 96px;
  flex: 0 1 148px;
}

.search-input :deep(.el-input__wrapper) {
  padding-left: 8px;
  padding-right: 8px;
}

.date-picker {
  width: 188px;
  max-width: 188px;
  min-width: 160px;
  flex: 0 1 188px;
}

.date-picker :deep(.el-range-input) {
  font-size: 12px;
}

.date-picker :deep(.el-range-separator) {
  padding: 0 2px;
  font-size: 12px;
}

.filter-toggles {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
  flex-shrink: 0;
}

/* 与图二一致：开关轨道 + 右侧文案，两项并排 */
.switch-pair-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
}

.toggle-with-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.filter-switch-wrap {
  cursor: default;
}

.toggle-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
}

.toggle-label--clickable {
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.toggle-label--clickable:focus-visible {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
  border-radius: 4px;
}

/* 筛选开关：关态浅灰轨道，开态主题色（过敏 / 里程碑一致） */
.filter-switch-wrap :deep(.el-switch__core) {
  border-color: transparent;
}

.filter-switch-wrap :deep(.el-switch:not(.is-checked) .el-switch__core) {
  background: var(--el-switch-off-color, #dcdce8) !important;
}

.filter-switch-wrap :deep(.el-switch.is-checked .el-switch__core) {
  background-color: var(--el-color-primary) !important;
}
</style>
