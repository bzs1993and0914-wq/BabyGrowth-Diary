<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { VideoPlay } from '@element-plus/icons-vue'
import { getMediaUrl, getThumbnailUrl } from '@/api/media'
import VideoPlayer from '@/components/media/VideoPlayer.vue'
import type { MediaEntryResponse } from '@/types/api'

const props = defineProps<{
  media: MediaEntryResponse
}>()

const dialogVisible = ref(false)
/** 缩略图 URL 加载失败时改用视频元素展示首帧 */
const thumbLoadError = ref(false)

/** 移动端：弹层全屏展示视频 */
const isMobileViewport = ref(false)
let mql: MediaQueryList | null = null

function syncViewport() {
  isMobileViewport.value = window.matchMedia('(max-width: 768px)').matches
}

onMounted(() => {
  mql = window.matchMedia('(max-width: 768px)')
  isMobileViewport.value = mql.matches
  mql.addEventListener('change', syncViewport)
})

onUnmounted(() => {
  mql?.removeEventListener('change', syncViewport)
})

const dialogFullscreen = computed(() => isMobileViewport.value)

const videoSrc = computed(() => getMediaUrl(props.media.id))
const posterSrc = computed(() =>
  props.media.thumbnail_path ? getThumbnailUrl(props.media.id) : '',
)

const showPosterImage = computed(
  () => !!props.media.thumbnail_path && !thumbLoadError.value,
)

function openPlayer() {
  dialogVisible.value = true
}

function onPosterError() {
  thumbLoadError.value = true
}

function onFallbackVideoLoaded(e: Event) {
  const v = e.target as HTMLVideoElement
  try {
    v.pause()
    v.currentTime = 0
  } catch {
    /* ignore */
  }
}
</script>

<template>
  <div class="video-thumb-preview" @click="openPlayer">
    <img
      v-if="showPosterImage"
      class="thumb-cover"
      :src="posterSrc"
      :alt="media.description || media.original_filename || '视频'"
      loading="lazy"
      @error="onPosterError"
    />
    <video
      v-else
      class="thumb-cover thumb-cover--video"
      muted
      playsinline
      preload="metadata"
      :src="videoSrc"
      @loadeddata="onFallbackVideoLoaded"
    />

    <div class="play-overlay" aria-hidden="true">
      <span class="play-icon-wrap">
        <el-icon :size="36"><VideoPlay /></el-icon>
      </span>
    </div>

    <el-dialog
      v-model="dialogVisible"
      title="视频播放"
      :fullscreen="dialogFullscreen"
      :width="dialogFullscreen ? '100%' : 'min(92vw, 720px)'"
      align-center
      append-to-body
      destroy-on-close
      :class="[
        'video-preview-dialog',
        { 'video-preview-dialog--mobile': dialogFullscreen },
      ]"
    >
      <VideoPlayer :src="videoSrc" :poster="posterSrc || undefined" />
    </el-dialog>
  </div>
</template>

<style scoped>
.video-thumb-preview {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  background: #0a0a0a;
}

.thumb-cover {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.thumb-cover--video {
  pointer-events: none;
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(0, 0, 0, 0.12) 0%,
    rgba(0, 0, 0, 0.35) 100%
  );
}

.play-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}
</style>

<style>
/* 视频弹层内：去掉关闭按钮等点击时的蓝色高亮 */
.video-preview-dialog .el-dialog__headerbtn {
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

.video-preview-dialog .el-dialog__headerbtn:focus,
.video-preview-dialog .el-dialog__headerbtn:focus-visible {
  outline: none;
}

.video-preview-dialog .el-dialog__headerbtn .el-dialog__close {
  outline: none;
}

/* 桌面：对话框内黑底贴边 */
.video-preview-dialog:not(.video-preview-dialog--mobile) .el-dialog__body {
  padding: 0 0 12px;
  background: #000;
}

/* 移动端：全屏弹层，视频区占满剩余空间 */
.video-preview-dialog--mobile.el-dialog {
  margin: 0 !important;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100dvh;
  background: #0a0a0a;
}

.video-preview-dialog--mobile .el-dialog__header {
  flex-shrink: 0;
  margin: 0;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: #121212;
}

.video-preview-dialog--mobile .el-dialog__title {
  color: rgba(255, 255, 255, 0.92);
  font-size: 16px;
  font-weight: 600;
}

.video-preview-dialog--mobile .el-dialog__headerbtn .el-dialog__close {
  color: rgba(255, 255, 255, 0.75);
}

.video-preview-dialog--mobile .el-dialog__body {
  flex: 1;
  min-height: 0;
  padding: 0 !important;
  display: flex;
  flex-direction: column;
  background: #000;
}

.video-preview-dialog--mobile .video-player {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.video-preview-dialog--mobile .video-shell {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  border-radius: 0;
  box-shadow: none;
}

.video-preview-dialog--mobile .video-shell .player {
  flex: 1 1 auto;
  min-height: 0;
  max-height: none !important;
  width: 100%;
  object-fit: contain;
}
</style>
