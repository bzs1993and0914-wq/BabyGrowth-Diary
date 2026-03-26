<script setup lang="ts">
import { computed, ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadMedia } from '@/api/media'
import type { MediaEntryResponse } from '@/types/api'
import { ElMessage } from 'element-plus'
import type { UploadRawFile } from 'element-plus'

const props = defineProps<{
  dailyRecordId: number
  /** Max media items allowed for this record (account tier cap). */
  maxPerRecord: number
  /** Already saved media count for this record. */
  existingMediaCount: number
}>()

const emit = defineEmits<{
  uploaded: [entry: MediaEntryResponse]
  'upload-batch-complete': [payload: { attempted: number; succeeded: number }]
}>()

const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'heic', 'heif', 'mp4', 'mov']
const MAX_SIZE = 2 * 1024 * 1024 * 1024 // 2GB

interface FileItem {
  file: File
  description: string
  uploading: boolean
  done: boolean
}

const fileList = ref<FileItem[]>([])
const uploading = ref(false)

const slotsLeft = computed(() =>
  Math.max(0, props.maxPerRecord - props.existingMediaCount),
)

const hintTier = computed(() =>
  props.maxPerRecord > 1
    ? `当前为 VIP，本条记录最多 ${props.maxPerRecord} 个媒体`
    : '普通账号每条记录最多 1 张照片/视频（可在设置中切换为 VIP 体验多图）',
)

function beforeUpload(rawFile: UploadRawFile) {
  const ext = rawFile.name.split('.').pop()?.toLowerCase() || ''
  if (!ALLOWED_EXT.includes(ext)) {
    ElMessage.error(`不支持的文件格式: .${ext}`)
    return false
  }
  if (rawFile.size > MAX_SIZE) {
    ElMessage.error('文件大小不能超过 2GB')
    return false
  }

  if (fileList.value.length >= slotsLeft.value) {
    ElMessage.warning(
      slotsLeft.value === 0
        ? '已达到当前账号本条记录可添加的媒体上限'
        : `最多再选择 ${slotsLeft.value} 个文件`,
    )
    return false
  }

  fileList.value.push({
    file: rawFile,
    description: '',
    uploading: false,
    done: false,
  })
  return false
}

function removeFile(idx: number) {
  fileList.value.splice(idx, 1)
}

async function uploadAll() {
  if (!fileList.value.length) return
  uploading.value = true
  let attempted = 0
  let succeeded = 0

  for (const item of fileList.value) {
    if (item.done) continue
    item.uploading = true
    attempted += 1
    try {
      const res = await uploadMedia(
        item.file,
        props.dailyRecordId,
        item.description || undefined,
      )
      item.done = true
      succeeded += 1
      emit('uploaded', res.data)
    } catch {
      ElMessage.error(`上传失败: ${item.file.name}`)
    } finally {
      item.uploading = false
    }
  }

  fileList.value = fileList.value.filter((f) => !f.done)
  uploading.value = false
  emit('upload-batch-complete', { attempted, succeeded })
  if (attempted > 0) {
    if (succeeded === attempted) {
      ElMessage.success('全部上传完成')
    } else if (succeeded > 0) {
      ElMessage.warning('部分文件上传失败')
    }
  }
}
</script>

<template>
  <div class="media-uploader">
    <p class="tier-hint">{{ hintTier }}</p>
    <el-upload
      drag
      multiple
      :show-file-list="false"
      :before-upload="beforeUpload"
      accept=".jpg,.jpeg,.png,.heic,.heif,.mp4,.mov"
      :disabled="slotsLeft === 0"
    >
      <el-icon class="upload-icon" :size="40"><UploadFilled /></el-icon>
      <div class="upload-text">拖拽文件到此处，或 <em>点击选择</em></div>
      <div class="upload-hint">支持 JPG、PNG、HEIC、MP4、MOV，单文件最大 2GB</div>
    </el-upload>

    <div v-if="fileList.length" class="file-list">
      <div v-for="(item, idx) in fileList" :key="idx" class="file-item">
        <div class="file-info">
          <span class="file-name">{{ item.file.name }}</span>
          <span class="file-size">{{ (item.file.size / 1024 / 1024).toFixed(1) }} MB</span>
        </div>
        <el-input
          v-model="item.description"
          placeholder="添加描述（可选）"
          size="small"
          :disabled="item.uploading || item.done"
        />
        <el-button
          v-if="!item.uploading && !item.done"
          size="small"
          text
          type="danger"
          @click="removeFile(idx)"
        >
          移除
        </el-button>
        <el-tag v-if="item.done" type="success" size="small">已上传</el-tag>
      </div>

      <el-button
        type="primary"
        :loading="uploading"
        @click="uploadAll"
        style="margin-top: 8px"
      >
        开始上传 ({{ fileList.filter((f) => !f.done).length }}个文件)
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.media-uploader {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tier-hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.media-uploader :deep(.el-upload-dragger) {
  border-radius: 12px;
  border: 2px dashed var(--border-color);
  background: var(--bg-secondary);
  padding: 32px 20px;
  transition: all 0.2s;
}

.media-uploader :deep(.el-upload-dragger:hover) {
  border-color: var(--color-primary);
}

.upload-icon {
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: var(--text-primary);
}

.upload-text em {
  color: var(--color-primary);
  font-style: normal;
}

.upload-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
}
</style>
