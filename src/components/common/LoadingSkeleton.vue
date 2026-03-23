<script setup lang="ts">
defineProps<{
  type: 'card' | 'detail' | 'list'
  count?: number
}>()
</script>

<template>
  <div class="skeleton-wrap">
    <template v-if="type === 'card'">
      <div v-for="i in (count ?? 3)" :key="i" class="skeleton-card">
        <el-skeleton animated>
          <template #template>
            <el-skeleton-item variant="image" class="skeleton-img" />
            <div class="skeleton-text">
              <el-skeleton-item variant="h3" style="width: 50%" />
              <el-skeleton-item variant="text" style="width: 80%" />
              <el-skeleton-item variant="text" style="width: 60%" />
            </div>
          </template>
        </el-skeleton>
      </div>
    </template>

    <template v-else-if="type === 'detail'">
      <el-skeleton animated>
        <template #template>
          <el-skeleton-item variant="h1" style="width: 40%; margin-bottom: 16px" />
          <el-skeleton-item variant="image" class="skeleton-img-large" />
          <el-skeleton-item variant="text" style="width: 100%; margin-top: 16px" />
          <el-skeleton-item variant="text" style="width: 90%" />
          <el-skeleton-item variant="text" style="width: 70%" />
        </template>
      </el-skeleton>
    </template>

    <template v-else>
      <div v-for="i in (count ?? 3)" :key="i" class="skeleton-row">
        <el-skeleton animated>
          <template #template>
            <div class="skeleton-list-item">
              <el-skeleton-item variant="circle" style="width: 40px; height: 40px" />
              <div style="flex: 1">
                <el-skeleton-item variant="h3" style="width: 30%" />
                <el-skeleton-item variant="text" style="width: 60%" />
              </div>
            </div>
          </template>
        </el-skeleton>
      </div>
    </template>
  </div>
</template>

<style scoped>
.skeleton-wrap {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.skeleton-img {
  width: 100%;
  height: 160px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.skeleton-img-large {
  width: 100%;
  height: 300px;
  border-radius: 12px;
}

.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-row {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 12px 16px;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
