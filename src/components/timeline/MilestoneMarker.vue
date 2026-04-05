<script setup lang="ts">
defineProps<{
  name: string
  icon: string
  categoryName: string
}>()

const iconMap: Record<string, string> = {
  Trophy: '🏆',
  ChatDotRound: '💬',
  Heart: '❤️',
  Bowl: '🍼',
  Star: '⭐',
  User: '👤',
}
</script>

<template>
  <span class="milestone-marker">
    <span class="marker-icon">{{ iconMap[icon] || '🎯' }}</span>
    <span class="marker-name">{{ name }}</span>
  </span>
</template>

<style scoped>
.milestone-marker {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  border-radius: 20px;
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
  font-size: 12px;
  font-weight: 600;
  color: #e65100;
  white-space: nowrap;
}

.marker-icon {
  font-size: 13px;
}

.marker-name {
  max-width: 155px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
