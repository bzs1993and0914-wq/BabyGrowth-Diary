"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
let mainWindow = null;
let pythonProcess = null;
const isDev = !electron.app.isPackaged;
function startPythonBackend() {
  var _a, _b;
  if (isDev) {
    pythonProcess = child_process.spawn(
      "uvicorn",
      ["app.main:app", "--reload", "--port", "18900"],
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
electron.app.whenReady().then(() => {
  startPythonBackend();
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
