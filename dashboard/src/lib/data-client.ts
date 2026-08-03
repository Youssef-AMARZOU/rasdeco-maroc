/**
 * Data client for RASD-Maroc dashboard.
 *
 * In production (HF Space static): reads from generated data.json.
 * In development with API server: fetches from FastAPI.
 *
 * Run `python scripts/export_data_json.py` after ETL pipeline updates
 * to regenerate the static data file.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const USE_API = process.env.NEXT_PUBLIC_USE_API === "true";

let _staticData: any = null;

async function loadStaticData(): Promise<any> {
  if (_staticData) return _staticData;
  const resp = await fetch("/data.json");
  if (!resp.ok) {
    const alt = await fetch("/lib/data.json");
    if (!alt.ok) throw new Error("No static data available");
    _staticData = await alt.json();
  } else {
    _staticData = await resp.json();
  }
  return _staticData;
}

export async function fetchSummary() {
  if (USE_API) {
    const resp = await fetch(`${API_BASE}/summary`);
    return resp.json();
  }
  const data = await loadStaticData();
  return data.summary;
}

export async function fetchImfIndicators() {
  if (USE_API) {
    const resp = await fetch(`${API_BASE}/imf`);
    return resp.json();
  }
  const data = await loadStaticData();
  return Object.entries(data.imf || {}).map(([code, v]: any) => ({
    code,
    indicator: v.indicator,
    unit: v.unit,
    year_min: v.data?.[0]?.year,
    year_max: v.data?.[v.data.length - 1]?.year,
  }));
}

export async function fetchImf(code: string) {
  if (USE_API) {
    const resp = await fetch(`${API_BASE}/imf/${code}`);
    return resp.json();
  }
  const data = await loadStaticData();
  return data.imf?.[code] || { error: `Indicator '${code}' not found` };
}

export async function fetchSources() {
  if (USE_API) {
    const resp = await fetch(`${API_BASE}/sources`);
    return resp.json();
  }
  const data = await loadStaticData();
  return data.sources || {};
}

export async function fetchSource(name: string) {
  if (USE_API) {
    const resp = await fetch(`${API_BASE}/source/${name}`);
    return resp.json();
  }
  const data = await loadStaticData();
  return data.sources?.[name] || { error: `Source '${name}' not found` };
}

export async function fetchTimeseries(code: string, yearMin?: number, yearMax?: number) {
  if (USE_API) {
    const params = new URLSearchParams();
    if (yearMin) params.set("year_min", String(yearMin));
    if (yearMax) params.set("year_max", String(yearMax));
    const resp = await fetch(`${API_BASE}/timeseries/${code}?${params}`);
    return resp.json();
  }
  const data = await loadStaticData();
  const ts = data.timeseries?.[code];
  if (!ts) return { indicator: code, rows: 0, data: [] };
  let rows = ts.data;
  if (yearMin) rows = rows.filter((r: any) => parseInt(r.date) >= yearMin);
  if (yearMax) rows = rows.filter((r: any) => parseInt(r.date) <= yearMax);
  return { indicator: code, rows: rows.length, data: rows };
}