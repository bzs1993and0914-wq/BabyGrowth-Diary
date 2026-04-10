<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'
import type { MediaEntryResponse, TextEntryResponse } from '@/types/api'
import { getMediaUrl } from '@/api/media'
import ImagePreview from '@/components/media/ImagePreview.vue'
import VideoThumbnailPreview from '@/components/media/VideoThumbnailPreview.vue'

/** 移动端：长按后开始拖动排序；略移动则视为滚动/误触，取消长按 */
const TOUCH_LONG_PRESS_MS = 480
const TOUCH_MOVE_CANCEL_PX = 14

const props = withDefaults(
  defineProps<{
    mediaEntries: MediaEntryResponse[]
    textEntries: TextEntryResponse[]
    useDefaultMediaPlaceholder?: boolean
    /** 详情页多图网格：启用后可拖拽调整顺序（首张影响时间轴缩略图） */
    reorderable?: boolean
    reorderBusy?: boolean
  }>(),
  { useDefaultMediaPlaceholder: false, reorderable: false, reorderBusy: false }
)

const emit = defineEmits<{
  reorderMedia: [orderedIds: number[]]
}>()

const placeholderSrc = `${import.meta.env.BASE_URL}default-growth-placeholder.jpg`

const multiMedia = computed(() => props.mediaEntries.length > 1)
const gridClass = computed(() => {
  const n = props.mediaEntries.length
  if (n <= 1) return ''
  if (n === 2) return 'grid-2'
  if (n <= 4) return 'grid-4'
  if (n <= 6) return 'grid-6'
  return 'grid-9'
})

const draggingIndex = ref<number | null>(null)
const dragOverIndex = ref<number | null>(null)
/** 移动端长按已激活，正在跨格拖动 */
const touchDragging = ref(false)

const cellDraggable = computed(
  () => props.reorderable && props.mediaEntries.length > 1 && !props.reorderBusy
)

let longPressTimer: ReturnType<typeof setTimeout> | null = null
let touchStartX = 0
let touchStartY = 0
let onDocTouchMove: ((e: TouchEvent) => void) | null = null
let onDocTouchEnd: ((e: TouchEvent) => void) | null = null

function clearLongPressTimer() {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
}

function removeDocumentTouchListeners() {
  if (onDocTouchMove) {
    document.removeEventListener('touchmove', onDocTouchMove)
    onDocTouchMove = null
  }
  if (onDocTouchEnd) {
    document.removeEventListener('touchend', onDocTouchEnd)
    document.removeEventListener('touchcancel', onDocTouchEnd)
    onDocTouchEnd = null
  }
}

function resolveTouchDropIndex(clientX: number, clientY: number) {
  const el = document.elementFromPoint(clientX, clientY)
  const cell = el?.closest('[data-reorder-cell]') as HTMLElement | null
  if (!cell?.dataset.reorderIdx) return null
  const n = Number(cell.dataset.reorderIdx)
  return Number.isNaN(n) ? null : n
}

function bindDocumentTouchDrag() {
  removeDocumentTouchListeners()
  onDocTouchMove = (e: TouchEvent) => {
    if (!touchDragging.value) return
    e.preventDefault()
    const t = e.touches[0]
    if (!t) return
    const over = resolveTouchDropIndex(t.clientX, t.clientY)
    if (over !== null) dragOverIndex.value = over
  }
  onDocTouchEnd = (e: TouchEvent) => {
    if (!touchDragging.value) {
      removeDocumentTouchListeners()
      return
    }
    e.preventDefault()
    const from = draggingIndex.value
    let to = dragOverIndex.value
    const tc = e.changedTouches[0]
    if (tc) {
      const over = resolveTouchDropIndex(tc.clientX, tc.clientY)
      if (over !== null) to = over
    }
    touchDragging.value = false
    draggingIndex.value = null
    dragOverIndex.value = null
    removeDocumentTouchListeners()
    if (from !== null && to !== null && from !== to) {
      emit('reorderMedia', reorderIds(from, to))
    }
  }
  document.addEventListener('touchmove', onDocTouchMove, { passive: false })
  document.addEventListener('touchend', onDocTouchEnd, { passive: false })
  document.addEventListener('touchcancel', onDocTouchEnd, { passive: false })
}

onUnmounted(() => {
  clearLongPressTimer()
  removeDocumentTouchListeners()
})

function reorderIds(from: number, to: number): number[] {
  const next = props.mediaEntries.map((m) => m.id)
  const [removed] = next.splice(from, 1)
  next.splice(to, 0, removed)
  return next
}

function onDragStart(e: DragEvent, index: number) {
  draggingIndex.value = index
  e.dataTransfer?.setData('text/plain', String(index))
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}

function onDragOver(e: DragEvent, index: number) {
  e.preventDefault()
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
  dragOverIndex.value = index
}

function onDragLeave(index: number) {
  if (dragOverIndex.value === index) dragOverIndex.value = null
}

function onDrop(e: DragEvent, index: number) {
  e.preventDefault()
  const raw = e.dataTransfer?.getData('text/plain')
  const from =
    raw !== '' && raw !== undefined ? Number(raw) : draggingIndex.value
  dragOverIndex.value = null
  draggingIndex.value = null
  if (from === null || Number.isNaN(from)) return
  if (from === index) return
  emit('reorderMedia', reorderIds(from, index))
}

function onDragEnd() {
  draggingIndex.value = null
  dragOverIndex.value = null
}

