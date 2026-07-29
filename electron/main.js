const { app, BrowserWindow, protocol, ipcMain, net } = require('electron')
const path = require('path')
const fs = require('fs')

app.commandLine.appendSwitch('disable-gpu')
app.commandLine.appendSwitch('disable-software-rasterizer')

const OUT_DIR = path.join(__dirname, '..', 'out')
const API_BASE = process.env.API_URL || 'http://localhost:8080'

const MIME = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
}

let mainWindow = null
let sseConnection = null

async function checkApi() {
  try {
    const resp = await net.fetch(`${API_BASE}/health`, { method: 'GET', timeout: 3000 })
    return { connected: resp.ok, apiUrl: API_BASE }
  } catch {
    return { connected: false, apiUrl: API_BASE }
  }
}

function startSSE() {
  if (sseConnection) return
  try {
    const request = net.fetch(`${API_BASE}/stream?collections=economie,imf_weo`)
    sseConnection = request
    let buffer = ''
    const reader = request.body?.getReader()
    if (!reader) return

    const read = () => {
      reader.read().then(({ done, value }) => {
        if (done) { sseConnection = null; setTimeout(startSSE, 5000); return }
        buffer += new TextDecoder().decode(value)
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (mainWindow) mainWindow.webContents.send('realtime-update', data)
            } catch { /* skip */ }
          }
        }
        if (mainWindow) read()
      }).catch(() => {
        sseConnection = null
        setTimeout(startSSE, 5000)
      })
    }
    read()
  } catch {
    sseConnection = null
    setTimeout(startSSE, 10000)
  }
}

async function pollApiStatus() {
  const status = await checkApi()
  if (mainWindow) mainWindow.webContents.send('connection-change', status)
}

app.whenReady().then(() => {
  protocol.handle('app', (request) => {
    const url = new URL(request.url)
    let filePath = path.join(OUT_DIR, url.pathname === '/' ? 'index.html' : url.pathname)
    if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
      filePath = path.join(OUT_DIR, 'index.html')
    }
    const ext = path.extname(filePath)
    const contentType = MIME[ext] || 'application/octet-stream'
    const data = fs.readFileSync(filePath)
    return new Response(data, {
      headers: { 'Content-Type': contentType },
    })
  })

  ipcMain.handle('check-api', checkApi)
  ipcMain.handle('get-version', () => app.getVersion())

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'MAROC STAT',
    icon: path.join(__dirname, '..', 'public', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    autoHideMenuBar: true,
    backgroundColor: '#0a0a1a',
  })

  mainWindow.loadURL('app://index.html')
  mainWindow.maximize()

  pollApiStatus()
  setInterval(pollApiStatus, 30000)

  startSSE()
})

app.on('window-all-closed', () => {
  if (sseConnection) sseConnection = null
  app.quit()
})
