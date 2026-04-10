import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  apiBaseUrl: 'http://localhost:18900',
  platform: process.platform,
  onDailyRecordNudge(callback: (message: string) => void) {
    ipcRenderer.on('daily-record-nudge', (_event, message: string) => {
      callback(message)
    })
  },
})
