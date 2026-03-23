import client from './client'
import type { StorageStats } from '@/types/api'

export function fetchStorageStats(): Promise<StorageStats> {
  return client.get('/api/storage/stats').then((r) => r.data)
}
