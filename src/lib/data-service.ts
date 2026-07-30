import type { ModuleData, KPIData, IndicatorData, TimeSeriesPoint } from "./rasd-data"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"
const USE_API = process.env.NEXT_PUBLIC_USE_API === "true"

interface DataCache {
  imf: Record<string, { indicator: string; unit: string; data: { year: number; value: number }[] }>
  timeseries: Record<string, { data: { date: string; valeur: number; unite: string; source_code: string }[] }>
}

let cache: DataCache | null = null

type RealtimeCallback = (data: any) => void
let realtimeSubscribers: RealtimeCallback[] = []
let eventSource: EventSource | null = null
let loadedPrefixes = new Set<string>()

function broadcastRealtime(data: any) {
  for (const cb of realtimeSubscribers) cb(data)
}

function subscribeSSE(collections: string) {
  if (eventSource) return
  if (!USE_API || !API_BASE) return
  try {
    const es = new EventSource(`${API_BASE}/stream?collections=${collections}`)
    es.onmessage = (event) => {
      try { const data = JSON.parse(event.data); if (data.type === "update") broadcastRealtime(data) } catch { }
    }
    es.onerror = () => { es.close(); eventSource = null; setTimeout(() => subscribeSSE(collections), 5000) }
    eventSource = es
  } catch { eventSource = null }
}

export function onRealtimeUpdate(cb: RealtimeCallback) {
  realtimeSubscribers.push(cb)
  return () => { realtimeSubscribers = realtimeSubscribers.filter((f) => f !== cb) }
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
  try { const db = await openDB(); db.transaction(store, "readwrite").objectStore(store).put(value, key) } catch { }
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

function toDotCode(code: string): string {
  return code.replace(/_/g, ".")
}

async function fetchJSON(url: string): Promise<any> {
  const resp = await fetch(url)
  return resp.json()
}

async function loadIMF(): Promise<Record<string, any>> {
  try { return await fetchJSON("/data/imf.json") } catch { }
  try {
    if (USE_API && API_BASE) {
      const imfResp = await fetchJSON(`${API_BASE}/imf`)
      if (Array.isArray(imfResp)) {
        const imf: Record<string, any> = {}
        for (const ind of imfResp) imf[ind.code] = await fetchJSON(`${API_BASE}/imf/${ind.code}`)
        await cacheSet("imf", "latest", imf)
        return imf
      }
    }
  } catch {
    const cached = await cacheGet("imf", "latest")
    if (cached) return cached
  }
  return {}
}

function inferRequiredPrefixes(module: ModuleData): string[] {
  const prefixes = new Set<string>()
  for (const kpi of module.kpis) {
    const code = (kpi as any).indicatorCode as string | undefined
    if (code) {
      const p = code.split("_")[0]
      prefixes.add(p)
    }
  }
  for (const ind of module.indicators) {
    const p = ind.code.split("_")[0]
    prefixes.add(p)
  }
  return Array.from(prefixes)
}

async function loadTimeseriesForModule(module: ModuleData): Promise<Record<string, any>> {
  const ts: Record<string, any> = {}
  if (cache?.timeseries) Object.assign(ts, cache.timeseries)
  const prefixes = inferRequiredPrefixes(module)
  const toLoad = prefixes.filter((p) => !loadedPrefixes.has(p))
  if (toLoad.length === 0) return ts
  for (const prefix of toLoad) {
    const url = `/data/ts_${prefix.toLowerCase()}.json`
    try {
      const data = await fetchJSON(url)
      Object.assign(ts, data)
      loadedPrefixes.add(prefix)
    } catch { }
  }
  return ts
}

async function ensureBaseData() {
  if (cache) return
  cache = { imf: {}, timeseries: {} }
  const imf = await loadIMF()
  if (cache) cache.imf = imf
  subscribeSSE("economie,imf_weo")
}

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
  "exportation": "EXPORTATIONS", "importation": "IMPORTATIONS", "ide": "IDE.FLUX",
  "balance commerciale": "BALANCE.COMMERCIALE", "chomage": "CHOMAGE.TAUX",
  "pib.*croissance": "PIB.CROISSANCE", "emploi": "EMPLOI.VOLUME",
  "inflation": "IPC.GLISSEMENT", "investissement public": "INVESTISSEMENT.PUBLIC",
  "dette publique.*pib": "DETTE.PUBLIQUE.PCT_PIB", "dette publique": "DETTE.PUBLIQUE",
  "deficit budgetaire": "DEFICIT.BUDGET", "recettes fiscales": "RECETTES.FISCALES",
  "depenses totales": "DEPENSES.TOTAL", "reserves de change": "RESERVES.CHANGE",
  "taux de change": "CHANGE.USD",
}

const CODE_TO_ECONOMIE: Record<string, string> = {
  "PIB_CROISSANCE": "PIB.CROISSANCE", "IPC_GLISSEMENT": "IPC.GLISSEMENT",
  "CHOMAGE": "CHOMAGE.TAUX", "DETTE_PUBLIQUE": "DETTE.PUBLIQUE",
  "RESERVES_CHANGE": "RESERVES.CHANGE", "IDE_FLUX": "IDE.FLUX",
  "DEFICIT_BUDGET": "DEFICIT.BUDGET", "EXPORTATIONS": "EXPORTATIONS",
  "IMPORTATIONS": "IMPORTATIONS", "BALANCE_COURANTE": "BALANCE.COMMERCIALE",
  "EMPLOI": "EMPLOI.VOLUME", "INVESTISSEMENT_PUBLIC": "INVESTISSEMENT.PUBLIC",
}

