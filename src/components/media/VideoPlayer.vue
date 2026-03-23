<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  src: string
  poster?: string
}>()

const broken = ref(false)
</script>

<template>
  <div class="video-player">
    <video
      v-if="!broken"
      controls
      preload="metadata"
      :poster="poster || undefined"
      class="player"
      @error="broken = true"
    >
      <source :src="src" />
    </video>
    <div v-else class="video-placeholder">
      <span>视频无法播放</span>
    </div>
  </div>
</template>

<style scoped>
.video-player {
  width: 100%;
}

.player {
  width: 100%;
  border-radius: 4px;
  background: #000;
  display: block;
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
</style>
