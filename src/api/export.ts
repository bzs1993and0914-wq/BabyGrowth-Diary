import client from './client'
import type { ExportRequest, ExportStatus } from '@/types/api'

export function startExport(data?: ExportRequest): Promise<ExportStatus> {
  return client.post('/api/export', data ?? {}).then((r) => r.data)
}

export function getExportStatus(exportId: string): Promise<ExportStatus> {
  return client.get('/api/export/status', { params: { export_id: exportId } }).then((r) => r.data)
}
