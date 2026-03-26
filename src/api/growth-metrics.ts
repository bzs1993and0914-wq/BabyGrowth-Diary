import client from './client'
import type { GrowthMetricCreate, GrowthMetricResponse, GrowthMetricQuery, GrowthCurveData } from '@/types/api'

/** 为指定记录添加一条生长指标数据（身高/体重/头围）。 */
export function createGrowthMetric(data: GrowthMetricCreate): Promise<GrowthMetricResponse> {
  return client.post('/api/growth-metrics', data).then((r) => r.data)
}

/** 删除指定生长指标记录。 */
export function deleteGrowthMetric(id: number): Promise<void> {
  return client.delete(`/api/growth-metrics/${id}`).then(() => undefined)
}

/** 查询生长指标列表，支持按类型和日期范围过滤。 */
export function fetchGrowthMetrics(params?: GrowthMetricQuery): Promise<GrowthMetricResponse[]> {
  return client.get('/api/growth-metrics', { params }).then((r) => r.data)
}

/** 获取生长曲线数据（日期序列 + 数值序列），供图表组件直接渲染。 */
export function fetchGrowthCurve(params?: GrowthMetricQuery): Promise<GrowthCurveData> {
  return client.get('/api/growth-metrics/curve', { params }).then((r) => r.data)
}
