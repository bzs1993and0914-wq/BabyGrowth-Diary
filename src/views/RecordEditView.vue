<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Delete } from '@element-plus/icons-vue'
import { useRecordsStore } from '@/stores/records'
import { getMediaUrl, getThumbnailUrl } from '@/api/media'
import MediaUploader from '@/components/media/MediaUploader.vue'
import GrowthMetricInput from '@/components/record/GrowthMetricInput.vue'
import type { MediaEntryResponse, TextEntryInput } from '@/types/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useRecordsStore()

const isNew = computed(() => route.params.date === undefined || route.name === 'record-new')
const recordDate = ref('')
const texts = ref<{ id?: number; content: string; sort_order: number }[]>([])
const uploadedMedia = ref<MediaEntryResponse[]>([])
const saving = ref(false)
const loading = ref(false)
const recordId = ref<number | null>(null)

onMounted(async () => {
  if (!isNew.value && route.params.date) {
    loading.value = true
    try {
      await store.loadRecord(route.params.date as string)
      const rec = store.currentRecord
      if (rec) {
        recordDate.value = rec.date
        recordId.value = rec.id
        texts.value = rec.text_entries.map((t) => ({
          id: t.id,
          content: t.content,
          sort_order: t.sort_order,
        }))
        uploadedMedia.value = [...rec.media_entries]
      }
    } catch {
      ElMessage.error('加载记录失败')
    } finally {
      loading.value = false
    }
  } else {
    recordDate.value = new Date().toISOString().slice(0, 10)
    texts.value = [{ content: '', sort_order: 0 }]
  }
})

function addText() {
  texts.value.push({ content: '', sort_order: texts.value.length })
}

function removeText(idx: number) {
  texts.value.splice(idx, 1)
  texts.value.forEach((t, i) => (t.sort_order = i))
}

function onMediaUploaded(entry: MediaEntryResponse) {
  uploadedMedia.value.push(entry)
}

async function handleSave() {
  if (!recordDate.value) {
    ElMessage.warning('请选择日期')
    return
  }

  saving.value = true
  try {
    const validTexts: TextEntryInput[] = texts.value
      .filter((t) => t.content.trim())
      .map((t) => ({ id: t.id, content: t.content.trim(), sort_order: t.sort_order }))

    if (isNew.value) {
      const rec = await store.saveRecord({
        date: recordDate.value,
        texts: validTexts,
      })
      recordId.value = rec.id
      ElMessage.success('记录已创建')
      router.replace(`/record/${rec.date}`)
    } else {
      await store.editRecord(recordDate.value, { texts: validTexts })
      ElMessage.success('记录已更新')
      router.push(`/record/${recordDate.value}`)
    }
  } catch (e: any) {
    const msg = e?.response?.data?.detail || '保存失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  router.back()
}
</script>

<template>
  <div class="record-edit">
    <div class="page-header">
      <h2>{{ isNew ? '新建记录' : '编辑记录' }}</h2>
    </div>

    <el-card shadow="never" class="edit-card">
      <div class="form-section">
        <label class="field-label">日期</label>
        <el-date-picker
          v-model="recordDate"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          :disabled="!isNew"
          style="width: 220px"
        />
      </div>

      <div class="form-section">
        <label class="field-label">文字记录</label>
        <div class="text-list">
          <div v-for="(text, idx) in texts" :key="idx" class="text-row">
            <el-input
              v-model="text.content"
              type="textarea"
              :rows="3"
              placeholder="记录宝宝今天的故事..."
              resize="vertical"
            />
            <el-button
              v-if="texts.length > 1"
              :icon="Delete"
              size="small"
              text
              type="danger"
              @click="removeText(idx)"
            />
          </div>
        </div>
        <el-button :icon="Plus" text type="primary" @click="addText">
          添加更多文字
        </el-button>
      </div>

      <div class="form-section" v-if="recordId">
        <label class="field-label">照片/视频</label>
        <MediaUploader :daily-record-id="recordId" @uploaded="onMediaUploaded" />

        <div v-if="uploadedMedia.length" class="media-grid">
          <div v-for="m in uploadedMedia" :key="m.id" class="media-thumb">
            <img
              v-if="m.media_type === 'image'"
              :src="getThumbnailUrl(m.id)"
              :alt="m.description || ''"
            />
            <div v-else class="video-thumb">
              <img
                v-if="m.thumbnail_path"
                :src="getThumbnailUrl(m.id)"
                :alt="m.description || ''"
              />
              <span v-else class="video-label">视频</span>
            </div>
            <span v-if="m.description" class="thumb-desc">{{ m.description }}</span>
          </div>
        </div>
      </div>

      <div v-if="!recordId && isNew" class="form-section">
        <p class="hint-text">保存记录后可以上传照片和视频，以及添加成长数据</p>
      </div>

      <div class="form-section" v-if="recordId && store.currentRecord">
        <GrowthMetricInput
          :daily-record-id="recordId"
          :existing-metrics="store.currentRecord.growth_metrics"
        />
      </div>
    </el-card>

    <div class="action-bar">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">
        {{ isNew ? '创建记录' : '保存修改' }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.record-edit {
  max-width: 700px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.edit-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.text-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 8px;
}

.text-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.text-row .el-input {
  flex: 1;
}

.hint-text {
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 12px 16px;
  border-radius: 8px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  margin-top: 12px;
}

.media-thumb {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.media-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-thumb {
  width: 100%;
  height: 100%;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.thumb-desc {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px 6px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-bottom: 40px;
}
</style>
