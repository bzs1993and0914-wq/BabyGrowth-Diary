<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMilestonesStore } from '@/stores/milestones'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
  dailyRecordId: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: []
}>()

const store = useMilestonesStore()
const selectedCategory = ref<number | null>(null)
const name = ref('')
const description = ref('')
const saving = ref(false)

const iconMap: Record<string, string> = {
  Trophy: '🏆',
  ChatDotRound: '💬',
  Heart: '❤️',
  Bowl: '🍼',
  Star: '⭐',
  User: '👤',
}

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

onMounted(() => {
  if (!store.categories.length) store.loadCategories()
})

async function handleSave() {
  if (!selectedCategory.value) {
    ElMessage.warning('请选择一个分类')
    return
  }
  if (!name.value.trim()) {
    ElMessage.warning('请输入里程碑名称')
    return
  }

  saving.value = true
  try {
    await store.addMilestone({
      daily_record_id: props.dailyRecordId,
      category_id: selectedCategory.value,
      name: name.value.trim(),
      description: description.value.trim() || undefined,
    })
    ElMessage.success('里程碑已保存')
    emit('saved')
    visible.value = false
    selectedCategory.value = null
    name.value = ''
    description.value = ''
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <el-dialog
    v-model="visible"
    title="标记里程碑"
    width="480px"
    destroy-on-close
  >
    <div class="picker-body">
      <p class="section-label">选择分类</p>
      <div class="category-grid">
        <div
          v-for="cat in store.categories"
          :key="cat.id"
          :class="['cat-item', { active: selectedCategory === cat.id }]"
          @click="selectedCategory = cat.id"
        >
          <span class="cat-icon">{{ iconMap[cat.icon || ''] || '🎯' }}</span>
          <span class="cat-name">{{ cat.name }}</span>
        </div>
      </div>

      <el-input
        v-model="name"
        placeholder="里程碑名称，如：第一次翻身"
        maxlength="50"
        show-word-limit
        class="field"
      />

      <el-input
        v-model="description"
        type="textarea"
        placeholder="描述（可选）"
        :rows="3"
        maxlength="200"
        class="field"
      />
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.picker-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.cat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
}

.cat-item:hover {
  border-color: var(--color-primary);
}

.cat-item.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.cat-icon {
  font-size: 24px;
}

.cat-name {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.field {
  margin-top: 4px;
}
</style>
