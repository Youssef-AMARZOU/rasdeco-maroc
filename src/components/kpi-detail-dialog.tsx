'use client'

import * as React from 'react'
import { useState, useMemo } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  Treemap as RTreemap, ScatterChart, Scatter,
  AreaChart, Area, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ReferenceLine,
  XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip, Legend, ResponsiveContainer,
  ComposedChart,
} from 'recharts'
import type { IndicatorData, RegionalValue } from '@/lib/rasd-data'

const CHART_COLORS = [
  '#f97316', '#22c55e', '#3b82f6', '#a855f7', '#ef4444',
  '#eab308', '#06b6d4', '#ec4899', '#14b8a6', '#8b5cf6',
  '#f43f5e', '#84cc16',
]

function formatVal(v: number): string {
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`
  if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(1)}K`
  if (Number.isInteger(v)) return v.toString()
  return v.toFixed(2)
}

interface KPIDetailDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  label: string
  unit: string
  indicator: IndicatorData
  startYear: number
  endYear: number
}

type ChartTab = 'line' | 'bar' | 'area' | 'pie' | 'donut' | 'treemap' | 'scatter' | 'composed' | 'table'

const TABS: { key: ChartTab; label: string; icon: string }[] = [
  { key: 'line', label: 'Lignes', icon: '📈' },
  { key: 'area', label: 'Aires', icon: '📊' },
  { key: 'bar', label: 'Barres', icon: '📶' },
  { key: 'composed', label: 'Composé', icon: '📉' },
  { key: 'pie', label: 'Camembert', icon: '🥧' },
  { key: 'donut', label: 'Anneau', icon: '🍩' },
  { key: 'treemap', label: 'Treemap', icon: '🗺️' },
  { key: 'scatter', label: 'Scatter', icon: '⚬' },
  { key: 'table', label: 'Tableau', icon: '📋' },
]

