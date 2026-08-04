import re

with open('dashboard/src/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
old_import = """import {
  DonutDistributionWidget,
  RadarRegionalWidget,
  RoundedBarWidget,
  AreaWaveChartWidget,
} from '@/components/dashboard-widgets'"""

new_import = """import {
  ThreeDonutBudgetsWidget,
  PositionsListWidget,
  CalendarHeatmapWidget,
  WorkBalanceMetersWidget,
  AreaWaveChartWithToggleWidget,
  RoundedBarWidget,
  RadarRegionalWidget,
} from '@/components/dashboard-widgets'"""

if old_import in content:
    content = content.replace(old_import, new_import)
    print('Imports updated')

# 2. Insert liveJitter state
old_state = """  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)"""

new_state = """  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  // ── Live Stream Feed Dynamism (updates every 3s as in reference code) ──
  const [liveJitter, setLiveJitter] = useState({
    payroll: 1.04,
    sales: 976,
    headcount: 248,
    satisfaction: 86,
    donut1: 67,
    donut2: 70,
    donut3: 86,
    donut4: 47,
    donut5: 63,
    meter1: 78,
    meter2: 34,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setLiveJitter((prev) => ({
        payroll: Number((1.0 + (Math.random() - 0.5) * 0.08).toFixed(2)),
        sales: Math.round(976 * (1 + (Math.random() - 0.5) * 0.04)),
        headcount: Math.round(248 * (1 + (Math.random() - 0.5) * 0.02)),
        satisfaction: Math.round(86 + (Math.random() - 0.5) * 4),
        donut1: Math.min(99, Math.max(50, Math.round(prev.donut1 + (Math.random() - 0.5) * 4))),
        donut2: Math.min(99, Math.max(50, Math.round(prev.donut2 + (Math.random() - 0.5) * 4))),
        donut3: Math.min(99, Math.max(50, Math.round(prev.donut3 + (Math.random() - 0.5) * 4))),
        donut4: Math.min(99, Math.max(30, Math.round(prev.donut4 + (Math.random() - 0.5) * 5))),
        donut5: Math.min(99, Math.max(40, Math.round(prev.donut5 + (Math.random() - 0.5) * 5))),
        meter1: Math.min(99, Math.max(50, Math.round(prev.meter1 + (Math.random() - 0.5) * 6))),
        meter2: Math.min(99, Math.max(10, Math.round(prev.meter2 + (Math.random() - 0.5) * 6))),
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])"""

if old_state in content:
    content = content.replace(old_state, new_state)
    print('Live state updated')

# 3. Update 5-row widget grid inside header
old_widget_grid = """              {/* ─── Executive Analytical Widgets Grid (Matching User Images 1, 2, 3) ─── */}
              <div className="mx-auto max-w-7xl mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 text-left">
                <DonutDistributionWidget
                  title={t('Répartition des Secteurs', lang)}
                  totalLabel={t('Données Live', lang)}
                  totalValue={`${Math.round(GLOBAL_STATS.totalLignes / 1000)}K`}
                />
                <AreaWaveChartWidget
                  title={t('Séries Temporelles & Prédictions', lang)}
                />
                <RadarRegionalWidget
                  title={t('Indice Régional Multi-Variables', lang)}
                />
                <RoundedBarWidget
                  title={t('Précision des Modèles BI', lang)}
                />
              </div>"""

new_widget_grid = """              {/* ─── 5-Row Executive Analytical Dashboard Grid (Exact Match to Reference v2 HTML) ─── */}
              <div className="mx-auto max-w-7xl mt-8 space-y-6 text-left">
                {/* ── ROW 1 : 4 KPI Stat Cards with Sparkline + Trend Badges ── */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <KPISparklineCard
                    title="Masse Salariale / Payroll"
                    value={`$${(liveJitter.payroll).toFixed(2)}M`}
                    trend="up"
                    trendLabel="+4.2%"
                    color="#E63E9C"
                    sparklinePoints={[30, 34, 32, 38, 40, 42, 46]}
                  />
                  <KPISparklineCard
                    title="Ventes Totales / Sales"
                    value={`${liveJitter.sales}K`}
                    trend="up"
                    trendLabel="+2.8%"
                    color="#3E7BF7"
                    sparklinePoints={[50, 48, 52, 55, 53, 58, 60]}
                  />
                  <KPISparklineCard
                    title="Effectifs / Headcount"
                    value={liveJitter.headcount}
                    trend="down"
                    trendLabel="-1.1%"
                    color="#F87171"
                    sparklinePoints={[60, 58, 57, 55, 56, 54, 53]}
                  />
                  <KPISparklineCard
                    title="Satisfaction BI / Avg"
                    value={`${liveJitter.satisfaction}%`}
                    trend="up"
                    trendLabel="+0.9%"
                    color="#4ADE80"
                    sparklinePoints={[70, 72, 74, 73, 76, 78, 79]}
                  />
                </div>

                {/* ── ROW 2 : 3 Budget Donuts + Positions Breakdown ── */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                  <div className="lg:col-span-3">
                    <ThreeDonutBudgetsWidget
                      donut1Val={liveJitter.donut1}
                      donut2Val={liveJitter.donut2}
                      donut3Val={liveJitter.donut3}
                    />
                  </div>
                  <div className="lg:col-span-1">
                    <PositionsListWidget />
                  </div>
                </div>

                {/* ── ROW 3 : Area Chart with Toggle Pills + Radar Chart ── */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <AreaWaveChartWithToggleWidget />
                  <RadarRegionalWidget />
                </div>

                {/* ── ROW 4 : Weekly Bar Chart + Calendar Heatmap ── */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <RoundedBarWidget title="Budget Salarial Hebdomadaire (Weekly Payroll)" />
                  <CalendarHeatmapWidget title="Carte Thermique d'Activité (Heat map · 30 Jours)" />
                </div>

                {/* ── ROW 5 : Work Balance Donuts & Progress Meters ── */}
                <WorkBalanceMetersWidget
                  donut4Val={liveJitter.donut4}
                  donut5Val={liveJitter.donut5}
                  meter1Val={liveJitter.meter1}
                  meter2Val={liveJitter.meter2}
                />
              </div>"""

if old_widget_grid in content:
    content = content.replace(old_widget_grid, new_widget_grid)
    print('Widget grid updated')

# 4. Remove bottom section starting from '{/* ─── Normal Dashboard ──────────────────────────────────────────────── */}' to '<footer className='
pattern = r'\{\/\* ─── Normal Dashboard ─── \*\/\}.*?(?=<footer className=)'
match = re.search(pattern, content, re.DOTALL)
if match:
    print('Found bottom section, removing...')
    content = content[:match.start()] + content[match.end():]

with open('dashboard/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('UPDATE COMPLETE SUCCESS')
