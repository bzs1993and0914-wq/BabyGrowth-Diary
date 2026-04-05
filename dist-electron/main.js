"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
const http = require("http");
let mainWindow = null;
let pythonProcess = null;
const isDev = !electron.app.isPackaged;
const BACKEND_PORT = 18900;
const DEV_BACKEND_HEALTH_URL = `http://127.0.0.1:${BACKEND_PORT}/api/health`;
function waitForExistingDevBackend(maxWaitMs, intervalMs) {
  const deadline = Date.now() + maxWaitMs;
  const tryOnce = () => new Promise((resolve) => {
    const req = http.get(DEV_BACKEND_HEALTH_URL, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.setTimeout(400, () => {
      req.destroy();
      resolve(false);
    });
  });
  return new Promise((resolve) => {
    const poll = () => {
      void tryOnce().then((ok) => {
        if (ok) {
          resolve(true);
          return;
        }
        if (Date.now() >= deadline) {
          resolve(false);
          return;
        }
        setTimeout(poll, intervalMs);
      });
    };
    poll();
  });
}
function startPythonBackend() {
  var _a, _b;
  if (isDev) {
    pythonProcess = child_process.spawn(
      "uvicorn",
      ["app.main:app", "--reload", `--port`, String(BACKEND_PORT)],
      {
        cwd: path.join(__dirname, "..", "backend"),
        shell: true,
        stdio: "pipe"
      }
    );
  } else {
    const serverPath = path.join(process.resourcesPath, "babygrow-server");
    pythonProcess = child_process.spawn(serverPath, [], {
      stdio: "pipe"
    });
  }
  (_a = pythonProcess.stdout) == null ? void 0 : _a.on("data", (data) => {
    console.log(`[Backend] ${data.toString().trim()}`);
  });
  (_b = pythonProcess.stderr) == null ? void 0 : _b.on("data", (data) => {
    console.error(`[Backend] ${data.toString().trim()}`);
  });
  pythonProcess.on("error", (err) => {
    console.error("Failed to start Python backend:", err);
  });
}
function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}
function createWindow() {
  mainWindow = new electron.BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    },
    title: "BabyGrow - 宝宝成长记录"
  });
  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}
electron.app.whenReady().then(async () => {
  if (isDev) {
    const alreadyUp = await waitForExistingDevBackend(15e3, 250);
    if (alreadyUp) {
      console.log(
        "[Backend] 开发模式下检测到端口",
        BACKEND_PORT,
        "已有健康实例，跳过 Electron 内嵌 uvicorn（避免双进程锁库）"
      );
    } else {
      startPythonBackend();
    }
  } else {
    startPythonBackend();
  }
  createWindow();
  electron.app.on("activate", () => {
    if (electron.BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});
electron.app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    electron.app.quit();
  }
});
electron.app.on("before-quit", () => {
  stopPythonBackend();
});
