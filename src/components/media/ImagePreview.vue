<script setup lang="ts">
import { ref } from 'vue'
import { ZoomIn, ZoomOut, Close } from '@element-plus/icons-vue'

const props = withDefaults(
  defineProps<{
    src: string
    alt?: string
    clickable?: boolean
    /** 为 true 时禁止 img 原生拖拽，便于外层单元格承接 HTML5 拖放排序 */
    suppressNativeDrag?: boolean
  }>(),
  { alt: '', clickable: true, suppressNativeDrag: false }
)

const showOverlay = ref(false)
const scale = ref(1)
const broken = ref(false)

function handleClick() {
  if (props.clickable && !broken.value) {
    showOverlay.value = true
    scale.value = 1
  }
}

function zoomIn() {
  scale.value = Math.min(scale.value + 0.25, 4)
}

function zoomOut() {
  scale.value = Math.max(scale.value - 0.25, 0.25)
}

function closeOverlay() {
  showOverlay.value = false
}
</script>

<template>
  <div class="image-preview">
    <img
      v-if="!broken"
      :src="src"
      :alt="alt"
      class="preview-img"
      :class="{ clickable }"
      :draggable="!suppressNativeDrag"
      @click="handleClick"
      @error="broken = true"
    />
    <div v-else class="broken-placeholder">
      <span>图片加载失败</span>
    </div>

    <teleport to="body">
      <transition name="overlay-fade">
        <div
          v-if="showOverlay"
          class="fullscreen-overlay"
          @click.self="closeOverlay"
        >
          <div class="overlay-controls">
            <el-button :icon="ZoomIn" circle @click="zoomIn" />
            <el-button :icon="ZoomOut" circle @click="zoomOut" />
            <el-button :icon="Close" circle @click="closeOverlay" />
          </div>
          <img
            :src="src"
            :alt="alt"
            class="overlay-img"
            :style="{ transform: `scale(${scale})` }"
          />
        </div>
      </transition>
    </teleport>
  </div>
</template>

<style scoped>
.image-preview {
  width: 100%;
}

.preview-img {
  width: 100%;
  display: block;
  border-radius: 4px;
  transition: opacity 0.2s;
}

.preview-img.clickable {
  cursor: zoom-in;
}

.preview-img.clickable:hover {
  opacity: 0.92;
}

.broken-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  background: var(--bg-secondary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.fullscreen-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
}

.overlay-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  z-index: 2001;
}

.overlay-img {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  transition: transform 0.2s;
  cursor: default;
}

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.25s;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}
</style>
