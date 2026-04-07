<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Delete, Warning } from '@element-plus/icons-vue'
import { useRecordsStore } from '@/stores/records'
import { getRecord } from '@/api/records'
import { useAuthStore } from '@/stores/auth'
import {
  deleteMedia,
  buildMediaApiUrl,
  getMediaUrl,
  getThumbnailUrl,
} from '@/api/media'
import MediaUploader from '@/components/media/MediaUploader.vue'
import GrowthMetricInput from '@/components/record/GrowthMetricInput.vue'
import type { MediaEntryResponse, TextEntryInput } from '@/types/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useRecordsStore()
const auth = useAuthStore()

const tierCap = computed(() => (auth.user?.account_tier === 'vip' ? 9 : 1))

const isNew = computed(
  () => route.params.date === undefined || route.name === 'record-new'
)
const recordDate = ref('')
const texts = ref<{ id?: number; content: string; sort_order: number }[]>([])
const uploadedMedia = ref<MediaEntryResponse[]>([])
const saving = ref(false)
const loading = ref(false)
const recordId = ref<number | null>(null)
const allergyNotes = ref('')
/** 宝宝过敏：默认折叠，点击后展开填写（与「添加更多文字」交互一致） */
const showAllergySection = ref(false)

/** 当前新建页在服务端已绑定的记录日期（用于切换日期时删旧建新） */
const draftCreatedForDate = ref<string | null>(null)

const hasAllergyContent = computed(() => allergyNotes.value.trim().length > 0)

/** 禁止选择今天以后的日期（与后端 assert_record_date_not_after_today 一致） */
function disableFutureDate(d: Date): boolean {
  const today = new Date()
  today.setHours(23, 59, 59, 999)
  return d.getTime() > today.getTime()
}

function todayLocalDateStr(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function recordExistsRedirectMessage(dateStr: string): string {
  return dateStr === todayLocalDateStr()
    ? '今日已有记录，已切换到编辑'
    : '该日期已有记录，已切换到编辑'
}

/**
 * 为所选日期准备一条空记录（新建页上传媒体/成长数据需要 daily_record_id）。
 * 若该日已有记录则跳转编辑；若当前已有其他日期的草稿则先删再建。
 */
async function applyNewRecordDate(newDateStr: string) {
  if (!isNew.value || !newDateStr) return
  if (draftCreatedForDate.value === newDateStr && recordId.value) return

  loading.value = true
  /** 已 replace 到编辑页时由路由 watch 接管 loading，避免 finally 提前关 loading */
  let handOffLoadingToRoute = false
  try {
    try {
      await getRecord(newDateStr)
      ElMessage.info(recordExistsRedirectMessage(newDateStr))
      await router.replace(`/record/${newDateStr}/edit`)
      handOffLoadingToRoute = true
      return
    } catch (e: unknown) {
      if ((e as { response?: { status?: number } })?.response?.status !== 404) {
        throw e
      }
    }

    const oldDate = draftCreatedForDate.value
    const hasText = texts.value.some((t) => t.content.trim())
    const hasMedia = uploadedMedia.value.length > 0
    const hasMetrics = (store.currentRecord?.growth_metrics?.length ?? 0) > 0
    const hasAllergy = allergyNotes.value.trim().length > 0
    if (
      oldDate &&
      oldDate !== newDateStr &&
      (hasText || hasMedia || hasMetrics || hasAllergy)
    ) {
      try {
        await ElMessageBox.confirm(
          '切换日期将放弃当前日期的草稿（含已上传的媒体与成长数据），并在新日期创建空白记录。是否继续？',
          '切换日期',
          {
            type: 'warning',
            confirmButtonText: '继续',
            cancelButtonText: '取消',
          }
        )
      } catch {
        recordDate.value = oldDate
        return
      }
    }

    if (oldDate && recordId.value) {
      try {
        await store.removeRecord(oldDate)
      } catch {
        ElMessage.error('无法删除旧日期的草稿，请稍后重试')
        recordDate.value = oldDate
        return
      }
      recordId.value = null
      draftCreatedForDate.value = null
      store.currentRecord = null
      uploadedMedia.value = []
      texts.value = [{ content: '', sort_order: 0 }]
      allergyNotes.value = ''
      showAllergySection.value = false
    }

    try {
      await store.saveRecord({
        date: newDateStr,
        texts: [],
        allergy_notes: null,
      })
    } catch (e: unknown) {
      if ((e as { response?: { status?: number } })?.response?.status === 409) {
        ElMessage.info(recordExistsRedirectMessage(newDateStr))
        await router.replace(`/record/${newDateStr}/edit`)
        handOffLoadingToRoute = true
        return
      }
      throw e
    }
    await store.loadRecord(newDateStr)
    const rec = store.currentRecord
    if (rec) {
      recordId.value = rec.id
      draftCreatedForDate.value = newDateStr
      uploadedMedia.value = [...rec.media_entries]
    }
  } catch (e: unknown) {
    const d = (e as { response?: { data?: { detail?: string } } })?.response
      ?.data?.detail
    ElMessage.error(typeof d === 'string' ? d : '无法为该日期创建记录')
    if (draftCreatedForDate.value) {
      recordDate.value = draftCreatedForDate.value
    }
  } finally {
    if (!handOffLoadingToRoute) loading.value = false
  }
}

function onNewRecordDateChange(val: string | null) {
  if (!isNew.value || !val) return
  void applyNewRecordDate(val)
}

/** 新建与编辑共用同一组件，从 /record/new replace 到 /record/:date/edit 时不会再次 onMounted，必须随路由重载数据 */
async function loadRecordForEditRoute(dateStr: string) {
  draftCreatedForDate.value = null
  loading.value = true
  try {
    await store.loadRecord(dateStr)
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
      allergyNotes.value = rec.allergy_notes ?? ''
      showAllergySection.value = allergyNotes.value.trim().length > 0
    }
  } catch {
    ElMessage.error('加载记录失败')
  } finally {
    loading.value = false
  }
}

