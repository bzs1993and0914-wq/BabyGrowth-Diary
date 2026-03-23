"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("electronAPI", {
  apiBaseUrl: "http://localhost:18900",
  platform: process.platform
});
