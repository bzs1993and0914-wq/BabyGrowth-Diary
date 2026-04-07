<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import {
  DArrowLeft,
  DArrowRight,
  VideoPlay,
  VideoPause,
  FullScreen,
} from '@element-plus/icons-vue'

const props = defineProps<{
  src: string
  poster?: string
}>()

const broken = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const shellRef = ref<HTMLElement | null>(null)
const playing = ref(false)
const currentTime = ref(0)
const duration = ref(0)

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

const progressPct = computed(() => {
  const d = duration.value
  if (!Number.isFinite(d) || d <= 0) return 0
  return Math.min(100, Math.max(0, (currentTime.value / d) * 100))
})

/** 与 el-option 绑定需稳定相等，用字符串键避免 0.75 浮点问题 */
const RATES = [
  { key: '0.75', value: 0.75 },
  { key: '1', value: 1 },
  { key: '1.25', value: 1.25 },
  { key: '1.5', value: 1.5 },
  { key: '2', value: 2 },
] as const

const rateKey = ref<(typeof RATES)[number]['key']>('1')

function rateFromKey(k: string): number {
  const found = RATES.find((r) => r.key === k)
  return found ? found.value : 1
}

function formatTime(s: number) {
  if (!Number.isFinite(s) || s < 0) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function applyPlaybackRate() {
  const v = videoRef.value
  if (v) v.playbackRate = rateFromKey(rateKey.value)
}

function onTimeUpdate() {
  const v = videoRef.value
  if (v) {
    currentTime.value = v.currentTime
    duration.value = v.duration
  }
}

function onLoadedMetadata() {
  const v = videoRef.value
  if (v) {
    duration.value = v.duration
    applyPlaybackRate()
  }
}

function onCanPlay() {
  applyPlaybackRate()
}

function onEnded() {
  const v = videoRef.value
  if (!v) return
  v.pause()
  v.currentTime = 0
  playing.value = false
  currentTime.value = 0
}

async function togglePlay() {
  const v = videoRef.value
  if (!v) return
  try {
    if (v.paused) {
      await v.play()
    } else {
      v.pause()
    }
  } catch {
    /* ignore autoplay policy */
  }
}

function onVideoPlay() {
  playing.value = true
}

function onVideoPause() {
  playing.value = false
}

function onSeekBarClick(e: MouseEvent) {
  const v = videoRef.value
  const track = e.currentTarget as HTMLElement
  if (!v || !Number.isFinite(v.duration) || v.duration <= 0) return
  const rect = track.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  v.currentTime = Math.min(Math.max(0, ratio * v.duration), v.duration)
}

function skip(seconds: number) {
  const v = videoRef.value
  if (!v) return
  const d = v.duration
  if (!Number.isFinite(d) || d <= 0) return
  v.currentTime = Math.min(Math.max(0, v.currentTime + seconds), d)
}

async function toggleBrowserFullscreen() {
  const el = shellRef.value
  if (!el) return
  try {
    if (!document.fullscreenElement) {
      await el.requestFullscreen()
    } else {
      await document.exitFullscreen()
    }
  } catch {
    /* ignore */
  }
}

watch(rateKey, () => applyPlaybackRate())

watch(
  () => props.src,
  () => {
    broken.value = false
    rateKey.value = '1'
    currentTime.value = 0
    duration.value = 0
  },
)
</script>

<template>
  <div class="video-player">
    <div v-if="!broken" ref="shellRef" class="video-shell">
      <video
        ref="videoRef"
        playsinline
        preload="metadata"
        :poster="poster || undefined"
        class="player"
        @error="broken = true"
        @ended="onEnded"
        @loadedmetadata="onLoadedMetadata"
        @canplay="onCanPlay"
        @timeupdate="onTimeUpdate"
        @play="onVideoPlay"
        @pause="onVideoPause"
        @click="togglePlay"
      >
        <source :src="src" />
      </video>

      <!-- 叠在画面底部：进度条 + 倍速/跳转，与 video 同一组件内 -->
      <div class="overlay-controls" @click.stop>
        <div
          class="seek-track"
          role="slider"
          tabindex="0"
          :aria-valuenow="Math.round(currentTime)"
          :aria-valuemax="Math.round(duration)"
          aria-label="播放进度"
          @click="onSeekBarClick"
        >
          <div class="seek-fill" :style="{ width: progressPct + '%' }" />
        </div>

        <div class="control-row">
          <button
            type="button"
            class="icon-btn"
            :aria-label="playing ? '暂停' : '播放'"
            @click="togglePlay"
          >
            <el-icon :size="22">
              <VideoPause v-if="playing" />
              <VideoPlay v-else />
            </el-icon>
          </button>

          <span class="time-text" aria-live="polite">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </span>

          <div class="control-right">
            <span class="dock-label">倍速</span>
            <el-select
              v-model="rateKey"
              size="small"
              class="dock-rate-select"
              teleported
              popper-class="dock-rate-select-dropdown"
            >
              <el-option
                v-for="r in RATES"
                :key="r.key"
                :label="`${r.value === 1 ? '1' : r.value}×`"
                :value="r.key"
              />
            </el-select>

            <button type="button" class="dock-action" @click="skip(-10)">
              <el-icon class="dock-action-icon"><DArrowLeft /></el-icon>
              <span class="dock-action-text">10 秒</span>
            </button>
            <button type="button" class="dock-action" @click="skip(10)">
              <span class="dock-action-text">10 秒</span>
              <el-icon class="dock-action-icon"><DArrowRight /></el-icon>
            </button>

            <button
              v-if="!isMobileViewport"
              type="button"
              class="icon-btn icon-btn--fs"
              aria-label="全屏"
              @click="toggleBrowserFullscreen"
            >
              <el-icon :size="20"><FullScreen /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="video-placeholder">
      <span>视频无法播放</span>
    </div>
  </div>
</template>

<style scoped>
/* 去掉点击/触摸时的蓝色高亮与默认焦点环（保留自定义 hover 反馈） */
.video-player {
  width: 100%;
  height: 100%;
  min-height: 0;
  -webkit-tap-highlight-color: transparent;
}

.video-shell {
  position: relative;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  background: #0a0a0a;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

.player {
  width: 100%;
  display: block;
  vertical-align: top;
  background: #000;
  max-height: min(72vh, 560px);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

/* 底部渐变遮罩 + 控件，叠在 video 上 */
.overlay-controls {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2;
  padding: 0 0 max(10px, env(safe-area-inset-bottom));
  background: linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.82) 0%,
    rgba(0, 0, 0, 0.45) 65%,
    transparent 100%
  );
  pointer-events: auto;
  -webkit-tap-highlight-color: transparent;
}

.seek-track {
  height: 4px;
  margin: 0 12px 10px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.22);
  cursor: pointer;
  overflow: hidden;
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

.seek-track:focus {
  outline: none;
}

.seek-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--el-color-primary, #409eff);
  pointer-events: none;
}

