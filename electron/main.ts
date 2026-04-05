import { app, BrowserWindow } from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import http from 'http'

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null

const isDev = !app.isPackaged

const BACKEND_PORT = 18900
const DEV_BACKEND_HEALTH_URL = `http://127.0.0.1:${BACKEND_PORT}/api/health`

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

  app.on('activate', () => {
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
  stopPythonBackend()
})