watch(
  () => route.fullPath,
  async () => {
    if (route.name === 'record-edit' && route.params.date) {
      const dateStr = String(route.params.date)
      await loadRecordForEditRoute(dateStr)
      return
    }
    if (route.name === 'record-new') {
      recordDate.value = new Date().toISOString().slice(0, 10)
      texts.value = [{ content: '', sort_order: 0 }]
      recordId.value = null
      draftCreatedForDate.value = null
      uploadedMedia.value = []
      allergyNotes.value = ''
      showAllergySection.value = false
      store.currentRecord = null
      await applyNewRecordDate(recordDate.value)
    }
  },
  { immediate: true }
)

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

async function handleDeleteMedia(media: MediaEntryResponse) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这张照片/视频吗？删除后无法恢复。',
      '删除媒体',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await deleteMedia(media.id)
    uploadedMedia.value = uploadedMedia.value.filter((m) => m.id !== media.id)
    if (store.currentRecord) {
      store.currentRecord.media_entries = uploadedMedia.value
    }
    ElMessage.success('已删除')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || '删除失败')
    }
  }
}

async function handleSave() {
  if (!recordDate.value) {
    ElMessage.warning('请选择日期')
    return
  }
  if (isNew.value && !recordId.value) {
    ElMessage.warning('正在准备记录，请稍候再保存')
    return
  }

  saving.value = true
  try {
    const validTexts: TextEntryInput[] = texts.value
      .filter((t) => t.content.trim())
      .map((t) => ({
        id: t.id,
        content: t.content.trim(),
        sort_order: t.sort_order,
      }))

    await store.editRecord(recordDate.value, {
      texts: validTexts,
      allergy_notes: allergyNotes.value.trim() || null,
    })
    if (isNew.value) {
      ElMessage.success('记录已保存')
      await router.replace(`/record/${recordDate.value}`)
    } else {
      ElMessage.success('记录已更新')
      await router.push(`/record/${recordDate.value}`)
    }
  } catch (e: any) {
    const d = e?.response?.data?.detail
    let msg = '保存失败'
    if (typeof d === 'string') msg = d
    else if (Array.isArray(d) && d.length)
      msg = d.map((x: { msg?: string }) => x.msg || '参数有误').join('；')
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  router.back()
}

function collapseAllergySection() {
  showAllergySection.value = false
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
          :disabled="!isNew || loading"
          :disabled-date="disableFutureDate"
          style="width: 220px"
          @change="onNewRecordDateChange"
        />
      </div>

      <div class="form-section allergy-block">
        <el-button
          v-if="!showAllergySection"
          :icon="Warning"
          text
          type="primary"
          class="allergy-expand-btn"
          @click="showAllergySection = true"
        >
          {{
            hasAllergyContent
              ? '已填写过敏信息 · 点击展开修改'
              : '填写宝宝过敏食物（可选）'
          }}
        </el-button>

        <div v-else class="allergy-section">
          <div class="allergy-section-head">
            <label class="field-label allergy-label"
              >⚠️ 宝宝过敏食物（请谨慎填写）</label
            >
            <el-button
              text
              type="info"
              size="small"
              @click="collapseAllergySection"
            >
              收起
            </el-button>
          </div>
          <el-input
            v-model="allergyNotes"
            type="textarea"
            :rows="3"
            maxlength="2000"
            show-word-limit
            placeholder="例：花生、虾蟹…（可为空）"
          />
        </div>
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
        <MediaUploader
          :daily-record-id="recordId"
          :max-per-record="tierCap"
          :existing-media-count="uploadedMedia.length"
          @uploaded="onMediaUploaded"
        />

        <div v-if="uploadedMedia.length" class="media-grid">
          <div v-for="m in uploadedMedia" :key="m.id" class="media-thumb">
            <div class="thumb-wrap">
              <img
                v-if="m.media_type === 'image'"
                :src="
                  m.thumbnail_path ? getThumbnailUrl(m.id) : getMediaUrl(m.id)
                "
                :alt="m.description || ''"
                @error="
                  (e) => {
                    ;(e.target as HTMLImageElement).src = getMediaUrl(m.id)
                  }
                "
              />
              <div v-else class="video-thumb">
                <img
                  v-if="m.thumbnail_path"
                  :src="getThumbnailUrl(m.id)"
                  :alt="m.description || ''"
                  @error="
                    (e) => {
                      ;(e.target as HTMLImageElement).onerror = null
                      ;(e.target as HTMLImageElement).src = getMediaUrl(m.id)
                    }
                  "
                />
                <span v-else class="video-label">视频</span>
              </div>
              <el-button
                class="delete-btn"
                :icon="Delete"
                circle
                size="small"
                type="danger"
                @click="handleDeleteMedia(m)"
              />
            </div>
            <span v-if="m.description" class="thumb-desc">{{
              m.description
            }}</span>
          </div>
        </div>
      </div>

      <div class="form-section" v-if="recordId">
        <GrowthMetricInput
          :key="recordId"
          :daily-record-id="recordId"
          :existing-metrics="store.currentRecord?.growth_metrics ?? []"
        />
      </div>
    </el-card>

    <div class="action-bar">
      <el-button @click="handleCancel">取消</el-button>
      <el-button
        type="primary"
        :loading="saving"
        :disabled="isNew && (!recordId || loading)"
        @click="handleSave"
      >
        {{ isNew ? (recordId ? '保存记录' : '准备中…') : '保存修改' }}
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

.thumb-wrap {
  position: relative;
  width: 100%;
  height: 100%;
}

.thumb-wrap .delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0.85;
}

.thumb-wrap .delete-btn:hover {
  opacity: 1;
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

.allergy-block {
  margin-bottom: 24px;
}

.allergy-expand-btn {
  padding-left: 0;
  height: auto;
  font-weight: 500;
}

.allergy-expand-btn :deep(.el-icon) {
  color: #e65100;
}

.allergy-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.allergy-section-head .field-label {
  margin-bottom: 0;
}

.allergy-section :deep(.el-textarea__inner) {
  border-color: #d84315;
  background: #fff8f5;
}

.allergy-label {
  color: #bf360c;
}
</style>
