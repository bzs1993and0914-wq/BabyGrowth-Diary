<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getRecords } from '@/api/records'
import type { RecordListItem } from '@/types/api'
import TimelineCard from '@/components/timeline/TimelineCard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const items = ref<RecordListItem[]>([])
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  try {
    // 后端 page_size 上限为 100（records.py），多页拉齐直到取完
    const all: typeof items.value = []
    let page = 1
    let total = Infinity
    const pageSize = 20
    while (all.length < total) {
      const res = await getRecords({
        view: 'day',
        page,
        page_size: pageSize,
        has_allergy: true,
      })
      all.push(...res.data.items)
      total = res.data.total
      page += 1
      if (res.data.items.length === 0) break
    }
    items.value = all
  } catch {
    ElMessage.error('加载过敏相关记录失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="allergy-page">
    <div class="page-nav">
      <el-button text :icon="ArrowLeft" @click="router.push('/')"
        >返回时间轴</el-button
      >
    </div>
    <header class="page-header">
      <h1>⚠️ 过敏记录汇总</h1>
      <p class="sub">以下为填写过「宝宝过敏食物」的记录，按日期从新到旧排列</p>
    </header>

    <LoadingSkeleton v-if="loading" type="card" :count="4" />

    <div v-else-if="items.length" class="day-grid">
      <TimelineCard
        v-for="item in items"
        :key="item.date"
        :item="item"
        layout="flat"
      />
    </div>

    <EmptyState
      v-else
      icon="🍼"
      title="暂无过敏记录"
      description="在新建或编辑记录时填写「宝宝过敏食物」后，将在此处集中显示"
      action-text="去添加记录"
      action-route="/record/new"
    />
  </div>
</template>

<style scoped>
.allergy-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-nav {
  margin-bottom: 8px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 22px;
  font-weight: 700;
  color: #bf360c;
  margin: 0 0 8px;
}

.sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.day-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding-bottom: 40px;
}
</style>
