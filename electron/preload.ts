import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  apiBaseUrl: 'http://localhost:18900',
  platform: process.platform,
})
