/**
 * Data service for RASD-Maroc dashboard.
 * Fetches real data from API or data.json and merges it into ModuleData.
 *
 * The KPI values and time series are replaced with real dataset values
 * while preserving the module structure (labels, descriptions, etc.).
 */
import type { ModuleData, KPIData, IndicatorData, TimeSeriesPoint, RegionalValue } from "./rasd-data"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ""
const USE_API = process.env.NEXT_PUBLIC_USE_API === "true"

interface DataCache {
  imf: Record<string, { indicator: string; unit: string; data: { year: number; value: number }[] }>
  timeseries: Record<string, { data: { date: string; valeur: number; unite: string; source_code: string }[] }>
  sources: Record<string, { rows: number; data: any[] }>
}

let cache: DataCache | null = null
let cacheTime = 0
const CACHE_TTL = 60_000 // 1 minute

async function loadData(): Promise<DataCache> {
  const now = Date.now()
  if (cache && now - cacheTime < CACHE_TTL) return cache

  if (USE_API && API_BASE) {
    try {
      const [imfResp, tsResp, srcResp] = await Promise.all([
        fetch(`${API_BASE}/imf`).then((r) => r.json()),
        fetch(`${API_BASE}/indicators`).then((r) => r.json()),
        fetch(`${API_BASE}/sources`).then((r) => r.json()),
      ])
      // Fetch each IMF indicator
      const imf: Record<string, any> = {}
      if (Array.isArray(imfResp)) {
        for (const ind of imfResp) {
          const detail = await fetch(`${API_BASE}/imf/${ind.code}`).then((r) => r.json())
          imf[ind.code] = detail
        }
      }
      cache = { imf, timeseries: {}, sources: {} }
      cacheTime = now
      return cache
    } catch {
      // fallback to static
    }
  }

  // Static fallback: read data.json
  try {
    const resp = await fetch("/data.json")
    const json = await resp.json()
    cache = json as DataCache
    cacheTime = now
    return cache
  } catch {
    return { imf: {}, timeseries: {}, sources: {} }
  }
}

function findImfMatch(kpi: KPIData, imf: Record<string, any>): any | null {
  const code = (kpi as any).indicatorCode
  if (code && imf[code]) return imf[code]

  // Fuzzy match by label keywords
  const label = kpi.label.toLowerCase()
  for (const [key, val] of Object.entries(imf)) {
    const indName = (val as any).indicator?.toLowerCase() || ""
    if (label.includes("pib") && key === "NGDP_RPCH") return val
    if (label.includes("inflation") && key === "PCPIEPCH") return val
    if (label.includes("chomage") && key === "LUR") return val
    if (label.includes("dette") && key === "GGXWDG") return val
    if (label.includes("deficit") && key === "GGXCNL") return val
    if (label.includes("investissement") && key === "NID_NGDP") return val
    if (label.includes("exportation") && key === "TX_RPCH") return val
    if (label.includes("importation") && key === "TM_RPCH") return val
    if (label.includes("population") && key === "LP") return val
    if (label.includes("balance") && key === "BCA") return val
    if (label.includes("recette") && key === "GGR") return val
    if (label.includes("depense") && key === "GGX") return val
    if (label.includes("pib.*habitant") && key === "NGDPDPC") return val
  }
  return null
}

function kpiFromImf(kpi: KPIData, imfData: any): Partial<KPIData> {
  if (!imfData?.data?.length) return {}

  const points = imfData.data as { year: number; value: number }[]
  const latest = points[points.length - 1]
  const prev = points.length > 1 ? points[points.length - 2] : null

  const value = latest.value
  const previousValue = prev?.value ?? kpi.previousValue
  const diff = value - previousValue
  const trend: "up" | "down" | "stable" = diff > 0.01 ? "up" : diff < -0.01 ? "down" : "stable"
  const unit = imfData.unit || kpi.unit

  return { value, previousValue, trend, unit }
}

function timeseriesFromImf(imfData: any): TimeSeriesPoint[] {
  if (!imfData?.data?.length) return []
  return imfData.data.map((d: { year: number; value: number }) => ({
    year: d.year,
    value: d.value,
  }))
}

/**
 * Enrich a ModuleData with real dataset values.
 * Returns a new ModuleData object with updated KPIs and indicators.
 */
export async function enrichModule(module: ModuleData): Promise<ModuleData> {
  const data = await loadData()
  if (!data.imf || Object.keys(data.imf).length === 0) return module

  const newKpis = module.kpis.map((kpi) => {
    const match = findImfMatch(kpi, data.imf)
    if (match) {
      const updates = kpiFromImf(kpi, match)
      return { ...kpi, ...updates }
    }
    return kpi
  })

  const newIndicators = module.indicators.map((ind) => {
    const match = data.imf[ind.code]
    if (match?.data?.length) {
      return { ...ind, national: timeseriesFromImf(match) }
    }
    return ind
  })

  return { ...module, kpis: newKpis, indicators: newIndicators }
}