export function KPIDetailDialog({
  open, onOpenChange, label, unit, indicator, startYear, endYear,
}: KPIDetailDialogProps) {
  const [activeChart, setActiveChart] = useState<ChartTab>('line')

  const nationalFiltered = useMemo(
    () => indicator.national.filter((p) => p.year >= startYear && p.year <= endYear),
    [indicator, startYear, endYear]
  )

  const nationalAll = indicator.national

  const subKPIs = useMemo(() => {
    const vals = nationalFiltered.map((p) => p.value)
    if (vals.length === 0) return null
    const current = vals[vals.length - 1]
    const min = Math.min(...vals)
    const max = Math.max(...vals)
    const avg = vals.reduce((s, v) => s + v, 0) / vals.length
    const minYear = nationalFiltered.find((p) => p.value === min)?.year
    const maxYear = nationalFiltered.find((p) => p.value === max)?.year
    const first = vals[0]
    const last = vals[vals.length - 1]
    const change = last - first
    const changePct = first !== 0 ? (change / Math.abs(first)) * 100 : 0
    const trend = change > 0.001 ? 'up' : change < -0.001 ? 'down' : 'stable'
    return { current, min, max, avg, minYear, maxYear, change, changePct, trend, count: vals.length }
  }, [nationalFiltered])

  const lineData = useMemo(
    () => nationalAll.map((p) => ({
      year: p.year,
      value: p.value,
      inRange: p.year >= startYear && p.year <= endYear,
    })),
    [nationalAll, startYear, endYear]
  )

  const regionalData = useMemo(() => {
    const reg = endYear < 2015 && indicator.regionalOld ? indicator.regionalOld : indicator.regional
    return reg.map((r) => ({ name: r.region, value: r.value }))
  }, [indicator, endYear])

  const pieData = useMemo(() => {
    const total = regionalData.reduce((s, r) => s + r.value, 0)
    return regionalData.map((r) => ({
      name: r.name.length > 20 ? r.name.slice(0, 18) + '…' : r.name,
      fullName: r.name,
      value: r.value,
      pct: total > 0 ? ((r.value / total) * 100).toFixed(1) : '0',
    }))
  }, [regionalData])

  const treemapData = useMemo(
    () => regionalData.map((r, i) => ({
      name: r.name,
      size: r.value,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    })),
    [regionalData]
  )

  const scatterData = useMemo(
    () => nationalAll.map((p) => ({ x: p.year, y: p.value })),
    [nationalAll]
  )

  const avgLine = subKPIs?.avg ?? 0

  if (!subKPIs) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">{label}</DialogTitle>
          <DialogDescription className="space-y-1">
            <p>Unité : {unit || 'Valeur'} — Source : HCP / BAM / MESRS</p>
            <p className="text-xs text-muted-foreground">
              Période : {startYear === endYear ? startYear : `${startYear}–${endYear}`} — {subKPIs.count} observations
            </p>
          </DialogDescription>
        </DialogHeader>

        {/* Sub-KPIs Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-2">
          <SubKPIBox label="Actuel" value={formatVal(subKPIs.current)} color="#3b82f6" />
          <SubKPIBox label="Min" value={formatVal(subKPIs.min)} sub={`${subKPIs.minYear}`} color="#ef4444" />
          <SubKPIBox label="Max" value={formatVal(subKPIs.max)} sub={`${subKPIs.maxYear}`} color="#22c55e" />
          <SubKPIBox label="Moyenne" value={formatVal(subKPIs.avg)} color="#a855f7" />
          <SubKPIBox label="Variation" value={`${subKPIs.change >= 0 ? '+' : ''}${formatVal(subKPIs.change)}`} sub={`${subKPIs.changePct >= 0 ? '+' : ''}${subKPIs.changePct.toFixed(1)}%`} color={subKPIs.trend === 'up' ? '#22c55e' : subKPIs.trend === 'down' ? '#ef4444' : '#eab308'} />
          <SubKPIBox label="Obs." value={`${subKPIs.count}`} color="#64748b" />
        </div>

        {/* Chart Tabs */}
        <div className="flex gap-1 overflow-x-auto pb-1 mt-3">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveChart(t.key)}
              className={`shrink-0 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeChart === t.key
                  ? 'bg-primary text-white shadow'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              <span className="mr-1">{t.icon}</span>{t.label}
            </button>
          ))}
        </div>

        {/* Chart Content */}
        <div className="mt-3 min-h-[300px]">
          {activeChart === 'line' && (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <ReTooltip />
                <Legend />
                <ReferenceLine y={avgLine} stroke="#a855f7" strokeDasharray="5 5" label="Moy." />
                <Line type="monotone" dataKey="value" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} name={label} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'area' && (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={lineData}>
                <defs>
                  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f97316" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <ReTooltip />
                <Area type="monotone" dataKey="value" stroke="#f97316" fill="url(#areaGrad)" strokeWidth={2} name={label} />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'bar' && (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <ReTooltip />
                <Bar dataKey="value" name={label} radius={[4, 4, 0, 0]}>
                  {lineData.map((entry, i) => (
                    <Cell key={i} fill={entry.inRange ? '#f97316' : '#cbd5e1'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'composed' && (
            <ResponsiveContainer width="100%" height={320}>
              <ComposedChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <ReTooltip />
                <Legend />
                <Area type="monotone" dataKey="value" fill="#f97316" fillOpacity={0.15} stroke="#f97316" name={label} />
                <Bar dataKey="value" barSize={16} fill="#3b82f6" fillOpacity={0.5} name={label} />
                <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} name={label} />
              </ComposedChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'pie' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label={({ name, pct }) => `${name} ${pct}%`}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <ReTooltip formatter={(v: number) => formatVal(v)} />
                </PieChart>
              </ResponsiveContainer>
              <div className="max-h-[320px] overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/50">
                      <TableHead className="text-xs">Région</TableHead>
                      <TableHead className="text-xs text-right">Valeur</TableHead>
                      <TableHead className="text-xs text-right">%</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pieData.map((d, i) => (
                      <TableRow key={i} className={i % 2 === 0 ? 'bg-background' : 'bg-muted/30'}>
                        <TableCell className="text-xs font-medium py-1">
                          <span className="inline-block w-2.5 h-2.5 rounded-full mr-1.5" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                          {d.fullName}
                        </TableCell>
                        <TableCell className="text-xs text-right font-mono py-1">{formatVal(d.value)}</TableCell>
                        <TableCell className="text-xs text-right font-mono py-1">{d.pct}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {activeChart === 'donut' && (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={110}
                  paddingAngle={2}
                  label={({ name, pct }) => `${name} ${pct}%`}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <ReTooltip formatter={(v: number) => formatVal(v)} />
              </PieChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'treemap' && (
            <ResponsiveContainer width="100%" height={320}>
              <RTreemap
                data={treemapData}
                dataKey="size"
                nameKey="name"
                stroke="#fff"
                fill="#f97316"
              >
                <ReTooltip formatter={(v: number) => formatVal(v)} />
              </RTreemap>
            </ResponsiveContainer>
          )}

          {activeChart === 'scatter' && (
            <ResponsiveContainer width="100%" height={320}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" dataKey="x" name="Année" tick={{ fontSize: 11 }} />
                <YAxis type="number" dataKey="y" name="Valeur" tick={{ fontSize: 11 }} />
                <ReTooltip cursor={{ strokeDasharray: '3 3' }} formatter={(v: number) => formatVal(v)} />
                <Scatter data={scatterData} fill="#f97316" />
              </ScatterChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'table' && (
            <div className="max-h-[400px] overflow-y-auto rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow className="bg-muted/80 hover:bg-muted/80">
                    <TableHead className="sticky top-0 bg-background z-10 font-semibold">Année</TableHead>
                    <TableHead className="sticky top-0 bg-background z-10 text-right font-semibold">Valeur ({unit})</TableHead>
                    <TableHead className="sticky top-0 bg-background z-10 text-right font-semibold">Variation</TableHead>
                    <TableHead className="sticky top-0 bg-background z-10 text-right font-semibold">%</TableHead>
                    <TableHead className="sticky top-0 bg-background z-10 text-center font-semibold">Tendance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {nationalAll.map((pt, idx) => {
                    const prev = idx > 0 ? nationalAll[idx - 1].value : pt.value
                    const diff = pt.value - prev
                    const pct = prev !== 0 ? (diff / Math.abs(prev)) * 100 : 0
                    const trend = diff > 0.001 ? 'up' : diff < -0.001 ? 'down' : 'stable'
                    const inRange = pt.year >= startYear && pt.year <= endYear
                    return (
                      <TableRow
                        key={pt.year}
                        className={
                          inRange
                            ? idx % 2 === 0 ? 'bg-blue-50/60' : 'bg-blue-100/40'
                            : idx % 2 === 0 ? 'bg-background' : 'bg-muted/30'
                        }
                      >
                        <TableCell className="font-medium text-sm py-1.5">
                          {pt.year}
                          {inRange && startYear !== endYear && (
                            <span className="ml-1 text-[10px] text-blue-600">• plage</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right font-mono tabular-nums font-semibold text-sm py-1.5">
                          {formatVal(pt.value)}
                        </TableCell>
                        <TableCell className={`text-right font-mono tabular-nums text-sm py-1.5 ${
                          diff > 0.001 ? 'text-emerald-600' : diff < -0.001 ? 'text-red-500' : 'text-amber-500'
                        }`}>
                          {idx === 0 ? '—' : `${diff > 0 ? '+' : ''}${formatVal(diff)}`}
                        </TableCell>
                        <TableCell className={`text-right font-mono tabular-nums text-sm py-1.5 ${
                          diff > 0.001 ? 'text-emerald-600' : diff < -0.001 ? 'text-red-500' : 'text-amber-500'
                        }`}>
                          {idx === 0 ? '—' : `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`}
                        </TableCell>
                        <TableCell className="text-center py-1.5">
                          {idx === 0 ? '—' : (
                            <span className={`text-sm font-medium ${trend === 'up' ? 'text-emerald-600' : trend === 'down' ? 'text-red-500' : 'text-amber-500'}`}>
                              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
                            </span>
                          )}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

function SubKPIBox({ label, value, sub, color }: { label: string; value: string; sub?: string; color: string }) {
  return (
    <div className="rounded-lg border bg-card p-3 text-center">
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium">{label}</p>
      <p className="text-lg font-bold mt-0.5" style={{ color }}>{value}</p>
      {sub && <p className="text-[10px] text-muted-foreground mt-0.5">{sub}</p>}
    </div>
  )
}
