import { app, BrowserWindow } from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null

const isDev = !app.isPackaged

function startPythonBackend(): void {
  if (isDev) {
    pythonProcess = spawn(
      'uvicorn',
      ['app.main:app', '--reload', '--port', '18900'],
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

app.whenReady().then(() => {
  startPythonBackend()
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
