<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useParentWordsStore } from '@/stores/parentWords'
import ParentWordCard from '@/components/parent-words/ParentWordCard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useRouter } from 'vue-router'
import { EditPen } from '@element-plus/icons-vue'

const store = useParentWordsStore()
const router = useRouter()

function loadMore() {
  if (store.hasMore && !store.loading) {
    store.nextPage()
    store.loadList(true)
  }
}

function handleScroll() {
  const scrollY = window.scrollY + window.innerHeight
  const docHeight = document.documentElement.scrollHeight
  if (docHeight - scrollY < 200) {
    loadMore()
  }
}

onMounted(() => {
  store.resetList()
  store.loadList()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="pw-list-view">
    <div class="pw-list-header">
      <h2 class="pw-list-title">父母有话说</h2>
      <el-button
        type="primary"
        round
        :icon="EditPen"
        @click="router.push('/parent-words/new')"
      >
        写下心里话
      </el-button>
    </div>

    <LoadingSkeleton v-if="store.loading && !store.items.length" type="card" :count="4" />

    <template v-else-if="store.items.length">
      <div class="pw-grid">
        <ParentWordCard
          v-for="item in store.items"
          :key="item.id"
          :item="item"
        />
      </div>

      <div v-if="store.loading" class="loading-more">
        <el-icon class="is-loading" :size="20">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8Z"/>
          </svg>
        </el-icon>
        <span>加载中...</span>
      </div>

      <div v-if="!store.hasMore && store.items.length > 0" class="end-hint">
        已加载全部心语
      </div>
    </template>

    <EmptyState
      v-else
      icon="✉️"
      title="还没有心里话"
      description="写下你想对宝宝说的第一句话吧"
      action-text="写下第一句话"
      action-route="/parent-words/new"
    />
  </div>
</template>

<style scoped>
.pw-list-view {
  min-height: 60vh;
}

.pw-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.pw-list-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.pw-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.end-hint {
  text-align: center;
  padding: 24px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

@media (max-width: 767px) {
  .pw-list-header {
    margin-bottom: 16px;
  }

  .pw-list-title {
    font-size: 18px;
  }

  .pw-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .loading-more {
    padding: 20px 0;
    font-size: 13px;
  }

  .end-hint {
    padding: 20px 0;
    font-size: 12px;
  }
}
</style>
