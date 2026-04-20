import { ref, watch, onUnmounted } from 'vue'

/**
 * 草稿数据结构，对应 localStorage 中存储的 JSON。
 */
interface DraftData {
  title: string
  content: string
  authorRole: string | null
  /** ISO 8601 时间戳，记录草稿最近一次保存的时刻 */
  savedAt: string
}

/** localStorage 键名前缀，完整键形如 `pw-draft-new` 或 `pw-draft-42` */
const DRAFT_PREFIX = 'pw-draft-'

/**
 * 轻量防抖：在最后一次调用后等待 `delay` ms 才真正执行 `fn`。
 * 项目未引入 @vueuse/core，因此手写替代。
 */
function useDebounceFn<T extends (...args: any[]) => void>(fn: T, delay: number): T {
  let timer: ReturnType<typeof setTimeout> | null = null
  return ((...args: any[]) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }) as unknown as T
}

function draftKey(key: string): string {
  return `${DRAFT_PREFIX}${key}`
}

/**
 * 父母心语草稿自动保存 composable。
 *
 * 将编辑中的标题、正文、作者身份持久化到 `localStorage`，
 * 防止浏览器意外关闭或误操作导致长文丢失。
 *
 * @param key - 草稿标识。新建心语传 `'new'`，编辑已有心语传其 id（如 `'42'`）。
 *
 * @example
 * ```ts
 * // ---- 在 ParentWordEditView.vue 中 ----
 * import { useParentWordDraft } from '@/composables/useParentWordDraft'
 *
 * const isNew = computed(() => route.name === 'parent-word-new')
 * const wordId = computed(() => isNew.value ? null : Number(route.params.id))
 * const draftKey = computed(() => isNew.value ? 'new' : String(wordId.value))
 *
 * // 1. 初始化 composable
 * const draft = useParentWordDraft(draftKey.value)
 *
 * // 2. 页面挂载后检测并恢复草稿
 * onMounted(async () => {
 *   if (draft.hasDraft.value) {
 *     await ElMessageBox.confirm('检测到未保存的草稿，是否恢复？')
 *     const saved = draft.restoreDraft()
 *     if (saved) {
 *       title.value = saved.title
 *       content.value = saved.content
 *       authorRole.value = saved.authorRole || ''
 *     }
 *   }
 *
 *   // 3. 启动自动保存（2s 防抖 + 30s 兜底定时器）
 *   draft.startAutoSave(() => ({
 *     title: title.value,
 *     content: content.value,
 *     authorRole: authorRole.value || null,
 *   }))
 * })
 *
 * // 4. 保存成功后清除草稿
 * async function handleSave() {
 *   await store.create({ ... })
 *   draft.clearDraft()
 * }
 * ```
 */
export function useParentWordDraft(key: string) {
  /** 是否存在可恢复的草稿（初始化时自动检测） */
  const hasDraft = ref(false)

  /**
   * 从 localStorage 读取草稿原始数据。
   * @returns 解析后的草稿对象；不存在或解析失败时返回 `null`。
   */
  function loadDraft(): DraftData | null {
    try {
      const raw = localStorage.getItem(draftKey(key))
      if (!raw) return null
      return JSON.parse(raw) as DraftData
    } catch {
      return null
    }
  }

  /**
   * 手动保存草稿到 localStorage，自动附加当前时间戳。
   * @param data - 不含 `savedAt` 的草稿字段。
   */
  function saveDraft(data: Omit<DraftData, 'savedAt'>) {
    const payload: DraftData = {
      ...data,
      savedAt: new Date().toISOString(),
    }
    localStorage.setItem(draftKey(key), JSON.stringify(payload))
    hasDraft.value = true
  }

  /** 删除 localStorage 中的草稿，同时将 `hasDraft` 置为 `false`。 */
  function clearDraft() {
    localStorage.removeItem(draftKey(key))
    hasDraft.value = false
  }

  /**
   * 读取并返回草稿内容（语义别名，等价于 `loadDraft()`）。
   * 适合在"是否恢复草稿"对话框确认后调用。
   */
  function restoreDraft(): DraftData | null {
    return loadDraft()
  }

  // 初始化：检测是否已有草稿
  hasDraft.value = !!loadDraft()

  /** 防抖版 saveDraft，编辑时每次按键最多 2s 写一次 localStorage */
  const debouncedSave = useDebounceFn(saveDraft, 2000)

  let intervalId: ReturnType<typeof setInterval> | null = null

  /**
   * 启动双重自动保存机制：
   * 1. **响应式 watch**：表单数据变化后 2s（防抖）自动保存；
   * 2. **30s 定时器**：兜底保障，即使 watch 因某些原因未触发也不会丢失。
   *
   * @param getData - 返回当前表单数据的函数，会被 `watch` 和定时器反复调用。
   */
  function startAutoSave(getData: () => Omit<DraftData, 'savedAt'>) {
    watch(getData, (data) => {
      if (data.title || data.content) {
        debouncedSave(data)
      }
    }, { deep: true })

    intervalId = setInterval(() => {
      const data = getData()
      if (data.title || data.content) {
        saveDraft(data)
      }
    }, 30000)
  }

  // 组件卸载时清理定时器，避免内存泄漏
  onUnmounted(() => {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  })

  return {
    hasDraft,
    loadDraft,
    saveDraft,
    clearDraft,
    restoreDraft,
    startAutoSave,
  }
}
