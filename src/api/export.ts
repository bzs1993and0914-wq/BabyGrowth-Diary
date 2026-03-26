import client from './client'
import type { ExportRequest, ExportStatus } from '@/types/api'

/** 触发数据导出任务，返回 export_id；实际打包在后台异步进行。 */
export function startExport(data?: ExportRequest): Promise<ExportStatus> {
  return client.post('/api/export', data ?? {}).then((r) => r.data)
}

/** 轮询导出任务进度，completed 状态下 file_path 字段包含 ZIP 文件路径。 */
export function getExportStatus(exportId: string): Promise<ExportStatus> {
  return client.get('/api/export/status', { params: { export_id: exportId } }).then((r) => r.data)
}
