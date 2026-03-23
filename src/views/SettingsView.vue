<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { fetchStorageStats } from '@/api/storage'
import { startExport, getExportStatus } from '@/api/export'
import type { StorageStats, ExportStatus } from '@/types/api'
import ThemeSwitcher from '@/components/common/ThemeSwitcher.vue'
import { ElMessage } from 'element-plus'

const settingsStore = useSettingsStore()

const stats = ref<StorageStats | null>(null)
const statsLoading = ref(true)
const exportStatus = ref<ExportStatus | null>(null)
const exporting = ref(false)

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

onMounted(async () => {
  try {
    stats.value = await fetchStorageStats()
  } catch {
    // stats unavailable
  } finally {
    statsLoading.value = false
  }
})

async function handleExport() {
  exporting.value = true
  try {
    const res = await startExport()
    exportStatus.value = res
    pollExport(res.export_id)
  } catch {
    ElMessage.error('导出启动失败')
    exporting.value = false
  }
}

async function pollExport(exportId: string) {
  const poll = async () => {
    try {
      const status = await getExportStatus(exportId)
      exportStatus.value = status
      if (status.status === 'processing') {
        setTimeout(poll, 1500)
      } else {
        exporting.value = false
        if (status.status === 'completed') {
          ElMessage.success('导出完成')
        } else {
          ElMessage.error(status.message || '导出失败')
        }
      }
    } catch {
      exporting.value = false
    }
  }
  poll()
}
</script>

<template>
  <div class="settings-view">
    <h2 class="page-title">设置</h2>

    <el-card shadow="never" class="section-card">
      <ThemeSwitcher />
    </el-card>

    <el-card shadow="never" class="section-card">
      <h3 class="section-title">存储统计</h3>
      <div v-if="statsLoading" class="stats-loading">加载中...</div>
      <div v-else-if="stats" class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ stats.total_records }}</span>
          <span class="stat-label">记录总数</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.total_images }}</span>
          <span class="stat-label">照片数量</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.total_videos }}</span>
          <span class="stat-label">视频数量</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatSize(stats.database_size_bytes) }}</span>
          <span class="stat-label">数据库大小</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatSize(stats.media_size_bytes) }}</span>
          <span class="stat-label">媒体文件大小</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ formatSize(stats.thumbnail_size_bytes) }}</span>
          <span class="stat-label">缩略图大小</span>
        </div>
      </div>
      <div v-else class="stats-empty">暂无统计数据</div>
    </el-card>

    <el-card shadow="never" class="section-card">
      <h3 class="section-title">数据导出</h3>
      <p class="export-desc">导出所有记录和媒体文件为 ZIP 压缩包</p>
      <el-button
        type="primary"
        :loading="exporting"
        @click="handleExport"
      >
        {{ exporting ? '导出中...' : '导出数据' }}
      </el-button>
      <el-progress
        v-if="exportStatus && exportStatus.status === 'processing'"
        :percentage="exportStatus.progress"
        :stroke-width="6"
        style="margin-top: 12px"
      />
      <div v-if="exportStatus?.status === 'completed'" class="export-done">
        <span>导出完成</span>
        <span class="export-size">{{ formatSize(exportStatus.file_size || 0) }}</span>
      </div>
    </el-card>

    <el-card shadow="never" class="section-card">
      <h3 class="section-title">关于</h3>
      <div class="about-info">
        <div class="about-row">
          <span>应用名称</span>
          <span>BabyGrow</span>
        </div>
        <div class="about-row">
          <span>版本号</span>
          <span>0.1.0</span>
        </div>
        <div class="about-row">
          <span>技术栈</span>
          <span>Electron + Vue 3 + FastAPI</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.settings-view {
  max-width: 640px;
  margin: 0 auto;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.section-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 8px;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.stats-loading,
.stats-empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px 0;
  font-size: 14px;
}

.export-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.export-done {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 14px;
  color: #67c23a;
  font-weight: 500;
}

.export-size {
  color: var(--text-secondary);
  font-weight: 400;
}

.about-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.about-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
}

.about-row:last-child {
  border-bottom: none;
}

.about-row span:first-child {
  color: var(--text-secondary);
}

.about-row span:last-child {
  color: var(--text-primary);
  font-weight: 500;
}
</style>
