"use strict";const e=require("electron");e.contextBridge.exposeInMainWorld("electronAPI",{apiBaseUrl:"http://localhost:18900",platform:process.platform});
