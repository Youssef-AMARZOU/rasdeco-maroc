'use client'

import React, { useState } from 'react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  AreaChart,
  Area,
  Legend,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

// ─── Custom Tooltip Formatter ────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label, unit = '' }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-950/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-3 shadow-xl text-xs z-50">
        <p className="font-bold text-slate-200 mb-1.5 border-b border-slate-800 pb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={`item-${index}`} className="flex items-center justify-between gap-4 py-0.5">
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color || entry.fill }} />
              {entry.name}:
            </span>
            <span className="font-mono font-bold text-slate-100">
              {typeof entry.value === 'number' ? entry.value.toLocaleString('fr-FR') : entry.value} {unit}
            </span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

// ─── 1. Single Mini Donut Gauge ───────────────────────────────────────────
export function MiniDonutGauge({
  val = 67,
  label = 'Indicateur National',
  subtitle,
  colorA = '#7B2FF7',
  colorB = '#E63E9C',
  id = 'donut-mini-1',
}: {
  val: number
  label: string
  subtitle?: string
  colorA?: string
  colorB?: string
  id?: string
}) {
  const normalizedVal = Math.min(100, Math.max(0, val))
  const data = [
    { name: label, value: normalizedVal },
    { name: 'Reste', value: 100 - normalizedVal },
  ]
  return (
    <div className="flex flex-col items-center justify-center relative py-1">
      <div className="relative h-24 w-24">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <defs>
              <linearGradient id={`grad-${id}`} x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor={colorA} />
                <stop offset="100%" stopColor={colorB} />
              </linearGradient>
            </defs>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={30}
              outerRadius={42}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
            >
              <Cell fill={`url(#grad-${id})`} stroke="none" />
              <Cell fill="rgba(255,255,255,0.06)" stroke="none" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-sm font-extrabold text-slate-900 dark:text-white tracking-tight">{Math.round(normalizedVal)}%</span>
        </div>
      </div>
      <span className="text-xs font-bold text-slate-800 dark:text-slate-200 mt-1.5 text-center truncate max-w-full">
        {label}
      </span>
      {subtitle && (
        <span className="text-[10px] text-slate-400 font-medium text-center">
          {subtitle}
        </span>
      )}
    </div>
  )
}

// ─── 2. Three National Strategic Gauges ─────────────────────────────────────
export function ThreeDonutBudgetsWidget({
  donut1Val = 32,
  donut2Val = 44,
  donut3Val = 86,
}: {
  donut1Val?: number
  donut2Val?: number
  donut3Val?: number
}) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <Card className="glass-card-value p-4 relative overflow-hidden border border-blue-500/20 bg-slate-900/40">
        <div className="absolute top-2 right-2">
          <Badge variant="outline" className="text-[9px] border-blue-500/30 text-blue-400">Eau & Barrages</Badge>
        </div>
        <MiniDonutGauge 
          val={donut1Val} 
          label="Taux Remplissage Barrages" 
          subtitle="Capacité : 19.8 Mda m³"
          colorA="#3B82F6" 
          colorB="#06B6D4" 
          id="hydrique" 
        />
      </Card>
      <Card className="glass-card-value p-4 relative overflow-hidden border border-emerald-500/20 bg-slate-900/40">
        <div className="absolute top-2 right-2">
          <Badge variant="outline" className="text-[9px] border-emerald-500/30 text-emerald-400">ENR 2030</Badge>
        </div>
        <MiniDonutGauge 
          val={donut2Val} 
          label="Part Énergies Renouvelables" 
          subtitle="Cible Royale : 52%"
          colorA="#10B981" 
          colorB="#34D399" 
          id="enr" 
        />
      </Card>
      <Card className="glass-card-value p-4 relative overflow-hidden border border-purple-500/20 bg-slate-900/40">
        <div className="absolute top-2 right-2">
          <Badge variant="outline" className="text-[9px] border-purple-500/30 text-purple-400">Protection Sociale</Badge>
        </div>
        <MiniDonutGauge 
          val={donut3Val} 
          label="Taux Couverture AMO" 
          subtitle="Généralisation Nationale"
          colorA="#7B2FF7" 
          colorB="#E63E9C" 
          id="amo" 
        />
      </Card>
    </div>
  )
}