.control-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
  padding: 0 10px 10px;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  border-radius: 50%;
  color: #fff;
  background: rgba(255, 255, 255, 0.12);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s ease;
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

.icon-btn::-moz-focus-inner {
  border: 0;
}

.icon-btn:focus,
.icon-btn:focus-visible,
.icon-btn:active {
  outline: none;
  box-shadow: none;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.22);
}

.icon-btn--fs {
  margin-left: auto;
}

.time-text {
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  color: rgba(255, 255, 255, 0.88);
  flex-shrink: 0;
}

.control-right {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  justify-content: flex-end;
}

.dock-label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.55);
}

.dock-rate-select {
  width: 84px;
}

.dock-rate-select :deep(.el-select__wrapper) {
  min-height: 30px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: none !important;
  outline: none !important;
  -webkit-tap-highlight-color: transparent;
}

.dock-rate-select :deep(.el-select__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.12);
}

.dock-rate-select :deep(.el-select__wrapper.is-focused),
.dock-rate-select :deep(.el-select__wrapper:focus),
.dock-rate-select :deep(.el-select__wrapper:focus-within) {
  box-shadow: none !important;
  outline: none !important;
  border-color: rgba(255, 255, 255, 0.25);
}

.dock-rate-select :deep(.el-select__selected-item),
.dock-rate-select :deep(.el-select__placeholder) {
  color: rgba(255, 255, 255, 0.92);
  font-size: 12px;
  font-weight: 500;
}

.dock-rate-select :deep(.el-select__caret) {
  color: rgba(255, 255, 255, 0.55);
}

.dock-rate-select :deep(.el-select__input) {
  outline: none !important;
}

.dock-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  margin: 0;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: background 0.15s ease;
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

.dock-action::-moz-focus-inner {
  border: 0;
}

.dock-action:focus,
.dock-action:focus-visible,
.dock-action:active {
  outline: none;
  box-shadow: none;
}

.dock-action:hover {
  background: rgba(255, 255, 255, 0.18);
}

.dock-action-icon {
  font-size: 14px;
  opacity: 0.95;
}

.dock-action-text {
  max-width: 52px;
  overflow: hidden;
}

.video-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 240px;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

@media (max-width: 768px) {
  .player {
    max-height: none;
  }

  .control-row {
    padding: 0 8px 8px;
  }

  .control-right {
    width: 100%;
    margin-left: 0;
    justify-content: space-between;
  }

  .icon-btn--fs {
    margin-left: 0;
  }
}
</style>

<style>
/* 下拉面板（teleport） */
.dock-rate-select-dropdown.el-popper {
  background: #2a2a30 !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45) !important;
  -webkit-tap-highlight-color: transparent;
}

.dock-rate-select-dropdown .el-select-dropdown__item {
  color: rgba(255, 255, 255, 0.88);
  outline: none;
}

.dock-rate-select-dropdown .el-select-dropdown__item:focus,
.dock-rate-select-dropdown .el-select-dropdown__item:focus-visible {
  outline: none;
}

.dock-rate-select-dropdown .el-select-dropdown__item.is-selected {
  color: var(--el-color-primary);
  font-weight: 600;
}

.dock-rate-select-dropdown .el-select-dropdown__item:hover {
  background: rgba(255, 255, 255, 0.08);
}
</style>