function onCellTouchStart(e: TouchEvent, idx: number) {
  if (!cellDraggable.value || e.touches.length !== 1) return
  clearLongPressTimer()
  const t = e.touches[0]
  touchStartX = t.clientX
  touchStartY = t.clientY
  longPressTimer = setTimeout(() => {
    longPressTimer = null
    touchDragging.value = true
    draggingIndex.value = idx
    dragOverIndex.value = idx
    bindDocumentTouchDrag()
    try {
      navigator.vibrate?.(12)
    } catch {
      /* ignore */
    }
  }, TOUCH_LONG_PRESS_MS)
}

function onCellTouchMove(e: TouchEvent) {
  if (!cellDraggable.value || touchDragging.value || !longPressTimer) return
  const t = e.touches[0]
  if (!t) return
  const dx = t.clientX - touchStartX
  const dy = t.clientY - touchStartY
  if (dx * dx + dy * dy > TOUCH_MOVE_CANCEL_PX * TOUCH_MOVE_CANCEL_PX) {
    clearLongPressTimer()
  }
}

function onCellTouchEnd() {
  if (touchDragging.value) return
  clearLongPressTimer()
}
</script>

<template>
  <div class="diary-view">
    <!-- 无媒体：仅默认图占位 -->
    <template v-if="mediaEntries.length === 0 && useDefaultMediaPlaceholder">
      <div class="media-frame placeholder-frame">
        <img
          :src="placeholderSrc"
          alt="宝宝成长曲线默认配图"
          class="placeholder-img"
        />
      </div>
      <div v-for="text in textEntries" :key="text.id" class="text-block">
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>

    <!-- 无媒体无占位：仅文字 -->
    <template
      v-else-if="mediaEntries.length === 0 && !useDefaultMediaPlaceholder"
    >
      <div v-for="text in textEntries" :key="text.id" class="text-block">
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>

    <!-- 多图：网格 + 文字 -->
    <template v-else-if="multiMedia">
      <div :class="['multi-media-grid', gridClass]">
        <div
          v-for="(media, idx) in mediaEntries"
          :key="media.id"
          class="grid-cell"
          :data-reorder-cell="cellDraggable ? '' : undefined"
          :data-reorder-idx="cellDraggable ? idx : undefined"
          :class="{
            'is-reorderable': cellDraggable,
            'drag-over': dragOverIndex === idx,
            'is-dragging': draggingIndex === idx,
            'touch-dragging': touchDragging && draggingIndex === idx,
          }"
          :draggable="cellDraggable"
          @dragstart="cellDraggable && onDragStart($event, idx)"
          @dragover="cellDraggable && onDragOver($event, idx)"
          @dragleave="cellDraggable && onDragLeave(idx)"
          @drop="cellDraggable && onDrop($event, idx)"
          @dragend="cellDraggable && onDragEnd()"
          @touchstart="cellDraggable && onCellTouchStart($event, idx)"
          @touchmove.passive="cellDraggable && onCellTouchMove($event)"
          @touchend="cellDraggable && onCellTouchEnd()"
          @touchcancel="cellDraggable && onCellTouchEnd()"
        >
          <div class="media-frame">
            <ImagePreview
              v-if="media.media_type === 'image'"
              :src="getMediaUrl(media.id)"
              :alt="media.description || media.original_filename || ''"
              :suppress-native-drag="cellDraggable"
            />
            <VideoThumbnailPreview
              v-else
              :media="media"
              :suppress-native-drag="cellDraggable"
            />
          </div>
          <p v-if="media.description" class="media-caption">
            {{ media.description }}
          </p>
        </div>
      </div>
      <div v-for="text in textEntries" :key="text.id" class="text-block">
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>

    <!-- 单图：与文字交错（保持原有体验） -->
    <template v-else>
      <div
        v-for="(media, idx) in mediaEntries"
        :key="media.id"
        class="diary-block"
      >
        <div class="media-frame">
          <ImagePreview
            v-if="media.media_type === 'image'"
            :src="getMediaUrl(media.id)"
            :alt="media.description || media.original_filename || ''"
          />
          <VideoThumbnailPreview v-else :media="media" />
        </div>
        <p v-if="media.description" class="media-caption">
          {{ media.description }}
        </p>

        <div v-if="textEntries[idx]" class="text-block">
          <p class="diary-text">{{ textEntries[idx].content }}</p>
        </div>
      </div>

      <div
        v-for="text in textEntries.slice(mediaEntries.length)"
        :key="text.id"
        class="text-block"
      >
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.diary-view {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.diary-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.media-frame {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px var(--shadow-color);
}

.placeholder-frame {
  max-height: 360px;
  background: var(--bg-secondary);
}

.placeholder-img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: contain;
}

.multi-media-grid {
  display: grid;
  gap: 10px;
  width: 100%;
}

.grid-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-4 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-6 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-9 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-cell .media-frame {
  aspect-ratio: 1;
}

.grid-cell .media-frame :deep(img),
.grid-cell .media-frame :deep(video) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.grid-cell.is-reorderable {
  cursor: grab;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
}

.grid-cell.is-reorderable:active {
  cursor: grabbing;
}

.grid-cell.drag-over {
  outline: 2px dashed var(--el-color-primary);
  outline-offset: 3px;
  border-radius: 12px;
}

.grid-cell.is-dragging {
  opacity: 0.6;
}

.grid-cell.touch-dragging {
  z-index: 2;
  opacity: 0.92;
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
}

.media-caption {
  font-size: 14px;
  color: var(--text-secondary);
  font-style: italic;
  text-align: center;
  padding: 0 16px;
}

.text-block {
  padding: 16px 0;
}

.diary-text {
  font-family: 'Georgia', 'Noto Serif SC', 'STSong', serif;
  font-size: 16px;
  line-height: 1.9;
  color: var(--text-primary);
  text-indent: 2em;
  white-space: pre-wrap;
}
</style>
