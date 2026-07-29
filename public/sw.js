const CACHE = "rasd-v1"
const API_CACHE = "rasd-api-v1"
const STATIC_FILES = ["/", "/data.json", "/lib/data.json"]

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(STATIC_FILES)).then(() => self.skipWaiting())
  )
})

self.addEventListener("activate", (event) => {
  event.waitUntil(clients.claim())
})

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url)

  // API requests - cache-first, network-update
  if (url.port === "8080" || url.hostname === "localhost" || url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(event.request))
    return
  }

  // Static assets - cache-first
  if (url.pathname.match(/\.(js|css|json|png|ico|woff2?|ttf)$/)) {
    event.respondWith(cacheFirst(event.request))
    return
  }

  // HTML / main page - network-first
  event.respondWith(networkFirst(event.request))
})

async function cacheFirst(request) {
  const cached = await caches.match(request)
  if (cached) return cached
  try {
    const resp = await fetch(request)
    if (resp.ok) {
      const clone = resp.clone()
      caches.open(CACHE).then((c) => c.put(request, clone))
    }
    return resp
  } catch {
    return new Response("Offline", { status: 503 })
  }
}

async function networkFirst(request) {
  try {
    const resp = await fetch(request)
    if (resp.ok) {
      const clone = resp.clone()
      caches.open(API_CACHE).then((c) => c.put(request, clone))
    }
    return resp
  } catch {
    const cached = await caches.match(request)
    if (cached) return cached
    const cachedData = await caches.match("/data.json")
    if (cachedData && request.url.includes("/imf")) return cachedData
    return new Response(JSON.stringify({ error: "offline", data: [] }), {
      headers: { "Content-Type": "application/json" },
    })
  }
}
