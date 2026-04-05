<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Picture, VideoCamera } from '@element-plus/icons-vue'
import type { RecordListItem } from '@/types/api'
import type { LayoutMode } from '@/types/models'
import { buildMediaApiUrl } from '@/api/media'
import MilestoneMarker from './MilestoneMarker.vue'

const props = defineProps<{
  item: RecordListItem
  layout: LayoutMode
}>()

const router = useRouter()

const placeholderSrc = `${import.meta.env.BASE_URL}default-growth-placeholder.jpg`

/** 列表缩略图：有附件用首图；无附件且开启占位则用默认图；否则空白（与 use_default_media_placeholder 一致） */
const thumbnailSrc = computed(() => {
  if (!props.item.first_thumbnail) return ''
  return props.item.first_thumbnail.startsWith('http')
    ? props.item.first_thumbnail
    : buildMediaApiUrl(props.item.first_thumbnail)
})

const cardThumbSrc = computed(() => {
  if (thumbnailSrc.value) return thumbnailSrc.value
  if (props.item.use_default_media_placeholder) return placeholderSrc
  return ''
})

const formattedDate = computed(() => {
  const d = new Date(props.item.date)
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 周${weekDays[d.getDay()]}`
})

function goDetail() {
  router.push(`/record/${props.item.date}`)
}

function onThumbError(e: Event) {
  const img = e.target as HTMLImageElement
  if (props.item.use_default_media_placeholder) {
    img.src = placeholderSrc
  } else {
    img.removeAttribute('src')
  }
  img.onerror = null
}
</script>

<template>
  <div :class="['timeline-card', layout]" @click="goDetail">
    <template v-if="layout === 'flat'">
      <div class="card-thumb" :class="{ 'card-thumb--empty': !cardThumbSrc }">
        <img
          v-if="cardThumbSrc"
          :src="cardThumbSrc"
          alt="缩略图"
          class="default-thumb"
          @error="onThumbError"
        />
        <div v-else class="thumb-empty" aria-hidden="true">
          <el-icon :size="28"><Picture /></el-icon>
        </div>
        <span v-if="item.media_count > 1" class="media-badge">
          <el-icon><Picture /></el-icon>
          {{ item.media_count }}
        </span>
      </div>

      <div class="card-body">
        <div class="card-date">{{ formattedDate }}</div>
        <p v-if="item.preview_text" class="card-text">
          {{ item.preview_text }}
        </p>
        <div class="card-meta">
          <span v-if="item.media_count" class="meta-item">
            <el-icon><Picture /></el-icon> {{ item.media_count }}张
          </span>
          <span v-if="item.text_count" class="meta-item">
            <el-icon><VideoCamera /></el-icon> {{ item.text_count }}条文字
          </span>
          <MilestoneMarker
            v-if="
              item.has_milestone && item.milestone_name && item.milestone_icon
            "
            :name="item.milestone_name"
            :icon="item.milestone_icon"
            category-name=""
          />
        </div>
      </div>
    </template>

    <template v-else>
      <div
        class="collapsed-left"
        :class="{ 'collapsed-left--empty': !cardThumbSrc }"
      >
        <img
          v-if="cardThumbSrc"
          :src="cardThumbSrc"
          class="collapsed-thumb"
          alt=""
          @error="onThumbError"
        />
        <div v-else class="collapsed-thumb-empty" aria-hidden="true">
          <el-icon :size="22"><Picture /></el-icon>
        </div>
      </div>
      <span class="collapsed-date">{{ formattedDate }}</span>
      <span v-if="item.preview_text" class="collapsed-text">{{
        item.preview_text
      }}</span>
      <span class="collapsed-meta">{{ item.media_count }}张</span>
      <MilestoneMarker
        v-if="item.has_milestone && item.milestone_name && item.milestone_icon"
        :name="item.milestone_name"
        :icon="item.milestone_icon"
        category-name=""
      />
    </template>
  </div>
</template>

<style scoped>
.timeline-card {
  cursor: pointer;
  transition: all 0.2s;
}

.default-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.timeline-card.flat {
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.timeline-card.flat:hover {
  box-shadow: 0 4px 16px var(--shadow-color);
  transform: translateY(-2px);
}

.card-thumb {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: var(--bg-secondary);
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  opacity: 0.45;
}

.media-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 12px;
}

.card-body {
  padding: 14px 16px;
}

.card-date {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.card-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* Collapsed layout */
.timeline-card.collapsed {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--bg-card);
  box-shadow: 0 1px 3px var(--shadow-color);
}

.timeline-card.collapsed:hover {
  background: var(--color-primary-light);
}

.collapsed-left {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapsed-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.collapsed-thumb-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  opacity: 0.45;
}

.collapsed-date {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  flex-shrink: 0;
}

.collapsed-text {
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.collapsed-meta {
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
}
</style>
