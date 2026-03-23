<script setup lang="ts">
import type { MediaEntryResponse, TextEntryResponse } from '@/types/api'
import { getMediaUrl, getThumbnailUrl } from '@/api/media'
import ImagePreview from '@/components/media/ImagePreview.vue'
import VideoPlayer from '@/components/media/VideoPlayer.vue'

defineProps<{
  mediaEntries: MediaEntryResponse[]
  textEntries: TextEntryResponse[]
}>()
</script>

<template>
  <div class="diary-view">
    <div
      v-for="(media, idx) in mediaEntries"
      :key="media.id"
      class="diary-block"
    >
      <div class="media-frame">
        <ImagePreview
          v-if="media.media_type === 'image'"
          :src="getMediaUrl(media.id)"
          :alt="media.description || media.original_filename || ''"
        />
        <VideoPlayer
          v-else
          :src="getMediaUrl(media.id)"
          :poster="media.thumbnail_path ? getThumbnailUrl(media.id) : ''"
        />
      </div>
      <p v-if="media.description" class="media-caption">{{ media.description }}</p>

      <!-- Interleave text entries between media -->
      <div
        v-if="textEntries[idx]"
        class="text-block"
      >
        <p class="diary-text">{{ textEntries[idx].content }}</p>
      </div>
    </div>

    <!-- Remaining text entries not paired with media -->
    <div
      v-for="text in textEntries.slice(mediaEntries.length)"
      :key="text.id"
      class="text-block"
    >
      <p class="diary-text">{{ text.content }}</p>
    </div>

    <!-- If only text entries and no media -->
    <template v-if="mediaEntries.length === 0">
      <div
        v-for="text in textEntries"
        :key="text.id"
        class="text-block"
      >
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.diary-view {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.diary-block {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.media-frame {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px var(--shadow-color);
}

.media-caption {
  font-size: 14px;
  color: var(--text-secondary);
  font-style: italic;
  text-align: center;
  padding: 0 16px;
}

.text-block {
  padding: 16px 0;
}

.diary-text {
  font-family: 'Georgia', 'Noto Serif SC', 'STSong', serif;
  font-size: 16px;
  line-height: 1.9;
  color: var(--text-primary);
  text-indent: 2em;
  white-space: pre-wrap;
}
</style>
