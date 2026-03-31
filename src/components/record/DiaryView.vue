<script setup lang="ts">
import { computed } from 'vue'
import type { MediaEntryResponse, TextEntryResponse } from '@/types/api'
import { getMediaUrl, getThumbnailUrl } from '@/api/media'
import ImagePreview from '@/components/media/ImagePreview.vue'
import VideoPlayer from '@/components/media/VideoPlayer.vue'

const props = withDefaults(
  defineProps<{
    mediaEntries: MediaEntryResponse[]
    textEntries: TextEntryResponse[]
    useDefaultMediaPlaceholder?: boolean
  }>(),
  { useDefaultMediaPlaceholder: false }
)

const placeholderSrc = `${import.meta.env.BASE_URL}default-growth-placeholder.svg`

const multiMedia = computed(() => props.mediaEntries.length > 1)
const gridClass = computed(() => {
  const n = props.mediaEntries.length
  if (n <= 1) return ''
  if (n === 2) return 'grid-2'
  if (n <= 4) return 'grid-4'
  if (n <= 6) return 'grid-6'
  return 'grid-9'
})

console.log('mediaEntries', props, 123)
</script>

<template>
  <div class="diary-view">
    <!-- 无媒体：仅默认图占位 -->
    <template v-if="mediaEntries.length === 0 && useDefaultMediaPlaceholder">
      <div class="media-frame placeholder-frame">
        <img
          :src="placeholderSrc"
          alt="宝宝成长曲线默认配图"
          class="placeholder-img"
        />
      </div>
      <div v-for="text in textEntries" :key="text.id" class="text-block">
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>

    <!-- 无媒体无占位：仅文字 -->
    <template
      v-else-if="mediaEntries.length === 0 && !useDefaultMediaPlaceholder"
    >
      <div v-for="text in textEntries" :key="text.id" class="text-block">
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>

    <!-- 多图：网格 + 文字 -->
    <template v-else-if="multiMedia">
      <div :class="['multi-media-grid', gridClass]">
        <div v-for="media in mediaEntries" :key="media.id" class="grid-cell">
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
          <p v-if="media.description" class="media-caption">
            {{ media.description }}
          </p>
        </div>
      </div>
      <div v-for="text in textEntries" :key="text.id" class="text-block">
        <p class="diary-text">{{ text.content }}</p>
      </div>
    </template>

    <!-- 单图：与文字交错（保持原有体验） -->
    <template v-else>
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
        <p v-if="media.description" class="media-caption">
          {{ media.description }}
        </p>

        <div v-if="textEntries[idx]" class="text-block">
          <p class="diary-text">{{ textEntries[idx].content }}</p>
        </div>
      </div>

      <div
        v-for="text in textEntries.slice(mediaEntries.length)"
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

.placeholder-frame {
  max-height: 360px;
  background: var(--bg-secondary);
}

.placeholder-img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: contain;
}

.multi-media-grid {
  display: grid;
  gap: 10px;
  width: 100%;
}

.grid-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-4 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-6 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-9 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-cell .media-frame {
  aspect-ratio: 1;
}

.grid-cell .media-frame :deep(img),
.grid-cell .media-frame :deep(video) {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
