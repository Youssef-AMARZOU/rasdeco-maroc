'use client'

import { Suspense, useMemo, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Cell,
  ReferenceLine, AreaChart, Area, PieChart, Pie, ScatterChart, Scatter,
  ComposedChart, Legend, ResponsiveContainer, Tooltip as ReTooltip,
} from 'recharts'
import { ArrowLeft, FileText } from 'lucide-react'
import { ALL_MODULES, MODULE_COLORS, type IndicatorData, type TimeSeriesPoint } from '@/lib/rasd-data'

const MIN_YEAR = 1999
const MAX_YEAR = 2026

function filterTimeSeries(pts: TimeSeriesPoint[], startYear: number, endYear: number) {
  return pts.filter((p) => p.year >= startYear && p.year <= endYear)
}
function formatTableValue(value: number) {
  return value.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const COLORS = ['#f97316','#22c55e','#3b82f6','#a855f7','#ef4444','#eab308','#06b6d4','#ec4899','#14b8a6','#8b5cf6','#f43f5e','#84cc16','#0ea5e9','#d946ef','#f59e0b','#6366f1']

export default function KPIDetailPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Chargement...</div>}>
      <KPIDetailContent />
    </Suspense>
  )
}

function KPIDetailContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const code = searchParams.get('code') || ''
  const [startYear, setStartYear] = useState(2015)
  const [endYear, setEndYear] = useState(2026)
  const [activeChart, setActiveChart] = useState('line')

  const { indicator, moduleColor } = useMemo(() => {
    for (const mod of ALL_MODULES) {
      const found = mod.indicators.find((ind) => ind.code === code)
      if (found) return { indicator: found, moduleColor: MODULE_COLORS[mod.name] || '#f97316' }
    }
    return { indicator: null, moduleColor: '#f97316' }
  }, [code])

  if (!indicator) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white dark:bg-slate-900">
        <div className="text-center space-y-4">
          <p className="text-lg text-slate-600 dark:text-slate-400">Indicateur non trouvé : {code || '(aucun code)'}</p>
          <button onClick={() => router.back()} className="px-4 py-2 bg-slate-200 dark:bg-slate-700 rounded-lg text-sm">Retour</button>
        </div>
      </div>
    )
  }

  const allPts = indicator.national
  const filteredPts = allPts.filter((p) => p.year >= startYear && p.year <= endYear)
  const vals = filteredPts.map((p) => p.value)
  const current = vals[vals.length - 1]
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const avg = vals.reduce((s, v) => s + v, 0) / vals.length
  const minYear = filteredPts.find((p) => p.value === min)?.year
  const maxYear = filteredPts.find((p) => p.value === max)?.year
  const first = vals[0]
  const change = current - first
  const changePct = first !== 0 ? (change / Math.abs(first)) * 100 : 0

  const reg = endYear < 2015 && indicator.regionalOld ? indicator.regionalOld : indicator.regional
  const regData = reg.map((r) => ({ name: r.region.length > 18 ? r.region.slice(0, 16) + '…' : r.region, fullName: r.region, value: r.value }))

  const chartTabs = [
    { key: 'line', label: 'Courbes' }, { key: 'area', label: 'Aires' },
    { key: 'bar', label: 'Barres' }, { key: 'composed', label: 'Composé' },
    { key: 'pie', label: 'Camembert' }, { key: 'donut', label: 'Anneau' },
    { key: 'treemap', label: 'Treemap' }, { key: 'scatter', label: 'Points' },
  ]

  const subKPIs = [
    { label: 'Valeur actuelle', value: formatTableValue(current), sub: `${endYear}`, color: '#3b82f6', bg: 'bg-blue-50 dark:bg-blue-950/40' },
    { label: 'Minimum', value: formatTableValue(min), sub: `${minYear}`, color: '#ef4444', bg: 'bg-red-50 dark:bg-red-950/40' },
    { label: 'Maximum', value: formatTableValue(max), sub: `${maxYear}`, color: '#22c55e', bg: 'bg-emerald-50 dark:bg-emerald-950/40' },
    { label: 'Moyenne', value: formatTableValue(avg), sub: `${startYear}–${endYear}`, color: '#a855f7', bg: 'bg-purple-50 dark:bg-purple-950/40' },
    { label: 'Variation totale', value: `${change >= 0 ? '+' : ''}${formatTableValue(change)}`, sub: `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`, color: change >= 0 ? '#22c55e' : '#ef4444', bg: change >= 0 ? 'bg-emerald-50 dark:bg-emerald-950/40' : 'bg-red-50 dark:bg-red-950/40' },
    { label: 'Observations', value: `${filteredPts.length}`, sub: 'années', color: '#64748b', bg: 'bg-slate-50 dark:bg-slate-800' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-900">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        <div className="flex items-center gap-4">
          <button onClick={() => router.back()} className="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 shadow-sm hover:shadow">
            <ArrowLeft className="h-4 w-4" />
            Retour
          </button>
          <div className="h-6 w-px bg-slate-300 dark:bg-slate-600" />
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">{indicator.label}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">Unité : {indicator.unit} — Source : HCP / BAM — {indicator.national.length} observations</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Début</span>
            <select value={startYear} onChange={(e) => setStartYear(Number(e.target.value))} className="px-2 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white">
              {Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, i) => MIN_YEAR + i).map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">Fin</span>
            <select value={endYear} onChange={(e) => setEndYear(Number(e.target.value))} className="px-2 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white">
              {Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, i) => MIN_YEAR + i).map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {subKPIs.map((b) => (
            <div key={b.label} className={`rounded-xl border border-slate-200 dark:border-slate-700 ${b.bg} p-4 text-center`}>
              <p className="text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">{b.label}</p>
              <p className="text-2xl font-bold mt-1" style={{ color: b.color }}>{b.value}</p>
              {b.sub && <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{b.sub}</p>}
            </div>
          ))}
        </div>

        <div className="flex gap-1 overflow-x-auto pb-1">
          {chartTabs.map((tr) => (
            <button key={tr.key} onClick={() => setActiveChart(tr.key)} className={`shrink-0 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeChart === tr.key ? 'text-white shadow-md' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'}`} style={activeChart === tr.key ? { backgroundColor: moduleColor } : undefined}>
              {tr.label}
            </button>
          ))}
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
          {activeChart === 'line' && (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={allPts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <ReferenceLine y={avg} stroke="#a855f7" strokeDasharray="5 5" label={{ value: `Moy: ${formatTableValue(avg)}`, position: 'right', fill: '#a855f7', fontSize: 11 }} />
                <Line type="monotone" dataKey="value" stroke={moduleColor} strokeWidth={2.5} dot={{ r: 3, fill: moduleColor }} activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }} name={indicator.label} />
              </LineChart>
            </ResponsiveContainer>
          )}
          {activeChart === 'area' && (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={allPts}>
                <defs><linearGradient id="gA" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={moduleColor} stopOpacity={0.3} /><stop offset="95%" stopColor={moduleColor} stopOpacity={0.02} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <Area type="monotone" dataKey="value" stroke={moduleColor} fill="url(#gA)" strokeWidth={2} name={indicator.label} />
              </AreaChart>
            </ResponsiveContainer>
          )}
          {activeChart === 'bar' && (
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={allPts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <Bar dataKey="value" name={indicator.label} radius={[4, 4, 0, 0]}>
                  {allPts.map((entry, i) => <Cell key={i} fill={entry.year >= startYear && entry.year <= endYear ? moduleColor : '#cbd5e1'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
          {activeChart === 'composed' && (
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={allPts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <Legend />
                <Area type="monotone" dataKey="value" fill={moduleColor} fillOpacity={0.12} stroke={moduleColor} name={indicator.label} />
                <Bar dataKey="value" barSize={18} fill="#3b82f6" fillOpacity={0.45} name={indicator.label} />
                <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} name={indicator.label} />
              </ComposedChart>
            </ResponsiveContainer>
          )}
          {activeChart === 'pie' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ResponsiveContainer width="100%" height={400}>
                <PieChart><Pie data={regData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={150} label={({ name, value }) => `${name}: ${formatTableValue(value)}`}>{regData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></PieChart>
              </ResponsiveContainer>
              <div className="max-h-[400px] overflow-y-auto"><table className="w-full text-sm"><thead><tr className="bg-slate-100 dark:bg-slate-700"><th className="text-left p-2 text-xs font-semibold">Région</th><th className="text-right p-2 text-xs font-semibold">Valeur</th></tr></thead><tbody>{regData.map((d, i) => <tr key={i} className={i % 2 === 0 ? '' : 'bg-slate-50 dark:bg-slate-800'}><td className="p-2"><span className="inline-block w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[i % COLORS.length] }} />{d.fullName}</td><td className="p-2 text-right font-mono font-semibold">{formatTableValue(d.value)}</td></tr>)}</tbody></table></div>
            </div>
          )}
          {activeChart === 'donut' && (
            <ResponsiveContainer width="100%" height={400}>
              <PieChart><Pie data={regData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={140} paddingAngle={2} label={({ name }) => name}>{regData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></PieChart>
            </ResponsiveContainer>
          )}
          {activeChart === 'treemap' && (
            <ResponsiveContainer width="100%" height={400}>
              <div className="grid grid-cols-3 gap-2 h-full">
                {regData.slice(0, 9).map((r, i) => (
                  <div key={i} className="rounded-lg p-3 flex flex-col justify-end" style={{ backgroundColor: COLORS[i % COLORS.length], opacity: 0.8 }}>
                    <span className="text-white text-[10px] font-semibold truncate">{r.name}</span>
                    <span className="text-white text-lg font-bold">{formatTableValue(r.value)}</span>
                  </div>
                ))}
              </div>
            </ResponsiveContainer>
          )}
          {activeChart === 'scatter' && (
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /><XAxis type="number" dataKey="year" name="Année" domain={[startYear, endYear]} tick={{ fontSize: 11, fill: '#94a3b8' }} /><YAxis type="number" dataKey="value" name="Valeur" tick={{ fontSize: 11, fill: '#94a3b8' }} /><ReTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} /><Scatter data={filteredPts} fill={moduleColor} /></ScatterChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="p-4 border-b border-slate-200 dark:border-slate-700">
            <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
              <FileText className="h-4 w-4 text-slate-500" />
              Données complètes — {indicator.national.length} observations
            </h3>
          </div>
          <div className="max-h-[500px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                <th className="text-left p-2 font-semibold">Année</th>
                <th className="text-right p-2 font-semibold">Valeur ({indicator.unit})</th>
                <th className="text-right p-2 font-semibold">Variation</th>
                <th className="text-right p-2 font-semibold">%</th>
                <th className="text-center p-2 font-semibold">Tendance</th>
              </tr></thead>
              <tbody>
                {indicator.national.map((pt, idx) => {
                  const prev = idx > 0 ? indicator.national[idx - 1].value : pt.value
                  const diff = pt.value - prev
                  const pct = prev !== 0 ? (diff / Math.abs(prev)) * 100 : 0
                  const trend = diff > 0.001 ? 'up' : diff < -0.001 ? 'down' : 'stable'
                  const inRange = pt.year >= startYear && pt.year <= endYear
                  return (
                    <tr key={pt.year} className={inRange ? (idx % 2 === 0 ? 'bg-blue-50/70 dark:bg-blue-950/30' : 'bg-blue-100/40 dark:bg-blue-950/20') : (idx % 2 === 0 ? '' : 'bg-slate-50 dark:bg-slate-800/50')}>
                      <td className="p-2 font-medium text-slate-900 dark:text-slate-100">{pt.year}{inRange && startYear !== endYear && <span className="ml-1 text-[10px] text-blue-600 dark:text-blue-400">• plage</span>}</td>
                      <td className="p-2 text-right font-mono tabular-nums font-semibold text-slate-900 dark:text-slate-100">{formatTableValue(pt.value)}</td>
                      <td className={`p-2 text-right font-mono tabular-nums ${diff > 0.001 ? 'text-emerald-600 dark:text-emerald-400' : diff < -0.001 ? 'text-red-500 dark:text-red-400' : 'text-amber-500 dark:text-amber-400'}`}>{idx === 0 ? '—' : `${diff > 0 ? '+' : ''}${formatTableValue(diff)}`}</td>
                      <td className={`p-2 text-right font-mono tabular-nums ${diff > 0.001 ? 'text-emerald-600 dark:text-emerald-400' : diff < -0.001 ? 'text-red-500 dark:text-red-400' : 'text-amber-500 dark:text-amber-400'}`}>{idx === 0 ? '—' : `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`}</td>
                      <td className="p-2 text-center">{idx === 0 ? '—' : <span className={`font-medium ${trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' : trend === 'down' ? 'text-red-500 dark:text-red-400' : 'text-amber-500 dark:text-amber-400'}`}>{trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}</span>}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
