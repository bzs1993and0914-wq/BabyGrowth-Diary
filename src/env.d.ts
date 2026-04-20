/// <reference types="vite/client" />

import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    hideHeader?: boolean
  }
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<
    Record<string, unknown>,
    Record<string, unknown>,
    unknown
  >
  export default component
}

declare global {
  interface Window {
    electronAPI?: {
      apiBaseUrl: string
      platform: string
    }
  }
}
