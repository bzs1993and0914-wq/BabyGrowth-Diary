import client from './client'
import type { GrowthMetricCreate, GrowthMetricResponse, GrowthMetricQuery, GrowthCurveData } from '@/types/api'

export function createGrowthMetric(data: GrowthMetricCreate): Promise<GrowthMetricResponse> {
  return client.post('/api/growth-metrics', data).then((r) => r.data)
}

export function deleteGrowthMetric(id: number): Promise<void> {
  return client.delete(`/api/growth-metrics/${id}`).then(() => undefined)
}

export function fetchGrowthMetrics(params?: GrowthMetricQuery): Promise<GrowthMetricResponse[]> {
  return client.get('/api/growth-metrics', { params }).then((r) => r.data)
}

export function fetchGrowthCurve(params?: GrowthMetricQuery): Promise<GrowthCurveData> {
  return client.get('/api/growth-metrics/curve', { params }).then((r) => r.data)
}
