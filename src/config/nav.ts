import { Clock, Star, TrendCharts, EditPen } from '@element-plus/icons-vue'
import type { NavItem, NavGroupItem, NavLinkItem } from '@/types/nav'
import { isNavGroup } from '@/types/nav'

/**
 * 顶部主导航配置
 *
 * 扩展方式：
 *  - 新增普通链接：追加 { label, path, name, icon } 对象
 *  - 新增下拉分组：追加 { label, children: [...] } 对象
 *  - 调整顺序：直接移动数组元素位置
 */
export const navItems: NavItem[] = [
  {
    label: '宝宝成长',
    children: [
      { label: '时间轴', path: '/', name: 'timeline', icon: Clock },
      { label: '里程碑', path: '/milestones', name: 'milestones', icon: Star },
      { label: '成长曲线', path: '/growth', name: 'growth', icon: TrendCharts },
    ],
  },
  {
    label: '父母有话说',
    path: '/parent-words',
    name: 'parent-words',
    icon: EditPen,
  },
]

/** 所有导航项对应的路由 name 集合，用于判断当前页面是否展示 Tab Bar */
export const navRouteNames: ReadonlySet<string> = new Set(
  navItems.flatMap((item) =>
    isNavGroup(item)
      ? (item as NavGroupItem).children.map((c) => c.name)
      : [(item as NavLinkItem).name],
  ),
)
