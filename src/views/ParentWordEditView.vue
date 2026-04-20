<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete } from '@element-plus/icons-vue'
import { useParentWordsStore } from '@/stores/parentWords'
import { useAuthStore } from '@/stores/auth'
import { uploadMediaForParentWord, deleteMedia, getThumbnailUrl } from '@/api/media'
import { useParentWordDraft } from '@/composables/useParentWordDraft'
import type { MediaEntryResponse } from '@/types/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useParentWordsStore()
const auth = useAuthStore()

const isNew = computed(() => route.name === 'parent-word-new')
const wordId = computed(() => (isNew.value ? null : Number(route.params.id)))

const draftKey = computed(() => isNew.value ? 'new' : String(wordId.value))
const draft = useParentWordDraft(draftKey.value)

const title = ref('')
const content = ref('')
const authorRole = ref('')
const mediaEntries = ref<MediaEntryResponse[]>([])
const saving = ref(false)
const loading = ref(false)
const uploading = ref(false)

const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'heic', 'heif']
const MAX_MEDIA = 5

const roleOptions = [
  { label: '爸爸', value: 'dad' },
  { label: '妈妈', value: 'mom' },
  { label: '不标注', value: '' },
]

onMounted(async () => {
  if (!isNew.value && wordId.value) {
    loading.value = true
    try {
      await store.loadDetail(wordId.value)
      if (store.currentWord) {
        title.value = store.currentWord.title
        content.value = store.currentWord.content
        authorRole.value = store.currentWord.author_role || ''
        mediaEntries.value = [...store.currentWord.media_entries]
      }
    } catch {
      ElMessage.error('记录不存在')
      router.replace('/parent-words')
    } finally {
      loading.value = false
    }
  } else {
    authorRole.value = auth.user?.parent_role || ''
  }

  if (draft.hasDraft.value) {
    try {
      await ElMessageBox.confirm('检测到未保存的草稿，是否恢复？', '恢复草稿', {
        confirmButtonText: '恢复',
        cancelButtonText: '放弃草稿',
        type: 'info',
      })
      const saved = draft.restoreDraft()
      if (saved) {
        title.value = saved.title
        content.value = saved.content
        authorRole.value = saved.authorRole || ''
      }
    } catch {
      draft.clearDraft()
    }
  }

  draft.startAutoSave(() => ({
    title: title.value,
    content: content.value,
    authorRole: authorRole.value,
  }))
})

