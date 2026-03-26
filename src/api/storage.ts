import client from './client'
import type { StorageStats } from '@/types/api'

/** 获取当前用户的存储使用统计（记录数、媒体文件数及磁盘占用字节数）。 */
export function fetchStorageStats(): Promise<StorageStats> {
  return client.get('/api/storage/stats').then((r) => r.data)
}
