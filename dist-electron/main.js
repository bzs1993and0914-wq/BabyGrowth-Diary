"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
const http = require("http");
let mainWindow = null;
let pythonProcess = null;
let tray = null;
let quitFromTray = false;
let hideToTrayOnClose = false;
const isDev = !electron.app.isPackaged;
const BACKEND_PORT = 18900;
const DEV_BACKEND_HEALTH_URL = `http://127.0.0.1:${BACKEND_PORT}/api/health`;
const TRAY_ICON_NAME = "trayBaby.png";
const TRAY_FALLBACK_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAP0lEQVR4nGNgGGjAiEfuPzFqGYnQiFcPE4maMdQwMVAImEi0HUMtEzVdMPAGMJKgj5FmXmAkxXZCGohKygMPACD0Bxb1lodaAAAAAElFTkSuQmCC";
function normalizeTrayIconSize(img) {
  const { width, height } = img.getSize();
  const max = process.platform === "darwin" ? 22 : 16;
  if (width <= max && height <= max) {
    return img;
  }
  return img.resize({ width: max, height: max, quality: "best" });
}
function trayIconPath() {
  if (isDev) {
    return path.join(__dirname, "..", "public", TRAY_ICON_NAME);
  }
  return path.join(__dirname, "..", "dist", TRAY_ICON_NAME);
}
function createTrayIcon() {
  try {
    const p = trayIconPath();
    let img = electron.nativeImage.createFromPath(p);
    if (img.isEmpty()) {
      console.warn("[Tray] Icon empty at path, using embedded fallback", p);
      img = electron.nativeImage.createFromBuffer(
        Buffer.from(TRAY_FALLBACK_PNG_BASE64, "base64")
      );
      img = normalizeTrayIconSize(img);
      if (process.platform === "darwin") {
        img.setTemplateImage(true);
      }
      return img;
    }
    img = normalizeTrayIconSize(img);
    return img;
  } catch (e) {
    console.warn("[Tray] Failed to load icon", e);
    let fb = electron.nativeImage.createFromBuffer(
      Buffer.from(TRAY_FALLBACK_PNG_BASE64, "base64")
    );
    fb = normalizeTrayIconSize(fb);
    if (process.platform === "darwin") {
      fb.setTemplateImage(true);
    }
    return fb;
  }
}
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
function showMainWindow() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.show();
    mainWindow.focus();
    return;
  }
  createWindow();
}
function destroyTray() {
  if (tray) {
    tray.destroy();
    tray = null;
  }
}
function setupTray() {
  destroyTray();
  hideToTrayOnClose = false;
  try {
    const icon = createTrayIcon();
    tray = new electron.Tray(icon);
    hideToTrayOnClose = true;
    tray.setToolTip("BabyGrow - 苒宝宝成长记录");
    const contextMenu = electron.Menu.buildFromTemplate([
      {
        label: "显示主窗口",
        click: () => showMainWindow()
      },
      { type: "separator" },
      {
        label: "退出",
        click: () => {
          quitFromTray = true;
          destroyTray();
          electron.app.quit();
        }
      }
    ]);
    tray.setContextMenu(contextMenu);
  } catch (e) {
    console.warn("[Tray] Unavailable, falling back to minimize-on-close", e);
    tray = null;
    hideToTrayOnClose = false;
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
  mainWindow.on("close", (event) => {
    if (!quitFromTray) {
      event.preventDefault();
      if (hideToTrayOnClose) {
        mainWindow == null ? void 0 : mainWindow.hide();
      } else {
        mainWindow == null ? void 0 : mainWindow.minimize();
      }
    }
  });
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
  setupTray();
  electron.app.on("activate", () => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.show();
      return;
    }
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
  quitFromTray = true;
  stopPythonBackend();
  destroyTray();
});
