'use client'

import React from 'react'
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'

export interface KPISparklineCardProps {
  title: string
  value: string | number
  unit?: string
  trend?: 'up' | 'down' | 'neutral'
  trendLabel?: string
  color?: string
  icon?: React.ComponentType<{ className?: string }>
  sparklinePoints?: number[]
  description?: string
  onClick?: () => void
}

export function KPISparklineCard({
  title,
  value,
  unit,
  trend = 'up',
  trendLabel = '+12.4%',
  color = '#8b5cf6',
  icon: Icon,
  sparklinePoints = [40, 55, 35, 60, 50, 75, 90, 85, 100],
  description,
  onClick,
}: KPISparklineCardProps) {
  // Generate SVG cubic Bezier path for sparkline
  const width = 240
  const height = 45
  const max = Math.max(...sparklinePoints, 1)
  const min = Math.min(...sparklinePoints, 0)
  const range = max - min || 1

  const coords = sparklinePoints.map((val, idx) => {
    const x = (idx / (sparklinePoints.length - 1)) * width
    const y = height - ((val - min) / range) * (height - 10) - 5
    return { x, y }
  })

  // Create smooth SVG cubic path
  let pathD = `M ${coords[0].x} ${coords[0].y}`
  for (let i = 0; i < coords.length - 1; i++) {
    const curr = coords[i]
    const next = coords[i + 1]
    const mx = (curr.x + next.x) / 2
    pathD += ` C ${mx} ${curr.y}, ${mx} ${next.y}, ${next.x} ${next.y}`
  }

  const fillD = `${pathD} L ${width} ${height} L 0 ${height} Z`

  const trendStyles =
    trend === 'up'
      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
      : trend === 'down'
      ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'
      : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'

  const TrendIconComponent = trend === 'up' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : Minus

  const uniqueId = React.useId().replace(/:/g, '')

  return (
    <div
      onClick={onClick}
      className={`group relative overflow-hidden rounded-2xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200/80 dark:border-slate-800/80 p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:border-purple-500/40 ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {/* Dynamic top gradient line */}
      <div
        className="absolute top-0 left-0 right-0 h-1"
        style={{ backgroundColor: color }}
      />

      {/* Header Row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          {Icon && (
            <div
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-transform duration-200 group-hover:scale-110"
              style={{ backgroundColor: `${color}18`, border: `1px solid ${color}35` }}
            >
              <Icon className="h-4 w-4" style={{ color }} />
            </div>
          )}
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 leading-tight truncate">
            {title}
          </span>
        </div>

        {/* Trend Badge */}
        <div
          className={`shrink-0 flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[11px] font-bold border ${trendStyles}`}
        >
          <TrendIconComponent className="h-3 w-3 inline" />
          <span>{trendLabel}</span>
        </div>
      </div>

      {/* Main Value Display */}
      <div className="mb-2">
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            {value}
          </span>
          {unit && (
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
              {unit}
            </span>
          )}
        </div>
        {description && (
          <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1 mt-0.5">
            {description}
          </p>
        )}
      </div>

      {/* Embedded Sparkline Graphic Curve (Exact match to image 1) */}
      <div className="relative h-11 w-full mt-2 -mb-1">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-full w-full overflow-visible"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id={`sparkline-grad-${uniqueId}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.35} />
              <stop offset="100%" stopColor={color} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <path d={fillD} fill={`url(#sparkline-grad-${uniqueId})`} />
          <path
            d={pathD}
            fill="none"
            stroke={color}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </div>
  )
}
