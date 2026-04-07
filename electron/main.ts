import {
  app,
  BrowserWindow,
  Tray,
  Menu,
  nativeImage,
  Notification,
} from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import http from 'http'
import Store from 'electron-store'
import type { NativeImage } from 'electron'

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null
let tray: Tray | null = null
let quitFromTray = false
/** false 时关闭窗口改为最小化（托盘不可用降级，见 research R-006） */
let hideToTrayOnClose = false

const isDev = !app.isPackaged

const BACKEND_PORT = 18900
const DEV_BACKEND_HEALTH_URL = `http://127.0.0.1:${BACKEND_PORT}/api/health`

type ReminderStoreSchema = {
  lastDailyRecordNudgeDate: string | null
}

const reminderStore = new Store<ReminderStoreSchema>({
  name: 'babygrow-reminders',
  defaults: { lastDailyRecordNudgeDate: null },
})

/** 专用托盘图（小 PNG）；勿用大尺寸 JPG 作菜单栏图标 — macOS 上几乎不可见或显示异常。彩色图标勿用 Template 模式。 */
const TRAY_ICON_NAME = 'trayBaby.png'

/** 16×16 单色 PNG（base64），文件缺失时兜底，避免 Tray 为空。 */
const TRAY_FALLBACK_PNG_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAP0lEQVR4nGNgGGjAiEfuPzFqGYnQiFcPE4maMdQwMVAImEi0HUMtEzVdMPAGMJKgj5FmXmAkxXZCGohKygMPACD0Bxb1lodaAAAAAElFTkSuQmCC'

/** 与系统托盘/菜单栏常规图标尺寸对齐（过大 PNG 会占满通知区高度）。 */
function normalizeTrayIconSize(img: NativeImage): NativeImage {
  const { width, height } = img.getSize()
  const max = process.platform === 'darwin' ? 22 : 16
  if (width <= max && height <= max) {
    return img
  }
  return img.resize({ width: max, height: max, quality: 'best' })
}

function trayIconPath(): string {
  if (isDev) {
    return join(__dirname, '..', 'public', TRAY_ICON_NAME)
  }
  return join(__dirname, '..', 'dist', TRAY_ICON_NAME)
}
// 彩色托盘图保留 PNG 原色，勿 setTemplateImage（否则菜单栏会按单色模板着色）。
// 兜底图为单色小 PNG，在 macOS 上仍可用 Template 以保证可见性。
function createTrayIcon(): NativeImage {
  try {
    const p = trayIconPath()
    let img = nativeImage.createFromPath(p)
    if (img.isEmpty()) {
      console.warn('[Tray] Icon empty at path, using embedded fallback', p)
      img = nativeImage.createFromBuffer(
        Buffer.from(TRAY_FALLBACK_PNG_BASE64, 'base64')
      )
      img = normalizeTrayIconSize(img)
      if (process.platform === 'darwin') {
        img.setTemplateImage(true)
      }
      return img
    }
    img = normalizeTrayIconSize(img)
    return img
  } catch (e) {
    console.warn('[Tray] Failed to load icon', e)
    let fb = nativeImage.createFromBuffer(
      Buffer.from(TRAY_FALLBACK_PNG_BASE64, 'base64')
    )
    fb = normalizeTrayIconSize(fb)
    if (process.platform === 'darwin') {
      fb.setTemplateImage(true)
    }
    return fb
  }
}

/** npm run dev 已由 concurrently 启动 uvicorn 时，避免再启一个进程争抢同一 SQLite 库。 */
function waitForExistingDevBackend(
  maxWaitMs: number,
  intervalMs: number
): Promise<boolean> {
  const deadline = Date.now() + maxWaitMs
  const tryOnce = (): Promise<boolean> =>
    new Promise((resolve) => {
      const req = http.get(DEV_BACKEND_HEALTH_URL, (res) => {
        resolve(res.statusCode === 200)
      })
      req.on('error', () => resolve(false))
      req.setTimeout(400, () => {
        req.destroy()
        resolve(false)
      })
    })
  return new Promise((resolve) => {
    const poll = (): void => {
      void tryOnce().then((ok) => {
        if (ok) {
          resolve(true)
          return
        }
        if (Date.now() >= deadline) {
          resolve(false)
          return
        }
        setTimeout(poll, intervalMs)
      })
    }
    poll()
  })
}

