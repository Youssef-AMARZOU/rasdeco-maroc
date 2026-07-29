const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("rasd", {
  // Check if API services are reachable
  checkApi: () => ipcRenderer.invoke("check-api"),

  // Get app version and build info
  getVersion: () => ipcRenderer.invoke("get-version"),

  // Listen for real-time data updates from main process
  onRealtimeUpdate: (callback) => {
    const handler = (_event, data) => callback(data)
    ipcRenderer.on("realtime-update", handler)
    return () => ipcRenderer.removeListener("realtime-update", handler)
  },

  // Listen for connection status changes
  onConnectionChange: (callback) => {
    const handler = (_event, status) => callback(status)
    ipcRenderer.on("connection-change", handler)
    return () => ipcRenderer.removeListener("connection-change", handler)
  },

  // Force sync data
  syncData: () => ipcRenderer.invoke("sync-data"),
})