// ─── 3. Sectoral GDP Weights ────────────────────────────────────────────────
export function PositionsListWidget({
  positions = [
    { name: 'Services & Tertiaire', pct: 51.4, val: '584 Mda MAD', color: '#7B2FF7' },
    { name: 'Industrie & Mines', pct: 26.2, val: '298 Mda MAD', color: '#3B82F6' },
    { name: 'Agriculture & Pêche', pct: 12.8, val: '145 Mda MAD', color: '#10B981' },
    { name: 'BTP & Construction', pct: 9.6, val: '109 Mda MAD', color: '#F59E0B' },
  ],
}: {
  positions?: Array<{ name: string; pct: number; val?: string; color: string }>
}) {
  return (
    <Card className="glass-card-value p-4 flex flex-col justify-between h-full border border-slate-800 bg-slate-900/50">
      <CardHeader className="p-0 pb-3">
        <CardTitle className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
          <span>Structure du PIB National</span>
          <span className="text-[10px] font-mono text-slate-400">HCP 2024</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 space-y-3">
        {positions.map((pos) => (
          <div key={pos.name} className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full shadow-sm" style={{ backgroundColor: pos.color }} />
                <span className="font-semibold text-slate-200">{pos.name}</span>
              </div>
              <div className="flex items-center gap-2 font-mono">
                {pos.val && <span className="text-[10px] text-slate-400">{pos.val}</span>}
                <span className="font-bold text-slate-100">{pos.pct}%</span>
              </div>
            </div>
            <div className="w-full h-1.5 rounded-full bg-slate-800/80 overflow-hidden">
              <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pos.pct}%`, backgroundColor: pos.color }} />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

// ─── 4. Hydric & Regional Matrix ────────────────────────────────────────────
export function CalendarHeatmapWidget({
  title = 'Taux de Remplissage des Barrages par Région (%)',
}: {
  title?: string
}) {
  const regionsHydric = [
    { code: 'TTA', name: 'Tanger-Tétouan-Al Hoceïma', rate: 58, status: 'Normal' },
    { code: 'OR', name: 'L\'Oriental', rate: 24, status: 'Alerte' },
    { code: 'FM', name: 'Fès-Meknès', rate: 41, status: 'Modéré' },
    { code: 'RSK', name: 'Rabat-Salé-Kénitra', rate: 52, status: 'Normal' },
    { code: 'BMK', name: 'Béni Mellal-Khénifra', rate: 28, status: 'Alerte' },
    { code: 'CS', name: 'Casablanca-Settat', rate: 19, status: 'Critique' },
    { code: 'MS', name: 'Marrakech-Safi', rate: 15, status: 'Critique' },
    { code: 'DT', name: 'Drâa-Tafilalet', rate: 22, status: 'Alerte' },
    { code: 'SM', name: 'Souss-Massa', rate: 14, status: 'Critique' },
    { code: 'GON', name: 'Guelmim-Oued Noun', rate: 31, status: 'Modéré' },
    { code: 'LSH', name: 'Laâyoune-Sakia El Hamra', rate: 45, status: 'Modéré' },
    { code: 'DOD', name: 'Dakhla-Oued Ed-Dahab', rate: 60, status: 'Normal' },
  ]

  const getColor = (rate: number) => {
    if (rate >= 50) return 'from-emerald-600/80 to-teal-500/80 text-emerald-100 border-emerald-500/30'
    if (rate >= 30) return 'from-amber-600/80 to-yellow-500/80 text-amber-100 border-amber-500/30'
    return 'from-rose-600/80 to-red-500/80 text-rose-100 border-rose-500/30'
  }

  return (
    <Card className="glass-card-value h-full flex flex-col justify-between border border-slate-800 bg-slate-900/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-bold text-slate-200 flex items-center justify-between">
          <span>{title}</span>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            MATRICE HYDRIQUE
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col justify-center">
        <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
          {regionsHydric.map((item) => (
            <div
              key={item.code}
              className={`p-2 rounded-xl border bg-gradient-to-br transition-all duration-300 hover:scale-105 shadow-md flex flex-col justify-between ${getColor(item.rate)}`}
              title={`${item.name} : ${item.rate}% de remplissage (${item.status})`}
            >
              <div className="flex justify-between items-center text-[10px] font-extrabold uppercase">
                <span>{item.code}</span>
                <span className="text-[9px] opacity-80">{item.status}</span>
              </div>
              <div className="mt-1 text-right font-mono text-sm font-black">
                {item.rate}%
              </div>
            </div>
          ))}
        </div>
        {/* Legend */}
        <div className="flex items-center justify-end gap-3 mt-3 pt-2 border-t border-slate-800/60 text-[10px] font-medium text-slate-400">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500" /> &gt;50% Normal</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500" /> 30-50% Modéré</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-rose-500" /> &lt;30% Alerte</span>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── 5. Strategic Project Progress Meters ───────────────────────────────────
export function WorkBalanceMetersWidget({
  donut4Val = 58,
  donut5Val = 76,
  meter1Val = 82,
  meter2Val = 64,
}: {
  donut4Val?: number
  donut5Val?: number
  meter1Val?: number
  meter2Val?: number
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card className="glass-card-value p-4 border border-slate-800 bg-slate-900/50">
        <MiniDonutGauge 
          val={donut4Val} 
          label="Dessalement de l'Eau" 
          subtitle="Projets Agadir & Casablanca" 
          colorA="#3B82F6" 
          colorB="#6366F1" 
          id="dessalement" 
        />
      </Card>
      <Card className="glass-card-value p-4 border border-slate-800 bg-slate-900/50">
        <MiniDonutGauge 
          val={donut5Val} 
          label="Numérisation Administrations" 
          subtitle="Stratégie Maroc Digital 2030" 
          colorA="#10B981" 
          colorB="#06B6D4" 
          id="digital" 
        />
      </Card>
      <Card className="glass-card-value p-4 flex flex-col justify-between border border-slate-800 bg-slate-900/50">
        <div>
          <div className="flex justify-between items-center text-xs font-bold text-slate-200 mb-1">
            <span>Port Tanger Med (Capacité)</span>
            <span className="text-cyan-400 font-mono">{meter1Val}%</span>
          </div>
          <p className="text-[10px] text-slate-400 mb-1.5">9,0 M TEUs / 10 M TEUs Capacité cible</p>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 transition-all duration-500"
              style={{ width: `${meter1Val}%` }}
            />
          </div>
        </div>

        <div className="mt-3">
          <div className="flex justify-between items-center text-xs font-bold text-slate-200 mb-1">
            <span>Réseau Autoroutier & LGV</span>
            <span className="text-pink-400 font-mono">{meter2Val}%</span>
          </div>
          <p className="text-[10px] text-slate-400 mb-1.5">Extension LGV Marrakech-Agadir en cours</p>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
              style={{ width: `${meter2Val}%` }}
            />
          </div>
        </div>
      </Card>
    </div>
  )
}

// ─── 6. Macroeconomic Growth & Inflation Trends Chart ───────────────────────
export function AreaWaveChartWithToggleWidget() {
  const [activeSerie, setActiveSerie] = useState<'growth' | 'inflation'>('growth')

  const seriesData = {
    growth: [
      { year: '2018', val: 3.1, label: 'Croissance PIB' },
      { year: '2019', val: 2.9, label: 'Croissance PIB' },
      { year: '2020', val: -7.2, label: 'Croissance PIB' },
      { year: '2021', val: 8.0, label: 'Croissance PIB' },
      { year: '2022', val: 1.3, label: 'Croissance PIB' },
      { year: '2023', val: 3.4, label: 'Croissance PIB' },
      { year: '2024', val: 3.7, label: 'Croissance PIB' },
      { year: '2025 (P)', val: 4.2, label: 'Croissance PIB' },
    ],
    inflation: [
      { year: '2018', val: 1.1, label: 'Inflation IPC' },
      { year: '2019', val: 0.2, label: 'Inflation IPC' },
      { year: '2020', val: 0.7, label: 'Inflation IPC' },
      { year: '2021', val: 1.4, label: 'Inflation IPC' },
      { year: '2022', val: 6.6, label: 'Inflation IPC' },
      { year: '2023', val: 6.1, label: 'Inflation IPC' },
      { year: '2024', val: 1.3, label: 'Inflation IPC' },
      { year: '2025 (P)', val: 2.1, label: 'Inflation IPC' },
    ],
  }

  const currentData = seriesData[activeSerie]
  const isGrowth = activeSerie === 'growth'
  const strokeColor = isGrowth ? '#3B82F6' : '#EC4899'
  const gradId = isGrowth ? 'gradGrowth' : 'gradInflation'

  return (
    <Card className="glass-card-value h-full flex flex-col border border-slate-800 bg-slate-900/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-bold text-slate-200 flex items-center justify-between">
          <span>Trajectoire Macroéconomique du Maroc</span>
          {/* Toggle Pills */}
          <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-xl border border-slate-700">
            <button
              onClick={() => setActiveSerie('growth')}
              className={`px-2.5 py-1 text-[10px] font-bold rounded-lg transition-all ${
                activeSerie === 'growth'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Croissance PIB (%)
            </button>
            <button
              onClick={() => setActiveSerie('inflation')}
              className={`px-2.5 py-1 text-[10px] font-bold rounded-lg transition-all ${
                activeSerie === 'inflation'
                  ? 'bg-pink-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Inflation IPC (%)
            </button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={currentData} margin={{ top: 10, right: 15, left: -20, bottom: 20 }}>
            <defs>
              <linearGradient id="gradGrowth" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.5} />
                <stop offset="100%" stopColor="#3B82F6" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="gradInflation" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#EC4899" stopOpacity={0.5} />
                <stop offset="100%" stopColor="#EC4899" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="year" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} unit="%" />
            <Tooltip content={<CustomTooltip unit="%" />} />
            <Legend 
              verticalAlign="bottom" 
              height={24} 
              formatter={() => (
                <span className="text-xs font-semibold text-slate-300">
                  {isGrowth ? 'Taux de Croissance Annuel du PIB (HCP / BAM)' : 'Indice des Prix à la Consommation (IPC)'}
                </span>
              )} 
            />
            <Area
              type="monotone"
              dataKey="val"
              name={isGrowth ? 'Croissance PIB' : 'Inflation IPC'}
              stroke={strokeColor}
              strokeWidth={3}
              fillOpacity={1}
              fill={`url(#${gradId})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

// ─── 7. Regional GDP Per Capita Bar Chart ────────────────────────────────────
export function RoundedBarWidget({
  title = 'PIB Régional par Habitant (MAD)',
  data = [
    { label: 'Casa-Settat', val: 54200 },
    { label: 'Dakhla-Oued', val: 48500 },
    { label: 'Rabat-Salé', val: 41800 },
    { label: 'Tanger-Tét', val: 36900 },
    { label: 'Marrakech-Safi', val: 28400 },
    { label: 'Souss-Massa', val: 26800 },
    { label: 'Fès-Meknès', val: 24100 },
  ],
}: {
  title?: string
  data?: Array<{ label: string; val: number }>
}) {
  return (
    <Card className="glass-card-value h-full flex flex-col border border-slate-800 bg-slate-900/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-bold text-slate-200 flex items-center justify-between">
          <span>{title}</span>
          <span className="text-[10px] font-mono font-bold text-indigo-400">Moy. Nat : 35 100 MAD</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 20 }}>
            <defs>
              <linearGradient id="barGradIndigoPurple" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366F1" />
                <stop offset="100%" stopColor="#A855F7" />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="label" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} interval={0} />
            <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
            <Tooltip content={<CustomTooltip unit="MAD" />} />
            <Legend 
              verticalAlign="bottom" 
              height={24} 
              formatter={() => (
                <span className="text-xs font-semibold text-slate-300">PIB par Habitant par Région (MAD)</span>
              )} 
            />
            <Bar 
              dataKey="val" 
              name="PIB / Habitant" 
              fill="url(#barGradIndigoPurple)" 
              radius={[6, 6, 0, 0]} 
              maxBarThickness={28} 
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

// ─── 8. Regional Multi-Dimension Radar Chart ────────────────────────────────
export function RadarRegionalWidget({
  title = 'Profil de Développement Régional Multi-Axes',
  data = [
    { subject: 'Infrastructures', Metropole: 92, Nord: 85, National: 65 },
    { subject: 'Industrie & IDE', Metropole: 88, Nord: 80, National: 58 },
    { subject: 'Capital Humain', Metropole: 78, Nord: 70, National: 62 },
    { subject: 'Tourisme & MRE', Metropole: 75, Nord: 82, National: 60 },
    { subject: 'Pôle Financier', Metropole: 95, Nord: 60, National: 50 },
    { subject: 'Énergies & Eau', Metropole: 65, Nord: 75, National: 70 },
  ],
}: {
  title?: string
  data?: Array<{ subject: string; Metropole: number; Nord: number; National: number }>
}) {
  return (
    <Card className="glass-card-value h-full flex flex-col border border-slate-800 bg-slate-900/50">
      <CardHeader className="pb-2">
        <CardTitle className="text-xs font-bold text-slate-200">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="68%" data={data}>
            <defs>
              <linearGradient id="radarGradPink" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#EC4899" stopOpacity={0.5} />
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis dataKey="subject" stroke="#94a3b8" tick={{ fontSize: 10 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748b" tick={false} />
            <Radar 
              name="Casablanca-Settat" 
              dataKey="Metropole" 
              stroke="#EC4899" 
              strokeWidth={2} 
              fill="url(#radarGradPink)" 
              fillOpacity={0.6} 
            />
            <Radar 
              name="Tanger-Tétouan-Al Hoceïma" 
              dataKey="Nord" 
              stroke="#3B82F6" 
              strokeWidth={2} 
              fill="#3B82F6" 
              fillOpacity={0.2} 
            />
            <Radar 
              name="Moyenne Nationale" 
              dataKey="National" 
              stroke="#10B981" 
              strokeWidth={1.5} 
              strokeDasharray="3 3" 
              fill="none" 
            />
            <Tooltip content={<CustomTooltip unit="/100" />} />
            <Legend 
              verticalAlign="bottom" 
              height={30}
              formatter={(value) => <span className="text-[11px] font-semibold text-slate-300">{value}</span>}
            />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