const CODE_TO_IMF: Record<string, string> = {
  "PIB_CROISSANCE": "NGDP_RPCH", "IPC_GLISSEMENT": "PCPIEPCH",
  "DETTE_PUBLIQUE": "GGXWDG", "PIB_PAR_HAB": "NGDPDPC", "POPULATION": "LP",
  "BALANCE_COURANTE": "BCA_NGDPD", "DEFICIT_BUDGET": "GGXCNL",
}

const IMF_KEYWORDS: Record<string, string> = {
  "pib": "NGDP_RPCH", "inflation": "PCPIEPCH", "chomage": "LUR",
  "dette": "GGXWDG", "deficit": "GGXCNL", "investissement": "NID_NGDP",
  "exportation": "TX_RPCH", "importation": "TM_RPCH", "population": "LP",
  "balance courante": "BCA_NGDPD", "recette publique": "GGR",
  "depense publique": "GGX", "pib.*habitant": "NGDPDPC",
}

function findEconomieByCode(indicatorCode: string | undefined, ts: Record<string, any>): any | null {
  if (!indicatorCode) return null
  const dotCode = toDotCode(indicatorCode)
  if (ts[dotCode]?.data?.length) return { data: ts[dotCode].data, code: dotCode }
  const mapped = CODE_TO_ECONOMIE[indicatorCode]
  if (mapped && ts[mapped]?.data?.length) return { data: ts[mapped].data, code: mapped }
  return null
}

function findImfByCode(indicatorCode: string | undefined, imf: Record<string, any>): any | null {
  if (!indicatorCode) return null
  if (imf[indicatorCode]?.data?.length) return imf[indicatorCode]
  const mapped = CODE_TO_IMF[indicatorCode]
  if (mapped && imf[mapped]?.data?.length) return imf[mapped]
  return null
}

function findEconomieByLabel(kpi: KPIData, ts: Record<string, any>): any | null {
  const label = kpi.label.toLowerCase()
  const indicatorCode = (kpi as any).indicatorCode as string | undefined
  for (const [keyword, code] of Object.entries(ECONOMIE_TO_CODE)) {
    if (new RegExp(keyword).test(label) && ts[code]) {
      const dotCode = indicatorCode ? indicatorCode.replace(/_/g, ".") : ""
      if (dotCode === code) continue
      return { data: ts[code].data, code }
    }
  }
  return null
}

function findImfByLabel(kpi: KPIData, imf: Record<string, any>): any | null {
  const label = kpi.label.toLowerCase()
  for (const [keyword, imfCode] of Object.entries(IMF_KEYWORDS)) {
    if (new RegExp(keyword).test(label) && imf[imfCode]) return imf[imfCode]
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
  return dataPoints.map((d) => ({ year: d.year || parseInt(d.date || "0"), value: d.valeur }))
}

function kpiFromImf(imfData: any): Partial<KPIData> {
  if (!imfData?.data?.length) return {}
  const points = imfData.data as { year: number; value: number }[]
  const targetYear = 2025
  let best = points[0]
  let bestIdx = 0
  for (let i = 1; i < points.length; i++) {
    if (Math.abs(points[i].year - targetYear) < Math.abs(best.year - targetYear)) {
      best = points[i]
      bestIdx = i
    }
  }
  const prev = bestIdx > 0 ? points[bestIdx - 1] : null
  const value = best.value
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
  await ensureBaseData()
  if (!cache) return module
  const imf = cache.imf || {}
  const ts = await loadTimeseriesForModule(module)
  const hasImf = Object.keys(imf).length > 0
  const hasTs = Object.keys(ts).length > 0

  if (!hasImf && !hasTs) return module

  const indicatorCode = (kpi: KPIData) => (kpi as any).indicatorCode as string | undefined

  const newKpis = module.kpis.map((kpi) => {
    const code = indicatorCode(kpi)
    if (hasImf) {
      const byCode = findImfByCode(code, imf)
      if (byCode) return { ...kpi, ...kpiFromImf(byCode) }
    }
    if (hasTs) {
      const byCode = findEconomieByCode(code, ts)
      if (byCode) return { ...kpi, ...matchToKpi(kpi, byCode.data) }
    }
    if (code) return kpi
    if (hasImf) {
      const byLabel = findImfByLabel(kpi, imf)
      if (byLabel) return { ...kpi, ...kpiFromImf(byLabel) }
    }
    if (hasTs) {
      const byLabel = findEconomieByLabel(kpi, ts)
      if (byLabel) return { ...kpi, ...matchToKpi(kpi, byLabel.data) }
    }
    return kpi
  })

  const newIndicators = module.indicators.map((ind) => {
    if (hasTs) {
      const dotCode = toDotCode(ind.code)
      const match = ts[dotCode]
      if (match?.data?.length) return { ...ind, national: matchToTimeSeries(match.data) }
    }
    if (hasImf && imf[ind.code]?.data?.length) {
      return { ...ind, national: imfToTimeSeries(imf[ind.code]) }
    }
    if (hasTs) {
      const mapped = CODE_TO_ECONOMIE[ind.code]
      if (mapped && ts[mapped]?.data?.length) return { ...ind, national: matchToTimeSeries(ts[mapped].data) }
    }
    if (hasTs) {
      for (const [keyword, code] of Object.entries(ECONOMIE_TO_CODE)) {
        if (new RegExp(keyword).test(ind.code.toLowerCase()) && ts[code]?.data?.length) {
          return { ...ind, national: matchToTimeSeries(ts[code].data) }
        }
      }
    }
    return ind
  })

  return { ...module, kpis: newKpis, indicators: newIndicators }
}
