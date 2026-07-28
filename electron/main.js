const { app, BrowserWindow, protocol } = require('electron')
const path = require('path')
const fs = require('fs')

app.commandLine.appendSwitch('disable-gpu')
app.commandLine.appendSwitch('disable-software-rasterizer')
app.commandLine.appendSwitch('disk-cache-size', '0')

const OUT_DIR = path.join(__dirname, '..', 'out')

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

  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    title: 'MAROC STAT',
    icon: path.join(__dirname, '..', 'public', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    autoHideMenuBar: true,
    backgroundColor: '#0a0a1a',
  })

  win.loadURL('app://index.html')
  win.maximize()
})

app.on('window-all-closed', () => {
  app.quit()
})
