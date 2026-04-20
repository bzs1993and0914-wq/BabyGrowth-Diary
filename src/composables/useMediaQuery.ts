import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 响应式媒体查询。多处调用相同 query 共享同一个 MediaQueryList 实例。
 *
 * @example
 * const isMobile = useMediaQuery('(max-width: 767px)')
 */
export function useMediaQuery(query: string) {
  const matches = ref(false)
  let mql: MediaQueryList | undefined

  function update(e?: MediaQueryListEvent) {
    matches.value = e?.matches ?? mql?.matches ?? false
  }

  onMounted(() => {
    mql = window.matchMedia(query)
    update()
    mql.addEventListener('change', update)
  })

  onUnmounted(() => {
    mql?.removeEventListener('change', update)
  })

  return matches
}