function startPythonBackend(): void {
  if (isDev) {
    pythonProcess = spawn(
      'uvicorn',
      ['app.main:app', '--reload', `--port`, String(BACKEND_PORT)],
      {
        cwd: join(__dirname, '..', 'backend'),
        shell: true,
        stdio: 'pipe',
      }
    )
  } else {
    const serverPath = join(process.resourcesPath, 'babygrow-server')
    pythonProcess = spawn(serverPath, [], {
      stdio: 'pipe',
    })
  }

  pythonProcess.stdout?.on('data', (data: Buffer) => {
    console.log(`[Backend] ${data.toString().trim()}`)
  })

  pythonProcess.stderr?.on('data', (data: Buffer) => {
    console.error(`[Backend] ${data.toString().trim()}`)
  })

  pythonProcess.on('error', (err: Error) => {
    console.error('Failed to start Python backend:', err)
  })
}

function stopPythonBackend(): void {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }
}

function showMainWindow(): void {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.show()
    mainWindow.focus()
    return
  }
  createWindow()
}

function destroyTray(): void {
  if (tray) {
    tray.destroy()
    tray = null
  }
}

function setupTray(): void {
  destroyTray()
  hideToTrayOnClose = false
  try {
    const icon = createTrayIcon()
    tray = new Tray(icon)
    hideToTrayOnClose = true
    tray.setToolTip('BabyGrow - 苒宝宝成长记录')
    const contextMenu = Menu.buildFromTemplate([
      {
        label: '显示主窗口',
        click: () => showMainWindow(),
      },
      { type: 'separator' },
      {
        label: '退出',
        click: () => {
          quitFromTray = true
          destroyTray()
          app.quit()
        },
      },
    ])
    tray.setContextMenu(contextMenu)
    // 不设 tray.on('click')：左键仅弹出上述菜单；由「显示主窗口」再 show（与 US4 验收一致）。
    // macOS 在已设 contextMenu 时通常不派发 click，见 Electron Tray 文档说明。
  } catch (e) {
    console.warn('[Tray] Unavailable, falling back to minimize-on-close', e)
    tray = null
    hideToTrayOnClose = false
  }
}

function localDateKey(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function maybeShowDailyRecordNudge(): void {
  const now = new Date()
  if (now.getHours() !== 17) {
    return
  }
  const key = localDateKey(now)
  if (reminderStore.get('lastDailyRecordNudgeDate') === key) {
    return
  }
  if (!Notification.isSupported()) {
    reminderStore.set('lastDailyRecordNudgeDate', key)
    return
  }
  const n = new Notification({
    title: 'BabyGrow',
    body: '该给宝宝创建新的记录啦',
  })
  n.on('click', () => showMainWindow())
  n.show()
  reminderStore.set('lastDailyRecordNudgeDate', key)
}

function startDailyReminderLoop(): void {
  maybeShowDailyRecordNudge()
  setInterval(() => maybeShowDailyRecordNudge(), 60_000)
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    title: 'BabyGrow - 宝宝成长记录',
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.on('close', (event) => {
    if (!quitFromTray) {
      event.preventDefault()
      if (hideToTrayOnClose) {
        mainWindow?.hide()
      } else {
        mainWindow?.minimize()
      }
    }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(async () => {
  if (isDev) {
    const alreadyUp = await waitForExistingDevBackend(15000, 250)
    if (alreadyUp) {
      console.log(
        '[Backend] 开发模式下检测到端口',
        BACKEND_PORT,
        '已有健康实例，跳过 Electron 内嵌 uvicorn（避免双进程锁库）'
      )
    } else {
      startPythonBackend()
    }
  } else {
    startPythonBackend()
  }

  createWindow()
  setupTray()
  startDailyReminderLoop()

  app.on('activate', () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show()
      return
    }
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  // 允许主窗口真正关闭（否则会因 close 里的 preventDefault 而无法退出）
  quitFromTray = true
  stopPythonBackend()
  destroyTray()
})
