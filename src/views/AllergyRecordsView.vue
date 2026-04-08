<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordsStore } from '@/stores/records'

/** 旧链接 /allergy-records：打开「过敏」筛选并回到时间轴，不再单独展示一页 */
const router = useRouter()
const store = useRecordsStore()

onMounted(() => {
  store.timeline.allergyOnly = true
  store.timeline.page = 1
  router.replace('/')
})
</script>

<template>
  <div class="redirect-placeholder" aria-hidden="true" />
</template>

<style scoped>
.redirect-placeholder {
  min-height: 40vh;
}
</style>
