import { ref, computed, type Ref } from 'vue'
import type { HighlightResponse } from '@/types/api'
import { addHighlight, removeHighlight } from '@/api/parentWords'

export interface TextSegment {
  text: string
  highlighted: boolean
  highlightIds: number[]
  color: string | null
}

export interface SelectionInfo {
  startOffset: number
  endOffset: number
  text: string
}

/**
 * Sweep-line algorithm: flatten overlapping highlights into non-overlapping segments.
 *
 * 1. Build boundary events (open/close) from all highlight intervals
 * 2. Sort by position; at same position process closes before opens to avoid empty segments
 * 3. Walk events, track active highlight set, emit segments
 */
function buildSegments(content: string, highlights: HighlightResponse[]): TextSegment[] {
  if (!highlights.length) {
    return [{ text: content, highlighted: false, highlightIds: [], color: null }]
  }

  const clamped = highlights.map((h) => ({
    ...h,
    start_offset: Math.max(0, Math.min(h.start_offset, content.length)),
    end_offset: Math.max(0, Math.min(h.end_offset, content.length)),
  })).filter((h) => h.start_offset < h.end_offset)

  if (!clamped.length) {
    return [{ text: content, highlighted: false, highlightIds: [], color: null }]
  }

  type Event = { pos: number; type: 'open' | 'close'; highlight: typeof clamped[0] }
  const events: Event[] = []

  for (const h of clamped) {
    events.push({ pos: h.start_offset, type: 'open', highlight: h })
    events.push({ pos: h.end_offset, type: 'close', highlight: h })
  }

  events.sort((a, b) => {
    if (a.pos !== b.pos) return a.pos - b.pos
    if (a.type === 'close' && b.type === 'open') return -1
    if (a.type === 'open' && b.type === 'close') return 1
    return 0
  })

  const segments: TextSegment[] = []
  const activeSet = new Map<number, typeof clamped[0]>()
  let cursor = 0

  for (const event of events) {
    if (event.pos > cursor) {
      const ids = Array.from(activeSet.keys())
      const topColor = activeSet.size > 0
        ? Array.from(activeSet.values()).at(-1)?.color ?? 'yellow'
        : null
      segments.push({
        text: content.slice(cursor, event.pos),
        highlighted: activeSet.size > 0,
        highlightIds: ids,
        color: topColor,
      })
    }
    cursor = event.pos

    if (event.type === 'open') {
      activeSet.set(event.highlight.id, event.highlight)
    } else {
      activeSet.delete(event.highlight.id)
    }
  }

  if (cursor < content.length) {
    segments.push({
      text: content.slice(cursor),
      highlighted: false,
      highlightIds: [],
      color: null,
    })
  }

  return segments.filter((s) => s.text.length > 0)
}

/**
 * Resolve char offset from a Selection anchor/focus within a container element.
 * Walks text nodes in DOM order, accumulating lengths until reaching the target node.
 */
function resolveOffset(container: HTMLElement, node: Node, nodeOffset: number): number {
  let offset = 0
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT)
  let current = walker.nextNode()
  while (current) {
    if (current === node) {
      return offset + nodeOffset
    }
    offset += (current.textContent?.length ?? 0)
    current = walker.nextNode()
  }
  return offset + nodeOffset
}

export function useTextHighlight(
  wordId: Ref<number>,
  content: Ref<string>,
  highlights: Ref<HighlightResponse[]>,
) {
  const saving = ref(false)
  const selectionInfo = ref<SelectionInfo | null>(null)
  const toolbarPos = ref({ x: 0, y: 0 })
  const showToolbar = ref(false)

  const segments = computed(() => buildSegments(content.value, highlights.value))

  function handleSelection(containerEl: HTMLElement) {
    const sel = window.getSelection()
    if (!sel || sel.isCollapsed || !sel.rangeCount) {
      showToolbar.value = false
      selectionInfo.value = null
      return
    }

    const range = sel.getRangeAt(0)
    if (!containerEl.contains(range.commonAncestorContainer)) {
      showToolbar.value = false
      selectionInfo.value = null
      return
    }

    const start = resolveOffset(containerEl, range.startContainer, range.startOffset)
    const end = resolveOffset(containerEl, range.endContainer, range.endOffset)

    if (start === end) {
      showToolbar.value = false
      selectionInfo.value = null
      return
    }

    const normalStart = Math.min(start, end)
    const normalEnd = Math.max(start, end)

    selectionInfo.value = {
      startOffset: normalStart,
      endOffset: normalEnd,
      text: content.value.slice(normalStart, normalEnd),
    }

    const rect = range.getBoundingClientRect()
    toolbarPos.value = {
      x: rect.left + rect.width / 2,
      y: rect.top - 8,
    }
    showToolbar.value = true
  }

  async function addNewHighlight(color = 'yellow') {
    if (!selectionInfo.value || saving.value) return

    saving.value = true
    try {
      const res = await addHighlight(wordId.value, {
        start_offset: selectionInfo.value.startOffset,
        end_offset: selectionInfo.value.endOffset,
        color,
      })
      highlights.value = [...highlights.value, res.data]
      window.getSelection()?.removeAllRanges()
      showToolbar.value = false
      selectionInfo.value = null
    } finally {
      saving.value = false
    }
  }

  async function removeHighlightById(highlightId: number) {
    if (saving.value) return
    saving.value = true
    try {
      await removeHighlight(wordId.value, highlightId)
      highlights.value = highlights.value.filter((h) => h.id !== highlightId)
    } finally {
      saving.value = false
    }
  }

  async function removeHighlightsAt(ids: number[]): Promise<{ success: number; failed: number }> {
    if (saving.value || !ids.length) return { success: 0, failed: 0 }
    saving.value = true
    try {
      // 使用 allSettled 隔离单个失败：只把接口成功的 id 从本地列表移除，
      // 避免"前端乐观清空 → 服务端保留"导致 UI 与数据库不一致。
      const results = await Promise.allSettled(
        ids.map((id) => removeHighlight(wordId.value, id).then(() => id)),
      )
      const removed = new Set<number>()
      let failed = 0
      for (const r of results) {
        if (r.status === 'fulfilled') removed.add(r.value)
        else failed += 1
      }
      if (removed.size) {
        highlights.value = highlights.value.filter((h) => !removed.has(h.id))
      }
      return { success: removed.size, failed }
    } finally {
      saving.value = false
    }
  }

  function dismissToolbar() {
    showToolbar.value = false
    selectionInfo.value = null
  }

  return {
    segments,
    saving,
    selectionInfo,
    toolbarPos,
    showToolbar,
    handleSelection,
    addNewHighlight,
    removeHighlightById,
    removeHighlightsAt,
    dismissToolbar,
  }
}