async function handleSave() {
  if (!title.value.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!content.value.trim()) {
    ElMessage.warning('请输入正文内容')
    return
  }

  saving.value = true
  try {
    const roleToSave = authorRole.value || null
    if (isNew.value) {
      const created = await store.create({
        title: title.value.trim(),
        content: content.value.trim(),
        author_role: roleToSave,
      })
      draft.clearDraft()
      ElMessage.success('已保存')
      router.push(`/parent-words/${created.id}`)
    } else if (wordId.value) {
      await store.update(wordId.value, {
        title: title.value.trim(),
        content: content.value.trim(),
        author_role: roleToSave,
      })
      draft.clearDraft()
      ElMessage.success('已保存')
      router.push(`/parent-words/${wordId.value}`)
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  if (wordId.value) {
    router.push(`/parent-words/${wordId.value}`)
  } else {
    router.push('/parent-words')
  }
}

async function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  const targetId = wordId.value
  if (!targetId && isNew.value) {
    ElMessage.info('请先保存心语内容，再上传图片')
    input.value = ''
    return
  }
  if (!targetId) return

  if (mediaEntries.value.length >= MAX_MEDIA) {
    ElMessage.warning(`最多上传 ${MAX_MEDIA} 张图片`)
    input.value = ''
    return
  }

  const files = Array.from(input.files)
  uploading.value = true
  try {
    for (const file of files) {
      if (mediaEntries.value.length >= MAX_MEDIA) break
      const ext = file.name.split('.').pop()?.toLowerCase() || ''
      if (!ALLOWED_EXT.includes(ext)) {
        ElMessage.error(`不支持的格式: .${ext}`)
        continue
      }
      const res = await uploadMediaForParentWord(file, targetId, undefined, mediaEntries.value.length)
      mediaEntries.value.push(res.data)
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function handleDeleteMedia(mediaId: number) {
  try {
    await deleteMedia(mediaId)
    mediaEntries.value = mediaEntries.value.filter(m => m.id !== mediaId)
  } catch {
    ElMessage.error('删除图片失败')
  }
}
</script>

<template>
  <div class="pw-edit-view">
    <div class="pw-edit-topbar">
      <el-button text @click="handleCancel">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回</span>
      </el-button>
      <h3 class="pw-edit-topbar-title">{{ isNew ? '写下心里话' : '编辑' }}</h3>
      <el-button
        type="primary"
        round
        :loading="saving"
        @click="handleSave"
      >
        保存
      </el-button>
    </div>

    <div v-if="loading" class="pw-edit-loading">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else class="pw-edit-form">
      <div class="pw-edit-field">
        <label class="pw-edit-label">标题</label>
        <el-input
          v-model="title"
          placeholder="给这段话起个标题"
          maxlength="100"
          show-word-limit
          clearable
        />
      </div>

      <div class="pw-edit-field">
        <label class="pw-edit-label">正文</label>
        <el-input
          v-model="content"
          type="textarea"
          placeholder="写下你想对宝宝说的话..."
          :autosize="{ minRows: 6, maxRows: 20 }"
        />
      </div>

      <div class="pw-edit-field">
        <label class="pw-edit-label">作者身份</label>
        <el-radio-group v-model="authorRole">
          <el-radio v-for="opt in roleOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </el-radio>
        </el-radio-group>
      </div>

      <div v-if="!isNew && wordId" class="pw-edit-field">
        <label class="pw-edit-label">图片（最多 {{ MAX_MEDIA }} 张）</label>
        <div class="pw-media-grid">
          <div
            v-for="media in mediaEntries"
            :key="media.id"
            class="pw-media-item"
          >
            <img :src="getThumbnailUrl(media.id)" alt="" loading="lazy" />
            <button class="pw-media-delete" @click="handleDeleteMedia(media.id)">
              <el-icon :size="14"><Delete /></el-icon>
            </button>
          </div>
          <label
            v-if="mediaEntries.length < MAX_MEDIA"
            class="pw-media-add"
          >
            <el-icon :size="24"><Plus /></el-icon>
            <span>添加图片</span>
            <input
              type="file"
              accept=".jpg,.jpeg,.png,.heic,.heif"
              multiple
              hidden
              @change="handleFileSelect"
            />
          </label>
        </div>
        <div v-if="uploading" class="pw-upload-hint">上传中...</div>
      </div>

      <div v-if="isNew" class="pw-edit-hint">
        保存后可添加图片
      </div>
    </div>
  </div>
</template>

<style scoped>
.pw-edit-view {
  max-width: 720px;
  margin: 0 auto;
}

.pw-edit-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 12px;
}

.pw-edit-topbar-title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.pw-edit-loading {
  padding: 20px 0;
}

.pw-edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pw-edit-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pw-edit-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.pw-media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}

.pw-media-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.pw-media-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pw-media-delete {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.pw-media-item:hover .pw-media-delete {
  opacity: 1;
}

.pw-media-add {
  aspect-ratio: 1;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 12px;
  transition: border-color 0.2s, color 0.2s;
}

.pw-media-add:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.pw-upload-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.pw-edit-hint {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
  padding: 12px;
  background: var(--bg-secondary, #f9f9f9);
  border-radius: 8px;
}

@media (max-width: 767px) {
  .pw-edit-topbar {
    margin-bottom: 16px;
  }

  .pw-media-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
}
</style>
