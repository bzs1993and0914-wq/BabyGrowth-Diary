<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Edit, Delete } from '@element-plus/icons-vue'
import { useParentWordsStore } from '@/stores/parentWords'
import { getMediaUrl, getThumbnailUrl } from '@/api/media'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTextHighlight } from '@/composables/useTextHighlight'
import type { HighlightResponse } from '@/types/api'

const route = useRoute()
const router = useRouter()
const store = useParentWordsStore()

const wordId = computed(() => Number(route.params.id))
const word = computed(() => store.currentWord)

const roleLabel = computed(() => {
  switch (word.value?.author_role) {
    case 'dad': return '爸爸'
    case 'mom': return '妈妈'
    default: return '父母'
  }
})

const roleClass = computed(() => {
  switch (word.value?.author_role) {
    case 'dad': return 'role-dad'
    case 'mom': return 'role-mom'
    default: return 'role-default'
  }
})

const formattedCreatedAt = computed(() => {
  if (!word.value) return ''
  const d = new Date(word.value.created_at)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

const showEdited = computed(() => {
  if (!word.value) return false
  return word.value.updated_at !== word.value.created_at
})

const formattedUpdatedAt = computed(() => {
  if (!word.value) return ''
  const d = new Date(word.value.updated_at)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

function openMedia(mediaId: number) {
  window.open(getMediaUrl(mediaId), '_blank')
}

const contentRef = ref<HTMLElement | null>(null)
const wordContent = computed(() => word.value?.content ?? '')
const wordHighlights = ref<HighlightResponse[]>([])

const {
  segments,
  saving,
  showToolbar,
  toolbarPos,
  handleSelection,
  addNewHighlight,
  removeHighlightsAt,
  dismissToolbar,
} = useTextHighlight(wordId, wordContent, wordHighlights)

const HIGHLIGHT_COLORS = [
  { value: 'yellow', label: '黄色', bg: '#fff3a8' },
  { value: 'green', label: '绿色', bg: '#b8f0c0' },
  { value: 'blue', label: '蓝色', bg: '#bde0fe' },
  { value: 'pink', label: '粉色', bg: '#ffc8dd' },
]

function getHighlightBg(color: string | null): string {
  const found = HIGHLIGHT_COLORS.find((c) => c.value === color)
  return found?.bg ?? '#fff3a8'
}

function onMouseUp() {
  if (!contentRef.value) return
  setTimeout(() => {
    handleSelection(contentRef.value!)
  }, 10)
}

function onClickHighlight(ids: number[], event: MouseEvent) {
  event.stopPropagation()
  ElMessageBox.confirm('取消选中内容的高亮？', '取消高亮', {
    confirmButtonText: '取消高亮',
    cancelButtonText: '保留',
    type: 'info',
  }).then(async () => {
    const { failed } = await removeHighlightsAt(ids)
    if (failed > 0) {
      ElMessage.warning(`${failed} 个高亮取消失败，请稍后重试`)
    }
  }).catch(() => {})
}

function onDocClick(e: MouseEvent) {
  if (showToolbar.value) {
    const toolbar = document.querySelector('.hl-toolbar')
    if (toolbar && !toolbar.contains(e.target as Node)) {
      dismissToolbar()
    }
  }
}

onMounted(async () => {
  try {
    await store.loadDetail(wordId.value)
    if (word.value) {
      wordHighlights.value = [...word.value.highlights]
    }
  } catch {
    ElMessage.error('记录不存在')
    router.replace('/parent-words')
  }
  document.addEventListener('click', onDocClick, true)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocClick, true)
})

function goEdit() {
  router.push(`/parent-words/${wordId.value}/edit`)
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除这篇心语吗？删除后无法恢复。', '删除心语', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await store.remove(wordId.value)
    ElMessage.success('已删除')
    router.push('/parent-words')
  } catch {
  }
}
</script>

<template>
  <div class="pw-detail-view">
    <div class="pw-detail-topbar">
      <el-button text @click="router.push('/parent-words')">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回列表</span>
      </el-button>
      <div class="pw-detail-actions">
        <el-button :icon="Edit" round @click="goEdit">编辑</el-button>
        <el-button :icon="Delete" round type="danger" plain @click="handleDelete">删除</el-button>
      </div>
    </div>

    <LoadingSkeleton v-if="store.loading && !word" type="card" :count="1" />

    <template v-else-if="word">
      <article class="pw-detail-article">
        <header class="pw-detail-header">
          <h1 class="pw-detail-title">{{ word.title }}</h1>
          <div class="pw-detail-meta">
            <span :class="['pw-role-tag', roleClass]">{{ roleLabel }}</span>
            <span class="pw-detail-date">{{ formattedCreatedAt }}</span>
            <span v-if="showEdited" class="pw-detail-edited">
              （最后编辑于 {{ formattedUpdatedAt }}）
            </span>
          </div>
        </header>

        <div
          ref="contentRef"
          class="pw-detail-content"
          @mouseup="onMouseUp"
        >
          <template v-for="(seg, idx) in segments" :key="idx">
            <mark
              v-if="seg.highlighted"
              class="hl-mark"
              :style="{ backgroundColor: getHighlightBg(seg.color) }"
              @click="onClickHighlight(seg.highlightIds, $event)"
            >{{ seg.text }}</mark>
            <template v-else>{{ seg.text }}</template>
          </template>
        </div>

        <Teleport to="body">
          <Transition name="hl-toolbar-fade">
            <div
              v-if="showToolbar"
              class="hl-toolbar"
              :style="{
                left: toolbarPos.x + 'px',
                top: toolbarPos.y + 'px',
              }"
            >
              <button
                v-for="c in HIGHLIGHT_COLORS"
                :key="c.value"
                class="hl-toolbar-btn"
                :title="c.label"
                :disabled="saving"
                :style="{ backgroundColor: c.bg }"
                @click.stop="addNewHighlight(c.value)"
              />
            </div>
          </Transition>
        </Teleport>

        <div v-if="word.media_entries.length" class="pw-detail-gallery">
          <div
            v-for="media in word.media_entries"
            :key="media.id"
            class="pw-gallery-item"
          >
            <img
              :src="getThumbnailUrl(media.id)"
              :alt="media.description || ''"
              loading="lazy"
              @click="openMedia(media.id)"
            />
          </div>
        </div>
      </article>
    </template>
  </div>
</template>

<style scoped>
.pw-detail-view {
  max-width: 720px;
  margin: 0 auto;
}

.pw-detail-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.pw-detail-actions {
  display: flex;
  gap: 8px;
}

.pw-detail-article {
  background: var(--bg-primary, #fff);
  border-radius: 12px;
  padding: 32px;
  border: 1px solid var(--border-color);
}

.pw-detail-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.pw-detail-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
  line-height: 1.4;
}

.pw-detail-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.pw-role-tag {
  display: inline-flex;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.role-dad {
  background: #e8f4fd;
  color: #1890ff;
}

.role-mom {
  background: #fff0f6;
  color: #eb2f96;
}

.role-default {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-secondary);
}

.pw-detail-date {
  color: var(--text-secondary);
}

.pw-detail-edited {
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.pw-detail-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  cursor: text;
  user-select: text;
}

.hl-mark {
  border-radius: 3px;
  padding: 1px 0;
  cursor: pointer;
  transition: filter 0.15s ease;
}

.hl-mark:hover {
  filter: brightness(0.92);
}

.pw-detail-gallery {
  margin-top: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
}

.pw-gallery-item {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.pw-gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s;
}

.pw-gallery-item:hover img {
  transform: scale(1.05);
}

@media (max-width: 767px) {
  .pw-detail-article {
    padding: 20px;
    border-radius: 0;
    border-left: none;
    border-right: none;
  }

  .pw-detail-title {
    font-size: 20px;
  }

  .pw-detail-content {
    font-size: 15px;
    line-height: 1.7;
  }

  .pw-detail-gallery {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }

  .pw-detail-topbar {
    margin-bottom: 16px;
  }
}
</style>

<style>
.hl-toolbar {
  position: fixed;
  transform: translate(-50%, -100%);
  display: flex;
  gap: 6px;
  padding: 6px 10px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
}

.hl-toolbar-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  padding: 0;
}

.hl-toolbar-btn:hover:not(:disabled) {
  transform: scale(1.2);
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.2);
}

.hl-toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hl-toolbar-fade-enter-active,
.hl-toolbar-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.hl-toolbar-fade-enter-from,
.hl-toolbar-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -100%) scale(0.9);
}
</style>
