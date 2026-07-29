import type { ModuleData, KPIData, IndicatorData, TimeSeriesPoint } from "./rasd-data"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"
const USE_API = process.env.NEXT_PUBLIC_USE_API === "true"

interface DataCache {
  imf: Record<string, { indicator: string; unit: string; data: { year: number; value: number }[] }>
  timeseries: Record<string, { data: { date: string; valeur: number; unite: string; source_code: string }[] }>
}

let cache: DataCache | null = null
let cacheTime = 0
const CACHE_TTL = 60_000

type RealtimeCallback = (data: any) => void
let realtimeSubscribers: RealtimeCallback[] = []
let eventSource: EventSource | null = null

function broadcastRealtime(data: any) {
  for (const cb of realtimeSubscribers) cb(data)
}

function subscribeSSE(collections: string) {
  if (eventSource) return
  if (!USE_API || !API_BASE) return

  try {
    const es = new EventSource(`${API_BASE}/stream?collections=${collections}`)
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === "update") broadcastRealtime(data)
      } catch { /* ignore parse errors */ }
    }
    es.onerror = () => {
      es.close()
      eventSource = null
      setTimeout(() => subscribeSSE(collections), 5000)
    }
    eventSource = es
  } catch {
    eventSource = null
  }
}

export function onRealtimeUpdate(cb: RealtimeCallback) {
  realtimeSubscribers.push(cb)
  return () => {
    realtimeSubscribers = realtimeSubscribers.filter((f) => f !== cb)
  }
}

async function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open("rasd-maroc-cache", 1)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains("imf")) db.createObjectStore("imf")
      if (!db.objectStoreNames.contains("timeseries")) db.createObjectStore("timeseries")
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function cacheSet(store: string, key: string, value: any) {
  try {
    const db = await openDB()
    db.transaction(store, "readwrite").objectStore(store).put(value, key)
  } catch { /* silently fail */ }
}

async function cacheGet(store: string, key: string): Promise<any> {
  try {
    const db = await openDB()
    return new Promise((resolve) => {
      const req = db.transaction(store, "readonly").objectStore(store).get(key)
      req.onsuccess = () => resolve(req.result)
      req.onerror = () => resolve(null)
    })
  } catch { return null }
}

async function loadData(): Promise<DataCache> {
  const now = Date.now()
  if (cache && now - cacheTime < CACHE_TTL) return cache

  if (USE_API && API_BASE) {
    try {
      const imfResp = await fetch(`${API_BASE}/imf`).then((r) => r.json())
      const imf: Record<string, any> = {}
      if (Array.isArray(imfResp)) {
        for (const ind of imfResp) {
          const detail = await fetch(`${API_BASE}/imf/${ind.code}`).then((r) => r.json())
          imf[ind.code] = detail
        }
      }
      cache = { imf, timeseries: {} }
      cacheTime = now
      await cacheSet("imf", "latest", imf)
      subscribeSSE("economie,imf_weo")
      return cache
    } catch {
      const cached = await cacheGet("imf", "latest")
      if (cached) {
        cache = { imf: cached, timeseries: {} }
        cacheTime = now
        return cache
      }
    }
  }

  try {
    const resp = await fetch("/data.json")
    const json = await resp.json()
    cache = json as DataCache
    cacheTime = now
    return cache
  } catch {
    return { imf: {}, timeseries: {} }
  }
}

// Apply real-time updates into cache
export function applyRealtimeUpdate(data: any) {
  if (!data?.events || !cache) return
  for (const evt of data.events) {
    for (const doc of evt.docs || []) {
      if (doc.code && doc.year !== undefined) {
        if (!cache.timeseries[doc.code]) cache.timeseries[doc.code] = { data: [] }
        const existing = cache.timeseries[doc.code].data
        const idx = existing.findIndex((d: any) => d.date === String(doc.year))
        const point = { date: String(doc.year), valeur: doc.value, unite: "", source_code: doc.source || "" }
        if (idx >= 0) existing[idx] = point
        else existing.push(point)
      }
    }
  }
}

const ECONOMIE_TO_CODE: Record<string, string> = {
  "exportation": "EXPORTATIONS",
  "importation": "IMPORTATIONS",
  "ide": "IDE.FLUX",
  "balance commerciale": "BALANCE.COMMERCIALE",
  "chomage": "CHOMAGE.TAUX",
  "pib.*croissance": "PIB.CROISSANCE",
  "emploi": "EMPLOI.VOLUME",
  "inflation": "IPC.GLISSEMENT",
  "investissement public": "INVESTISSEMENT.PUBLIC",
  "dette publique.*pib": "DETTE.PUBLIQUE.PCT_PIB",
  "dette publique": "DETTE.PUBLIQUE",
  "deficit budgetaire": "DEFICIT.BUDGET",
  "recettes fiscales": "RECETTES.FISCALES",
  "depenses totales": "DEPENSES.TOTAL",
  "reserves de change": "RESERVES.CHANGE",
  "taux de change": "CHANGE.USD",
}

