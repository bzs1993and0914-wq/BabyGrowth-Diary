import type { Component } from 'vue'

/** 无子级的普通导航项 */
export interface NavLinkItem {
  label: string
  path: string
  name: string
  icon?: Component
}

/** 带子级下拉的导航组 */
export interface NavGroupItem {
  label: string
  icon?: Component
  children: NavLinkItem[]
}

/** 顶层导航项：可以是链接或分组 */
export type NavItem = NavLinkItem | NavGroupItem

export function isNavGroup(item: NavItem): item is NavGroupItem {
  return 'children' in item && Array.isArray(item.children)
}
