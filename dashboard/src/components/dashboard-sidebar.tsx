'use client'

import React from 'react'
import {
  TrendingUp,
  Sprout,
  Users,
  GraduationCap,
  HeartPulse,
  Trophy,
  Plane,
  Zap,
  Building2,
  Cpu,
  MapPin,
  Home,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Globe,
  PieChart,
} from 'lucide-react'

export interface SidebarItem {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
}

const MENU_ITEMS: SidebarItem[] = [
  { id: 'Overview', name: 'Vue d\'ensemble', icon: Home },
  { id: 'Économie', name: 'Économie & Finances', icon: TrendingUp },
  { id: 'Agriculture', name: 'Agriculture & Eau', icon: Sprout },
  { id: 'Social', name: 'Social & Emploi', icon: Users },
  { id: 'Éducation', name: 'Éducation & Recherche', icon: GraduationCap },
  { id: 'Santé', name: 'Santé & Protection', icon: HeartPulse },
  { id: 'Sport', name: 'Sport & Titres', icon: Trophy, badge: 'OFFICIEL' },
  { id: 'Tourisme', name: 'Tourisme & Transport', icon: Plane },
  { id: 'Énergie', name: 'Énergie & Climat', icon: Zap },
  { id: 'Industrie & Compétitivité', name: 'Industrie & Commerce', icon: Building2 },
  { id: 'Numérique & Innovation', name: 'Numérique & Tech', icon: Cpu },
  { id: 'Démographie', name: 'Démographie & Régions', icon: MapPin },
]

interface DashboardSidebarProps {
  activeTab: string
  onSelectTab: (id: string) => void
  isCollapsed: boolean
  onToggleCollapse: () => void
  lang?: 'fr' | 'en'
}

export function DashboardSidebar({
  activeTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
  lang = 'fr',
}: DashboardSidebarProps) {
  return (
    <aside
      className={`fixed top-0 left-0 z-40 h-screen transition-all duration-300 flex flex-col bg-slate-900/95 text-slate-100 border-r border-slate-800/80 backdrop-blur-2xl ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* ── Top Brand Header ────────────────────────────────────────── */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800/80 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-500 shadow-lg shadow-purple-500/20">
            <PieChart className="h-5 w-5 text-white" />
          </div>
          {!isCollapsed && (
            <div className="min-w-0 flex-1">
              <h2 className="text-base font-extrabold tracking-wider bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent truncate">
                MAROC STAT
              </h2>
              <p className="text-[10px] text-purple-400 font-medium truncate">
                Observatoire Prédictif BI
              </p>
            </div>
          )}
        </div>

        <button
          onClick={onToggleCollapse}
          className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
          title={isCollapsed ? 'Déplier le menu' : 'Replier le menu'}
        >
          {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* ── Menu List ──────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1 custom-scrollbar">
        <div className={`px-3 mb-2 text-[10px] font-bold tracking-widest text-slate-400 uppercase ${isCollapsed ? 'hidden' : 'block'}`}>
          {lang === 'fr' ? 'ANALYTICS & DOMAINES' : 'DOMAINS & ANALYTICS'}
        </div>

        {MENU_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id || (item.id === 'Overview' && activeTab === 'Économie')
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id === 'Overview' ? 'Économie' : item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 group relative ${
                isActive
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/25 border border-purple-400/30 font-bold'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100'
              }`}
              title={isCollapsed ? item.name : undefined}
            >
              <Icon className={`h-4 w-4 shrink-0 transition-transform duration-200 group-hover:scale-110 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-purple-400'}`} />
              
              {!isCollapsed && (
                <span className="truncate flex-1 text-left">{item.name}</span>
              )}

              {!isCollapsed && item.badge && (
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {item.badge}
                </span>
              )}

              {/* Glowing Left Indicator for Active Item */}
              {isActive && (
                <div className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-cyan-400 shadow-glow" />
              )}
            </button>
          )
        })}
      </div>

      {/* ── Footer Profile / Copyright ─────────────────────────────── */}
      <div className="p-3 border-t border-slate-800/80 shrink-0">
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl bg-slate-800/40 border border-slate-800/60">
          <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white text-xs font-bold shadow-md">
            YA
            <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full bg-emerald-400 border-2 border-slate-900" />
          </div>
          {!isCollapsed && (
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-white truncate">Youssef AMARZOU</p>
              <p className="text-[10px] text-slate-400 flex items-center gap-1">
                <ShieldCheck className="h-3 w-3 text-emerald-400 inline" /> Licence MIT
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