function findEconomieMatch(kpi: KPIData, ts: Record<string, any>): any | null {
  const label = kpi.label.toLowerCase()
  for (const [keyword, code] of Object.entries(ECONOMIE_TO_CODE)) {
    if (new RegExp(keyword).test(label) && ts[code]) return { data: ts[code].data, code }
  }
  return null
}

function matchToKpi(kpi: KPIData, dataPoints: { date?: string; year?: number; valeur: number }[]): Partial<KPIData> {
  if (!dataPoints?.length) return {}
  const sorted = [...dataPoints].sort((a, b) => {
    const ay = a.year || parseInt(a.date || "0")
    const by = b.year || parseInt(b.date || "0")
    return by - ay
  })
  const latest = sorted[0]
  const prev = sorted.length > 1 ? sorted[1] : null
  const value = latest.valeur
  const previousValue = prev?.valeur ?? kpi.previousValue
  const diff = value - previousValue
  const trend: "up" | "down" | "stable" = diff > 0.01 ? "up" : diff < -0.01 ? "down" : "stable"
  return { value, previousValue, trend }
}

function matchToTimeSeries(dataPoints: { date?: string; year?: number; valeur: number }[]): TimeSeriesPoint[] {
  if (!dataPoints?.length) return []
  return dataPoints.map((d) => ({
    year: d.year || parseInt(d.date || "0"),
    value: d.valeur,
  }))
}

const IMF_KEYWORDS: Record<string, string> = {
  "pib": "NGDP_RPCH",
  "inflation": "PCPIEPCH",
  "chomage": "LUR",
  "dette": "GGXWDG",
  "deficit": "GGXCNL",
  "investissement": "NID_NGDP",
  "exportation": "TX_RPCH",
  "importation": "TM_RPCH",
  "population": "LP",
  "balance courante": "BCA_NGDPD",
  "recette publique": "GGR",
  "depense publique": "GGX",
  "pib.*habitant": "NGDPDPC",
}

function findImfMatch(kpi: KPIData, imf: Record<string, any>): any | null {
  const code = (kpi as any).indicatorCode
  if (code && imf[code]) return imf[code]
  const label = kpi.label.toLowerCase()
  for (const [keyword, imfCode] of Object.entries(IMF_KEYWORDS)) {
    if (new RegExp(keyword).test(label) && imf[imfCode]) return imf[imfCode]
  }
  return null
}

function kpiFromImf(imfData: any): Partial<KPIData> {
  if (!imfData?.data?.length) return {}
  const points = imfData.data as { year: number; value: number }[]
  const latest = points[points.length - 1]
  const prev = points.length > 1 ? points[points.length - 2] : null
  const value = latest.value
  const previousValue = prev?.value ?? 0
  const diff = value - previousValue
  const trend: "up" | "down" | "stable" = diff > 0.01 ? "up" : diff < -0.01 ? "down" : "stable"
  return { value, previousValue, trend }
}

function imfToTimeSeries(imfData: any): TimeSeriesPoint[] {
  if (!imfData?.data?.length) return []
  return imfData.data.map((d: { year: number; value: number }) => ({ year: d.year, value: d.value }))
}

export async function enrichModule(module: ModuleData): Promise<ModuleData> {
  const data = await loadData()
  const hasImf = data.imf && Object.keys(data.imf).length > 0
  const hasTs = data.timeseries && Object.keys(data.timeseries).length > 0

  if (!hasImf && !hasTs) return module

  const newKpis = module.kpis.map((kpi) => {
    if (hasImf) {
      const match = findImfMatch(kpi, data.imf)
      if (match) return { ...kpi, ...kpiFromImf(match) }
    }
    if (hasTs) {
      const match = findEconomieMatch(kpi, data.timeseries)
      if (match) return { ...kpi, ...matchToKpi(kpi, match.data) }
    }
    return kpi
  })

  const newIndicators = module.indicators.map((ind) => {
    if (hasImf && data.imf[ind.code]?.data?.length) {
      return { ...ind, national: imfToTimeSeries(data.imf[ind.code]) }
    }
    if (hasTs) {
      const match = data.timeseries[ind.code]
      if (match?.data?.length) {
        return { ...ind, national: matchToTimeSeries(match.data) }
      }
      for (const [keyword, code] of Object.entries(ECONOMIE_TO_CODE)) {
        if (new RegExp(keyword).test(ind.code.toLowerCase()) && data.timeseries[code]?.data?.length) {
          return { ...ind, national: matchToTimeSeries(data.timeseries[code].data) }
        }
      }
    }
    return ind
  })

  return { ...module, kpis: newKpis, indicators: newIndicators }
}
