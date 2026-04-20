<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { ParentWordListItem } from '@/types/api'
import { buildMediaApiUrl } from '@/api/media'

const props = defineProps<{
  item: ParentWordListItem
}>()

const router = useRouter()

const roleLabel = computed(() => {
  switch (props.item.author_role) {
    case 'dad': return '爸爸'
    case 'mom': return '妈妈'
    default: return '父母'
  }
})

const roleClass = computed(() => {
  switch (props.item.author_role) {
    case 'dad': return 'role-dad'
    case 'mom': return 'role-mom'
    default: return 'role-default'
  }
})

const thumbnailUrl = computed(() =>
  props.item.first_thumbnail ? buildMediaApiUrl(props.item.first_thumbnail) : null
)

const formattedDate = computed(() => {
  const d = new Date(props.item.created_at)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
})

function goDetail() {
  router.push(`/parent-words/${props.item.id}`)
}
</script>

<template>
  <div class="pw-card" @click="goDetail">
    <div v-if="thumbnailUrl" class="pw-card-thumb">
      <img :src="thumbnailUrl" alt="" loading="lazy" />
    </div>
    <div class="pw-card-body">
      <h3 class="pw-card-title">{{ item.title }}</h3>
      <p class="pw-card-preview">{{ item.content_preview }}</p>
      <div class="pw-card-meta">
        <span :class="['pw-role-tag', roleClass]">{{ roleLabel }}</span>
        <span class="pw-card-date">{{ formattedDate }}</span>
        <span v-if="item.media_count > 0" class="pw-card-media-count">
          📷 {{ item.media_count }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pw-card {
  background: var(--bg-primary, #fff);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.pw-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.pw-card-thumb {
  width: 100%;
  height: 160px;
  overflow: hidden;
}

.pw-card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pw-card-body {
  padding: 16px;
}

.pw-card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pw-card-preview {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pw-card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.pw-role-tag {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.role-dad {
  background: #e8f4fd;
  color: #1890ff;
}

.role-mom {
  background: #fff0f6;
  color: #eb2f96;
}

.role-default {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-secondary);
}

.pw-card-date {
  flex: 1;
}

.pw-card-media-count {
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .pw-card-thumb {
    height: 140px;
  }

  .pw-card-body {
    padding: 12px;
  }

  .pw-card-title {
    font-size: 15px;
  }

  .pw-card-preview {
    font-size: 13px;
    margin-bottom: 8px;
  }
}
</style>
