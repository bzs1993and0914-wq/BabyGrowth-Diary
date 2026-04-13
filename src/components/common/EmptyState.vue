<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps<{
  icon: string
  title: string
  description: string
  actionText?: string
  actionRoute?: string
}>()

const router = useRouter()

function handleAction() {
  if (props.actionRoute) {
    router.push(props.actionRoute)
  }
}
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">{{ icon }}</div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-desc">{{ description }}</p>
    <el-button
      v-if="actionText"
      type="primary"
      round
      size="large"
      @click="handleAction"
    >
      {{ actionText }}
    </el-button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.8;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
  max-width: 320px;
  line-height: 1.6;
}

@media (max-width: 767px) {
  .empty-state {
    padding: 48px 24px;
  }

  .empty-icon {
    font-size: 56px;
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 18px;
  }

  .empty-desc {
    font-size: 13px;
    max-width: 280px;
    margin-bottom: 20px;
  }
}
</style>
