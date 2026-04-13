<script setup lang="ts">
import { ref, computed } from 'vue'
import type { RecordListItem } from '@/types/api'
import type { LayoutMode } from '@/types/models'
import TimelineCard from './TimelineCard.vue'

const props = defineProps<{
  title: string
  items: RecordListItem[]
  layout: LayoutMode
}>()

const collapsed = ref(false)

const mediaTotalCount = computed(() =>
  props.items.reduce((s, i) => s + i.media_count, 0),
)
</script>

<template>
  <div class="timeline-group">
    <div class="group-header" @click="collapsed = !collapsed">
      <div class="group-title">
        <span class="group-name">{{ title }}</span>
        <span class="group-stats">{{ items.length }}条记录 · {{ mediaTotalCount }}张照片</span>
      </div>
      <el-icon class="collapse-icon" :class="{ open: !collapsed }">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z" />
        </svg>
      </el-icon>
    </div>

    <transition name="slide">
      <div v-show="!collapsed" class="group-body" :class="layout">
        <TimelineCard
          v-for="item in items"
          :key="item.date"
          :item="item"
          :layout="layout"
        />
      </div>
    </transition>
  </div>
</template>

<style scoped>
.timeline-group {
  margin-bottom: 24px;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 4px 12px;
  cursor: pointer;
  user-select: none;
}

.group-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.group-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.group-stats {
  font-size: 13px;
  color: var(--text-secondary);
}

.collapse-icon {
  transition: transform 0.2s;
  color: var(--text-secondary);
}

.collapse-icon.open {
  transform: rotate(180deg);
}

.group-body.flat {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.group-body.collapsed {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 2000px;
}

/* ═══ 移动端优化 ═══ */
@media (max-width: 767px) {
  .timeline-group {
    margin-bottom: 20px;
  }

  .group-header {
    padding: 6px 2px 10px;
    -webkit-tap-highlight-color: transparent;
  }

  .group-header:active {
    opacity: 0.7;
  }

  .group-title {
    flex-direction: column;
    gap: 2px;
  }

  .group-name {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.3px;
  }

  .group-stats {
    font-size: 12px;
  }

  .group-body.flat {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .group-body.collapsed {
    gap: 6px;
  }
}
</style>
