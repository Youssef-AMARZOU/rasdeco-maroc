'use client'

// ═══════════════════════════════════════════════════════════════════════════
// RASD-Maroc — Observatoire Prédictif Multi-Domaines du Maroc
// Professional BI Dashboard — Main Page
// ═══════════════════════════════════════════════════════════════════════════

import { useState, useMemo, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
  ReferenceLine,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Treemap as RTreemap,
  ScatterChart,
  Scatter,
  ComposedChart,
  Legend,
  ResponsiveContainer,
  Tooltip as ReTooltip,
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowLeft,
  Wheat,
  Users,
  GraduationCap,
  HeartPulse,
  Trophy,
  BarChart3,
  Activity,
  AlertTriangle,
  Database,
  MapPin,
  Calendar,
  FileText,
  UsersRound,
  MapPinned,
  ChevronRight,
  Lightbulb,
  Layers,
  Crown,
  Building2,
  Landmark,
  Plane,
  RefreshCw,
  X,
  Truck,
  ShoppingCart,
  Zap,
  TreePine,
  Receipt,
  Globe,
  Factory,
  Cpu,
  Droplets,
  Wind,
  Recycle,
  PiggyBank,
  Percent,
  Home,
  KeyRound,
  Ship,
  ArrowLeftRight,
  Cog,
  Warehouse,
  Wifi,
  Smartphone,
  Rocket,
  Baby,
} from 'lucide-react'

import MoroccoMap from '@/components/morocco-map'
import {
  ALL_MODULES,
  MODULE_COLORS,
  MODULE_ICONS,
  SYNTHESE,
  GLOBAL_STATS,
  REGION_DETAILS,
  RECOMMENDATIONS,
  TOTAL_ASSOCIATIONS,
  REGIONS_OLD,
  getRegionsForYear,
  playChangeSound,
  type ModuleData,
  type KPIData,
  type IndicatorData,
  type TimeSeriesPoint,
  type RegionDetail,
  type ModuleRecommendation,
} from '@/lib/rasd-data'
import { enrichModule } from '@/lib/data-service'
import {
  UNIVERSITIES,
  DAMS,
  HOSPITALS,
  ENGINEERS_BY_FIELD,
  SPORTS_CLUBS,
  getDoctorData,
  formatKPIValue,
  getDetailedData,
  INTEGER_KPI_CODES,
  type University,
  type Dam,
  type Hospital,
  type EngineerGrad,
  type SportsClub,
  type SocialProgram,
  type DoctorSpecialty,
  SMIG_SMAG_DETAIL,
  type SmigSmagRow,
  TOURISM_HOTELS,
  TOURISM_AIRPORTS,
  TOURISM_SOURCE_MARKETS,
  TOURISM_DESTINATIONS,
  TOURISM_MRE,
  TOURISM_DOMESTIC,
  getTourismDetailData,
  FOOTBALL_CLUBS,
  type FootballClub,
  TRANSPORT_INFRASTRUCTURES,
  getTransportDetailData,
  type TransportInfrastructure,
  TOP_TRADING_PARTNERS,
  TOP_EXPORT_PRODUCTS,
  getCommerceDetailData,
  type TradingPartner,
  type ExportProduct,
  ENERGY_PROJECTS,
  ENERGY_DISTRIBUTORS,
  getEnergyDetailData,
  type EnergyProject,
  type EnergyDistributor,
} from '@/lib/detailed-data'

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from '@/components/ui/chart'

// ─── i18n Translations ──────────────────────────────────────────────────────
type Lang = 'fr' | 'en'
const translations: Record<string, Record<Lang, string>> = {
  'Retour au tableau de bord': { fr: 'Retour au tableau de bord', en: 'Back to Dashboard' },
  'Début': { fr: 'Début', en: 'Start' },
  'Fin': { fr: 'Fin', en: 'End' },
  'Suivi des indicateurs dans le temps': { fr: 'Suivi des indicateurs dans le temps', en: 'Indicator Tracking Over Time' },
  'Synthèse Conjoncturelle': { fr: 'Synthèse Conjoncturelle', en: 'Economic Snapshot' },
  'Tableau récapitulatif': { fr: 'Tableau récapitulatif', en: 'Summary Table' },
  'Année unique': { fr: 'Année unique', en: 'Single Year' },
  'Plage': { fr: 'Plage', en: 'Range' },
  'ans': { fr: 'ans', en: 'years' },
  'Période': { fr: 'Période', en: 'Period' },
  'Données complètes': { fr: 'Données complètes', en: 'Full Data' },
  'observations': { fr: 'observations', en: 'observations' },
  'Valeur actuelle': { fr: 'Valeur actuelle', en: 'Current Value' },
  'Minimum': { fr: 'Minimum', en: 'Minimum' },
  'Maximum': { fr: 'Maximum', en: 'Maximum' },
  'Moyenne': { fr: 'Moyenne', en: 'Average' },
  'Variation totale': { fr: 'Variation totale', en: 'Total Change' },
  'Observations': { fr: 'Observations', en: 'Observations' },
  'Valeur': { fr: 'Valeur', en: 'Value' },
  'Variation': { fr: 'Variation', en: 'Change' },
  'Tendance': { fr: 'Tendance', en: 'Trend' },
  'Région': { fr: 'Région', en: 'Region' },
  'Données : Open Data Maroc': { fr: 'Données : Open Data Maroc', en: 'Data: Open Data Morocco' },
  'Licence Ouverte': { fr: 'Licence Ouverte', en: 'Open License' },
  'Indicateurs clés': { fr: 'Indicateurs clés', en: 'Key Indicators' },
  'Module': { fr: 'Module', en: 'Module' },
  'Recommandations': { fr: 'Recommandations d\'interprétation', en: 'Interpretation Recommendations' },
  'Courbes': { fr: 'Courbes', en: 'Lines' },
  'Aires': { fr: 'Aires', en: 'Areas' },
  'Barres': { fr: 'Barres', en: 'Bars' },
  'Composé': { fr: 'Composé', en: 'Composed' },
  'Camembert': { fr: 'Camembert', en: 'Pie' },
  'Anneau': { fr: 'Anneau', en: 'Donut' },
  'Treemap': { fr: 'Treemap', en: 'Treemap' },
  'Points': { fr: 'Points', en: 'Scatter' },
  'Source': { fr: 'Source', en: 'Source' },
  'régions': { fr: 'régions', en: 'regions' },
  'Graphiques': { fr: 'Graphiques', en: 'Charts' },
  'Tableau de données': { fr: 'Tableau de données', en: 'Data Table' },
  'Carte régionale interactive': { fr: 'Carte régionale interactive', en: 'Interactive Regional Map' },
  'Données régionales complètes': { fr: 'Données régionales complètes', en: 'Full Regional Data' },
  'Recommandations d\'interprétation': { fr: 'Recommandations d\'interprétation', en: 'Interpretation Recommendations' },
  'lignes': { fr: 'lignes', en: 'rows' },
  'indicateurs': { fr: 'indicateurs', en: 'indicators' },
  'sources': { fr: 'sources', en: 'sources' },
  'Unité': { fr: 'Unité', en: 'Unit' },
  'Année': { fr: 'Année', en: 'Year' },
  'Années de règne': { fr: 'Années de règne', en: 'Years of Reign' },
  'Projets structurants': { fr: 'Projets structurants', en: 'Structural Projects' },
  'PIB par habitant': { fr: 'PIB par habitant', en: 'GDP per Capita' },
  'Investissements': { fr: 'Investissements', en: 'Investments' },
  'Infrastructures Stratégiques du Royaume': { fr: 'Infrastructures Stratégiques du Royaume', en: 'Strategic Infrastructure of the Kingdom' },
  'Des projets structurants qui font du Maroc un hub logistique et industriel de premier plan en Afrique et dans le monde': { fr: 'Des projets structurants qui font du Maroc un hub logistique et industriel de premier plan en Afrique et dans le monde', en: 'Structural projects making Morocco a leading logistics and industrial hub in Africa and the world' },
  'Sources Officielles': { fr: 'Sources Officielles', en: 'Official Sources' },
  'Informations': { fr: 'Informations', en: 'Information' },
  'Tous droits réservés': { fr: 'Tous droits réservés', en: 'All Rights Reserved' },
  'Sélection du module': { fr: 'Sélection du module', en: 'Module Selection' },
  'Indicateur cartographique': { fr: 'Indicateur cartographique', en: 'Map Indicator' },
  'Graphiques du module': { fr: 'Graphiques du module', en: 'Module Charts' },
  'Graphique temporel': { fr: 'Graphique temporel', en: 'Time Series Chart' },
  'Barres régionales': { fr: 'Barres régionales', en: 'Regional Bars' },
  'Tableau récapitulatif des indicateurs': { fr: 'Tableau récapitulatif des indicateurs', en: 'Indicator Summary Table' },
  'Observatoire Prédictif Multi-Domaines du Maroc': { fr: 'Observatoire Prédictif Multi-Domaines du Maroc', en: 'Morocco Multi-Domain Predictive Observatory' },
  'Statistiques & Analyses Nationales': { fr: 'Statistiques & Analyses Nationales', en: 'National Statistics & Analysis' },
  'Plateforme d\'analyse prédictive multi-domaines du Royaume du Maroc.': { fr: 'Plateforme d\'analyse prédictive multi-domaines du Royaume du Maroc.', en: 'Multi-domain predictive analysis platform of the Kingdom of Morocco.' },
  'Données officielles : HCP, BAM, MESRS.': { fr: 'Données officielles : HCP, BAM, MESRS.', en: 'Official data: HCP, BAM, MESRS.' },
  'Données sous Licence Ouverte': { fr: 'Données sous Licence Ouverte', en: 'Data under Open License' },
  'Développé par Youssef Amarzou': { fr: 'Développé par Youssef Amarzou', en: 'Developed by Youssef Amarzou' },
  'Haut-Commissariat au Plan (HCP)': { fr: 'Haut-Commissariat au Plan (HCP)', en: 'High Commission for Planning (HCP)' },
  'Bank Al-Maghrib (BAM)': { fr: 'Bank Al-Maghrib (BAM)', en: 'Bank Al-Maghrib (BAM)' },
  'Ministère de l\'Éducation': { fr: 'Ministère de l\'Éducation', en: 'Ministry of Education' },
  'Open Data Maroc (data.gov.ma)': { fr: 'Open Data Maroc (data.gov.ma)', en: 'Open Data Morocco (data.gov.ma)' },
  'Fait avec ❤️ pour le Maroc 🇲🇦': { fr: 'Fait avec ❤️ pour le Maroc 🇲🇦', en: 'Made with ❤️ for Morocco 🇲🇦' },

  // ── Synthèse ────────────────────────────────────────────────────
  "La croissance du PIB s'établit à 3,9%, portée par la reprise agricole et les investissements. L'inflation revient à 2,1% tandis que le taux directeur BAM est maintenu à 2,5%. La dette publique recule à 67,1% du PIB. Le déficit budgétaire se stabilise à -3,5% du PIB. Le chômage s'établit à 13,0% selon la nouvelle méthodologie HCP (EMO).": {
    fr: "La croissance du PIB s'établit à 3,9%, portée par la reprise agricole et les investissements. L'inflation revient à 2,1% tandis que le taux directeur BAM est maintenu à 2,5%. La dette publique recule à 67,1% du PIB. Le déficit budgétaire se stabilise à -3,5% du PIB. Le chômage s'établit à 13,0% selon la nouvelle méthodologie HCP (EMO).",
    en: "GDP growth stands at 3.9%, driven by agricultural recovery and investments. Inflation returns to 2.1% while BAM's key rate remains at 2.5%. Public debt declines to 67.1% of GDP. The budget deficit stabilizes at -3.5% of GDP. Unemployment stands at 13.0% under the new HCP methodology (EMO).",
  },
  "Dette publique/PIB à 67,1%, en repli progressif grâce aux efforts d'assainissement budgétaire.": {
    fr: "Dette publique/PIB à 67,1%, en repli progressif grâce aux efforts d'assainissement budgétaire.",
    en: "Public debt/GDP at 67.1%, gradually declining thanks to fiscal consolidation efforts.",
  },
  "Le chômage reste élevé à 13,0% (nouvelle EMO HCP), en particulier chez les jeunes et en milieu urbain.": {
    fr: "Le chômage reste élevé à 13,0% (nouvelle EMO HCP), en particulier chez les jeunes et en milieu urbain.",
    en: "Unemployment remains high at 13.0% (new HCP EMO), particularly among youth and in urban areas.",
  },
  "Réserves de change à 5,2 mois, niveau confortable bien au-dessus du seuil de 3 mois d'importation.": {
    fr: "Réserves de change à 5,2 mois, niveau confortable bien au-dessus du seuil de 3 mois d'importation.",
    en: "Foreign exchange reserves at 5.2 months, comfortable level well above the 3-month import threshold.",
  },

  // ── Économie Module ──────────────────────────────────────────────
  "Indicateurs macroéconomiques clés du Maroc : croissance, inflation, monnaie et finances publiques.": {
    fr: "Indicateurs macroéconomiques clés du Maroc : croissance, inflation, monnaie et finances publiques.",
    en: "Key macroeconomic indicators of Morocco: growth, inflation, currency and public finances.",
  },
  "Croissance du PIB": { fr: "Croissance du PIB", en: "GDP Growth" },
  "Accélération portée par la reprise agricole et les investissements.": {
    fr: "Accélération portée par la reprise agricole et les investissements.",
    en: "Acceleration driven by agricultural recovery and investments.",
  },
  "Inflation IPC": { fr: "Inflation IPC", en: "CPI Inflation" },
  "Remontée modérée de l'inflation après une période de faiblesse.": {
    fr: "Remontée modérée de l'inflation après une période de faiblesse.",
    en: "Moderate rise in inflation after a period of weakness.",
  },
  "Taux de chômage": { fr: "Taux de chômage", en: "Unemployment Rate" },
  "Baisse significative selon la nouvelle méthodologie EMO.": {
    fr: "Baisse significative selon la nouvelle méthodologie EMO.",
    en: "Significant decline under the new EMO methodology.",
  },
  "Taux directeur BAM": { fr: "Taux directeur BAM", en: "BAM Key Rate" },
  "Poursuite de l'assouplissement monétaire pour soutenir l'activité.": {
    fr: "Poursuite de l'assouplissement monétaire pour soutenir l'activité.",
    en: "Continued monetary easing to support economic activity.",
  },
  "Dette publique / PIB": { fr: "Dette publique / PIB", en: "Public Debt / GDP" },
  "Hausse continue ; le déficit primaire reste le facteur sous-jacent.": {
    fr: "Hausse continue ; le déficit primaire reste le facteur sous-jacent.",
    en: "Continuous rise; the primary deficit remains the underlying factor.",
  },
  "Réserves de change": { fr: "Réserves de change", en: "Foreign Exchange Reserves" },
  "Niveau correct, au-dessus du seuil de 3 mois d'importation.": {
    fr: "Niveau correct, au-dessus du seuil de 3 mois d'importation.",
    en: "Adequate level, above the 3-month import threshold.",
  },
  "Flux d'IDE": { fr: "Flux d'IDE", en: "FDI Flows" },
  "Rebond des investissements directs étrangers.": {
    fr: "Rebond des investissements directs étrangers.",
    en: "Rebound in foreign direct investments.",
  },
  "Déficit budgétaire": { fr: "Déficit budgétaire", en: "Budget Deficit" },
  "Réduction progressive du déficit budgétaire.": {
    fr: "Réduction progressive du déficit budgétaire.",
    en: "Gradual reduction of the budget deficit.",
  },

  // ── Agriculture Module ───────────────────────────────────────────
  "Production agricole, rendements, superficies cultivées et élevage par région du Maroc.": {
    fr: "Production agricole, rendements, superficies cultivées et élevage par région du Maroc.",
    en: "Agricultural production, yields, cultivated areas and livestock by region of Morocco.",
  },
  "Production céréalière": { fr: "Production céréalière", en: "Cereal Production" },
  "Rebond massif après les sécheresses consécutives.": { fr: "Rebond massif après les sécheresses consécutives.", en: "Massive rebound after consecutive droughts." },
  "Valeur ajoutée agricole": { fr: "Valeur ajoutée agricole", en: "Agricultural Value Added" },
  "Croissance portée par les céréales et l'arboriculture.": { fr: "Croissance portée par les céréales et l'arboriculture.", en: "Growth driven by cereals and arboriculture." },
  "Superficie cultivée": { fr: "Superficie cultivée", en: "Cultivated Area" },
  "Légère augmentation des terres exploitées.": { fr: "Légère augmentation des terres exploitées.", en: "Slight increase in cultivated land." },
  "Exportations agricoles": { fr: "Exportations agricoles", en: "Agricultural Exports" },
  "Progression des exportations d'agrumes, tomates et fruits.": { fr: "Progression des exportations d'agrumes, tomates et fruits.", en: "Growth in citrus, tomato and fruit exports." },
  "Rendement céréalier": { fr: "Rendement céréalier", en: "Cereal Yield" },
  "Amélioration grâce aux conditions climatiques favorables.": { fr: "Amélioration grâce aux conditions climatiques favorables.", en: "Improvement thanks to favorable climatic conditions." },
  "Élevage bovin": { fr: "Élevage bovin", en: "Cattle Farming" },
  "Stabilité du cheptel bovin national.": { fr: "Stabilité du cheptel bovin national.", en: "Stability of the national cattle herd." },
  "Arbres fruitiers": { fr: "Arbres fruitiers", en: "Fruit Trees" },
  "Extension des plantations d'agrumes, oliviers et amandiers.": { fr: "Extension des plantations d'agrumes, oliviers et amandiers.", en: "Expansion of citrus, olive and almond plantations." },
  "Eau potable": { fr: "Eau potable", en: "Drinking Water" },
  "Augmentation de la capacité de production d'eau potable agricole.": { fr: "Augmentation de la capacité de production d'eau potable agricole.", en: "Increased agricultural drinking water production capacity." },

  // ── Social Module ────────────────────────────────────────────────
  "Protection sociale, pauvreté, emploi et indicateurs démographiques par région.": {
    fr: "Protection sociale, pauvreté, emploi et indicateurs démographiques par région.",
    en: "Social protection, poverty, employment and demographic indicators by region.",
  },
  "Taux de pauvreté": { fr: "Taux de pauvreté", en: "Poverty Rate" },
  "Poursuite de la baisse de la pauvreté monétaire.": { fr: "Poursuite de la baisse de la pauvreté monétaire.", en: "Continued decline in monetary poverty." },
  "Taux de couverture AMO": { fr: "Taux de couverture AMO", en: "AMO Coverage Rate" },
  "Taux de dépendance économique": { fr: "Taux de dépendance économique", en: "Economic Dependency Ratio" },
  "Espérance de vie": { fr: "Espérance de vie", en: "Life Expectancy" },
  "Taux d'analphabétisme": { fr: "Taux d'analphabétisme", en: "Illiteracy Rate" },
  "Revenu médian": { fr: "Revenu médian", en: "Median Income" },
  "Taux de fécondité": { fr: "Taux de fécondité", en: "Fertility Rate" },

  // ── Éducation Module ─────────────────────────────────────────────
  "Système éducatif marocain : effectifs, réussite, formations et ressources pédagogiques.": {
    fr: "Système éducatif marocain : effectifs, réussite, formations et ressources pédagogiques.",
    en: "Moroccan education system: enrollment, success rates, training and educational resources.",
  },
  "Taux de scolarisation": { fr: "Taux de scolarisation", en: "School Enrollment Rate" },
  "Réussite au baccalauréat": { fr: "Réussite au baccalauréat", en: "Baccalaureate Success Rate" },
  "Effectifs étudiants": { fr: "Effectifs étudiants", en: "Student Enrollment" },
  "Budget de l'Éducation / PIB": { fr: "Budget de l'Éducation / PIB", en: "Education Budget / GDP" },
  "Taux d'encadrement": { fr: "Taux d'encadrement", en: "Student-Teacher Ratio" },
  "Taux d'abandon scolaire": { fr: "Taux d'abandon scolaire", en: "School Dropout Rate" },
  "Formations supérieures": { fr: "Formations supérieures", en: "Higher Education Programs" },
  "Universités publiques": { fr: "Universités publiques", en: "Public Universities" },

  // ── Santé Module ─────────────────────────────────────────────────
  "Indicateurs sanitaires du Maroc : accès aux soins, prévalence et capacité hospitalière.": {
    fr: "Indicateurs sanitaires du Maroc : accès aux soins, prévalence et capacité hospitalière.",
    en: "Health indicators of Morocco: access to care, prevalence and hospital capacity.",
  },
  "Espérance de vie à la naissance": { fr: "Espérance de vie à la naissance", en: "Life Expectancy at Birth" },
  "Âge médian": { fr: "Âge médian", en: "Median Age" },
  "Densité de population": { fr: "Densité de population", en: "Population Density" },
  "Mortalité infantile": { fr: "Mortalité infantile", en: "Infant Mortality" },
  "Lits d'hôpitaux": { fr: "Lits d'hôpitaux", en: "Hospital Beds" },
  "Médecins pour 1000 hab.": { fr: "Médecins pour 1000 hab.", en: "Doctors per 1000 pop." },
  "Dépenses de santé / PIB": { fr: "Dépenses de santé / PIB", en: "Health Expenditure / GDP" },
  "Couverture vaccinale": { fr: "Couverture vaccinale", en: "Vaccination Coverage" },
  "Espérance de vie en bonne santé": { fr: "Espérance de vie en bonne santé", en: "Healthy Life Expectancy" },
  "Taux d'obésité": { fr: "Taux d'obésité", en: "Obesity Rate" },

  // ── Sport Module ─────────────────────────────────────────────────
  "Performance sportive nationale : compétitions internationales, infrastructures et licences.": {
    fr: "Performance sportive nationale : compétitions internationales, infrastructures et licences.",
    en: "National sports performance: international competitions, infrastructure and licenses.",
  },
  "Classement mondial FIFA": { fr: "Classement mondial FIFA", en: "FIFA World Ranking" },
  "Médailles internationales": { fr: "Médailles internationales", en: "International Medals" },
  "Installations sportives": { fr: "Installations sportives", en: "Sports Facilities" },
  "Installations sportives réhabilitées": { fr: "Installations sportives réhabilitées", en: "Rehabilitated Sports Facilities" },
  "Nombre de licenciés sportifs": { fr: "Nombre de licenciés sportifs", en: "Registered Athletes" },
  "Licenciés sportifs (fédéraux)": { fr: "Licenciés sportifs (fédéraux)", en: "Federated License Holders" },
  "Budget du sport / PIB": { fr: "Budget du sport / PIB", en: "Sports Budget / GDP" },
  "Sport privé / PIB": { fr: "Sport privé / PIB", en: "Private Sport / GDP" },
  "Fédérations affiliées": { fr: "Fédérations affiliées", en: "Affiliated Federations" },
  "Fédérations sportives affiliées": { fr: "Fédérations sportives affiliées", en: "Affiliated Sports Federations" },
  "Ligues régionales sportives": { fr: "Ligues régionales sportives", en: "Regional Sports Leagues" },
  "Associations sportives": { fr: "Associations sportives", en: "Sports Associations" },
  "Bénéficiaires sport scolaire": { fr: "Bénéficiaires sport scolaire", en: "School Sports Beneficiaries" },
  "Revenus secteur sport privé": { fr: "Revenus secteur sport privé", en: "Private Sport Revenue" },
  "Pratiquants sportifs informels": { fr: "Pratiquants sportifs informels", en: "Informal Sports Practitioners" },

  // ── Recommendations ──────────────────────────────────────────────
  "Analyse et axes d'action prioritaires pour le module": { fr: "Analyse et axes d'action prioritaires pour le module", en: "Analysis and priority action areas for the" },
  "Haute": { fr: "Haute", en: "High" },
  "Moyenne": { fr: "Moyenne", en: "Medium" },
  "Basse": { fr: "Basse", en: "Low" },
  "Maîtriser la trajectoire de la dette": { fr: "Maîtriser la trajectoire de la dette", en: "Control the debt trajectory" },
  "La dette publique à 67,1% du PIB est en repli progressif, mais le différentiel taux-croissance reste à surveiller.": {
    fr: "La dette publique à 67,1% du PIB est en repli progressif, mais le différentiel taux-croissance reste à surveiller.",
    en: "Public debt at 67.1% of GDP is gradually declining, but the rate-growth differential needs monitoring.",
  },
  "Élargir l'assiette fiscale pour augmenter les recettes budgétaires": { fr: "Élargir l'assiette fiscale pour augmenter les recettes budgétaires", en: "Broaden the tax base to increase budget revenues" },
  "Rationaliser les dépenses courantes et les subventions": { fr: "Rationaliser les dépenses courantes et les subventions", en: "Rationalize current spending and subsidies" },
  "Accélérer les privatisations planifiées": { fr: "Accélérer les privatisations planifiées", en: "Accelerate planned privatizations" },
  "Réduire le chômage structurel": { fr: "Réduire le chômage structurel", en: "Reduce structural unemployment" },
  "Le taux de chômage à 13,0% (nouvelle EMO HCP) reste élevé, en particulier chez les jeunes et les diplômés.": {
    fr: "Le taux de chômage à 13,0% (nouvelle EMO HCP) reste élevé, en particulier chez les jeunes et les diplômés.",
    en: "The unemployment rate at 13.0% (new HCP EMO) remains high, particularly among youth and graduates.",
  },
  "Accélérer la formation professionnelle et l'insertion des jeunes": { fr: "Accélérer la formation professionnelle et l'insertion des jeunes", en: "Accelerate vocational training and youth integration" },
  "Soutenir l'entrepreneuriat et l'économie numérique": { fr: "Soutenir l'entrepreneuriat et l'économie numérique", en: "Support entrepreneurship and the digital economy" },
  "Adapter l'offre de formation aux besoins du marché du travail": { fr: "Adapter l'offre de formation aux besoins du marché du travail", en: "Adapt training to labor market needs" },
  "Soutenir l'investissement privé": { fr: "Soutenir l'investissement privé", en: "Support private investment" },
  "Les flux d'IDE à 34,0 Mds MAD restent en deçà du potentiel du pays.": {
    fr: "Les flux d'IDE à 34,0 Mds MAD restent en deçà du potentiel du pays.",
    en: "FDI flows at 34.0 billion MAD remain below the country's potential.",
  },
  "Améliorer le climat des affaires et la facilitation des procédures": { fr: "Améliorer le climat des affaires et la facilitation des procédures", en: "Improve the business climate and streamline procedures" },
  "Développer les zones d'accélération industrielle": { fr: "Développer les zones d'accélération industrielle", en: "Develop industrial acceleration zones" },
  "Renforcer les partenariats public-privé dans les infrastructures": { fr: "Renforcer les partenariats public-privé dans les infrastructures", en: "Strengthen public-private partnerships in infrastructure" },

  // ── Royal Section ────────────────────────────────────────────────
  "Sa Majesté le Roi Mohammed VI": { fr: "Sa Majesté le Roi Mohammed VI", en: "His Majesty King Mohammed VI" },
  "Roi du Maroc — Depuis le 23 juillet 1999": { fr: "Roi du Maroc — Depuis le 23 juillet 1999", en: "King of Morocco — Since July 23, 1999" },
  "Sous le règne de Sa Majesté le Roi Mohammed VI, le Maroc a connu une transformation sans précédent avec des projets structurants d'envergure nationale et internationale, faisant du Royaume un pôle économique majeur en Afrique et dans le monde méditerranéen.": {
    fr: "Sous le règne de Sa Majesté le Roi Mohammed VI, le Maroc a connu une transformation sans précédent avec des projets structurants d'envergure nationale et internationale, faisant du Royaume un pôle économique majeur en Afrique et dans le monde méditerranéen.",
    en: "Under the reign of His Majesty King Mohammed VI, Morocco has undergone an unprecedented transformation with major structural projects of national and international scope, making the Kingdom a major economic hub in Africa and the Mediterranean.",
  },

  // ── Region Section ───────────────────────────────────────────────
  "Tissu Associatif": { fr: "Tissu Associatif", en: "Associative Fabric" },
  "Associations et ONG par région": { fr: "Associations et ONG par région", en: "Associations and NGOs by Region" },
  "associations au total": { fr: "associations au total", en: "associations total" },
  "dont 257 reconnues d'utilité publique": { fr: "dont 257 reconnues d'utilité publique", en: "including 257 recognized as public utility" },
  "Max/région": { fr: "Max/région", en: "Max/region" },
  "Moy/région": { fr: "Moy/région", en: "Avg/region" },
  "Min/région": { fr: "Min/région", en: "Min/region" },

  // ── Infrastructure subtitles ─────────────────────────────────────
  "Port Conteneur #1 Afrique": { fr: "Port Conteneur #1 Afrique", en: "#1 Container Port in Africa" },
  "Premier TGV d'Afrique": { fr: "Premier TGV d'Afrique", en: "First High-Speed Train in Africa" },
  "Réseau Numérique National": { fr: "Réseau Numérique National", en: "National Digital Network" },
  "Plus Grand Complexe Solaire": { fr: "Plus Grand Complexe Solaire", en: "Largest Solar Complex" },
  "Hub Financier Africain": { fr: "Hub Financier Africain", en: "African Financial Hub" },
  "Réseau Portuaire National": { fr: "Réseau Portuaire National", en: "National Port Network" },
  "70 pays": { fr: "70 pays", en: "70 countries" },
  "180+ ports": { fr: "180+ ports", en: "180+ ports" },
  "1ère Afrique": { fr: "1ère Afrique", en: "1st in Africa" },
  "52% ENR 2030": { fr: "52% ENR 2030", en: "52% RE 2030" },
  "350+ entreprises": { fr: "350+ entreprises", en: "350+ companies" },
  "Top 50 mondial": { fr: "Top 50 mondial", en: "Top 50 worldwide" },
  "Répartition régionale": { fr: "Répartition régionale", en: "Regional Distribution" },
  "1er port d'Afrique et de la Méditerranée": { fr: "1er port d'Afrique et de la Méditerranée. Capacité : 9 millions de TEUs. Connecté à plus de 180 ports dans 70 pays.", en: "1st port in Africa and the Mediterranean. Capacity: 9 million TEUs. Connected to 180+ ports in 70 countries." },
  "LGV Tanger-Casablanca": { fr: "Ligne à grande vitesse Tanger-Casablanca. 320 km/h. Trajet en 2h10 au lieu de 4h45. 3e TGV le plus rapide au monde.", en: "High-speed line Tangier-Casablanca. 320 km/h. Journey in 2h10 instead of 4h45. 3rd fastest TGV in the world." },
  "Stratégie numérique nationale": { fr: "Stratégie nationale pour la transformation digitale. 66% de pénétration Internet. 12-tech cities et Casablanca Finance City.", en: "National strategy for digital transformation. 66% Internet penetration. 12 tech cities and Casablanca Finance City." },
  "Complexe solaire Noor": { fr: "Complexe solaire à concentration. 580 MW de capacité. Le plus grand au monde. Objectif : 52% d'énergies renouvelables en 2030.", en: "Concentrated solar complex. 580 MW capacity. Largest in the world. Target: 52% renewable energy by 2030." },
  "Place financière Casablanca": { fr: "Place financière africaine. +350 entreprises installées. Régime fiscal attractif. Classement Global Financial Centres : top 50 mondial.", en: "African financial hub. 350+ companies established. Attractive tax regime. Global Financial Centres ranking: top 50 worldwide." },
  "Réseau portuaire marocain": { fr: "35 ports et bases de pêche. Mohammed VI Tower, Jorf Lasfar, Nador West Med en cours. Capacité totale : 177 Mt/an.", en: "35 ports and fishing bases. Mohammed VI Tower, Jorf Lasfar, Nador West Med under construction. Total capacity: 177 Mt/year." },
  "Réseau Portuaire": { fr: "Réseau Portuaire", en: "Port Network" },

  // ── Agriculture water KPIs ────────────────────────────────────────
  "Capacité de dessalement": { fr: "Capacité de dessalement", en: "Desalination Capacity" },
  "Grands barrages": { fr: "Grands barrages", en: "Large Dams" },
  "Eau traitée ONEP": { fr: "Eau traitée ONEP", en: "ONEP Treated Water" },
  "Taux d'accès eau potable": { fr: "Taux d'accès eau potable", en: "Drinking Water Access Rate" },
  "Stress hydrique": { fr: "Stress hydrique", en: "Water Stress" },

  // ── Education new KPIs ────────────────────────────────────────────
  "Ingénieurs diplômés": { fr: "Ingénieurs diplômés", en: "Graduate Engineers" },
  "Médecins diplômés": { fr: "Médecins diplômés", en: "Graduate Doctors" },
  "Universités publiques": { fr: "Universités publiques", en: "Public Universities" },
  "Écoles d'ingénieurs": { fr: "Écoles d'ingénieurs", en: "Engineering Schools" },
  "Taux d'emploi des diplômés": { fr: "Taux d'emploi des diplômés", en: "Graduate Employment Rate" },
  "Frais de scolarité": { fr: "Frais de scolarité", en: "Tuition Fees" },

  // ── Sport detailed ──────────────────────────────────────────────
  'Clubs sportifs': { fr: 'Clubs sportifs', en: 'Sports Clubs' },
  'clubs': { fr: 'clubs', en: 'clubs' },
  'Universités et établissements': { fr: 'Universités et établissements', en: 'Universities and Institutions' },
  'établissements': { fr: 'établissements', en: 'institutions' },
  'Grands barrages du Maroc': { fr: 'Grands barrages du Maroc', en: 'Major Dams of Morocco' },
  'barrages': { fr: 'barrages', en: 'dams' },
  'Établissements hospitaliers': { fr: 'Établissements hospitaliers', en: 'Hospital Establishments' },
  'Ingénieurs par filière': { fr: 'Ingénieurs par filière', en: 'Engineers by Field' },
  'filières': { fr: 'filières', en: 'fields' },

  // ── Social detailed ─────────────────────────────────────────────
  'Programmes sociaux': { fr: 'Programmes sociaux', en: 'Social Programs' },
  'programmes': { fr: 'programmes', en: 'programs' },

  // ── Doctor detailed ────────────────────────────────────────────
  'Médecins par spécialité': { fr: 'Médecins par spécialité', en: 'Doctors by Specialty' },
  'spécialités': { fr: 'spécialités', en: 'specialties' },
  'Médecins par région': { fr: 'Médecins par région', en: 'Doctors by Region' },
  'Médecins par province': { fr: 'Médecins par province', en: 'Doctors by Province' },
  'provinces': { fr: 'provinces', en: 'provinces' },
  'Wilaya': { fr: 'Ville', en: 'City' },
  'Population desservie': { fr: 'Population desservie', en: 'Population Served' },
  'CA annuel (MAD)': { fr: 'CA annuel (MAD)', en: 'Annual Revenue (MAD)' },
  'Non-lucratif': { fr: 'Non-lucratif', en: 'Non-profit' },

  // ── Interpretation block headers ───────────────────────────────
  'Interprétation & Recommandations': { fr: 'Interprétation & Recommandations', en: 'Interpretation & Recommendations' },
  'C\'est quoi ?': { fr: 'C\'est quoi ?', en: 'What is it?' },
  'Interprétation': { fr: 'Interprétation', en: 'Interpretation' },
  'Situation actuelle': { fr: 'Situation actuelle', en: 'Current Status' },
  'Recommandations officielles': { fr: 'Recommandations officielles', en: 'Official Recommendations' },

  // ── Region name translations ───────────────────────────────────
  'Tanger-Tétouan-Al Hoceima': { fr: 'Tanger-Tétouan-Al Hoceima', en: 'Tangier-Tetouan-Al Hoceima' },
  'Oriental': { fr: 'Oriental', en: 'Oriental' },
  'Fès-Meknès': { fr: 'Fès-Meknès', en: 'Fes-Meknes' },
  'Rabat-Salé-Kénitra': { fr: 'Rabat-Salé-Kénitra', en: 'Rabat-Sale-Kenitra' },
  'Béni Mellal-Khénifra': { fr: 'Béni Mellal-Khénifra', en: 'Beni Mellal-Khenifra' },
  'Casablanca-Settat': { fr: 'Casablanca-Settat', en: 'Casablanca-Settat' },
  'Marrakech-Safi': { fr: 'Marrakech-Safi', en: 'Marrakech-Safi' },
  'Drâa-Tafilalet': { fr: 'Drâa-Tafilalet', en: 'Draa-Tafilalet' },
  'Souss-Massa': { fr: 'Souss-Massa', en: 'Souss-Massa' },
  'Guelmim-Oued Noun': { fr: 'Guelmim-Oued Noun', en: 'Guelmim-Oued Noun' },
  'Laâyoune-Sakia El Hamra': { fr: 'Laâyoune-Sakia El Hamra', en: 'Laayoune-Sakia El Hamra' },
  'Dakhla-Oued Ed-Dahab': { fr: 'Dakhla-Oued Ed-Dahab', en: 'Dakhla-Oued Ed-Dahab' },

  // ── Old region name translations (pre-2015) ────────────────────
  'Chaouia-Ouardigha': { fr: 'Chaouia-Ouardigha', en: 'Chaouia-Ouardigha' },
  'Doukkala-Abda': { fr: 'Doukkala-Abda', en: 'Doukkala-Abda' },
  'Fès-Boulemane': { fr: 'Fès-Boulemane', en: 'Fes-Boulemane' },
  'Gharb-Chrarda-Beni Hssen': { fr: 'Gharb-Chrarda-Beni Hssen', en: 'Gharb-Chrarda-Beni Hssen' },
  'Grand Casablanca': { fr: 'Grand Casablanca', en: 'Grand Casablanca' },
  'Guelmim-Es Semara': { fr: 'Guelmim-Es Semara', en: 'Guelmim-Es Semara' },
  'Laâyoune-Boujdour-Sakia el Hamra': { fr: 'Laâyoune-Boujdour-Sakia el Hamra', en: 'Laayoune-Boujdour-Sakia el Hamra' },
  'Marrakech-Tensift-Al Haouz': { fr: 'Marrakech-Tensift-Al Haouz', en: 'Marrakech-Tensift-Al Haouz' },
  'Meknès-Tafilalet': { fr: 'Meknès-Tafilalet', en: 'Meknes-Tafilalet' },
  'L\'Oriental': { fr: 'L\'Oriental', en: 'L\'Oriental' },
  'Oued ed Dahab-Lagouira': { fr: 'Oued ed Dahab-Lagouira', en: 'Oued ed Dahab-Lagouira' },
  'Rabat-Salé-Zemmour-Zaër': { fr: 'Rabat-Salé-Zemmour-Zaër', en: 'Rabat-Sale-Zemmour-Zaer' },
  'Souss-Massa-Drâa': { fr: 'Souss-Massa-Drâa', en: 'Souss-Massa-Draa' },
  'Tadla-Azilal': { fr: 'Tadla-Azilal', en: 'Tadla-Azilal' },
  'Tanger-Tétouan': { fr: 'Tanger-Tétouan', en: 'Tangier-Tetouan' },
  'Taza-Al Hoceïma-Taounate': { fr: 'Taza-Al Hoceïma-Taounate', en: 'Taza-Al Hoceima-Taounate' },

  // ── Indicator label translations (charts) ─────────────────────
  'Croissance du PIB': { fr: 'Croissance du PIB', en: 'GDP Growth' },
  'Croissance du PIB (T/T-4)': { fr: 'Croissance du PIB (T/T-4)', en: 'GDP Growth (Q/Q-4)' },
  'Inflation IPC': { fr: 'Inflation IPC', en: 'CPI Inflation' },
  'Inflation IPC (glissement annuel)': { fr: 'Inflation IPC (glissement annuel)', en: 'CPI Inflation (year-on-year)' },
  'Taux de chômage': { fr: 'Taux de chômage', en: 'Unemployment Rate' },
  'Taux directeur BAM': { fr: 'Taux directeur BAM', en: 'BAM Policy Rate' },
  'Dette publique / PIB': { fr: 'Dette publique / PIB', en: 'Public Debt / GDP' },
  'Réserves de change': { fr: 'Réserves de change', en: 'Foreign Reserves' },
  'Réserves de change (mois d\'importation)': { fr: 'Réserves de change (mois d\'importation)', en: 'Foreign Reserves (months of imports)' },
  'Flux d\'IDE': { fr: 'Flux d\'IDE', en: 'FDI Flows' },
  'Déficit budgétaire': { fr: 'Déficit budgétaire', en: 'Budget Deficit' },
  'Production céréalière': { fr: 'Production céréalière', en: 'Cereal Production' },
  'Production céréalière totale': { fr: 'Production céréalière totale', en: 'Total Cereal Production' },
  'Valeur ajoutée agricole': { fr: 'Valeur ajoutée agricole', en: 'Agricultural Value Added' },
  'Superficie cultivée': { fr: 'Superficie cultivée', en: 'Cultivated Area' },
  'Exportations agricoles': { fr: 'Exportations agricoles', en: 'Agricultural Exports' },
  'Rendement céréalier': { fr: 'Rendement céréalier', en: 'Cereal Yield' },
  'Rendement céréalier moyen': { fr: 'Rendement céréalier moyen', en: 'Average Cereal Yield' },
  'Élevage bovin': { fr: 'Élevage bovin', en: 'Cattle Farming' },
  'Arbres fruitiers': { fr: 'Arbres fruitiers', en: 'Fruit Trees' },
  'Eau potable': { fr: 'Eau potable', en: 'Drinking Water' },
  'Capacité de dessalement': { fr: 'Capacité de dessalement', en: 'Desalination Capacity' },
  'Capacité de dessalement installée': { fr: 'Capacité de dessalement installée', en: 'Installed Desalination Capacity' },
  'Grands barrages': { fr: 'Grands barrages', en: 'Major Dams' },
  'Nombre de grands barrages': { fr: 'Nombre de grands barrages', en: 'Number of Major Dams' },
  'Eau traitée ONEP': { fr: 'Eau traitée ONEP', en: 'ONEP Treated Water' },
  'Volume d\'eau traité par l\'ONEP': { fr: 'Volume d\'eau traité par l\'ONEP', en: 'Water Volume Treated by ONEP' },
  'Taux d\'accès eau potable': { fr: 'Taux d\'accès eau potable', en: 'Drinking Water Access Rate' },
  'Taux d\'accès à l\'eau potable': { fr: 'Taux d\'accès à l\'eau potable', en: 'Drinking Water Access Rate' },
  'Stress hydrique': { fr: 'Stress hydrique', en: 'Water Stress' },
  'Indice de stress hydrique': { fr: 'Indice de stress hydrique', en: 'Water Stress Index' },
  'Remplissage des barrages': { fr: 'Remplissage des barrages', en: 'Dam Fill Rate' },
  'Production fruitière': { fr: 'Production fruitière', en: 'Fruit Production' },
  'Cheptel bovin': { fr: 'Cheptel bovin', en: 'Cattle Herd' },
  'Cheptel ovin': { fr: 'Cheptel ovin', en: 'Sheep Herd' },
  'Superficie d\'arbres fruitiers': { fr: 'Superficie d\'arbres fruitiers', en: 'Fruit Tree Area' },
  'Production d\'eau potable': { fr: 'Production d\'eau potable', en: 'Drinking Water Production' },
  'Taux de pauvreté': { fr: 'Taux de pauvreté', en: 'Poverty Rate' },
  'Taux de couverture AMO': { fr: 'Taux de couverture AMO', en: 'AMO Coverage Rate' },
  'Indice de Gini': { fr: 'Indice de Gini', en: 'Gini Index' },
  'Population active': { fr: 'Population active', en: 'Active Population' },
  'Taux d\'urbanisation': { fr: 'Taux d\'urbanisation', en: 'Urbanization Rate' },
  'Aide sociale directe': { fr: 'Aide sociale directe', en: 'Direct Social Aid' },
  'Indice de développement humain': { fr: 'Indice de développement humain', en: 'Human Development Index' },
  'Taux de scolarisation (6-11 ans)': { fr: 'Taux de scolarisation (6-11 ans)', en: 'Enrollment Rate (6-11 years)' },
  'Taux de scolarisation primaire (6-11 ans)': { fr: 'Taux de scolarisation primaire (6-11 ans)', en: 'Primary Enrollment Rate (6-11 years)' },
  'Taux de scolarisation collège (12-14 ans)': { fr: 'Taux de scolarisation collège (12-14 ans)', en: 'Middle School Enrollment Rate (12-14 years)' },
  'Nombre d\'enseignants': { fr: 'Nombre d\'enseignants', en: 'Number of Teachers' },
  'Établissements scolaires': { fr: 'Établissements scolaires', en: 'Schools' },
  'Taux d\'abandon primaire': { fr: 'Taux d\'abandon primaire', en: 'Primary Dropout Rate' },
  'Dépenses éducation / PIB': { fr: 'Dépenses éducation / PIB', en: 'Education Spending / GDP' },
  'Étudiants universitaires': { fr: 'Étudiants universitaires', en: 'University Students' },
  'Ingénieurs diplômés': { fr: 'Ingénieurs diplômés', en: 'Engineering Graduates' },
  'Médecins diplômés': { fr: 'Médecins diplômés', en: 'Medical Graduates' },
  'Universités publiques': { fr: 'Universités publiques', en: 'Public Universities' },
  'Écoles d\'ingénieurs': { fr: 'Écoles d\'ingénieurs', en: 'Engineering Schools' },
  'Taux d\'emploi des diplômés': { fr: 'Taux d\'emploi des diplômés', en: 'Graduate Employment Rate' },
  'Lits d\'hôpital': { fr: 'Lits d\'hôpital', en: 'Hospital Beds' },
  'Médecins': { fr: 'Médecins', en: 'Doctors' },
  'Ratio médecins/1000 hab': { fr: 'Ratio médecins/1000 hab', en: 'Doctor/1000 Inhabitants Ratio' },
  'Taux de couverture médicale': { fr: 'Taux de couverture médicale', en: 'Medical Coverage Rate' },
  'Centres de santé': { fr: 'Centres de santé', en: 'Health Centers' },
  'Espérance de vie': { fr: 'Espérance de vie', en: 'Life Expectancy' },
  'Pharmacies': { fr: 'Pharmacies', en: 'Pharmacies' },
  'Hôpitaux privés': { fr: 'Hôpitaux privés', en: 'Private Hospitals' },
  'Transferts des MRE': { fr: 'Transferts des MRE', en: 'MRE Remittances' },
  'Contribution MRE au PIB': { fr: 'Contribution MRE au PIB', en: 'MRE Contribution to GDP' },
  'Transferts MRE': { fr: 'Transferts MRE', en: 'MRE Transfers' },
  'Tourisme intérieur': { fr: 'Tourisme intérieur', en: 'Domestic Tourism' },
  'Recettes tourisme intérieur': { fr: 'Recettes tourisme intérieur', en: 'Domestic Tourism Revenue' },

  // ── Transport et Logistique ────────────────────────────────────
  'Transport et Logistique': { fr: 'Transport et Logistique', en: 'Transport & Logistics' },
  'Passagers ONCF': { fr: 'Passagers ONCF', en: 'ONCF Passengers' },
  'Passagers aéroportuaires': { fr: 'Passagers aéroportuaires', en: 'Airport Passengers' },
  'Trafic portuaire': { fr: 'Trafic portuaire', en: 'Port Traffic' },
  'Tanger Med containers': { fr: 'Tanger Med containers', en: 'Tanger Med Containers' },
  'Réseau autoroutier': { fr: 'Réseau autoroutier', en: 'Highway Network' },
  'Revenu ONCF': { fr: 'Revenu ONCF', en: 'ONCF Revenue' },
  'Fret ferroviaire': { fr: 'Fret ferroviaire', en: 'Rail Freight' },
  'Trafic ADP aérien': { fr: 'Trafic ADP aérien', en: 'Air Traffic Movements' },
  'Passagers ONCF (millions)': { fr: 'Passagers ONCF (millions)', en: 'ONCF Passengers (millions)' },
  'Fret ferroviaire (Mt)': { fr: 'Fret ferroviaire (Mt)', en: 'Rail Freight (Mt)' },
  'Revenu ONCF (MDH)': { fr: 'Revenu ONCF (MDH)', en: 'ONCF Revenue (MDH)' },
  'Passagers Al Boraq (millions)': { fr: 'Passagers Al Boraq (millions)', en: 'Al Boraq Passengers (millions)' },
  'Passagers aéroportuaires (millions)': { fr: 'Passagers aéroportuaires (millions)', en: 'Airport Passengers (millions)' },
  'Fret aérien (tonnes)': { fr: 'Fret aérien (tonnes)', en: 'Air Cargo (tonnes)' },
  'Trafic portuaire (Mt)': { fr: 'Trafic portuaire (Mt)', en: 'Port Traffic (Mt)' },
  'Tanger Med TEU (millions)': { fr: 'Tanger Med TEU (millions)', en: 'Tanger Med TEU (millions)' },
  'Passagers portuaires': { fr: 'Passagers portuaires', en: 'Port Passengers' },
  'Réseau autoroutier (km)': { fr: 'Réseau autoroutier (km)', en: 'Highway Network (km)' },
  'Trafic autoroutier (millions vh)': { fr: 'Trafic autoroutier (millions vh)', en: 'Highway Traffic (million vehicles)' },
  'Revenu ADM (MDH)': { fr: 'Revenu ADM (MDH)', en: 'ADM Revenue (MDH)' },
  'Part transport dans PIB (%)': { fr: 'Part transport dans PIB (%)', en: 'Transport Share of GDP (%)' },

  // ── AMDL Logistics indicators ──────────────────────────────────
  'VA logistique totale': { fr: 'VA logistique totale', en: 'Total Logistics VA' },
  'Emplois transport/logistique': { fr: 'Emplois transport/logistique', en: 'Transport/Logistics Jobs' },
  'VA logistique totale (Mds MAD)': { fr: 'VA logistique totale (Mds MAD)', en: 'Total Logistics VA (Bn MAD)' },
  'VA logistique / PIB (%)': { fr: 'VA logistique / PIB (%)', en: 'Logistics VA / GDP (%)' },
  'Contribution directe logistique (Mds MAD)': { fr: 'Contribution directe logistique (Mds MAD)', en: 'Direct Logistics Contribution (Bn MAD)' },
  'Investissement logistique (Mds MAD)': { fr: 'Investissement logistique (Mds MAD)', en: 'Logistics Investment (Bn MAD)' },
  'LPI Infrastructure (score)': { fr: 'LPI Infrastructure (score)', en: 'LPI Infrastructure (score)' },
  'Réseau ferroviaire (km)': { fr: 'Réseau ferroviaire (km)', en: 'Rail Network (km)' },

  // ── Commerce ──────────────────────────────────────────────────
  'Commerce': { fr: 'Commerce', en: 'Trade & Commerce' },
  'Exports FOB': { fr: 'Exports FOB', en: 'FOB Exports' },
  'Imports CIF': { fr: 'Imports CIF', en: 'CIF Imports' },
  'Déficit commercial': { fr: 'Déficit commercial', en: 'Trade Deficit' },
  'IDE net reçus': { fr: 'IDE net reçus', en: 'Net FDI Received' },
  'E-commerce': { fr: 'E-commerce', en: 'E-commerce' },
  'Exports FOB (Mds MAD)': { fr: 'Exports FOB (Mds MAD)', en: 'FOB Exports (Bn MAD)' },
  'Imports CIF (Mds MAD)': { fr: 'Imports CIF (Mds MAD)', en: 'CIF Imports (Bn MAD)' },
  'Déficit commercial (Mds MAD)': { fr: 'Déficit commercial (Mds MAD)', en: 'Trade Deficit (Bn MAD)' },
  'Couverture des imports (%)': { fr: 'Couverture des imports (%)', en: 'Import Coverage (%)' },
  'IDE net reçus (Mds USD)': { fr: 'IDE net reçus (Mds USD)', en: 'Net FDI Received (Bn USD)' },
  'Volume e-commerce (Mds MAD)': { fr: 'Volume e-commerce (Mds MAD)', en: 'E-commerce Volume (Bn MAD)' },
  'Commerce/PBI (%)': { fr: 'Commerce/PBI (%)', en: 'Trade/GDP (%)' },
  'Emplois commerciaux': { fr: 'Emplois commerciaux', en: 'Commerce Jobs' },
  'Partenaires ALE (pays)': { fr: 'Partenaires ALE (pays)', en: 'FTA Partners (countries)' },

  // ── Énergie ───────────────────────────────────────────────────
  'Énergie': { fr: 'Énergie', en: 'Energy' },
  'Production électrique': { fr: 'Production électrique', en: 'Electricity Production' },
  'Capacité installée': { fr: 'Capacité installée', en: 'Installed Capacity' },
  'Part renouvelables': { fr: 'Part renouvelables', en: 'Renewable Share' },
  'Accès électricité': { fr: 'Accès électricité', en: 'Electricity Access' },
  'Capacité éolienne': { fr: 'Capacité éolienne', en: 'Wind Capacity' },
  'Capacité solaire': { fr: 'Capacité solaire', en: 'Solar Capacity' },
  'Émissions CO2': { fr: 'Émissions CO2', en: 'CO2 Emissions' },
  'Consommation par habitant': { fr: 'Consommation par habitant', en: 'Per Capita Consumption' },
  'Production électrique (TWh)': { fr: 'Production électrique (TWh)', en: 'Electricity Production (TWh)' },
  'Consommation électrique (TWh)': { fr: 'Consommation électrique (TWh)', en: 'Electricity Consumption (TWh)' },
  'Capacité installée (MW)': { fr: 'Capacité installée (MW)', en: 'Installed Capacity (MW)' },
  'Part renouvelables (%)': { fr: 'Part renouvelables (%)', en: 'Renewable Share (%)' },
  'Capacité éolienne (MW)': { fr: 'Capacité éolienne (MW)', en: 'Wind Capacity (MW)' },
  'Capacité solaire (MW)': { fr: 'Capacité solaire (MW)', en: 'Solar Capacity (MW)' },
  'Émissions CO2 (Mt)': { fr: 'Émissions CO2 (Mt)', en: 'CO2 Emissions (Mt)' },
  'Accès électricité (%)': { fr: 'Accès électricité (%)', en: 'Electricity Access (%)' },
  'Consommation/habitant (kWh)': { fr: 'Consommation/habitant (kWh)', en: 'Per Capita Consumption (kWh)' },
  'Production Noor Ouarzazate (GWh)': { fr: 'Production Noor Ouarzazate (GWh)', en: 'Noor Ouarzazate Output (GWh)' },
  'Part énergie/PBI (%)': { fr: 'Part énergie/PBI (%)', en: 'Energy Share of GDP (%)' },

  // ── Environnement & Climat translations ─────────────────────
  'Remplissage barrages (%)': { fr: 'Remplissage barrages (%)', en: 'Dam Fill Rate (%)' },
  'Émissions CO₂ (Mt éq. CO₂)': { fr: 'Émissions CO₂ (Mt éq. CO₂)', en: 'CO₂ Emissions (Mt CO₂eq)' },
  'Stress hydrique (%)': { fr: 'Stress hydrique (%)', en: 'Water Stress (%)' },
  'Superficie forestière (M ha)': { fr: 'Superficie forestière (M ha)', en: 'Forest Area (M ha)' },
  'Reboisement annuel (ha/an)': { fr: 'Reboisement annuel (ha/an)', en: 'Annual Reforestation (ha/yr)' },
  'Jours de vague de chaleur/an': { fr: 'Jours de vague de chaleur/an', en: 'Heatwave Days/Year' },
  'Précipitations annuelles moyennes (mm)': { fr: 'Précipitations annuelles moyennes (mm)', en: 'Avg Annual Precipitation (mm)' },
  'Aires protégées (% du territoire)': { fr: 'Aires protégées (% du territoire)', en: 'Protected Areas (% of Territory)' },
  'Valorisation des déchets (%)': { fr: 'Valorisation des déchets (%)', en: 'Waste Recycling Rate (%)' },

  // ── Finances Publiques translations ────────────────────────
  'Recettes fiscales totales (MM MAD)': { fr: 'Recettes fiscales totales (MM MAD)', en: 'Total Tax Revenues (Bn MAD)' },
  'Recettes TVA (MM MAD)': { fr: 'Recettes TVA (MM MAD)', en: 'VAT Revenues (Bn MAD)' },
  'Recettes IS (MM MAD)': { fr: 'Recettes IS (MM MAD)', en: 'Corporate Tax Revenues (Bn MAD)' },
  'Recettes IR (MM MAD)': { fr: 'Recettes IR (MM MAD)', en: 'Income Tax Revenues (Bn MAD)' },
  'Dépenses de fonctionnement (MM MAD)': { fr: 'Dépenses de fonctionnement (MM MAD)', en: 'Operating Expenses (Bn MAD)' },
  'Dépenses d\'investissement (MM MAD)': { fr: 'Dépenses d\'investissement (MM MAD)', en: 'Capital Expenditure (Bn MAD)' },
  'Masse salariale (% PIB)': { fr: 'Masse salariale (% PIB)', en: 'Wage Bill (% GDP)' },
  'Subventions (MM MAD)': { fr: 'Subventions (MM MAD)', en: 'Subsidies (Bn MAD)' },
  'Taux d\'exécution budgétaire (%)': { fr: 'Taux d\'exécution budgétaire (%)', en: 'Budget Execution Rate (%)' },
  'Dette publique (% PIB)': { fr: 'Dette publique (% PIB)', en: 'Public Debt (% GDP)' },
  'Service de la dette (MM MAD)': { fr: 'Service de la dette (MM MAD)', en: 'Debt Service (Bn MAD)' },

  // ── Immobilier translations ─────────────────────────────────
  'IPAI (base 100)': { fr: 'IPAI (base 100)', en: 'RE Price Index (base 100)' },
  'Transactions immobilières (actes)': { fr: 'Transactions immobilières (actes)', en: 'RE Transactions (deeds)' },
  'Prix moyen m² résidentiel (MAD)': { fr: 'Prix moyen m² résidentiel (MAD)', en: 'Avg Residential Price/m² (MAD)' },
  'Logements sociaux livrés (unités)': { fr: 'Logements sociaux livrés (unités)', en: 'Social Housing Delivered (units)' },
  'Programme VSB (% résorption)': { fr: 'Programme VSB (% résorption)', en: 'Slum Resorption Program (%)' },
  'Crédits immobiliers (MM MAD)': { fr: 'Crédits immobiliers (MM MAD)', en: 'Housing Loans (Bn MAD)' },
  'Taux de vacance logement (%)': { fr: 'Taux de vacance logement (%)', en: 'Housing Vacancy Rate (%)' },

  // ── Investissement translations ─────────────────────────────
  'IDE entrants par secteur (MM MAD)': { fr: 'IDE entrants par secteur (MM MAD)', en: 'Inbound FDI by Sector (Bn MAD)' },
  'Exportations totales (MM MAD)': { fr: 'Exportations totales (MM MAD)', en: 'Total Exports (Bn MAD)' },
  'Importations totales (MM MAD)': { fr: 'Importations totales (MM MAD)', en: 'Total Imports (Bn MAD)' },
  'Balance commerciale (MM MAD)': { fr: 'Balance commerciale (MM MAD)', en: 'Trade Balance (Bn MAD)' },
  'Exportations automobile (MM MAD)': { fr: 'Exportations automobile (MM MAD)', en: 'Automotive Exports (Bn MAD)' },
  'Exportations phosphates (MM MAD)': { fr: 'Exportations phosphates (MM MAD)', en: 'Phosphate Exports (Bn MAD)' },
  'Exportations textile et cuir (MM MAD)': { fr: 'Exportations textile et cuir (MM MAD)', en: 'Textile & Leather Exports (Bn MAD)' },
  'IDE France (Mds MAD)': { fr: 'IDE France (Mds MAD)', en: 'France FDI (Bn MAD)' },

  // ── Industrie translations ──────────────────────────────────
  'Indice production industrielle (base 100)': { fr: 'Indice production industrielle (base 100)', en: 'Industrial Production Index (base 100)' },
  'Production automobile (véhicules)': { fr: 'Production automobile (véhicules)', en: 'Automobile Production (vehicles)' },
  'Valeur ajoutée industrielle (% PIB)': { fr: 'Valeur ajoutée industrielle (% PIB)', en: 'Industrial Value Added (% GDP)' },
  'Effectifs industrie (K emplois)': { fr: 'Effectifs industrie (K emplois)', en: 'Industrial Employment (K jobs)' },
  'Zones d\'accélération industrielle': { fr: 'Zones d\'accélération industrielle', en: 'Industrial Acceleration Zones' },
  'Entreprises industrielles créées': { fr: 'Entreprises industrielles créées', en: 'Industrial Firms Created' },

  // ── Numérique translations ──────────────────────────────────
  'Pénétration Internet (%)': { fr: 'Pénétration Internet (%)', en: 'Internet Penetration (%)' },
  'Pénétration mobile (%)': { fr: 'Pénétration mobile (%)', en: 'Mobile Penetration (%)' },
  'Abonnés fibre optique (K)': { fr: 'Abonnés fibre optique (K)', en: 'Fiber Subscribers (K)' },
  'Startups labellisées': { fr: 'Startups labellisées', en: 'Labeled Startups' },
  'Investissement R&D (% PIB)': { fr: 'Investissement R&D (% PIB)', en: 'R&D Investment (% GDP)' },
  'E-services administratifs': { fr: 'E-services administratifs', en: 'Digital Government Services' },

  // ── Démographie translations ────────────────────────────────
  'Population totale (M habitants)': { fr: 'Population totale (M habitants)', en: 'Total Population (M)' },
  'Taux de natalité (‰)': { fr: 'Taux de natalité (‰)', en: 'Birth Rate (‰)' },
  'Taux de mortalité (‰)': { fr: 'Taux de mortalité (‰)', en: 'Death Rate (‰)' },
  'Indice synthétique de fécondité': { fr: 'Indice synthétique de fécondité', en: 'Total Fertility Rate' },
  'Taille moyenne des ménages': { fr: 'Taille moyenne des ménages', en: 'Average Household Size' },
  'Population urbaine (%)': { fr: 'Population urbaine (%)', en: 'Urban Population (%)' },
  'Solde migratoire net (K)': { fr: 'Solde migratoire net (K)', en: 'Net Migration Balance (K)' },

  // ── KPI card label translations ─────────────────────────────
  'Remplissage barrages': { fr: 'Remplissage barrages', en: 'Dam Fill Rate' },
  'Émissions CO₂': { fr: 'Émissions CO₂', en: 'CO₂ Emissions' },
  'Stress hydrique': { fr: 'Stress hydrique', en: 'Water Stress' },
  'Superficie forestière': { fr: 'Superficie forestière', en: 'Forest Area' },
  'Reboisement annuel': { fr: 'Reboisement annuel', en: 'Annual Reforestation' },
  'Jours canicule': { fr: 'Jours canicule', en: 'Heatwave Days' },
  'Aires protégées': { fr: 'Aires protégées', en: 'Protected Areas' },
  'Valorisation déchets': { fr: 'Valorisation déchets', en: 'Waste Recycling' },
  'Recettes fiscales': { fr: 'Recettes fiscales', en: 'Tax Revenues' },
  'Dépenses de fonctionnement': { fr: 'Dépenses de fonctionnement', en: 'Operating Expenses' },
  'Dépenses d\'investissement': { fr: 'Dépenses d\'investissement', en: 'Capital Expenditure' },
  'Masse salariale': { fr: 'Masse salariale', en: 'Wage Bill' },
  'Subventions': { fr: 'Subventions', en: 'Subsidies' },
  'Taux exécution budgétaire': { fr: 'Taux exécution budgétaire', en: 'Budget Execution Rate' },
  'Dette publique': { fr: 'Dette publique', en: 'Public Debt' },
  'Service de la dette': { fr: 'Service de la dette', en: 'Debt Service' },
  'IPAI': { fr: 'IPAI', en: 'RE Price Index' },
  'Transactions immobilières': { fr: 'Transactions immobilières', en: 'Real Estate Transactions' },
  'Prix moyen m²': { fr: 'Prix moyen m²', en: 'Avg Price/m²' },
  'Logements sociaux': { fr: 'Logements sociaux', en: 'Social Housing' },
  'Crédits immobiliers': { fr: 'Crédits immobiliers', en: 'Housing Loans' },
  'Taux vacance': { fr: 'Taux vacance', en: 'Vacancy Rate' },
  'IDE entrants': { fr: 'IDE entrants', en: 'Inbound FDI' },
  'Exportations totales': { fr: 'Exportations totales', en: 'Total Exports' },
  'Importations totales': { fr: 'Importations totales', en: 'Total Imports' },
  'Balance commerciale': { fr: 'Balance commerciale', en: 'Trade Balance' },
  'Exportations automobile': { fr: 'Exportations automobile', en: 'Automotive Exports' },
  'Exportations phosphates': { fr: 'Exportations phosphates', en: 'Phosphate Exports' },
  'Exportations textile': { fr: 'Exportations textile', en: 'Textile Exports' },
  'IDE par pays': { fr: 'IDE par pays', en: 'FDI by Country' },
  'Production industrielle': { fr: 'Production industrielle', en: 'Industrial Production' },
  'VA industrielle': { fr: 'VA industrielle', en: 'Industrial VA' },
  'Effectifs industrie': { fr: 'Effectifs industrie', en: 'Industrial Employment' },
  'Zones industrielles': { fr: 'Zones industrielles', en: 'Industrial Zones' },
  'Entreprises créées': { fr: 'Entreprises créées', en: 'Firms Created' },
  'Pénétration Internet': { fr: 'Pénétration Internet', en: 'Internet Penetration' },
  'Pénétration mobile': { fr: 'Pénétration mobile', en: 'Mobile Penetration' },
  'Fibre optique': { fr: 'Fibre optique', en: 'Fiber Optic' },
  'R&D (% PIB)': { fr: 'R&D (% PIB)', en: 'R&D (% GDP)' },
  'E-services admin': { fr: 'E-services admin', en: 'E-Gov Services' },
  'Population totale': { fr: 'Population totale', en: 'Total Population' },
  'Taux natalité': { fr: 'Taux natalité', en: 'Birth Rate' },
  'Taux mortalité': { fr: 'Taux mortalité', en: 'Death Rate' },
  'Indice fécondité': { fr: 'Indice fécondité', en: 'Fertility Rate' },
  'Taille ménages': { fr: 'Taille ménages', en: 'Household Size' },
  'Population urbaine': { fr: 'Population urbaine', en: 'Urban Population' },
  'Indicateur national': { fr: 'Indicateur national', en: 'National indicator' },

  // ── SMIG/SMAG explanation blocks ───────────────────────────────
  "C'est quoi le SMIG ?": { fr: "C'est quoi le SMIG ?", en: "What is the SMIG?" },
  "C'est quoi le SMAG ?": { fr: "C'est quoi le SMAG ?", en: "What is the SMAG?" },
  'SMIG explique': { fr: "SMIG = Salaire Minimum Interprofessionnel Garanti. C'est le salaire plancher légal au Maroc pour les secteurs industrie, commerce et services.", en: 'SMIG = Guaranteed Interprofessional Minimum Wage. It is the legal minimum wage in Morocco for industry, commerce, and services.' },
  'SMIG calcul': { fr: "Calcul : taux horaire × 191 heures/mois (durée légale 44h/semaine, soit 40h/semaine depuis 2004).", en: 'Calculation: hourly rate × 191 hours/month (legal working week of 44h, reduced to 40h since 2004).' },
  'SMIG evolution': { fr: "Le SMIG a été multiplié par 2,06 entre 1999 et 2026 (1 660 → 3 423 DH/mois).", en: 'The SMIG has multiplied by 2.06 between 1999 and 2026 (1,660 → 3,423 DH/month).' },
  'SMIG comparaison': { fr: "Comparaison : SMIC New York ≈ 8 500 DH/mois → ratio ~1:25 (reflète la différence de coût de la vie).", en: 'Comparison: NY Minimum Wage ≈ 8,500 DH/month → ratio ~1:25 (reflects cost of living differences).' },
  'SMIG exonération': { fr: "Les salariés au SMIG sont exonérés d'impôt sur le revenu au Maroc.", en: 'SMIG workers are exempt from income tax in Morocco.' },
  'SMAG explique': { fr: "SMAG = Salaire Minimum Agricole Garanti. S'applique aux travailleurs du secteur agricole et forestier.", en: 'SMAG = Guaranteed Agricultural Minimum Wage. Applies to agricultural and forestry workers.' },
  'SMAG calcul': { fr: "Calcul : taux journalier × 26 jours/mois (travail agricole saisonnier).", en: 'Calculation: daily rate × 26 days/month (seasonal agricultural work).' },
  'SMAG ecart': { fr: "Le SMAG est historiquement inférieur au SMIG (~74% en 2026). L'objectif est l'alignement d'ici 2028.", en: 'The SMAG has historically been lower than the SMIG (~74% in 2026). The goal is alignment by 2028.' },
  'SMAG agriculture': { fr: "L'agriculture emploie ~30% de la population active marocaine mais le secteur reste le moins rémunéré.", en: "Agriculture employs ~30% of Morocco's active population but remains the lowest-paid sector." },
  'SMAG augmentation': { fr: "Le SMAG a connu des augmentations plus fortes récemment (+10% en 2022) pour réduire l'écart avec le SMIG.", en: 'The SMAG has seen stronger recent increases (+10% in 2022) to narrow the gap with the SMIG.' },

  // ── Pedagogical essay ─────────────────────────────────────────
  "Comprendre l'évolution du salaire minimum au Maroc": { fr: "Comprendre l'évolution du salaire minimum au Maroc", en: 'Understanding the Evolution of Minimum Wage in Morocco' },
  'ESSAY_PARA1': {
    fr: 'Le salaire minimum au Maroc n\'a pas toujours été ce qu\'il est aujourd\'hui. Son histoire commence en 1970, avec l\'instauration du SMAG, réservé aux travailleurs agricoles. Il faudra attendre 1984 pour que le Maroc crée le SMIG, étendu aux secteurs industriel, commercial et des services. À l\'origine, les deux salaires minimaux étaient proches ; c\'est au fil des décennies que l\'écart s\'est creusé.',
    en: 'Morocco\'s minimum wage has not always been what it is today. Its story begins in 1970, with the introduction of the SMAG, reserved for agricultural workers. It was not until 1984 that Morocco created the SMIG, extended to the industrial, commercial, and services sectors. Initially, the two minimum wages were close; it was over the decades that the gap widened.',
  },
  'ESSAY_PARA2': {
    fr: 'La réforme la plus marquante est celle de 2004, lorsque le Maroc est passé de 44 heures de travail par semaine à 40 heures, conformément à la loi 65-99. Concrètement, cela signifie que la base mensuelle de calcul est passée de 208 heures (44h × 48 semaines) à 191 heures (40h × 48 semaines). Pour ne pas pénaliser les salariés, le taux horaire a été relevé d\'environ 10% la même année. Résultat : le salaire mensuel est resté quasi identique (1 845 DH), mais les travailleurs ont récupéré deux heures par semaine — un changement qui, à lui seul, a transformé les conditions de vie de millions de Marocains.',
    en: 'The most significant reform was in 2004, when Morocco moved from 44 working hours per week to 40, in accordance with Law 65-99. Concretely, this means the monthly calculation base changed from 208 hours (44h × 48 weeks) to 191 hours (40h × 48 weeks). To avoid penalizing workers, the hourly rate was increased by about 10% the same year. Result: the monthly salary remained nearly identical (1,845 DH), but workers recovered two hours per week — a change that alone transformed the living conditions of millions of Moroccans.',
  },
  'ESSAY_PARA3': {
    fr: 'Entre 2008 et 2012, dans le contexte du Printemps arabe et des revendications sociales, le gouvernement a procédé à des revalorisations plus fréquentes : +5% en 2008, +5% en 2009, puis +10% en 2011. Ce rythme s\'est ensuite ralenti, avec des augmentations de 5% tous les deux ou trois ans. La revalorisation de 2022, décidée de concertation tripartite (État, patronat, syndicats), visait explicitement à absorber l\'impact de l\'inflation post-Covid et de la crise ukrainienne, qui avait porté l\'IPC à 6,6%.',
    en: 'Between 2008 and 2012, in the context of the Arab Spring and social demands, the government carried out more frequent revaluations: +5% in 2008, +5% in 2009, then +10% in 2011. This pace then slowed, with 5% increases every two or three years. The 2022 revaluation, decided through tripartite consultation (government, employers, unions), explicitly aimed to absorb the impact of post-Covid inflation and the Ukrainian crisis, which had pushed the CPI to 6.6%.',
  },
  'ESSAY_PARA4': {
    fr: 'Le SMAG, de son côté, suit une trajectoire différente. Historiquement fixé à environ 65% du SMIG, il a progressé plus lentement. L\'agriculture marocaine, qui emploie près de 30% de la population active, reste le secteur le moins rémunéré. Depuis 2020, un effort délibéré a été fait pour réduire cet écart : le SMAG est passé de 69% du SMIG en 2020 à environ 74% en 2026. L\'objectif officiel, fixé dans le cadre du Nouveau Modèle de Développement (NMD), est l\'alignement progressif d\'ici 2028 — un défi considérable vu les contraintes structurelles de l\'agriculture marocaine (parcelles morcelées, faible mécanisation, dépendance aux aléas climatiques).',
    en: 'The SMAG, for its part, follows a different trajectory. Historically set at about 65% of the SMIG, it has progressed more slowly. Moroccan agriculture, which employs nearly 30% of the active population, remains the lowest-paid sector. Since 2020, a deliberate effort has been made to reduce this gap: the SMAG went from 69% of the SMIG in 2020 to about 74% in 2026. The official goal, set under the New Development Model (NMD), is gradual alignment by 2028 — a considerable challenge given the structural constraints of Moroccan agriculture (fragmented farms, low mechanization, dependence on climate hazards).',
  },
  'ESSAY_PARA5': {
    fr: 'Enfin, il faut garder à l\'esprit que le salaire minimum ne raconte qu\'une partie de l\'histoire. Le pouvoir d\'achat réel — c\'est-à-dire ce que le salaire permet vraiment d\'acheter — dépend étroitement de l\'inflation. En 27 ans (1999–2026), le SMIG a été multiplié par 2,06, mais les prix ont augmenté de 75%. Le gain réel est donc de seulement 17,6% sur toute la période. C\'est le sens du chiffre 117,6 affiché dans l\'indice de pouvoir d\'achat : un progrès, mais un progrès lent face au coût de la vie.',
    en: 'Finally, it is important to keep in mind that the minimum wage tells only part of the story. Real purchasing power — what the salary actually allows you to buy — depends closely on inflation. Over 27 years (1999–2026), the SMIG multiplied by 2.06, but prices rose by 75%. The real gain was therefore only 17.6% over the entire period. This is the meaning of the 117.6 figure shown in the purchasing power index: progress, but slow progress against the cost of living.',
  },
}
function t(key: string, lang: Lang): string {
  return translations[key]?.[lang] || key
}

// ─── KPI Interpretations ─────────────────────────────────────────────────────
const KPI_INTERPRETATIONS: Record<string, { what: Record<Lang, string>; meaning: Record<Lang, string>; status: Record<Lang, string>; recommendation: Record<Lang, string> }> = {
  PROD_CEREALIERE: {
    what: { fr: "Production totale de céréales (blé, orge, maïs, sorgho) au Maroc en millions de quintaux.", en: "Total cereal production (wheat, barley, corn, sorghum) in Morocco in millions of quintals." },
    meaning: { fr: "Indicateur clé de la sécurité alimentaire. Le Maroc est fortement dépendant des précipitations pour la production céréalière.", en: "Key indicator of food security. Morocco is heavily dependent on rainfall for cereal production." },
    status: { fr: "La production fluctue énormément selon les années pluvieuses ou sèches. 90 M qx en 2026 = excellente année.", en: "Production varies enormously between wet and dry years. 90M qx in 2026 = excellent year." },
    recommendation: { fr: "L'OM recommande de diversifier les sources de protéines et de renforcer les stocks stratégiques. Le Maroc reste importateur net de céréales.", en: "The FAO recommends diversifying protein sources and strengthening strategic stocks. Morocco remains a net cereal importer." },
  },
  VA_AGRICOLE: {
    what: { fr: "Valeur ajoutée du secteur agricole en milliards de MAD, mesurant la contribution nette de l'agriculture au PIB.", en: "Agricultural sector value added in billions of MAD, measuring the net contribution of agriculture to GDP." },
    meaning: { fr: "Le secteur représente ~12% du PIB et emploie ~30% de la population active. La VA inclut la production végétale, animale et la pêche.", en: "The sector represents ~12% of GDP and employs ~30% of the active population. VA includes crop, livestock, and fisheries production." },
    status: { fr: "Croissance de +10.6% = bonne performance portée par les céréales et l'arboriculture. Objectif du Plan Maroc Vert : 130 Mds MAD.", en: "+10.6% growth = good performance driven by cereals and tree crops. Green Morocco Plan target: 130 billion MAD." },
    recommendation: { fr: "La Banque Mondiale recommande d'accélérer la modernisation et l'irrigation pour réduire la dépendance au pluviométrique.", en: "The World Bank recommends accelerating modernization and irrigation to reduce dependence on rainfall." },
  },
  REMPLISSAGE_BARRAGES: {
    what: { fr: "Pourcentage moyen de remplissage des barrages au Maroc, mesurant les réserves d'eau douce disponibles.", en: "Average dam fill rate in Morocco, measuring available freshwater reserves." },
    meaning: { fr: "Taux vital pour l'agriculture irriguée, l'eau potable et l'hydroélectricité. <30% = sécheresse critique, >60% = bon niveau.", en: "Vital rate for irrigated agriculture, drinking water, and hydroelectricity. <30% = critical drought, >60% = good level." },
    status: { fr: "68% en 2026 = niveau satisfaisant après une période de sécheresse. Les précipitations ont été au-dessus de la moyenne.", en: "68% in 2026 = satisfactory level after a drought period. Rainfall was above average." },
    recommendation: { fr: "Le Programme National de l'Eau 2020-2050 recommande de généraliser le stockage et la réutilisation des eaux usées traitées.", en: "The National Water Program 2020-2050 recommends widespread storage and reuse of treated wastewater." },
  },
  TAUX_CHOMAGE: {
    what: { fr: "Taux de chômage national au sens du Bureau International du Travail (BIT) : personnes sans emploi et cherchant activement.", en: "National unemployment rate as defined by the ILO: people without jobs actively seeking work." },
    meaning: { fr: "Mesure la pression sur le marché du travail. Le Maroc a historiquement un chômage élevé chez les jeunes (30%+ pour les 15-24 ans).", en: "Measures pressure on the labor market. Morocco historically has high youth unemployment (30%+ for 15-24 year olds)." },
    status: { fr: "12.2% en 2026 (normes BIT / FMI WEO) = chômage structurel persistant. Le taux chez les jeunes 15-24 ans reste élevé (30%+).", en: "12.2% in 2026 (ILO standards / IMF WEO) = persistent structural unemployment. Youth 15-24 remains high (30%+)." },
    recommendation: { fr: "Le FMI recommande de renforcer la formation professionnelle et l'entrepreneuriat jeunesse. L'OCDE suggère de réduire le secteur informel.", en: "The IMF recommends strengthening vocational training and youth entrepreneurship. The OECD suggests reducing the informal sector." },
  },
  PIB_CROISSANCE: {
    what: { fr: "Taux de croissance du Produit Intérieur Brut (PIB) réel, mesurant l'expansion économique du pays.", en: "Real GDP growth rate, measuring the country's economic expansion." },
    meaning: { fr: ">3% = croissance satisfaisante pour un pays émergent, <2% = croissance molle, <0% = récession. Le Maroc vise 4-5%.", en: ">3% = satisfactory growth for an emerging country, <2% = sluggish growth, <0% = recession. Morocco targets 4-5%." },
    status: { fr: "4.0% en 2026 = croissance modérée, portée par l'agriculture et les exportations. Projections FMI stables à 4% jusqu'en 2028.", en: "4.0% in 2026 = moderate growth, driven by agriculture and exports. IMF projections stable at 4% through 2028." },
    recommendation: { fr: "La Banque Mondiale recommande de maintenir la stabilité macroéconomique et d'accélérer les réformes structurelles.", en: "The World Bank recommends maintaining macroeconomic stability and accelerating structural reforms." },
  },
  INFLATION: {
    what: { fr: "Taux d'inflation mesuré par l'indice des prix à la consommation (IPC), reflétant la hausse générale des prix.", en: "Inflation rate measured by the Consumer Price Index (CPI), reflecting general price increases." },
    meaning: { fr: "2% = cible idéale (BAM). >4% = inflation préoccupante, <0% = déflation. L'inflation alimentaire est plus volatile au Maroc.", en: "2% = ideal target (BAM). >4% = concerning inflation, <0% = deflation. Food inflation is more volatile in Morocco." },
    status: { fr: "2.0% en 2026 = retour à la cible de la BAM après le pic à 6.6% en 2022. Stabilité des prix retrouvée.", en: "2.0% in 2026 = back to BAM's target after the 6.6% peak in 2022. Price stability restored." },
    recommendation: { fr: "L'OM recommande une politique monétaire prudente. La BAM cible 2%±1 et utilise les taux directeurs comme outil principal.", en: "The IMF recommends prudent monetary policy. The BAM targets 2%±1 and uses policy rates as its main tool." },
  },
  PIB_PAR_HAB: {
    what: { fr: "Produit Intérieur Brut par habitant en USD courants, mesurant le niveau de vie moyen.", en: "GDP per capita in current USD, measuring average living standards." },
    meaning: { fr: ">5000 USD = seuil des pays à revenu intermédiaire. Le Maroc vise 6000 USD d'ici 2030.", en: ">5000 USD = upper-middle income threshold. Morocco targets 6000 USD by 2030." },
    status: { fr: "5 107 USD en 2026 = progression constante (+7.2% vs 2024). Source FMI WEO.", en: "5,107 USD in 2026 = steady growth (+7.2% vs 2024). Source IMF WEO." },
    recommendation: { fr: "La BM recommande d'accélérer la transformation structurelle pour créer des emplois à plus haute valeur ajoutée.", en: "The World Bank recommends accelerating structural transformation to create higher value-added jobs." },
  },
  BALANCE_COURANTE: {
    what: { fr: "Solde des transactions courantes (biens, services, revenus, transferts) en % du PIB.", en: "Current account balance (goods, services, income, transfers) as % of GDP." },
    meaning: { fr: "Déficit chronique lié à la facture énergétique et aux biens d'équipement. Les MRE compensent partiellement.", en: "Chronic deficit linked to energy imports and capital goods. MRE remittances partially offset." },
    status: { fr: "-3.2% en 2026 = déficit modéré en amélioration grâce aux exportations automobiles et aéronautiques.", en: "-3.2% in 2026 = moderate deficit improving thanks to automotive and aerospace exports." },
    recommendation: { fr: "Le FMI recommande de diversifier les exportations et de renforcer la compétitivité hors prix.", en: "The IMF recommends diversifying exports and strengthening non-price competitiveness." },
  },
  POPULATION: {
    what: { fr: "Population totale du Maroc estimée par le FMI WEO.", en: "Total population of Morocco estimated by the IMF WEO." },
    meaning: { fr: "Croissance démographique ralentie (<1%). Transition démographique avancée.", en: "Slowing demographic growth (<1%). Advanced demographic transition." },
    status: { fr: "32.3 millions en 2026 = croissance de 0.5% par an. Taux de fécondité proche du seuil de renouvellement.", en: "32.3 million in 2026 = 0.5% annual growth. Fertility rate near replacement level." },
    recommendation: { fr: "L'ONU recommande d'investir dans le capital humain et d'adapter le marché du travail à la transition démographique.", en: "The UN recommends investing in human capital and adapting the labor market to the demographic transition." },
  },
  EXPORTATIONS: {
    what: { fr: "Volume des exportations de biens et services (croissance annuelle en %).", en: "Volume of exports of goods and services (annual growth %)." },
    meaning: { fr: "Indicateur clé de la compétitivité externe. Secteurs porteurs : automobile, aéronautique, phosphates.", en: "Key indicator of external competitiveness. Growth sectors: automotive, aerospace, phosphates." },
    status: { fr: "3.9% en 2026 = ralentissement après le rebond post-COVID. Industrie automobile et aéronautique soutiennent la croissance.", en: "3.9% in 2026 = slowdown after post-COVID rebound. Automotive and aerospace industries support growth." },
    recommendation: { fr: "L'OMC recommande de renforcer l'intégration dans les chaînes de valeur mondiales.", en: "The WTO recommends strengthening integration into global value chains." },
  },
  IMPORTATIONS: {
    what: { fr: "Volume des importations de biens et services (croissance annuelle en %).", en: "Volume of imports of goods and services (annual growth %)." },
    meaning: { fr: "La croissance des importations reflète la demande intérieure et les besoins en biens d'équipement.", en: "Import growth reflects domestic demand and capital goods needs." },
    status: { fr: "3.5% en 2026 = modération des importations. Facture énergétique stabilisée.", en: "3.5% in 2026 = moderation of imports. Energy bill stabilized." },
    recommendation: { fr: "La BM recommande de promouvoir le contenu local et de réduire la dépendance aux importations énergétiques.", en: "The World Bank recommends promoting local content and reducing energy import dependence." },
  },
  INVESTISSEMENT: {
    what: { fr: "Formation brute de capital fixe (FBCF) en % du PIB, mesure de l'effort d'investissement national.", en: "Gross fixed capital formation as % of GDP, measuring national investment effort." },
    meaning: { fr: ">30% = bon niveau d'investissement pour un pays émergent. Le Maroc oscille autour de 30%.", en: ">30% = good investment level for an emerging country. Morocco hovers around 30%." },
    status: { fr: "29.8% du PIB en 2026 = investissement soutenu, porté par les grands projets d'infrastructure et l'industrie.", en: "29.8% of GDP in 2026 = sustained investment, driven by major infrastructure and industry projects." },
    recommendation: { fr: "Le FMI recommande de maintenir l'effort d'investissement public et de renforcer le partenariat public-privé.", en: "The IMF recommends maintaining public investment efforts and strengthening public-private partnerships." },
  },
  TAUX_DECOUVERT: {
    what: { fr: "Taux de bancarisation mesurant le pourcentage de la population ayant accès à un compte bancaire formel.", en: "Financial inclusion rate measuring the percentage of the population with access to a formal bank account." },
    meaning: { fr: "Indicateur d'inclusion financière. >70% = bonne bancarisation. Le Maroc progresse grâce aux banques digitales et mobile money.", en: "Financial inclusion indicator. >70% = good inclusion. Morocco is progressing thanks to digital banking and mobile money." },
    status: { fr: "55.2% en 2026 = progression continue mais en retard sur les standards internationaux (80%+).", en: "55.2% in 2026 = continued progress but behind international standards (80%+)." },
    recommendation: { fr: "Le G20 recommande d'atteindre 75% d'inclusion financière d'ici 2030. Les fintechs et l'agent banking sont des leviers clés.", en: "The G20 recommends reaching 75% financial inclusion by 2030. Fintechs and agent banking are key levers." },
  },
  SCOLARISATION_PRIMAIRE: {
    what: { fr: "Taux de scolarisation des enfants de 6-11 ans dans l'enseignement primaire.", en: "Enrollment rate of children aged 6-11 in primary education." },
    meaning: { fr: "Indicateur d'accès à l'éducation de base. >95% = quasi-universalisation. Le Maroc est proche de l'objectif ODD 4.", en: "Indicator of access to basic education. >95% = near-universalization. Morocco is close to SDG 4 target." },
    status: { fr: "99.3% = quasi-universalisation de l'enseignement primaire. Un succès du Plan Stratégique de la Santé.", en: "99.3% = near-universal primary education. A success of the Strategic Health Plan." },
    recommendation: { fr: "L'UNESCO recommande de maintenir la qualité tout en généralisant. L'abandon scolaire reste un défi en milieu rural.", en: "UNESCO recommends maintaining quality while expanding. Dropout rates remain a challenge in rural areas." },
  },
  DEPENSES_EDUCATION: {
    what: { fr: "Part des dépenses publiques d'éducation dans le PIB national.", en: "Share of public education spending in national GDP." },
    meaning: { fr: "Mesure l'effort budgétaire pour l'éducation. L'UNESCO recommande ≥4-6% du PIB. Le Maroc est dans cette fourchette.", en: "Measures the budgetary effort for education. UNESCO recommends 4-6% of GDP. Morocco is within this range." },
    status: { fr: "5.8% du PIB = dans la recommandation de l'UNESCO. L'effort budgétaire est soutenu.", en: "5.8% of GDP = within UNESCO's recommendation. The budgetary effort is sustained." },
    recommendation: { fr: "L'UNESCO recommande d'améliorer l'efficacité de la dépense plutôt que d'augmenter le volume. Réduire les classes de 40+ à 30 élèves.", en: "UNESCO recommends improving spending efficiency rather than increasing volume. Reduce classes from 40+ to 30 students." },
  },
  LITS_HOPITAL: {
    what: { fr: "Nombre total de lits d'hôpital disponibles pour la population (public et privé).", en: "Total number of hospital beds available to the population (public and private)." },
    meaning: { fr: "Indicateur de capacité sanitaire. L'OMS recommande ≥3 lits/1000 hab. Le Maroc est en progression.", en: "Healthcare capacity indicator. WHO recommends ≥3 beds/1000 inhabitants. Morocco is progressing." },
    status: { fr: "28.4K lits = amélioration continue. Ratio ~7.6 lits/1000 hab = en dessous de la recommandation OMS.", en: "28.4K beds = continuous improvement. Ratio ~7.6 beds/1000 inhabitants = below WHO recommendation." },
    recommendation: { fr: "L'OMS recommande de renforcer les soins primaires et la prévention plutôt que la seule augmentation des lits.", en: "WHO recommends strengthening primary care and prevention rather than solely increasing beds." },
  },
  HOPITAUX_PRIVES: {
    what: { fr: "Nombre total d'hôpitaux et cliniques privés au Maroc, incluant les cliniques à but lucratif et les structures semi-privées/non-lucratifs.", en: "Total number of private hospitals and clinics in Morocco, including for-profit clinics and semi-private/non-profit facilities." },
    meaning: { fr: "Le secteur privé hospitalier croît de +7.6%/an. Il complète l'offre publique, surtout en cardiologie, chirurgie et maternité.", en: "The private hospital sector grows at +7.6%/year. It complements public supply, especially in cardiology, surgery, and maternity." },
    status: { fr: "2 100+ établissements en 2026. Le secteur privé concentre ~45% des lits en milieu urbain.", en: "2,100+ facilities in 2026. The private sector concentrates ~45% of beds in urban areas." },
    recommendation: { fr: "L'OM recommande de renforcer la régulation du secteur privé et de garantir l'accessibilité des soins pour les populations vulnérables.", en: "The WHO recommends strengthening regulation of the private sector and ensuring healthcare accessibility for vulnerable populations." },
  },
  MEDOCINS: {
    what: { fr: "Nombre total de médecins exerçant au Maroc (généralistes et spécialistes).", en: "Total number of doctors practicing in Morocco (general practitioners and specialists)." },
    meaning: { fr: "Indicateur de ressources humaines en santé. L'OMS recommande ≥1 médecin/1000 hab. Le Maroc reste en deçà.", en: "Health human resources indicator. WHO recommends ≥1 doctor/1000 inhabitants. Morocco remains below." },
    status: { fr: "32.8K médecins = croissance de +7.5%. Ratio ~8.8‰ = progrès mais en retard sur l'UE (30-40‰).", en: "32.8K doctors = +7.5% growth. Ratio ~8.8‰ = progress but behind the EU (30-40‰)." },
    recommendation: { fr: "L'OM recommande de diversifier les spécialités et de renforcer la médecine de proximité et la santé mentale.", en: "The WHO recommends diversifying specialties and strengthening community medicine and mental health." },
  },
  FLUX_IDE: {
    what: { fr: "Flux des Investissements Directs Étrangers (IDE) entrant au Maroc, en millions de MAD.", en: "Foreign Direct Investment (FDI) inflows to Morocco, in millions of MAD." },
    meaning: { fr: "Mesure l'attractivité économique du pays pour les investisseurs étrangers. IDE élevé = confiance dans l'économie.", en: "Measures the country's economic attractiveness for foreign investors. High FDI = confidence in the economy." },
    status: { fr: "En progression = le Maroc attire des IDE dans l'automobile, l'aéronautique, l'offshoring et l'énergie renouvelable.", en: "Growing = Morocco attracts FDI in automotive, aerospace, offshoring, and renewable energy." },
    recommendation: { fr: "La CNUCED recommande de faciliter les procédures d'installation et de renforcer le cadre juridique pour les investisseurs.", en: "UNCTAD recommends streamlining installation procedures and strengthening the legal framework for investors." },
  },
  PRODUCTION_FRUITS: {
    what: { fr: "Production fruitière nationale (agrumes, oliviers, amandiers, avocatiers, etc.) en millions de tonnes.", en: "National fruit production (citrus, olives, almonds, avocados, etc.) in millions of tons." },
    meaning: { fr: "Les fruits sont le 1er poste d'exportation agricole. Le Maroc est le 1er exportateur d'agrumes en Europe.", en: "Fruits are the leading agricultural export. Morocco is the top citrus exporter to Europe." },
    status: { fr: "4.8 M tonnes en 2026 = croissance régulière. Les agrumes représentent ~60% de la production fruitière.", en: "4.8M tons in 2026 = steady growth. Citrus represents ~60% of fruit production." },
    recommendation: { fr: "Le Plan Maroc Vert recommande de diversifier les filières (avocat, mangue, grenade) et de renforcer la transformation.", en: "The Green Morocco Plan recommends diversifying supply chains (avocado, mango, pomegranate) and strengthening processing." },
  },
  CHEPTEL_BOVIN: {
    what: { fr: "Nombre total de têtes de bétail bovin (vaches, taureaux, génisses) au Maroc.", en: "Total number of cattle (cows, bulls, heifers) in Morocco." },
    meaning: { fr: "Indicateur de la filière laitière et viande. Le cheptel bovin est concentré dans les régions nord et centrales.", en: "Dairy and beef supply chain indicator. Cattle are concentrated in northern and central regions." },
    status: { fr: "3.2 M têtes = stabilité. Le secteur laitier est le 2e secteur agroalimentaire après le sucre.", en: "3.2M head = stability. The dairy sector is the 2nd agri-food sector after sugar." },
    recommendation: { fr: "La FAO recommande d'améliorer la productivité laitière par la génétique et l'alimentation animale.", en: "FAO recommends improving dairy productivity through genetics and animal nutrition." },
  },
  SCOLARISATION_COLLEGE: {
    what: { fr: "Taux de scolarisation des adolescents de 12-14 ans dans l'enseignement collégique.", en: "Enrollment rate of adolescents aged 12-14 in middle school." },
    meaning: { fr: "Indicateur de transition entre primaire et secondaire. Le taux d'abandon entre primaire et collège est un enjeu majeur.", en: "Transition indicator between primary and secondary. The dropout rate between primary and middle school is a major challenge." },
    status: { fr: "87.8% en 2026 = progrès mais en deçà du primaire (99%). Le fossé rural-urbain persiste.", en: "87.8% in 2026 = progress but below primary (99%). The rural-urban gap persists." },
    recommendation: { fr: "L'UNESCO recommande de renforcer l'orientation scolaire et l'accompagnement des élèves en difficulté.", en: "UNESCO recommends strengthening school guidance and support for struggling students." },
  },
  ENSEIGNANTS: {
    what: { fr: "Nombre total d'enseignants dans le système éducatif marocain (primaire, collège, lycée).", en: "Total number of teachers in the Moroccan education system (primary, middle, high school)." },
    meaning: { fr: "Indicateur de ressources humaines en éducation. Le ratio élèves/enseignant est un indicateur de qualité.", en: "Education human resources indicator. The student-teacher ratio is a quality indicator." },
    status: { fr: "249.3K enseignants en 2026 = augmentation continue. Le plan d'urgence de recrutement porte ses fruits.", en: "249.3K teachers in 2026 = continuous increase. The emergency recruitment plan is bearing fruit." },
    recommendation: { fr: "L'UNESCO recommande un ratio ≤30 élèves/enseignant et d'améliorer la formation initiale et continue.", en: "UNESCO recommends a ratio ≤30 students/teacher and improving initial and ongoing training." },
  },
  TAUX_ABANDON_PRIMAIRE: {
    what: { fr: "Pourcentage d'élèves qui quittent le système scolaire avant la fin du cycle primaire.", en: "Percentage of students who leave the school system before completing primary education." },
    meaning: { fr: "Indicateur critique de l'efficacité du système éducatif. <3% = bon, >5% = préoccupant. Le rural est plus touché.", en: "Critical indicator of education system effectiveness. <3% = good, >5% = concerning. Rural areas are more affected." },
    status: { fr: "3.1% en 2026 = amélioration significative (était 8.9% en 1999). Les efforts portent leurs fruits.", en: "3.1% in 2026 = significant improvement (was 8.9% in 1999). Efforts are paying off." },
    recommendation: { fr: "L'UNICEF recommande de cibler les zones rurales et de renforcer l'accès au transport scolaire et à la cantine.", en: "UNICEF recommends targeting rural areas and improving access to school transport and canteens." },
  },
  ETUDIANTS_TOTAL: {
    what: { fr: "Nombre total d'étudiants inscrits dans l'enseignement supérieur (universités, écoles, instituts).", en: "Total number of students enrolled in higher education (universities, schools, institutes)." },
    meaning: { fr: "Mesure la massification de l'enseignement supérieur. Le Maroc a multiplié par 2 le nombre d'étudiants en 20 ans.", en: "Measures the massification of higher education. Morocco doubled student numbers in 20 years." },
    status: { fr: "1.3 M d'étudiants en 2026 = massification importante. Le défi est l'employabilité des diplômés.", en: "1.3M students in 2026 = significant massification. The challenge is graduate employability." },
    recommendation: { fr: "L'OCDE recommande d'aligner la formation sur les besoins du marché du travail et de renforcer l'alternance.", en: "OECD recommends aligning training with labor market needs and strengthening work-study programs." },
  },
  UNIVERSITES_COUNT: {
    what: { fr: "Nombre total d'universités publiques au Maroc (universités à vocation régionale et établissements spécialisés).", en: "Total number of public universities in Morocco (regionally-oriented universities and specialized institutions)." },
    meaning: { fr: "Indicateur de l'offre de formation supérieure. Le Maroc a créé de nombreuses universités pour couvrir tout le territoire.", en: "Higher education supply indicator. Morocco created many universities to cover the entire territory." },
    status: { fr: "55 universités en 2026 = couverture territoriale satisfaisante. Le réseau s'est étendu avec les CER.", en: "55 universities in 2026 = satisfactory territorial coverage. The network has expanded with CERs." },
    recommendation: { fr: "L'enseignement supérieur doit se diversifier : filières technologiques, professionnalisantes, et partenariats entreprises.", en: "Higher education must diversify: technological tracks, professional training, and business partnerships." },
  },
  NOUVEAUX_INSCRITS: {
    what: { fr: "Nombre de nouveaux étudiants s'inscrivant chaque année dans l'enseignement supérieur.", en: "Number of new students enrolling each year in higher education." },
    meaning: { fr: "Mesure l'attrait de l'enseignement supérieur. L'augmentation continue pose des défis d'infrastructures et de qualité.", en: "Measures the appeal of higher education. Continuous growth poses infrastructure and quality challenges." },
    status: { fr: "335K nouveaux inscrits en 2026 = croissance forte. La capacité d'accueil est un enjeu majeur.", en: "335K new enrollments in 2026 = strong growth. Capacity is a major challenge." },
    recommendation: { fr: "L'OCDE recommande de rationaliser l'offre et de renforcer la sélectivité dans les filières à forte demande.", en: "OECD recommends rationalizing supply and strengthening selectivity in high-demand programs." },
  },
  SMIG: {
    what: { fr: "Salaire Minimum Interprofessionnel Garanti (secteur industriel, commercial et services), en MAD/mois.", en: "Guaranteed Interprofessional Minimum Wage (industry, commerce, and services), in MAD/month." },
    meaning: { fr: "Le SMIG est le salaire plancher légal au Maroc. Il a été multiplié par 2,06 depuis 1999 (1 660→3 423 MAD). Le SMIG NY ≈ 8 500 MAD/mois.", en: "The SMIG is the legal minimum wage in Morocco. It has multiplied by 2.06 since 1999 (1,660→3,423 MAD). NY minimum wage ≈ 8,500 MAD/month." },
    status: { fr: "3 423 MAD/mois (≈17,92 MAD/h × 191h) en 2026. Source : Décret 2-25-983, accord tripartite avril 2024.", en: "3,423 MAD/month (≈17.92 MAD/h × 191h) in 2026. Source: Decree 2-25-983, tripartite agreement April 2024." },
    recommendation: { fr: "Le FMI recommande d'indexer le SMIG sur la productivité. Le SMIG/NY ratio est de ~1:25, reflétant un écart structurel lié à la parité pouvoir d'achat.", en: "The IMF recommends indexing the SMIG to productivity. The SMIG/NY ratio is ~1:25, reflecting a structural gap linked to purchasing power parity." },
  },
  SMAG: {
    what: { fr: "Salaire Minimum Agricole Garanti (secteur agricole et forestier), en MAD/mois.", en: "Guaranteed Agricultural Minimum Wage (agricultural and forestry sector), in MAD/month." },
    meaning: { fr: "Le SMAG s'applique aux travailleurs agricoles. Il est historiquement inférieur au SMIG (~74% du SMIG en 2026). L'agriculture emploie ~30% de la population active.", en: "The SMAG applies to agricultural workers. It has historically been lower than the SMIG (~74% of SMIG in 2026). Agriculture employs ~30% of the active population." },
    status: { fr: "2 533 MAD/mois (≈97,44 MAD/j × 26 jours) en 2026. Augmentation de +5% en avril 2026 (accord tripartite avril 2024).", en: "2,533 MAD/month (≈97.44 MAD/day × 26 days) in 2026. +5% increase in April 2026 (tripartite agreement April 2024)." },
    recommendation: { fr: "L'OIT recommande de rapprocher le SMAG du SMIG. L'objectif gouvernemental est l'alignement complet d'ici 2028.", en: "The ILO recommends bringing the SMAG closer to the SMIG. The government's goal is full alignment by 2028." },
  },
  POUVOIR_ACHAT: {
    what: { fr: "Indice du pouvoir d'achat réel du SMIG corrigé de l'IPC (inflation), base 100 = 1999.", en: "Real purchasing power index of the SMIG adjusted for CPI (inflation), base 100 = 1999." },
    meaning: { fr: "Mesure l'évolution réelle du salaire minimum en tenant compte de la hausse des prix. >100 = amélioration, <100 = détérioration du pouvoir d'achat.", en: "Measures the real evolution of the minimum wage accounting for price increases. >100 = improvement, <100 = deterioration of purchasing power." },
    status: { fr: "117,6 en 2026 = le pouvoir d'achat réel a augmenté de 17,6% depuis 1999. L'inflation 2022-2023 (6,6% et 6,1%) a grignoté une partie des gains.", en: "117.6 in 2026 = real purchasing power increased by 17.6% since 1999. The 2022-2023 inflation (6.6% and 6.1%) eroded some of the gains." },
    recommendation: { fr: "La Banque Mondiale recommande de mieux cibler les transferts sociaux et d'améliorer la productivité pour soutenir le pouvoir d'achat réel.", en: "The World Bank recommends better targeting social transfers and improving productivity to support real purchasing power." },
  },
  ARRIVEES_TOURISTIQUES: {
    what: { fr: "Total des arrivées touristiques aux postes frontières du Maroc, incluant les touristes étrangers et les MRE.", en: "Total tourist arrivals at Moroccan border crossings, including foreign tourists and Moroccans living abroad (MRE)." },
    meaning: { fr: "Indicateur principal de la performance touristique. Le Maroc est la 1ère destination d'Afrique. Les MRE représentent ~49% des arrivées.", en: "Main indicator of tourism performance. Morocco is Africa's #1 destination. MREs account for ~49% of arrivals." },
    status: { fr: "19,8M en 2025 = record historique, +14% vs 2024. Objectif 26M d'ici 2030 (Coupe du Monde).", en: "19.8M in 2025 = all-time record, +14% vs 2024. Target 26M by 2030 (World Cup)." },
    recommendation: { fr: "L'OMT recommande de diversifier les marchés source et de renforcer le tourisme intérieur pour réduire la saisonnalité.", en: "UNWTO recommends diversifying source markets and strengthening domestic tourism to reduce seasonality." },
  },
  RECETTES_TOURISTIQUES: {
    what: { fr: "Recettes de voyages internationales (Office des Changes), en milliards de MAD. Source majeure de devises.", en: "International travel receipts (Office des Changes), in billions of MAD. Major source of foreign currency." },
    meaning: { fr: "Mesure directe de l'impact économique du tourisme. En 2024, le tourisme est devenu la 1ère source de devises du Maroc, devançant les transferts des MRE.", en: "Direct measure of tourism's economic impact. In 2024, tourism became Morocco's #1 source of foreign currency, surpassing MRE remittances." },
    status: { fr: "138 Mds MAD en 2025 (provisoire) = +43% vs 2019. Le Maroc vise 200 Mds MAD d'ici 2030.", en: "138 billion MAD in 2025 (provisional) = +43% vs 2019. Morocco targets 200 billion MAD by 2030." },
    recommendation: { fr: "La Banque Mondiale recommande d'augmenter la dépense moyenne par touriste en développement de l'offre haut de gamme et des circuits thématiques.", en: "The World Bank recommends increasing average tourist spending through high-end offerings and thematic circuits." },
  },
  NUITEES: {
    what: { fr: "Nombre de nuitées en hébergements classés au Maroc, mesurant la durée moyenne de séjour.", en: "Number of overnight stays in classified accommodations in Morocco, measuring average length of stay." },
    meaning: { fr: "Indicateur de la capacité d'attraction et de rétention des touristes. Plus de nuitées = plus de dépenses locales.", en: "Indicator of tourist attraction and retention capacity. More stays = more local spending." },
    status: { fr: "32,5M en 2025 = +13% vs 2024. Marrakech reste la 1ère destination, suivie d'Agadir.", en: "32.5M in 2025 = +13% vs 2024. Marrakech remains the #1 destination, followed by Agadir." },
    recommendation: { fr: "L'OMT recommande de prolonger la durée moyenne de séjour par le développement de produits touristiques innovants (tourisme culturel, gastronomique, bien-être).", en: "UNWTO recommends extending average stay through innovative tourism products (cultural, gastronomic, wellness)." },
  },
  PART_PIB_TOURISME: {
    what: { fr: "Part directe du tourisme dans le PIB national, en pourcentage.", en: "Direct contribution of tourism to national GDP, as a percentage." },
    meaning: { fr: "Mesure l'importance économique du secteur. >7% = secteur majeur. L'OMT évalue la contribution totale à 12,2% du PIB (direct + indirect).", en: "Measures the sector's economic importance. >7% = major sector. UNWTO estimates total contribution at 12.2% of GDP (direct + indirect)." },
    status: { fr: "7,3% en 2025. La contribution totale (WTTC) est de 12,2% du PIB, incluant les effets indirects sur l'économie.", en: "7.3% in 2025. Total contribution (WTTC) is 12.2% of GDP, including indirect economic effects." },
    recommendation: { fr: "Le FMI recommande de renforcer les retombées économiques du tourisme sur les secteurs connexes (agriculture, artisanat, transport).", en: "The IMF recommends strengthening tourism's economic spillovers on related sectors (agriculture, crafts, transport)." },
  },
  EMPLOI_TOURISME: {
    what: { fr: "Nombre total d'emplois directs et indirects dans le secteur touristique marocain.", en: "Total direct and indirect jobs in the Moroccan tourism sector." },
    meaning: { fr: "Le tourisme est un important pourvoyeur d'emplois, surtout pour les jeunes et les femmes. L'OMT estime 1,4 million d'emplois liés au tourisme.", en: "Tourism is a major job provider, especially for youth and women. UNWTO estimates 1.4 million tourism-related jobs." },
    status: { fr: "1,4M d'emplois en 2025 = ~13,6% de l'emploi total. Le secteur recrute massivement dans l'hôtellerie et la restauration.", en: "1.4M jobs in 2025 = ~13.6% of total employment. The sector is heavily recruiting in hotels and restaurants." },
    recommendation: { fr: "L'OIT recommande d'améliorer les conditions de travail et de renforcer la formation professionnelle touristique.", en: "ILO recommends improving working conditions and strengthening tourism vocational training." },
  },
  PASSAGERS_AEROPORT: {
    what: { fr: "Nombre total de passagers dans les aéroports marocains (ONDA), indicateur de connectivité.", en: "Total passengers in Moroccan airports (ONDA), connectivity indicator." },
    meaning: { fr: "Mesure la capacité d'accueil aérienne du Maroc. La connectivité aérienne est un levier clé de la croissance touristique.", en: "Measures Morocco's air reception capacity. Air connectivity is a key driver of tourism growth." },
    status: { fr: "38M en 2025 = +16% vs 2024. L'objectif 'Aérien x2' vise 13 millions de sièges supplémentaires.", en: "38M in 2025 = +16% vs 2024. The 'Air x2' strategy targets 13 million additional seats." },
    recommendation: { fr: "L'OMT recommande de développer la connectivité point à point avec les marchés émergents (Asie, Amérique latine).", en: "UNWTO recommends developing point-to-point connectivity with emerging markets (Asia, Latin America)." },
  },
  CAPACITE_HOTELIERE: {
    what: { fr: "Nombre total de chambres disponibles en hébergements classés au Maroc.", en: "Total rooms available in classified accommodations in Morocco." },
    meaning: { fr: "Mesure la capacité d'accueil du secteur hôtelier. L'expansion est nécessaire pour atteindre l'objectif 26M de touristes.", en: "Measures the hotel sector's reception capacity. Expansion is needed to reach the 26M tourist target." },
    status: { fr: "200 000 chambres en 2024. Le programme d'investissement 2030 prévoit l'ajout de 40 000 chambres supplémentaires.", en: "200,000 rooms in 2024. The 2030 investment program plans to add 40,000 additional rooms." },
    recommendation: { fr: "L'OMT recommande de diversifier l'offre d'hébergement (riads, éco-lodges, glamping) au-delà de l'hôtellerie traditionnelle.", en: "UNWTO recommends diversifying accommodation beyond traditional hotels (riads, eco-lodges, glamping)." },
  },
  'TAUX_OCCUPATION': {
    what: { fr: "Taux d'occupation moyen des chambres d'hôtels classés au Maroc.", en: "Average room occupancy rate of classified hotels in Morocco." },
    meaning: { fr: "Indicateur de performance du secteur hôtelier. >60% = bon niveau. La saisonnalité crée de fortes variations.", en: "Hotel sector performance indicator. >60% = good level. Seasonality creates strong variations." },
    status: { fr: "68% en 2025 = amélioration. Marrakech atteint 71% au T1 2025. Les regions côtières sont plus saisonnières.", en: "68% in 2025 = improvement. Marrakech reaches 71% in Q1 2025. Coastal regions are more seasonal." },
    recommendation: { fr: "Le Ministère du Tourisme recommande de développer le tourisme d'affaires et les événements pour lisser la saisonnalité.", en: "The Ministry of Tourism recommends developing business tourism and events to smooth seasonality." },
  },
  TRANSFERTS_MRE: {
    what: { fr: "Envois de fonds des Marocains Résidant à l'Étranger (MRE), première source de devises du Maroc.", en: "Remittances from Moroccans Living Abroad (MRE), Morocco's leading source of foreign currency." },
    meaning: { fr: "Les transferts des MRE financent la consommation des ménages, l'immobilier et les petites entreprises. Ils représentent ~7% du PIB.", en: "MRE transfers finance household consumption, real estate and small businesses. They represent ~7% of GDP." },
    status: { fr: "102 Mds MAD en 2025 = croissance continue. Les MRE restent la 2ème source de devises après le tourisme.", en: "102 billion MAD in 2025 = continued growth. MRE remain the 2nd source of foreign currency after tourism." },
    recommendation: { fr: "L'OMT recommande de faciliter les transferts (réduire les coûts) et d'orienter une partie vers l'investissement productif.", en: "The IMF recommends facilitating transfers (reducing costs) and directing part toward productive investment." },
  },
  PART_PIB_MRE: {
    what: { fr: "Contribution des transferts des MRE au PIB national, en pourcentage.", en: "Contribution of MRE remittances to national GDP, as a percentage." },
    meaning: { fr: "Mesure l'importance macroéconomique des envois de fonds de la diaspora marocaine. >6% = secteur majeur.", en: "Measures the macroeconomic importance of remittances from the Moroccan diaspora. >6% = major sector." },
    status: { fr: "7.0% du PIB en 2025. Le Maroc figure parmi les top 10 mondiaux pour les ratios transferts/PIB.", en: "7.0% of GDP in 2025. Morocco ranks among the global top 10 for remittance-to-GDP ratios." },
    recommendation: { fr: "La Banque Mondiale recommande de développer des produits financiers adaptés aux MRE pour canaliser l'épargne vers l'investissement.", en: "The World Bank recommends developing tailored financial products for MRE to channel savings toward investment." },
  },
  TOURISME_INTERNE: {
    what: { fr: "Nombre de voyages intérieurs effectués par les Marocains résidant au Maroc (tourisme domestique).", en: "Number of domestic trips made by Moroccans residing in Morocco (domestic tourism)." },
    meaning: { fr: "Le tourisme intérieur est un amortisseur contre la saisonnalité et les crises internationales. Il représente ~58% des nuitées totales.", en: "Domestic tourism is a buffer against seasonality and international crises. It represents ~58% of total overnight stays." },
    status: { fr: "16M de voyageurs en 2025 = forte reprise post-Covid. Les destinations côtières et de montagne sont les plus populaires.", en: "16M travelers in 2025 = strong post-Covid recovery. Coastal and mountain destinations are the most popular." },
    recommendation: { fr: "L'OMT recommande de promouvoir le tourisme domestique par des tarifs adaptés et des offres hors saison.", en: "UNWTO recommends promoting domestic tourism with adapted pricing and off-season offers." },
  },
  RECETTES_TOURISME_INTERNE: {
    what: { fr: "Recettes du tourisme intérieur : dépenses des Marocains voyageant au Maroc, en milliards de MAD.", en: "Domestic tourism receipts: spending by Moroccans traveling within Morocco, in billions of MAD." },
    meaning: { fr: "Mesure la contribution du tourisme domestique à l'économie locale. Ces dépenses bénéficient directement aux PME et artisans.", en: "Measures domestic tourism's contribution to the local economy. These expenditures directly benefit SMEs and artisans." },
    status: { fr: "50 Mds MAD en 2025. Le pouvoir d'achat des ménages et les infrastructures routières soutiennent la croissance.", en: "50 billion MAD in 2025. Household purchasing power and road infrastructure support growth." },
    recommendation: { fr: "Le Ministère du Tourisme recommande de développer l'offre touristique de proximité et le tourisme expérientiel.", en: "The Ministry of Tourism recommends developing nearby tourism offerings and experiential tourism." },
  },
  // ── Transport et Logistique ──────────────────────────────────────────────
  ONCF_PASSAGERS: {
    what: { fr: "Nombre de voyageurs transportés par le réseau ferroviaire ONCF (Al Boraq + trains conventionnels).", en: "Number of passengers transported by the ONCF rail network (Al Boraq + conventional trains)." },
    meaning: { fr: "Indicateur principal de la mobilité ferroviaire. Le Maroc investit massivement dans le Plan Rail 2040 (6 300 km cible).", en: "Main indicator of rail mobility. Morocco is investing massively in Rail Plan 2040 (6,300 km target)." },
    status: { fr: "55,6M en 2025 = record historique. Al Boraq (TGV) représente ~10% des passagers ONCF.", en: "55.6M in 2025 = all-time record. Al Boraq (TGV) accounts for ~10% of ONCF passengers." },
    recommendation: { fr: "La Banque Mondiale recommande de poursuivre l'extension du réseau ferroviaire et d'améliorer la desserte régionale.", en: "The World Bank recommends continuing rail network expansion and improving regional service." },
  },
  ONCF_FRET: {
    what: { fr: "Volume de marchandises transportées par voie ferroviaire (phosphates, céréales, conteneurs).", en: "Volume of goods transported by rail (phosphates, cereals, containers)." },
    meaning: { fr: "Le fret ferroviaire est essentiel pour les phosphates et le commerce extérieur. La performance dépend de l'état des infrastructures.", en: "Rail freight is essential for phosphates and foreign trade. Performance depends on infrastructure condition." },
    status: { fr: "22 Mt en 2025 = reprise après la baisse de 2023 (17 Mt). Les phosphates restent le principal produit transporté.", en: "22 Mt in 2025 = recovery after the 2023 decline (17 Mt). Phosphates remain the main transported product." },
    recommendation: { fr: "L'OM recommande de moderniser le parc de wagons et d'améliorer les connexions portuaires pour le fret.", en: "The IMF recommends modernizing the wagon fleet and improving port connections for freight." },
  },
  ONDA_PASSAGERS: {
    what: { fr: "Nombre total de passagers dans les 13 aéroports nationaux gérés par l'ONDA.", en: "Total passengers at 13 national airports managed by ONDA." },
    meaning: { fr: "Mesure la connectivité aérienne du Maroc avec le monde. Le secteur a connu une reprise spectaculaire post-Covid.", en: "Measures Morocco's air connectivity with the world. The sector has seen a spectacular post-Covid recovery." },
    status: { fr: "36,3M en 2025 = +11% vs 2024, record historique. Casablanca Mohammed V = 11M+ (30% du trafic).", en: "36.3M in 2025 = +11% vs 2024, all-time record. Casablanca Mohammed V = 11M+ (30% of traffic)." },
    recommendation: { fr: "La stratégie 'Aéroports 2030' vise à doubler la capacité à 65M passagers. Les investissements portent sur Casablanca, Marrakech, Tanger et Agadir.", en: "The 'Airports 2030' strategy targets doubling capacity to 65M passengers. Investments focus on Casablanca, Marrakech, Tangier and Agadir." },
  },
  PORT_TRAFFIC: {
    what: { fr: "Volume total de marchandises traitées par les ports marocains (Tanger Med, Jorf Lasfar, Casablanca, etc.).", en: "Total volume of goods handled by Moroccan ports (Tanger Med, Jorf Lasfar, Casablanca, etc.)." },
    meaning: { fr: "Le Maroc ambitionne de devenir une plateforme logistique Afrique-Europe. Le trafic portuaire est un indicateur clé du commerce extérieur.", en: "Morocco aims to become an Africa-Europe logistics hub. Port traffic is a key indicator of foreign trade." },
    status: { fr: "262,6 Mt en 2025 = +8,9%. Tanger Med = 11,11M TEU, 1er port d'Afrique et de la Méditerranée.", en: "262.6 Mt in 2025 = +8.9%. Tanger Med = 11.11M TEU, #1 port in Africa and the Mediterranean." },
    recommendation: { fr: "Le Ministère de l'Équipement recommande de développer Nador West Med et Dakhla Atlantic pour diversifier les accès maritimes.", en: "The Ministry of Equipment recommends developing Nador West Med and Dakhla Atlantic to diversify maritime access." },
  },
  TANGER_MED_TEU: {
    what: { fr: "Nombre de conteneurs (TEU) traités au complexe portuaire Tanger Med.", en: "Number of containers (TEU) handled at the Tanger Med port complex." },
    meaning: { fr: "Tanger Med est le 1er port d'Afrique et de la Méditerranée, 17ème mondial. Il connecte 180 ports dans 70 pays.", en: "Tanger Med is the #1 port in Africa and the Mediterranean, 17th globally. It connects 180 ports in 70 countries." },
    status: { fr: "11,11M TEU en 2025 = +8,5%. Record de performance. Revenue = 1,23 Md USD (+12,3%).", en: "11.11M TEU in 2025 = +8.5%. Performance record. Revenue = $1.23B (+12.3%)." },
    recommendation: { fr: "La Banque Mondiale recommande de maintenir l'avantage compétitif par l'efficacité opérationnelle et les investissements technologiques.", en: "The World Bank recommends maintaining competitive advantage through operational efficiency and technology investments." },
  },
  HIGHWAY_KM: {
    what: { fr: "Longueur totale du réseau autoroutier opérationnel géré par ADM (Autoroutes du Maroc).", en: "Total length of the operational highway network managed by ADM (Morocco Motorways)." },
    meaning: { fr: "L'autoroute est un levier de désenclavement et de développement économique régional. Le Maroc a un réseau en forte croissance.", en: "Highways are a lever for regional development and economic inclusion. Morocco has a rapidly growing network." },
    status: { fr: "1 800 km en 2025. Objectif 3 000 km d'ici 2030. Programme Coupe du Monde = 380 km supplémentaires.", en: "1,800 km in 2025. Target 3,000 km by 2030. World Cup program = 380 km additional." },
    recommendation: { fr: "L'OM recommande de poursuivre l'extension du réseau en priorisant les corridors économiques et la connectivité rurale.", en: "The IMF recommends continuing network expansion prioritizing economic corridors and rural connectivity." },
  },
  TRANS_GDP_SHARE: {
    what: { fr: "Part du secteur des transports dans la création de valeur nationale (PIB).", en: "Share of the transport sector in national value creation (GDP)." },
    meaning: { fr: "Le transport est un secteur stratégique qui facilite toutes les activités économiques. >8% = contribution significative.", en: "Transport is a strategic sector enabling all economic activities. >8% = significant contribution." },
    status: { fr: "8,7% en 2025 = croissance soutenue. Le secteur bénéficie de la reprise touristique et du commerce extérieur.", en: "8.7% in 2025 = sustained growth. The sector benefits from tourism recovery and foreign trade." },
    recommendation: { fr: "La Banque Africaine de Développement recommande d'investir dans les infrastructures logistiques pour réduire les coûts de transport.", en: "The African Development Bank recommends investing in logistics infrastructure to reduce transport costs." },
  },
  // ── Commerce ──────────────────────────────────────────────────────────────
  EXPORTS_FOB: {
    what: { fr: "Valeur des exportations de biens FOB (Free on Board), en milliards de MAD.", en: "Value of goods exports FOB (Free on Board), in billions of MAD." },
    meaning: { fr: "Les exportations reflètent la compétitivité de l'économie marocaine. L'automobile est le 1er poste d'exportation depuis 2023.", en: "Exports reflect Morocco's economic competitiveness. Automobiles are the #1 export item since 2023." },
    status: { fr: "470 Mds MAD en 2025 = +3,3%. Automobile (158 Mds), phosphates (87 Mds), agroalimentaire (86 Mds) = top 3.", en: "470 billion MAD in 2025 = +3.3%. Automobile (158B), phosphates (87B), agri-food (86B) = top 3." },
    recommendation: { fr: "L'OM recommande de diversifier les exportations et de monter en gamme dans les chaînes de valeur mondiales.", en: "The IMF recommends diversifying exports and moving up in global value chains." },
  },
  IMPORTS_CIF: {
    what: { fr: "Valeur des importations de biens CIF (Coût, Assurance, Fret), en milliards de MAD.", en: "Value of goods imports CIF (Cost, Insurance, Freight), in billions of MAD." },
    meaning: { fr: "Le Maroc est fortement dépendant des importations (énergie, alimentation, équipements). Le déficit structurel est un défi.", en: "Morocco is heavily dependent on imports (energy, food, equipment). The structural deficit is a challenge." },
    status: { fr: "780 Mds MAD en 2025 = +2,5%. Les produits énergétiques représentent ~15% du total.", en: "780 billion MAD in 2025 = +2.5%. Energy products account for ~15% of the total." },
    recommendation: { fr: "La Banque Centrale recommande de renforcer l'industrialisation pour réduire la dépendance aux importations.", en: "The Central Bank recommends strengthening industrialization to reduce import dependency." },
  },
  TRADE_DEFICIT: {
    what: { fr: "Différence entre les importations et les exportations de biens (déficit commercial).", en: "Difference between goods imports and exports (trade deficit)." },
    meaning: { fr: "Un déficit structurel chronique pèse sur la balance des paiements. Il est financé par le tourisme, les transferts MRE et l'IDE.", en: "A chronic structural deficit weighs on the balance of payments. It is financed by tourism, MRE remittances and FDI." },
    status: { fr: "310 Mds MAD en 2025. Le déficit se creuse légèrement malgré la hausse des exportations.", en: "310 billion MAD in 2025. The deficit widens slightly despite rising exports." },
    recommendation: { fr: "Le FMI recommande de réduire le déficit par la diversification des sources d'importation et le développement des exportations de services.", en: "The IMF recommends reducing the deficit by diversifying import sources and developing service exports." },
  },
  FDI_NET: {
    what: { fr: "Flux nets d'investissement direct étranger (IDE) entrant au Maroc.", en: "Net inflows of foreign direct investment (FDI) into Morocco." },
    meaning: { fr: "L'IDE est un indicateur de l'attractivité économique. Le Maroc attire des investissements dans l'automobile, l'aéronautique et l'IT.", en: "FDI is an indicator of economic attractiveness. Morocco attracts investment in automotive, aerospace and IT." },
    status: { fr: "1,80 Md USD en 2025 = rebond après le creux de 2023 (1,06 Md). La France, les EAU et l'Allemagne = top 3.", en: "$1.80B in 2025 = rebound after the 2023 trough ($1.06B). France, UAE and Germany = top 3." },
    recommendation: { fr: "La CNUCED recommande d'améliorer le climat des affaires et de renforcer l'intégration dans les chaînes de valeur mondiales.", en: "UNCTAD recommends improving the business climate and strengthening integration into global value chains." },
  },
  ECOMMERCE_VOLUME: {
    what: { fr: "Volume des transactions de commerce électronique au Maroc (paiements en ligne CMI/Wafir).", en: "Volume of e-commerce transactions in Morocco (online payments CMI/Wafir)." },
    meaning: { fr: "Le e-commerce est en forte croissance (+25-34%/an). Le Maroc compte 6,8M d'acheteurs en ligne et un panier moyen de 380 MAD.", en: "E-commerce is growing rapidly (+25-34%/year). Morocco has 6.8M online buyers and an average basket of 380 MAD." },
    status: { fr: "18 Mds MAD en 2025 = +20%. Jumia (28%), Marjane (18%), Glovo (12%) = top plateformes.", en: "18 billion MAD in 2025 = +20%. Jumia (28%), Marjane (18%), Glovo (12%) = top platforms." },
    recommendation: { fr: "La Banque Mondiale recommande de développer les infrastructures numériques et la confiance des consommateurs.", en: "The World Bank recommends developing digital infrastructure and consumer trust." },
  },
  COMMERCE_ESTABLISHMENTS: {
    what: { fr: "Nombre total d'établissements commerciaux au Maroc (commerce de gros, détail, réparation).", en: "Total number of commercial establishments in Morocco (wholesale, retail, repair)." },
    meaning: { fr: "Le commerce emploie >1M de personnes et représente 52% des établissements économiques. C'est le 1er secteur en nombre d'unités.", en: "Commerce employs >1M people and represents 52% of economic establishments. It is the #1 sector by unit count." },
    status: { fr: "587 177 en 2024 = +2,1%. Casablanca-Settat = 21,5% du total.", en: "587,177 in 2024 = +2.1%. Casablanca-Settat = 21.5% of total." },
    recommendation: { fr: "L'OMPIC recommande de digitaliser le commerce de détail et de soutenir les commerçants traditionnels.", en: "OMPIC recommends digitizing retail trade and supporting traditional merchants." },
  },
  TRADE_GDP_RATIO: {
    what: { fr: "Ratio du commerce extérieur (exports + imports) par rapport au PIB national.", en: "Ratio of foreign trade (exports + imports) to national GDP." },
    meaning: { fr: "Mesure l'ouverture commerciale du Maroc. >90% = économie très ouverte. Le Maroc parmi les pays les plus ouverts d'Afrique.", en: "Measures Morocco's trade openness. >90% = very open economy. Morocco among the most open countries in Africa." },
    status: { fr: "94,0% en 2025. Le Maroc est l'un des pays les plus ouverts commercialement d'Afrique.", en: "94.0% in 2025. Morocco is one of the most commercially open countries in Africa." },
    recommendation: { fr: "La Banque Mondiale recommande de profiter de l'ouverture pour diversifier les partenaires commerciaux.", en: "The World Bank recommends leveraging openness to diversify trade partners." },
  },
  // ── Énergie ───────────────────────────────────────────────────────────────
  ELECTRICITY_PRODUCTION: {
    what: { fr: "Production totale d'électricité au Maroc (ONEE + producteurs privés + renouvelables), en TWh.", en: "Total electricity production in Morocco (ONEE + private producers + renewables), in TWh." },
    meaning: { fr: "L'offre électrique reflète la croissance économique. Le Maroc reste importateur mais développe fortement les renouvelables.", en: "Electric supply reflects economic growth. Morocco remains a net importer but is heavily developing renewables." },
    status: { fr: "43,5 TWh en 2025 = +2,8%. Le charbon reste la première source (~60%).", en: "43.5 TWh in 2025 = +2.8%. Coal remains the leading source (~60%)." },
    recommendation: { fr: "L'AIE recommande d'accélérer la transition énergétique et de réduire la dépendance au charbon importé.", en: "The IEA recommends accelerating the energy transition and reducing dependence on imported coal." },
  },
  INSTALLED_CAPACITY: {
    what: { fr: "Capacité totale installée du parc électrique national, en MW.", en: "Total installed capacity of the national power fleet, in MW." },
    meaning: { fr: "La capacité installée doit dépasser la demande de pointe pour garantir la sécurité d'approvisionnement.", en: "Installed capacity must exceed peak demand to guarantee supply security." },
    status: { fr: "12 250 MW en 2025. Demande de pointe = 7 580 MW. Marge confortable de ~62%.", en: "12,250 MW in 2025. Peak demand = 7,580 MW. Comfortable margin of ~62%." },
    recommendation: { fr: "Le Plan National de l'Énergie vise 16 000 MW d'ici 2030, dont 10 000 MW de renouvelables.", en: "The National Energy Plan targets 16,000 MW by 2030, including 10,000 MW of renewables." },
  },
  RENEWABLE_SHARE: {
    what: { fr: "Part des énergies renouvelables (éolien, solaire, hydro) dans la capacité installée totale.", en: "Share of renewable energy (wind, solar, hydro) in total installed capacity." },
    meaning: { fr: "Indicateur clé de la transition énergétique. L'objectif est 52% en 2030 et 70% en 2040.", en: "Key indicator of the energy transition. The target is 52% by 2030 and 70% by 2040." },
    status: { fr: "30% en 2025 = en bonne voie. L'éolien (2 452 MW) domine, suivi du solaire (1 086 MW).", en: "30% in 2025 = on track. Wind (2,452 MW) leads, followed by solar (1,086 MW)." },
    recommendation: { fr: "IRENA recommande d'accélérer les appels d'offres pour les projets solaires et éoliens afin d'atteindre 52% en 2030.", en: "IRENA recommends accelerating tenders for solar and wind projects to reach 52% by 2030." },
  },
  WIND_CAPACITY: {
    what: { fr: "Capacité installée des parcs éoliens nationaux, en MW.", en: "Installed capacity of national wind farms, in MW." },
    meaning: { fr: "Le Maroc dispose d'un potentiel éolien exceptionnel ( côtes atlantique, nord). L'éolien est la source renouvelable #1.", en: "Morocco has exceptional wind potential (Atlantic coast, north). Wind is the #1 renewable source." },
    status: { fr: "2 452 MW en 2025. Tarfaya (301 MW), Boujdour (318 MW), Jbel Lahdid (270 MW) = grands parcs.", en: "2,452 MW in 2025. Tarfaya (301 MW), Boujdour (318 MW), Jbel Lahdid (270 MW) = major farms." },
    recommendation: { fr: "MASEN vise 5 200 MW d'éolien d'ici 2030. Les appels d'offres (Tiskrad 300 MW, etc.) se poursuivent.", en: "MASEN targets 5,200 MW of wind by 2030. Tenders (Tiskrad 300 MW, etc.) continue." },
  },
  SOLAR_CAPACITY: {
    what: { fr: "Capacité installée des centrales solaires (PV + CSP), en MW.", en: "Installed capacity of solar power plants (PV + CSP), in MW." },
    meaning: { fr: "Le Maroc a un ensoleillement parmi les meilleurs au monde. Le complexe Noor Ouarzazate est un monument de l'énergie solaire.", en: "Morocco has among the best solar irradiance in the world. The Noor Ouarzazate complex is a monument to solar energy." },
    status: { fr: "1 086 MW en 2025 = +22,7%. Noor Ouarzazate (580 MW) + projets Law 13-09 en cours.", en: "1,086 MW in 2025 = +22.7%. Noor Ouarzazate (580 MW) + Law 13-09 projects underway." },
    recommendation: { fr: "MASEN vise 4 028 MW de solaire supplémentaires d'ici 2030 (programme 2026-2030).", en: "MASEN targets 4,028 MW of additional solar by 2030 (2026-2030 program)." },
  },
  CO2_EMISSIONS: {
    what: { fr: "Émissions de CO2 fossile liées à la combustion d'énergie, en millions de tonnes.", en: "CO2 emissions from fossil fuel combustion, in millions of tonnes." },
    meaning: { fr: "Indicateur de l'empreinte carbone. Le charbon (60% de la production) est la principale source d'émissions.", en: "Indicator of carbon footprint. Coal (60% of production) is the main emission source." },
    status: { fr: "71 Mt en 2025 = quasi-stable. Le Maroc s'est engagé à réduire de 45,5% les émissions d'ici 2030 (NDC).", en: "71 Mt in 2025 = nearly stable. Morocco committed to reducing emissions by 45.5% by 2030 (NDC)." },
    recommendation: { fr: "L'UNFCCC recommande d'accélérer la fermeture des centrales à charbon et de renforcer les renouvelables.", en: "UNFCCC recommends accelerating coal plant closures and strengthening renewables." },
  },
  ELECTRICITY_ACCESS: {
    what: { fr: "Taux d'accès à l'électricité sur l'ensemble du territoire national.", en: "Rate of access to electricity across the national territory." },
    meaning: { fr: "L'accès universel à l'électricité est un ODD (Objectif 7). Le Maroc est très proche de l'universalisation.", en: "Universal access to electricity is an SDG (Goal 7). Morocco is very close to universalization." },
    status: { fr: "99,95% en 2025. Les dernières zones rurales enclavées sont en cours de raccordement.", en: "99.95% in 2025. The last remote rural areas are being connected." },
    recommendation: { fr: "L'AIE recommande de maintenir l'effort de raccordement tout en améliorant la qualité du service.", en: "The IEA recommends maintaining connection efforts while improving service quality." },
  },
  PER_CAPITA_KWH: {
    what: { fr: "Consommation d'électricité par habitant, en kWh.", en: "Electricity consumption per capita, in kWh." },
    meaning: { fr: "Indicateur du niveau de développement. >1 000 kWh/hab = bon niveau. La consommation est corrélée au PIB/hab.", en: "Indicator of development level. >1,000 kWh/capita = good level. Consumption is correlated with GDP/capita." },
    status: { fr: "1 090 kWh/hab en 2025. Le Maroc est au-dessus de la moyenne africaine mais en dessous de la moyenne mondiale.", en: "1,090 kWh/capita in 2025. Morocco is above the African average but below the global average." },
    recommendation: { fr: "La Banque Mondiale recommande d'améliorer l'efficacité énergétique pour réduire la consommation par unité de PIB.", en: "The World Bank recommends improving energy efficiency to reduce consumption per unit of GDP." },
  },
  REMPLISSAGE_BARRAGES_ENV: {
    what: { fr: "Taux moyen de remplissage des barrages nationaux, mesurant les réserves d'eau douce.", en: "Average national dam fill rate, measuring freshwater reserves." },
    meaning: { fr: "Indicateur vital pour l'agriculture irriguée, l'eau potable et l'hydroélectricité. <30% = sécheresse critique.", en: "Vital indicator for irrigated agriculture, drinking water, and hydroelectricity. <30% = critical drought." },
    status: { fr: "68% en 2026 = niveau satisfaisant après des années de sécheresse. Les précipitations ont été au-dessus de la moyenne.", en: "68% in 2026 = satisfactory level after drought years. Rainfall was above average." },
    recommendation: { fr: "Le Programme National de l'Eau 2020-2050 recommande le stockage et la réutilisation des eaux usées traitées.", en: "The National Water Program 2020-2050 recommends storage and reuse of treated wastewater." },
  },
  CO2_EMISSIONS_ENV: {
    what: { fr: "Émissions de CO₂ fossile liées à l'énergie et l'industrie, en millions de tonnes équivalent CO₂.", en: "Fossil CO₂ emissions from energy and industry, in million tonnes CO₂ equivalent." },
    meaning: { fr: "Indicateur clé du changement climatique. Le Maroc s'est engagé à réduire ses émissions de 45% d'ici 2030.", en: "Key climate change indicator. Morocco has committed to reducing emissions by 45% by 2030." },
    status: { fr: "71 Mt en 2026 = progression lente malgré les efforts sur les renouvelables.", en: "71 Mt in 2026 = slow progression despite renewable energy efforts." },
    recommendation: { fr: "L'ONU recommande d'accélérer la transition énergétique et de développer la capture du carbone.", en: "The UN recommends accelerating energy transition and developing carbon capture." },
  },
  HYDRIC_STRESS: {
    what: { fr: "Indice de stress hydrique national : ratio entre la demande et l'offre d'eau.", en: "National water stress index: ratio between water demand and supply." },
    meaning: { fr: ">40% = stress hydrique élevé. Le Maroc est classé parmi les pays à stress hydrique par l'ONU.", en: ">40% = high water stress. Morocco is classified as water-stressed by the UN." },
    status: { fr: "42% en 2026 = amélioration relative grâce aux précipitations. Le stress reste structurellement élevé.", en: "42% in 2026 = relative improvement thanks to rainfall. Stress remains structurally high." },
    recommendation: { fr: "La Banque Mondiale recommande de réduire les pertes dans les réseaux et de généraliser le dessalement.", en: "The World Bank recommends reducing network losses and widespread desalination." },
  },
  FOREST_AREA: {
    what: { fr: "Superficie totale des forêts au Maroc en millions d'hectares.", en: "Total forest area in Morocco in million hectares." },
    meaning: { fr: "Le Maroc est l'un des pays les plus boisés du Maghreb. Les forêts couvrent ~12% du territoire.", en: "Morocco is one of the most forested countries in North Africa. Forests cover ~12% of the territory." },
    status: { fr: "5.56 M ha en 2026 = stabilité après des décennies de dégradation et de reboisement.", en: "5.56 M ha in 2026 = stability after decades of degradation and reforestation." },
    recommendation: { fr: "L'ONU recommande d'atteindre 12% de couverture forestière mondiale d'ici 2030.", en: "The UN recommends reaching 12% global forest cover by 2030." },
  },
  REFORESTATION_RATE: {
    what: { fr: "Surface reboisée par an dans le cadre du Programme Forestier National.", en: "Area reforested per year under the National Forest Program." },
    meaning: { fr: "Le reboisement compense partiellement la déforestation et la désertification.", en: "Reforestation partially offsets deforestation and desertification." },
    status: { fr: "32 000 ha/an en 2026 = objectif atteint. Le Maroc vise 60 000 ha/an d'ici 2030.", en: "32,000 ha/year in 2026 = target met. Morocco aims for 60,000 ha/year by 2030." },
    recommendation: { fr: "L'ONU recommande le reboisement avec des espèces locales et la participation communautaire.", en: "The UN recommends reforestation with native species and community participation." },
  },
  HEATWAVE_DAYS: {
    what: { fr: "Nombre moyen de jours de vague de chaleur par an au Maroc.", en: "Average number of heatwave days per year in Morocco." },
    meaning: { fr: "Indicateur du changement climatique. >30 jours = impact significatif sur la santé et l'agriculture.", en: "Climate change indicator. >30 days = significant impact on health and agriculture." },
    status: { fr: "38 jours en 2026 = augmentation continue liée au réchauffement global.", en: "38 days in 2026 = continuous increase linked to global warming." },
    recommendation: { fr: "L'OMS recommande de renforcer les systèmes d'alerte précoce et l'urbanisme bioclimatique.", en: "The WHO recommends strengthening early warning systems and bioclimatic urban planning." },
  },
  PROTECTED_AREAS: {
    what: { fr: "Superficie des aires protégées par rapport au territoire national.", en: "Protected area as a percentage of national territory." },
    meaning: { fr: "Le Maroc a un réseau de 10+ parcs nationaux. L'objectif ODD 14/15 est de 30% d'ici 2030.", en: "Morocco has a network of 10+ national parks. The SDG 14/15 target is 30% by 2030." },
    status: { fr: "12.7% en 2026 = progrès mais en retard sur l'objectif 30x30.", en: "12.7% in 2026 = progress but behind the 30x30 target." },
    recommendation: { fr: "La CMN recommande d'étendre les aires protégées terrestres et marines.", en: "IUCN recommends extending terrestrial and marine protected areas." },
  },
  WASTE_RECYCLING: {
    what: { fr: "Taux de valorisation et recyclage des déchets solides au Maroc.", en: "Solid waste recycling and recovery rate in Morocco." },
    meaning: { fr: "Le Maroc produit ~7 Mt de déchets/an. Le taux de valorisation reste faible comparé aux standards européens.", en: "Morocco produces ~7 Mt of waste/year. The recovery rate remains low compared to European standards." },
    status: { fr: "22% en 2026 = amélioration mais loin de l'objectif de 40% en 2030.", en: "22% in 2026 = improvement but far from the 40% target by 2030." },
    recommendation: { fr: "La Banque Mondiale recommande de développer l'économie circulaire et les infrastructures de tri.", en: "The World Bank recommends developing circular economy and sorting infrastructure." },
  },
  TAX_REVENUES: {
    what: { fr: "Recettes fiscales totales de l'État : TVA, IS, IR, droits de douane.", en: "Total government tax revenues: VAT, CIT, PIT, customs duties." },
    meaning: { fr: "Les recettes fiscales financent ~85% du budget de l'État. La pression fiscale reste modérée.", en: "Tax revenues finance ~85% of the state budget. Tax burden remains moderate." },
    status: { fr: "289 MM MAD en 2026 = progression de +5.1%. La DGI modernise la collecte.", en: "289 billion MAD in 2026 = +5.1% growth. The DGI is modernizing collection." },
    recommendation: { fr: "Le FMI recommande d'élargir l'assiette fiscale et de réduire l'économie informelle.", en: "The IMF recommends broadening the tax base and reducing the informal economy." },
  },
  SUBSIDIES: {
    what: { fr: "Subventions de l'État : compensation carburants, blé, sucre, électricité.", en: "State subsidies: fuel, wheat, sugar, electricity compensation." },
    meaning: { fr: "Les subventions pèsent sur le budget. La réforme ciblée vise à réduire la facture tout en protégeant les plus vulnérables.", en: "Subsidies weigh on the budget. Targeted reform aims to reduce costs while protecting the most vulnerable." },
    status: { fr: "18.5 MM MAD en 2026 = baisse continue grâce à la réforme ciblée amorcée en 2013.", en: "18.5 billion MAD in 2026 = continued decline thanks to targeted reform started in 2013." },
    recommendation: { fr: "La Banque Mondiale recommande d'accélérer la réforme des subventions au profit de transferts monétaires ciblés.", en: "The World Bank recommends accelerating subsidy reform toward targeted cash transfers." },
  },
  PUBLIC_DEBT_GDP: {
    what: { fr: "Stock de la dette publique rapportée au PIB national.", en: "National public debt stock as a percentage of GDP." },
    meaning: { fr: "Le seuil de Maastricht est 60%. Le Maroc le dépasse depuis 2015. La soutenabilité est surveillée par la BAM.", en: "The Maastricht threshold is 60%. Morocco has exceeded it since 2015. Sustainability is monitored by BAM." },
    status: { fr: "79% PIB en 2026 = en progression. La COVID a aggravé la dette. Le FMI recommande la consolidation.", en: "79% GDP in 2026 = rising. COVID worsened debt. The IMF recommends consolidation." },
    recommendation: { fr: "L'UE recommande de ramener la dette sous 60% PIB à moyen terme par une discipline budgétaire.", en: "The EU recommends bringing debt below 60% GDP in the medium term through fiscal discipline." },
  },
  BUDGET_EXECUTION: {
    what: { fr: "Taux d'exécution du budget de l'État : dépenses réelles / dépenses autorisées.", en: "State budget execution rate: actual spending / authorized spending." },
    meaning: { fr: ">90% = bonne exécution. <80% = problèmes de programmation ou de capacité d'absorption.", en: ">90% = good execution. <80% = programming or absorption capacity problems." },
    status: { fr: "91% en 2026 = amélioration. Les grands projets d'infrastructure sont mieux exécutés.", en: "91% in 2026 = improvement. Major infrastructure projects are better executed." },
    recommendation: { fr: "La Cour des Comptes recommande le renforcement du contrôle budgétaire et la programmation pluriannuelle.", en: "The Court of Auditors recommends strengthening budget control and multi-year programming." },
  },
  DEBT_SERVICE: {
    what: { fr: "Service de la dette : paiements d'intérêts et amortissements.", en: "Debt service: interest payments and amortizations." },
    meaning: { fr: "Un service de la dette >20% des recettes = zone de vigilance. Le Maroc reste dans la zone sûre.", en: "Debt service >20% of revenue = watch zone. Morocco remains in the safe zone." },
    status: { fr: "34 MM MAD en 2026 = hausse liée à l'augmentation du stock de dette.", en: "34 billion MAD in 2026 = increase linked to rising debt stock." },
    recommendation: { fr: "Le Trésor recommande de diversifier les sources de financement et d'allonger les maturités.", en: "The Treasury recommends diversifying financing sources and extending maturities." },
  },
  IPAI: {
    what: { fr: "Indice des prix des actifs immobiliers (base 100 = 2020), mesurant l'évolution des prix de l'immobilier.", en: "Real estate asset price index (base 100 = 2020), measuring real estate price trends." },
    meaning: { fr: ">105 = inflation immobilière significative. Le Maroc connaît une hausse modérée des prix.", en: ">105 = significant real estate inflation. Morocco experiences moderate price increases." },
    status: { fr: "114.2 en 2026 = hausse continue mais contrôlée, portée par les grandes métropoles.", en: "114.2 in 2026 = continued but controlled increase, driven by major cities." },
    recommendation: { fr: "L'OM recommande de surveiller les bulles immobilières et de développer l'offre de logements.", en: "The IMF recommends monitoring real estate bubbles and increasing housing supply." },
  },
  PROPERTY_TRANSACTIONS: {
    what: { fr: "Volume total des transactions immobilières enregistrées (actes notariés).", en: "Total volume of real estate transactions (notarial deeds)." },
    meaning: { fr: "Indicateur de la dynamique du marché immobilier. >150K = marché actif.", en: "Indicator of real estate market dynamics. >150K = active market." },
    status: { fr: "158 000 en 2026 = reprise après le COVID. Le marché est porté par la demande résidentielle.", en: "158,000 in 2026 = recovery after COVID. Market driven by residential demand." },
    recommendation: { fr: "L'ANCFCC recommande la dématérialisation des actes et la réduction des délais.", en: "ANCFCC recommends dematerializing deeds and reducing delays." },
  },
  AUTO_PRODUCTION: {
    what: { fr: "Nombre total de véhicules produits au Maroc par an.", en: "Total number of vehicles produced in Morocco per year." },
    meaning: { fr: "Le Maroc est le 1er producteur automobile en Afrique. L'industrie représente 22% des exportations.", en: "Morocco is the #1 automobile producer in Africa. The industry represents 22% of exports." },
    status: { fr: "580 000 véhicules en 2026 = croissance soutenue. Nissan, Renault et Stellantis sont les principaux acteurs.", en: "580,000 vehicles in 2026 = sustained growth. Nissan, Renault and Stellantis are the main players." },
    recommendation: { fr: "La Banque Mondiale recommande d'augmenter le taux d'intégration locale et d'attirer les équipementiers.", en: "The World Bank recommends increasing local integration and attracting equipment suppliers." },
  },
  INDUSTRIAL_VA_GDP: {
    what: { fr: "Valeur ajoutée industrielle rapportée au PIB national.", en: "Industrial value added as a percentage of GDP." },
    meaning: { fr: "La part de l'industrie dans le PIB reflète le degré d'industrialisation du pays.", en: "The share of industry in GDP reflects the country's degree of industrialization." },
    status: { fr: "18.2% PIB en 2026 = en deçà de l'objectif Plan Industriel 2021-2030 (23%).", en: "18.2% GDP in 2026 = below the 2021-2030 Industrial Plan target (23%)." },
    recommendation: { fr: "Le Ministère de l'Industrie recommande de renforcer l'industrie 4.0 et la compétitivité.", en: "The Ministry of Industry recommends strengthening Industry 4.0 and competitiveness." },
  },
  INTERNET_PENETRATION: {
    what: { fr: "Taux de pénétration d'Internet au Maroc (pourcentage de la population).", en: "Internet penetration rate in Morocco (percentage of population)." },
    meaning: { fr: ">80% = bonne pénétration. Le Maroc fait partie des leaders numériques en Afrique.", en: ">80% = good penetration. Morocco is among the digital leaders in Africa." },
    status: { fr: "88.5% en 2026 = progression continue. La 4G et la fibre optique tirent la croissance.", en: "88.5% in 2026 = continued growth. 4G and fiber optic drive growth." },
    recommendation: { fr: "L'UIT recommande de combler la fracture numérique rurale et de renforcer la cybersécurité.", en: "ITU recommends bridging the rural digital divide and strengthening cybersecurity." },
  },
  LABELED_STARTUPS: {
    what: { fr: "Nombre de startups labellisées par le statut CRI (Convention d'Installation Récente).", en: "Number of startups labeled with CRI status (Recent Installation Convention)." },
    meaning: { fr: "Le label CRI offre des avantages fiscaux. L'écosystème startup marocain est l'un des plus dynamiques en Afrique.", en: "The CRI label offers tax benefits. Morocco's startup ecosystem is one of the most dynamic in Africa." },
    status: { fr: "4 200 en 2026 = croissance exponentielle depuis la loi startup 2019.", en: "4,200 in 2026 = exponential growth since the 2019 Startup Act." },
    recommendation: { fr: "L'OM recommende d'améliorer l'accès au financement et aux marchés internationaux.", en: "The IMF recommends improving access to financing and international markets." },
  },
  FIBER_SUBSCRIBERS: {
    what: { fr: "Nombre d'abonnés au très haut débit fibre (FTTH) au Maroc.", en: "Number of fiber optic (FTTH) subscribers in Morocco." },
    meaning: { fr: "La fibre optique offre des débits >100 Mbps. Le déploiement reste concentré sur les grandes villes.", en: "Fiber optic offers speeds >100 Mbps. Deployment remains concentrated in major cities." },
    status: { fr: "2,85 millions en 2026 = croissance forte (+18.8%). Les 3 opérateurs accélèrent le déploiement.", en: "2.85 million in 2026 = strong growth (+18.8%). All 3 operators are accelerating deployment." },
    recommendation: { fr: "L'ANRT recommande d'étendre la fibre aux zones semi-urbaines et rurales.", en: "ANRT recommends extending fiber to semi-urban and rural areas." },
  },
  TOTAL_POPULATION: {
    what: { fr: "Population totale du Maroc en millions d'habitants.", en: "Total population of Morocco in millions." },
    meaning: { fr: "Le Maroc est le 5ème pays le plus peuplé d'Afrique. La croissance ralentit.", en: "Morocco is the 5th most populous country in Africa. Growth is slowing." },
    status: { fr: "38,1 M en 2026 = croissance de 1,6%. Le taux de fécondité est proche du seuil de renouvellement.", en: "38.1M in 2026 = 1.6% growth. The fertility rate is near replacement level." },
    recommendation: { fr: "L'ONU recommande d'investir dans la jeunesse et de préparer la transition démographique.", en: "The UN recommends investing in youth and preparing for the demographic transition." },
  },
  BIRTH_RATE: {
    what: { fr: "Nombre de naissances pour 1000 habitants par an.", en: "Number of births per 1000 inhabitants per year." },
    meaning: { fr: "La baisse de la natalité reflète l'amélioration de l'accès à l'éducation et à la planification familiale.", en: "Declining birth rates reflect improved access to education and family planning." },
    status: { fr: "17,2‰ en 2026 = en baisse continue depuis 2005 (22‰). Le Maroc est en transition démographique.", en: "17.2‰ in 2026 = continuous decline since 2005 (22‰). Morocco is in demographic transition." },
    recommendation: { fr: "L'OMS recommande de maintenir les programmes de planification familiale.", en: "WHO recommends maintaining family planning programs." },
  },
  FERTILITY_RATE: {
    what: { fr: "Nombre moyen d'enfants par femme au cours de sa vie reproductive.", en: "Average number of children per woman over her reproductive life." },
    meaning: { fr: "2,1 = seuil de renouvellement des générations. Le Maroc approche ce seuil.", en: "2.1 = generational replacement level. Morocco is approaching this level." },
    status: { fr: "2,15 en 2026 = proche du seuil de renouvellement. L'éducation des femmes est le principal facteur.", en: "2.15 in 2026 = near replacement level. Women's education is the main factor." },
    recommendation: { fr: "L'ONU recommande d'améliorer l'accès à l'éducation pour les filles en milieu rural.", en: "The UN recommends improving access to education for girls in rural areas." },
  },
  URBAN_POPULATION: {
    what: { fr: "Pourcentage de la population vivant en milieu urbain.", en: "Percentage of the population living in urban areas." },
    meaning: { fr: "L'urbanisation croissante pose des défis : logement, transports, services publics.", en: "Growing urbanization poses challenges: housing, transportation, public services." },
    status: { fr: "64,8% en 2026 = le Maroc se urbanise moins vite que ses voisins (Algérie 74%, Tunisie 70%).", en: "64.8% in 2026 = Morocco urbanizes more slowly than its neighbors (Algeria 74%, Tunisia 70%)." },
    recommendation: { fr: "La BM recommande une planification urbaine intégrée et le développement des villes intermédiaires.", en: "The World Bank recommends integrated urban planning and developing intermediate cities." },
  },
}

// Module name translations
const MODULE_NAMETranslations: Record<string, Record<Lang, string>> = {
  'Économie': { fr: 'Économie', en: 'Economy' },
  'Agriculture': { fr: 'Agriculture', en: 'Agriculture' },
  'Social': { fr: 'Social', en: 'Social' },
  'Éducation': { fr: 'Éducation', en: 'Education' },
  'Santé': { fr: 'Santé', en: 'Health' },
  'Sport': { fr: 'Sport', en: 'Sport' },
  'Tourisme': { fr: 'Tourisme', en: 'Tourism' },
  'Transport et Logistique': { fr: 'Transport et Logistique', en: 'Transport & Logistics' },
  'Commerce': { fr: 'Commerce', en: 'Trade & Commerce' },
  'Énergie': { fr: 'Énergie', en: 'Energy' },
  'Environnement & Climat': { fr: 'Environnement & Climat', en: 'Environment & Climate' },
  'Finances Publiques': { fr: 'Finances Publiques', en: 'Public Finance' },
  'Immobilier & Habitat': { fr: 'Immobilier & Habitat', en: 'Real Estate & Housing' },
  'Investissement & Commerce Extérieur': { fr: 'Investissement & Commerce Extérieur', en: 'Investment & Foreign Trade' },
  'Industrie & Compétitivité': { fr: 'Industrie & Compétitivité', en: 'Industry & Competitiveness' },
  'Numérique & Innovation': { fr: 'Numérique & Innovation', en: 'Digital & Innovation' },
  'Démographie': { fr: 'Démographie', en: 'Demographics' },
}
function tModule(name: string, lang: Lang): string {
  return MODULE_NAMETranslations[name]?.[lang] || name
}

// ─── Constants ──────────────────────────────────────────────────────────────

const MIN_YEAR = 1999
const MAX_YEAR = 2026
const ALL_YEARS = Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, i) => MIN_YEAR + i)

const ICON_MAP: Record<string, React.ComponentType<{ className?: string; style?: React.CSSProperties }>> = {
  TrendingUp,
  Wheat,
  Users,
  GraduationCap,
  HeartPulse,
  Trophy,
  Plane,
  Truck,
  ShoppingCart,
  Zap,
  TreePine,
  Receipt,
  Building2,
  Globe,
  Factory,
  Cpu,
  UsersRound,
}

const REGIONAL_COLORS = [
  'hsl(24, 85%, 53%)',
  'hsl(142, 71%, 45%)',
  'hsl(200, 55%, 50%)',
  'hsl(262, 65%, 52%)',
  'hsl(0, 72%, 55%)',
  'hsl(47, 90%, 48%)',
  'hsl(175, 65%, 40%)',
  'hsl(340, 65%, 52%)',
  'hsl(160, 50%, 38%)',
  'hsl(30, 60%, 48%)',
  'hsl(210, 45%, 48%)',
  'hsl(280, 40%, 48%)',
]

const CHART_SECONDARY = 'hsl(200, 25%, 48%)'

// ─── Helpers ────────────────────────────────────────────────────────────────

function formatValue(value: number, code?: string): string {
  if (code && INTEGER_KPI_CODES.has(code)) return Math.round(value).toLocaleString('fr-FR')
  if (Number.isInteger(value)) return value.toLocaleString('fr-FR')
  if (value * 10 === Math.floor(value * 10)) {
    return value.toLocaleString('fr-FR', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    })
  }
  return value.toLocaleString('fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatTableValue(value: number, code?: string): string {
  if (code && INTEGER_KPI_CODES.has(code)) {
    return Math.round(value).toLocaleString('fr-FR')
  }
  if (Number.isInteger(value) || Math.abs(value - Math.round(value)) < 0.001) {
    return Math.round(value).toLocaleString('fr-FR')
  }
  return value.toLocaleString('fr-FR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

/** Filter a time series to a year range */
function filterTimeSeries(pts: TimeSeriesPoint[], startYear: number, endYear: number): TimeSeriesPoint[] {
  return pts.filter((p) => p.year >= startYear && p.year <= endYear)
}

/** Get the value for a specific year from a time series */
function getValueAtYear(pts: TimeSeriesPoint[], year: number): number | undefined {
  const exact = pts.find((p) => p.year === year)
  if (exact) return exact.value
  const sorted = [...pts].sort((a, b) => b.year - a.year)
  const closest = sorted.find((p) => p.year <= year)
  return closest?.value
}

/** Build merged time-series data for the chart */
function buildTimeSeriesData(
  indicators: IndicatorData[],
  startYear: number,
  endYear: number
): Record<string, number>[] {
  if (indicators.length === 0) return []
  const yearMap = new Map<number, Record<string, number>>()
  indicators.forEach((ind) => {
    const filtered = filterTimeSeries(ind.national, startYear, endYear)
    filtered.forEach((pt) => {
      if (!yearMap.has(pt.year)) yearMap.set(pt.year, { year: pt.year })
      yearMap.get(pt.year)![ind.code] = pt.value
    })
  })
  return Array.from(yearMap.entries())
    .sort(([a], [b]) => a - b)
    .map(([, d]) => d)
}

function getVariation(indicator: IndicatorData, endYear: number) {
  const d = filterTimeSeries(indicator.national, MIN_YEAR, endYear)
  if (d.length < 2) return { value: 0, percent: 0, trend: 'stable' as const }
  const last = d[d.length - 1].value
  const prev = d[d.length - 2].value
  const diff = last - prev
  const pct = prev !== 0 ? (diff / Math.abs(prev)) * 100 : 0
  return {
    value: diff,
    percent: pct,
    trend: (diff > 0.001 ? 'up' : diff < -0.001 ? 'down' : 'stable') as
      | 'up'
      | 'down'
      | 'stable',
  }
}

function trendArrow(trend: 'up' | 'down' | 'stable') {
  return trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'
}

function trendColor(trend: 'up' | 'down' | 'stable') {
  return trend === 'up'
    ? 'text-emerald-600'
    : trend === 'down'
      ? 'text-red-500'
      : 'text-amber-500'
}

function TrendIcon({ trend }: { trend: string }) {
  const cls =
    trend === 'up'
      ? 'text-emerald-600'
      : trend === 'down'
        ? 'text-red-500'
        : 'text-amber-500'
  if (trend === 'up')
    return <TrendingUp className={`h-4 w-4 ${cls}`} aria-label="Hausse" />
  if (trend === 'down')
    return <TrendingDown className={`h-4 w-4 ${cls}`} aria-label="Baisse" />
  return <Minus className={`h-4 w-4 ${cls}`} aria-label="Stable" />
}

/** Dynamic color scale based on module color */
function moduleColorScale(value: number, min: number, max: number, baseHue: number, baseSat: number): string {
  if (max === min) return `hsl(${baseHue}, ${baseSat}%, 70%)`
  const t = Math.max(0, Math.min(1, (value - min) / (max - min)))
  const l = 88 - t * 42
  const s = 50 + t * 30
  return `hsl(${baseHue}, ${s}%, ${l}%)`
}

/** Extract HSL hue and saturation from a CSS hsl() string */
function parseHSL(hslStr: string): { h: number; s: number } {
  const m = hslStr.match(/hsl\((\d+),\s*(\d+)%/) || []
  return { h: parseInt(m[1] || '24'), s: parseInt(m[2] || '85') }
}

// ─── Period Selector ────────────────────────────────────────────────────────

function PeriodSelector({
  startYear,
  endYear,
  onStartChange,
  onEndChange,
}: {
  startYear: number
  endYear: number
  onStartChange: (y: number) => void
  onEndChange: (y: number) => void
}) {
  const isSingleYear = startYear === endYear

  return (
    <Card className="border-dashed bg-white dark:bg-slate-800 dark:border-slate-700">
      <CardContent className="flex flex-wrap items-center gap-3 py-3 px-4">
        <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
        <span className="text-sm font-medium text-muted-foreground shrink-0">Période :</span>

        <div className="flex items-center gap-2">
          <Select
            value={String(startYear)}
            onValueChange={(v) => {
              const y = parseInt(v)
              onStartChange(y)
              if (y > endYear) onEndChange(y)
            }}
          >
            <SelectTrigger size="sm" className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="max-h-60">
              {ALL_YEARS.map((y) => (
                <SelectItem key={y} value={String(y)}>
                  {y}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <span className="text-muted-foreground text-sm">→</span>

          <Select
            value={String(endYear)}
            onValueChange={(v) => {
              const y = parseInt(v)
              onEndChange(y)
              if (y < startYear) onStartChange(y)
            }}
          >
            <SelectTrigger size="sm" className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="max-h-60">
              {ALL_YEARS.map((y) => (
                <SelectItem key={y} value={String(y)}>
                  {y}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <button
            onClick={() => { onStartChange(endYear) }}
            className={`text-xs px-2 py-1 rounded border transition-colors ${isSingleYear ? 'bg-emerald-100 text-emerald-700 border-emerald-300 font-semibold' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
          >
            1 an
          </button>
        </div>

        {isSingleYear ? (
          <Badge variant="secondary" className="bg-emerald-50 text-emerald-700 border-emerald-200">
            Année unique : {startYear}
          </Badge>
        ) : (
          <Badge variant="secondary" className="bg-blue-50 text-blue-700 border-blue-200">
            Plage : {startYear}–{endYear} ({endYear - startYear + 1} ans)
          </Badge>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Map Indicator Selector ─────────────────────────────────────────────────

function MapIndicatorSelector({
  indicators,
  selectedIndex,
  onChange,
  color,
  lang,
}: {
  indicators: IndicatorData[]
  selectedIndex: number
  onChange: (i: number) => void
  color: string
  lang?: Lang
}) {
  const regionalIndicators = indicators
    .map((ind, i) => ({ ind, originalIndex: i }))
    .filter(({ ind }) => !ind.isNationalOnly)
  const currentOriginal = regionalIndicators.find((r) => r.originalIndex === selectedIndex)
  return (
    <div className="flex items-center gap-2">
      <Layers className={`h-4 w-4 shrink-0`} style={{ color }} />
      <Select
        value={currentOriginal ? String(currentOriginal.originalIndex) : String(regionalIndicators[0]?.originalIndex ?? 0)}
        onValueChange={(v) => onChange(parseInt(v))}
      >
        <SelectTrigger size="sm" className="w-full max-w-xs">
          <SelectValue placeholder="Indicateur cartographique" />
        </SelectTrigger>
        <SelectContent className="max-h-60">
          {regionalIndicators.map(({ ind, originalIndex }) => (
            <SelectItem key={ind.code} value={String(originalIndex)}>
              {t(ind.label, lang || 'fr')} ({ind.unit})
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

// ─── KPI Card ───────────────────────────────────────────────────────────────

function KPICard({
  kpi,
  index,
  color,
  ModuleIcon,
  onClick,
  lang,
}: {
  kpi: { label: string; value: string | number; unit: string; trend: string; trendLabel: string; description: string; indicator?: IndicatorData }
  index: number
  color: string
  ModuleIcon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>
  onClick?: () => void
  lang?: Lang
}) {
  const trendBg = kpi.trend === 'up'
    ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800'
    : kpi.trend === 'down'
      ? 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800'
      : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800'

  return (
    <motion.div
      key={kpi.label}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      onClick={onClick}
      className={onClick ? 'cursor-pointer' : ''}
    >
      <Card
        className="relative overflow-hidden border-0 shadow-sm hover:shadow-lg transition-shadow duration-300"
        style={{
          background: `linear-gradient(135deg, white 60%, ${color}08 100%)`,
          borderTop: `3px solid ${color}`,
        }}
      >
        {/* Dark mode gradient */}
        <div
          className="absolute inset-0 dark:opacity-100 opacity-0 pointer-events-none"
          style={{ background: `linear-gradient(135deg, hsl(222 47% 11%) 60%, ${color}12 100%)` }}
        />

        <div className="relative p-5">
          {/* Header row */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2.5 min-w-0">
              <div
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-sm"
                style={{ backgroundColor: `${color}18`, border: `1px solid ${color}30` }}
              >
                <ModuleIcon className="h-5 w-5" style={{ color }} />
              </div>
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 leading-tight">
                {t(kpi.label, lang)}
              </span>
            </div>

            {/* Trend badge */}
            <div className={`shrink-0 flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold ${trendBg}`}>
              <TrendIcon trend={kpi.trend} />
              <span>{kpi.trendLabel}</span>
            </div>
          </div>

          {/* Value */}
          <div className="flex items-baseline gap-1.5">
            <span
              className="text-3xl font-extrabold tracking-tight"
              style={{ color }}
            >
              {typeof kpi.value === 'string' ? kpi.value : formatKPIValue(kpi.value, kpi.indicator?.code || '')}
            </span>
            {kpi.unit && (
              <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{kpi.unit}</span>
            )}
          </div>

          {/* Description */}
          <p className="mt-2 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
            {t(kpi.description, lang)}
          </p>

          {/* Clickable hint */}
          {onClick && (
            <div
              className="mt-3 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider opacity-60 hover:opacity-100 transition-opacity"
              style={{ color }}
            >
              <ChevronRight className="h-3 w-3" />
              <span>Détails</span>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  )
}

// ─── Time Series Line Chart ─────────────────────────────────────────────────

function TimeSeriesChart({
  indicators,
  moduleColor,
  startYear,
  endYear,
  lang,
}: {
  indicators: IndicatorData[]
  moduleColor: string
  startYear: number
  endYear: number
  lang?: Lang
}) {
  const firstTwo = indicators.slice(0, 2)
  const data = buildTimeSeriesData(firstTwo, startYear, endYear)

  const config: ChartConfig = {
    [firstTwo[0].code]: {
      label: `${t(firstTwo[0].label, lang || 'fr')} (${firstTwo[0].unit})`,
      color: moduleColor,
    },
  }
  if (firstTwo[1]) {
    config[firstTwo[1].code] = {
      label: `${t(firstTwo[1].label, lang || 'fr')} (${firstTwo[1].unit})`,
      color: CHART_SECONDARY,
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.15 }}
    >
      <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base dark:text-white">
            <Activity className="h-4 w-4" style={{ color: moduleColor }} />
            {t('Suivi des indicateurs dans le temps', lang)}
          </CardTitle>
          <CardDescription>
            {firstTwo.map((i) => t(i.label, lang || 'fr')).join(' / ')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={config}
            className="aspect-auto h-[320px] w-full"
          >
            <LineChart
              data={data}
              margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                className="stroke-border/50"
              />
              <XAxis
                dataKey="year"
                tick={{ fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                label={{
                  value: t('Année', lang),
                  position: 'insideBottom',
                  offset: -2,
                  fontSize: 11,
                  className: 'fill-muted-foreground',
                }}
              />
<YAxis
                tick={{ fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                width={48}
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    labelFormatter={(val) => `Année ${val}`}
                  />
                }
              />
              <ChartLegend content={<ChartLegendContent />} />
              {firstTwo.map((ind) => (
                <Line
                  key={ind.code}
                  type="monotone"
                  dataKey={ind.code}
                  stroke={`var(--color-${ind.code})`}
                  strokeWidth={2}
                  dot={{ r: 3, strokeWidth: 0 }}
                  activeDot={{ r: 5 }}
                  fill={`var(--color-${ind.code})`}
                  fillOpacity={0.08}
                />
              ))}
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </motion.div>
  )
}

// ─── Regional Bar Chart ─────────────────────────────────────────────────────

function RegionalBarChart({
  indicator,
  moduleColor,
  selectedRegion,
  year,
  lang,
}: {
  indicator: IndicatorData
  moduleColor: string
  selectedRegion: string | null
  year: number
  lang?: Lang
}) {
  const currentRegions = useMemo(() => getRegionsForYear(year), [year])
  const data = useMemo(() => {
    const regData = year < 2015 && indicator.regionalOld ? indicator.regionalOld : indicator.regional
    let regional = regData.slice(0, currentRegions.length)
    if (!indicator.regionalIsRate) {
      const totalRegional = regional.reduce((s, r) => s + r.value, 0)
      const nationalVal = getValueAtYear(indicator.national, year)
      if (totalRegional > 0 && nationalVal !== undefined) {
        regional = regional.map(r => ({
          ...r,
          value: Math.round((r.value / totalRegional) * nationalVal * 100) / 100,
        }))
      }
    }
    if (selectedRegion) {
      // Move selected region to top
      regional = [
        ...regional.filter((r) => r.region === selectedRegion),
        ...regional.filter((r) => r.region !== selectedRegion),
      ]
    }
    return regional
  }, [indicator, selectedRegion, year, currentRegions.length])

  const config: ChartConfig = {
    value: {
      label: `${t(indicator.label, lang || 'fr')} (${indicator.unit})`,
      color: moduleColor,
    },
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.25 }}
    >
      <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base dark:text-white">
            <MapPin className="h-4 w-4" style={{ color: moduleColor }} />
            {t('Répartition régionale', lang)}
          </CardTitle>
          <CardDescription className="dark:text-slate-400">{t(indicator.label, lang || 'fr')} — Top {currentRegions.length} {t('régions', lang || 'fr')}</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={config}
            className="aspect-auto h-[320px] w-full"
          >
            <BarChart
              layout="vertical"
              data={data}
              margin={{ left: 10, right: 56, top: 4, bottom: 4 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                horizontal={false}
                className="stroke-border/50"
              />
              <XAxis
                type="number"
                tick={{ fontSize: 10 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="region"
                tick={{ fontSize: 9 }}
                tickLine={false}
                axisLine={false}
                width={110}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar
                dataKey="value"
                radius={[0, 4, 4, 0]}
                label={{
                  position: 'right',
                  fill: '#64748b',
                  fontSize: 10,
                }}
              >
                {data.map((entry, i) => (
                  <Cell
                    key={`cell-${i}`}
                    fill={
                      selectedRegion && entry.region === selectedRegion
                        ? moduleColor
                        : REGIONAL_COLORS[i % REGIONAL_COLORS.length]
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </motion.div>
  )
}

// ─── Indicator Table ────────────────────────────────────────────────────────

function IndicatorTable({ indicators, startYear, endYear, lang, activeDetailIndicator, setActiveDetailIndicator }: { indicators: IndicatorData[]; startYear: number; endYear: number; lang?: Lang; activeDetailIndicator: IndicatorData | null; setActiveDetailIndicator: (ind: IndicatorData | null) => void }) {
  const isRange = startYear !== endYear
  // ── compute displayVal for active detail indicator ──
  let detailDisplayVal = 0
  if (activeDetailIndicator) {
    if (isRange) {
      const pts = filterTimeSeries(activeDetailIndicator.national, startYear, endYear)
      detailDisplayVal = pts.length > 0 ? pts.reduce((s, p) => s + p.value, 0) / pts.length : 0
    } else {
      detailDisplayVal = getValueAtYear(activeDetailIndicator.national, endYear) ?? 0
    }
  }
  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.35 }}
      >
      <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileText className="h-4 w-4 text-muted-foreground" />
            {t('Tableau récapitulatif', lang || 'fr')} — {isRange ? `${t('Moyenne', lang || 'fr')} ${startYear}–${endYear}` : `${t('Année', lang || 'fr')} ${endYear}`}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="max-h-96 overflow-y-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50 hover:bg-muted/50">
                  <TableHead className="sticky top-0 bg-background z-10">
                    Indicateur
                  </TableHead>
                  <TableHead className="sticky top-0 bg-background z-10 text-center">
                    Unité
                  </TableHead>
                  <TableHead className="sticky top-0 bg-background z-10 text-right">
                    {isRange ? `Moyenne (${startYear}–${endYear})` : `Valeur (${endYear})`}
                  </TableHead>
                  <TableHead className="sticky top-0 bg-background z-10 text-right">
                    {t('Variation', lang || 'fr')}
                  </TableHead>
                  <TableHead className="sticky top-0 bg-background z-10 text-center">
                    {t('Tendance', lang || 'fr')}
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {indicators.map((ind, idx) => {
                  let displayVal: number
                  let v: ReturnType<typeof getVariation>
                  if (isRange) {
                    const pts = filterTimeSeries(ind.national, startYear, endYear)
                    displayVal = pts.length > 0 ? pts.reduce((s, p) => s + p.value, 0) / pts.length : 0
                    v = { value: 0, percent: 0, trend: 'stable' as const }
                    if (pts.length >= 2) {
                      const first = pts[0].value
                      const last = pts[pts.length - 1].value
                      const diff = last - first
                      v = { value: diff, percent: first !== 0 ? (diff / Math.abs(first)) * 100 : 0, trend: (diff > 0.001 ? 'up' : diff < -0.001 ? 'down' : 'stable') as const }
                    }
                  } else {
                    displayVal = getValueAtYear(ind.national, endYear) ?? 0
                    v = getVariation(ind, endYear)
                  }
                  return (
                    <TableRow
                      key={ind.code}
                      className={`cursor-pointer transition-colors hover:bg-accent/50 ${idx % 2 === 0 ? 'bg-background' : 'bg-muted/30'} ${activeDetailIndicator?.code === ind.code ? 'ring-2 ring-inset ring-primary/30 bg-accent/20' : ''}`}
                      onClick={() => setActiveDetailIndicator(activeDetailIndicator?.code === ind.code ? null : ind)}
                    >
                      <TableCell className="font-medium">
                        <span>{t(ind.label, lang || 'fr')}</span>
                        {ind.source && (
                          <span className="block text-[9px] text-muted-foreground font-normal leading-tight mt-0.5">{ind.source}</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center text-muted-foreground">
                        {ind.unit || '—'}
                      </TableCell>
                       <TableCell className="text-right font-mono tabular-nums">
                         {formatTableValue(displayVal, ind.code)}
                       </TableCell>
                       <TableCell
                         className={`text-right font-mono tabular-nums ${
                           v.value > 0.001
                             ? 'text-emerald-600'
                             : v.value < -0.001
                               ? 'text-red-500'
                               : 'text-amber-500'
                         }`}
                       >
                         {v.value > 0 ? '+' : ''}
                         {formatTableValue(v.value, ind.code)}
                      </TableCell>
                      <TableCell className="text-center">
                        <span
                          className={`inline-flex items-center gap-1 text-sm font-medium ${trendColor(v.trend)}`}
                        >
                          {trendArrow(v.trend)}
                        </span>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </motion.div>
    {activeDetailIndicator && (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        className="mt-4"
      >
        <Card className="border-2 border-primary/20 bg-card">
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              {t(activeDetailIndicator.label, lang || 'fr')} —{' '}
              <span className="font-mono font-bold text-primary">{formatTableValue(detailDisplayVal, activeDetailIndicator.code)}</span>
              {activeDetailIndicator.unit && <span className="text-xs text-muted-foreground font-normal">{activeDetailIndicator.unit}</span>}
            </CardTitle>
            {activeDetailIndicator.source && (
              <p className="text-[9px] text-muted-foreground mt-0.5">{activeDetailIndicator.source}</p>
            )}
            <button onClick={() => setActiveDetailIndicator(null)} className="h-6 w-6 rounded-full hover:bg-muted flex items-center justify-center">
              <X className="h-3.5 w-3.5" />
            </button>
          </CardHeader>
          <CardContent className="pt-0">
            <IndicatorDetail ind={activeDetailIndicator} startYear={startYear} endYear={endYear} lang={lang} />
          </CardContent>
        </Card>
      </motion.div>
    )}
  </>
  )
}

function IndicatorDetail({ ind, startYear, endYear, lang }: { ind: IndicatorData; startYear: number; endYear: number; lang?: Lang }) {
  const [selectedClubRegion, setSelectedClubRegion] = useState<string | null>(null)
  const clubsInRegion = selectedClubRegion ? FOOTBALL_CLUBS.filter(c => c.region === selectedClubRegion) : []
  const regionCFTA = selectedClubRegion ? clubsInRegion.reduce((s, c) => s + c.totalCAFTitles, 0) : 0

  if (ind.code === 'BOTOLA_PRO_CLUBS' || ind.code === 'NB_CLUBS') {
    const data = FOOTBALL_CLUBS
    const regionColors: Record<string, string> = {
      "Casablanca-Settat": "#C1272D", "Rabat-Salé-Kénitra": "#000080", "Fès-Meknès": "#0000CD",
      "Tanger-Tétouan-Al Hoceima": "#FF4500", "Oriental": "#DAA520", "Marrakech-Safi": "#006400",
      "Souss-Massa": "#FF6347", "Béni Mellal-Khénifra": "#800080", "Drâa-Tafilalet": "#A0522D",
      "Laâyoune-Sakia El Hamra": "#4B0082", "Dakhla-Oued Ed-Dahab": "#00CED1", "Guelmim-Oued Noun": "#B8860B",
    }
    return (
      <div className="space-y-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="p-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {Object.entries(regionColors).map(([region, color]) => {
              const clubs = data.filter(c => c.region === region)
              if (clubs.length === 0) return null
              const b1 = clubs.filter(c => c.division === 'Botola 1').length
              const b2 = clubs.filter(c => c.division === 'Botola 2').length
              const isActive = selectedClubRegion === region
              return (
                <button key={region} onClick={() => setSelectedClubRegion(isActive ? null : region)}
                  className={`text-left rounded-lg p-3 border-2 transition-all ${isActive ? 'shadow-lg scale-[1.02]' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'}`}
                  style={{ borderColor: isActive ? color : undefined, backgroundColor: isActive ? `${color}10` : undefined }}>
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: color }} />
                    <span className="text-[11px] font-bold text-slate-900 dark:text-white truncate">{region}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400">
                    {b1 > 0 && <span className="font-semibold text-emerald-600 dark:text-emerald-400">{b1} B1</span>}
                    {b1 > 0 && b2 > 0 && <span> · </span>}
                    {b2 > 0 && <span className="font-semibold text-blue-600 dark:text-blue-400">{b2} B2</span>}
                  </div>
                </button>
              )
            })}
          </div>
        </div>
        {selectedClubRegion && (
          <div className="bg-white dark:bg-slate-800 rounded-xl border-2 overflow-hidden" style={{ borderColor: regionColors[selectedClubRegion] || '#64748b' }}>
            <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
              <div className="w-4 h-4 rounded-full shrink-0" style={{ backgroundColor: regionColors[selectedClubRegion] }} />
              <div>
                <h4 className="text-base font-bold text-slate-900 dark:text-white">{selectedClubRegion}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">{clubsInRegion.length} clubs</p>
              </div>
            </div>
            <div className="p-4 space-y-3">
              {clubsInRegion.sort((a, b) => (a.division === 'Botola 1' ? -1 : 1) - (b.division === 'Botola 1' ? -1 : 1)).map((club, i) => (
                <div key={i} className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
                  <div className="flex items-start gap-3 p-3 bg-gradient-to-r from-slate-50 to-white dark:from-slate-800/50 dark:to-slate-900/50">
                    <img src={club.logo} alt={club.name} className="w-14 h-14 rounded-lg object-contain bg-white dark:bg-slate-700 p-0.5 border shrink-0" style={{ borderColor: club.color }}
                      onError={(e) => {
                        const img = e.target as HTMLImageElement
                        if (!img.dataset.fallback) {
                          img.dataset.fallback = '1'
                          img.src = `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56"><rect width="56" height="56" fill="${club.color}" rx="8"/><text x="50%" y="55%" dominantBaseline="middle" textAnchor="middle" fill="#fff" font-size="14" font-weight="bold">${club.acronym}</text></svg>`)}`
                        }
                      }} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="font-bold text-sm text-slate-900 dark:text-white">{club.name}</span>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full" style={{ backgroundColor: `${club.color}20`, color: club.color }}>{club.acronym}</span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${club.division === 'Botola 1' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'}`}>{club.division}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{club.city} · {club.stadium} · Fondé {club.founded}</div>
                      <div className="flex gap-3 mt-1 text-[10px]">
                        {club.botolaTitles > 0 && <span className="font-semibold text-amber-600 dark:text-amber-400">{club.botolaTitles}x Botola</span>}
                        {club.totalCAFTitles > 0 && <span className="font-semibold" style={{ color: club.color }}>{club.totalCAFTitles}x CAF CL</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return <p className="text-xs text-muted-foreground py-2">Données détaillées non disponibles pour cet indicateur.</p>
}

// ─── Module Content ─────────────────────────────────────────────────────────

function ModuleContent({
  module,
  startYear,
  endYear,
  selectedRegion,
  setSelectedRegion,
  mapIndicatorIndex,
  setMapIndicatorIndex,
  onKPIClick,
  lang,
  activeDetailIndicator,
  setActiveDetailIndicator,
}: {
  module: ModuleData
  startYear: number
  endYear: number
  selectedRegion: string | null
  setSelectedRegion: (r: string | null) => void
  mapIndicatorIndex: number
  setMapIndicatorIndex: (i: number) => void
  onKPIClick: (kpi: { label: string; unit: string; indicator: IndicatorData }) => void
  lang?: Lang
  activeDetailIndicator: IndicatorData | null
  setActiveDetailIndicator: (ind: IndicatorData | null) => void
}) {
  const color = MODULE_COLORS[module.name] || 'hsl(24, 85%, 53%)'
  const ModuleIcon = ICON_MAP[MODULE_ICONS[module.name]] || BarChart3
  const { h, s } = parseHSL(color)

  // Build KPIs: single year = that year value; range = sum for counts, average for rates
  const COUNT_UNITS = ['millions', 'milliards', 'Mds MAD', 'MAD/mois', 'nuitées', 'emplois', 'passagers', 'chambres', 'milliers', 'habitants']
  const RANK_UNITS = ['e place']
  const periodKPIs = useMemo(() => {
    const RATE_UNITS = ['%', '% PIB', '‰']
    return module.kpis.map((kpi) => {
      // Fix: when indicatorCode is provided, use ONLY exact match.
      // The old fuzzy fallback was causing all "Taux de scolarisation" KPIs
      // to resolve to SCOLARISATION_PRIMAIRE (the first matching indicator).
      const kpiCode = (kpi as any).indicatorCode as string | undefined
      const matchingIndicator = kpiCode
        ? module.indicators.find(ind => ind.code === kpiCode)
        : module.indicators.find((ind) => {
            const kpiLower = kpi.label.toLowerCase()
            const indLabelLower = ind.label.toLowerCase()
            if (indLabelLower.includes(kpiLower.slice(0, 15))) return true
            const acronym = kpiLower.match(/^[\w\s]+/)?.[0]?.trim().split(/\s+/)[0] || ''
            if (acronym && ind.code.toLowerCase() === acronym) return true
            if (acronym && indLabelLower.startsWith(acronym)) return true
            return false
          })
      let displayValue: string | number = kpi.value
      let displayTrend = kpi.trend
      let displayTrendLabel = kpi.trendLabel
      if (matchingIndicator) {
        if (startYear === endYear) {
          const val = getValueAtYear(matchingIndicator.national, endYear)
          if (val !== undefined) {
            const isInt = INTEGER_KPI_CODES.has(matchingIndicator.code)
            displayValue = isInt ? Math.round(val) : Math.round(val * 100) / 100
          }
          const v = getVariation(matchingIndicator, endYear)
          displayTrend = v.trend
          const sign = v.value >= 0 ? '+' : ''
          displayTrendLabel = `${sign}${formatValue(v.value)}`
        } else {
          const isRank = RANK_UNITS.some(u => kpi.unit.includes(u))
          const isRate = RATE_UNITS.some(u => kpi.unit.includes(u))
          const isInt = INTEGER_KPI_CODES.has(matchingIndicator.code)
          if (isRank) {
            const firstVal = getValueAtYear(matchingIndicator.national, startYear)
            const lastVal = getValueAtYear(matchingIndicator.national, endYear)
            if (firstVal !== undefined && lastVal !== undefined) {
              displayValue = `${Math.round(firstVal)} → ${Math.round(lastVal)}`
              const diff = lastVal - firstVal
              displayTrend = diff > 0.001 ? 'down' : diff < -0.001 ? 'up' : 'stable'
              displayTrendLabel = `${Math.round(firstVal)} → ${Math.round(lastVal)}`
            }
          } else {
            const pts = filterTimeSeries(matchingIndicator.national, startYear, endYear)
            if (pts.length > 0) {
              const firstVal = pts[0].value
              const lastVal = pts[pts.length - 1].value
              const diff = lastVal - firstVal
              displayTrend = diff > 0.001 ? 'up' : diff < -0.001 ? 'down' : 'stable'
              if (isRate) {
                const avg = pts.reduce((s, p) => s + p.value, 0) / pts.length
                displayValue = Math.round(avg * 100) / 100
                displayTrendLabel = `Moy. ${formatValue(avg)}`
              } else {
                displayValue = isInt ? Math.round(lastVal) : Math.round(lastVal * 100) / 100
                displayTrendLabel = isInt ? `${Math.round(firstVal)} → ${Math.round(lastVal)}` : `${formatValue(firstVal)} → ${formatValue(lastVal)}`
              }
            }
          }
        }
      }
      return {
        label: kpi.label,
        value: displayValue,
        unit: kpi.unit,
        trend: displayTrend,
        trendLabel: displayTrendLabel,
        description: kpi.description,
        indicator: matchingIndicator || undefined,
      }
    })
  }, [module, startYear, endYear])

  // Map data from selected indicator
  const mapIndicator = module.indicators[mapIndicatorIndex] || module.indicators[0]
  const mapRegionValues = useMemo(() => {
    if (!mapIndicator) return {}
    const regData = endYear < 2015 && mapIndicator.regionalOld ? mapIndicator.regionalOld : mapIndicator.regional
    if (mapIndicator.regionalIsRate) {
      return Object.fromEntries(regData.map((r) => [r.region, r.value]))
    }
    const totalRegional = regData.reduce((s, r) => s + r.value, 0)
    const nationalVal = getValueAtYear(mapIndicator.national, endYear)
    if (totalRegional > 0 && nationalVal !== undefined) {
      return Object.fromEntries(
        regData.map((r) => [r.region, Math.round((r.value / totalRegional) * nationalVal * 100) / 100])
      )
    }
    return Object.fromEntries(
      regData.map((r) => [r.region, r.value])
    )
  }, [mapIndicator, endYear])

  const mapColorScale = useCallback(
    (value: number, min: number, max: number) =>
      moduleColorScale(value, min, max, h, s),
    [h, s]
  )

  return (
    <div className="space-y-8">
      {/* Module Description */}
      <div className="flex items-center gap-3">
        <div
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl"
          style={{ backgroundColor: `${color}15` }}
        >
          <ModuleIcon className="h-5 w-5" style={{ color }} />
        </div>
        <div>
          <h2 className="text-lg font-semibold dark:text-white">{tModule(module.name, lang || 'fr')}</h2>
          <p className="text-sm text-muted-foreground">{t(module.description, lang)}</p>
        </div>
      </div>

      {/* KPI Cards */}
      <section aria-label="Indicateurs clés">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {periodKPIs.map((kpi, i) => (
            <KPICard
              key={kpi.label}
              kpi={kpi}
              index={i}
              color={color}
              ModuleIcon={ModuleIcon}
              onClick={kpi.indicator ? () => onKPIClick({ label: kpi.label, unit: kpi.unit, indicator: kpi.indicator! }) : undefined}
              lang={lang}
            />
          ))}
        </div>
      </section>

      {/* Charts */}
      <section aria-label="Graphiques">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {module.indicators.length >= 2 && (
            <TimeSeriesChart
              indicators={module.indicators}
              moduleColor={color}
              startYear={startYear}
              endYear={endYear}
              lang={lang}
            />
          )}
          {module.indicators.length >= 1 && (
            <RegionalBarChart
              indicator={module.indicators[0]}
              moduleColor={color}
              selectedRegion={selectedRegion}
              year={endYear}
              lang={lang}
            />
          )}
        </div>
      </section>

      {/* Data Table */}
      <section aria-label="Tableau de données">
        <IndicatorTable indicators={module.indicators} startYear={startYear} endYear={endYear} lang={lang} activeDetailIndicator={activeDetailIndicator} setActiveDetailIndicator={setActiveDetailIndicator} />
      </section>

      {/* Interactive Map + Region Detail */}
      <section aria-label="Carte régionale interactive" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-3">
          {/* Indicator selector for map */}
          <MapIndicatorSelector
            indicators={module.indicators}
            selectedIndex={mapIndicatorIndex}
            onChange={setMapIndicatorIndex}
            color={color}
            lang={lang}
          />
          <MoroccoMap
            selectedRegion={selectedRegion}
            onRegionClick={setSelectedRegion}
            colorScale={mapColorScale}
            regionValues={mapRegionValues}
            unit={mapIndicator?.unit || ''}
          />
        </div>
        <div className="lg:col-span-2 space-y-6">
          {/* ONG summary card (always shown) */}
          <Card className="border-l-4 border-l-emerald-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <UsersRound className="h-4 w-4 text-emerald-600" />
                {t('Tissu Associatif', lang)}
              </CardTitle>
              <CardDescription>{t('Associations et ONG par région', lang)}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">
                  {(TOTAL_ASSOCIATIONS / 1000).toFixed(0)}K
                </span>
                <span className="text-sm text-muted-foreground">{t('associations au total', lang)}</span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                {t('dont 257 reconnues d\'utilité publique', lang)}
              </p>
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-md bg-emerald-50 dark:bg-emerald-950/30 px-2 py-1.5">
                  <p className="text-xs text-muted-foreground">{t('Max/région', lang)}</p>
                  <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                    {Math.max(...REGION_DETAILS.map((r) => r.ongCount)).toLocaleString('fr-FR')}
                  </p>
                </div>
                <div className="rounded-md bg-emerald-50 dark:bg-emerald-950/30 px-2 py-1.5">
                  <p className="text-xs text-muted-foreground">{t('Moy/région', lang)}</p>
                  <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                    {Math.round(
                      REGION_DETAILS.reduce((a, r) => a + r.ongCount, 0) / REGION_DETAILS.length
                    ).toLocaleString('fr-FR')}
                  </p>
                </div>
                <div className="rounded-md bg-emerald-50 dark:bg-emerald-950/30 px-2 py-1.5">
                  <p className="text-xs text-muted-foreground">{t('Min/région', lang)}</p>
                  <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
                    {Math.min(...REGION_DETAILS.map((r) => r.ongCount)).toLocaleString('fr-FR')}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Selected region detail — shows data from the ACTIVE module */}
          {selectedRegion
            ? (() => {
                const rd = REGION_DETAILS.find((r) => r.name === selectedRegion)
                if (!rd) return null
                // Get the selected indicator's value for this region
                const regData = endYear < 2015 && mapIndicator?.regionalOld ? mapIndicator.regionalOld : mapIndicator?.regional || []
                const regionIndicatorValue = regData.find(
                  (r) => r.region === selectedRegion
                )
                return (
                  <Card
                    className="border-l-4"
                    style={{ borderLeftColor: color }}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center gap-2">
                        <MapPinned className="h-4 w-4" style={{ color }} />
                        {rd.name}
                      </CardTitle>
                      <CardDescription className="text-xs">
                        {mapIndicator?.label} ({endYear}) : {(() => {
                          if (!mapIndicator) return '—'
                          if (mapIndicator.isNationalOnly) return `${formatValue(getValueAtYear(mapIndicator.national, endYear) ?? 0, mapIndicator.code)} ${mapIndicator.unit} — National`
                          const regArr = endYear < 2015 && mapIndicator.regionalOld ? mapIndicator.regionalOld : mapIndicator.regional
                          const rv = regArr.find((r) => r.region === selectedRegion)
                          if (!rv) return '—'
                          if (mapIndicator.regionalIsRate) return `${formatValue(rv.value, mapIndicator.code)} ${mapIndicator.unit}`
                          const totalRegional = regArr.reduce((s, r) => s + r.value, 0)
                          const share = totalRegional > 0 ? rv.value / totalRegional : 0
                          const nationalVal = getValueAtYear(mapIndicator.national, endYear)
                          return nationalVal !== undefined ? `${formatValue(share * nationalVal, mapIndicator.code)} ${mapIndicator.unit}` : '—'
                        })()}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground">Population (2024)</p>
                          <p className="text-sm font-semibold">{rd.population2024.toLocaleString('fr-FR')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Superficie</p>
                          <p className="text-sm font-semibold">{rd.superficie.toLocaleString('fr-FR')} km²</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Provinces / Préfectures</p>
                          <p className="text-sm font-semibold">{rd.provinceCount}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {rd.provinces.slice(0, 3).join(', ')}
                            {rd.provinces.length > 3 ? '...' : ''}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Associations / ONG</p>
                          <p className="text-sm font-semibold">{rd.ongCount.toLocaleString('fr-FR')}</p>
                          <p className="text-xs text-muted-foreground mt-1">{rd.ongPer100k} pour 100k hab.</p>
                        </div>
                      </div>

                      {/* All indicators values for this region — year-aware */}
                      <div className="mt-4 space-y-2">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                          Tous les indicateurs — {rd.name}
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {module.indicators.map((ind) => {
                            const nationalVal = getValueAtYear(ind.national, endYear)
                            if (ind.isNationalOnly) {
                              return (
                                <div
                                  key={ind.code}
                                  className="rounded-md border px-3 py-2 bg-slate-50 dark:bg-slate-800/50 border-dashed"
                                >
                                  <p className="text-[10px] text-muted-foreground">{t(ind.label, lang || 'fr')}</p>
                                  <p className="text-sm font-semibold">
                                    {nationalVal !== undefined ? formatValue(nationalVal, ind.code) : '—'}{' '}
                                    <span className="text-xs font-normal text-muted-foreground">{ind.unit}</span>
                                  </p>
                                  <p className="text-[9px] text-muted-foreground italic mt-0.5">Indicateur national</p>
                                  {ind.source && (
                                    <p className="text-[8px] text-muted-foreground/70 mt-0.5 truncate">{ind.source}</p>
                                  )}
                                </div>
                              )
                            }
                            const regArr = endYear < 2015 && ind.regionalOld ? ind.regionalOld : ind.regional
                            const rv = regArr.find((r) => r.region === selectedRegion)
                            if (!rv) return null
                            let yearValue: number | null
                            if (ind.regionalIsRate) {
                              yearValue = rv.value
                            } else {
                              const totalRegional = regArr.reduce((s, r) => s + r.value, 0)
                              const share = totalRegional > 0 ? rv.value / totalRegional : 0
                              yearValue = nationalVal !== undefined ? share * nationalVal : null
                            }
                            return (
                              <div
                                key={ind.code}
                                className="rounded-md border px-3 py-2"
                              >
                                <p className="text-[10px] text-muted-foreground">{t(ind.label, lang || 'fr')}</p>
                                <p className="text-sm font-semibold">
                                  {yearValue !== null ? formatValue(yearValue, ind.code) : '—'}{' '}
                                  <span className="text-xs font-normal text-muted-foreground">{ind.unit}</span>
                                </p>
                                {ind.source && (
                                  <p className="text-[8px] text-muted-foreground/70 mt-0.5 truncate">{ind.source}</p>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })()
            : (
              <p className="text-sm text-muted-foreground text-center py-12">
                Cliquez sur une région de la carte pour afficher ses détails
              </p>
            )}
        </div>
      </section>

      {/* Recommendations */}
      {(() => {
        const recs = RECOMMENDATIONS[module.name]
        if (!recs || recs.length === 0) return null
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" style={{ color }} />
                  Recommandations d&rsquo;interprétation
                </CardTitle>
                <CardDescription>
                  {t('Analyse et axes d\'action prioritaires pour le module', lang)} {tModule(module.name, lang)}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {recs.map((rec: ModuleRecommendation, i: number) => (
                  <div
                    key={i}
                    className="rounded-lg border p-4"
                    style={{
                      borderColor:
                        rec.priority === 'haute'
                          ? 'hsl(0, 84%, 60%, 0.3)'
                          : rec.priority === 'moyenne'
                            ? 'hsl(24, 85%, 53%, 0.3)'
                            : 'hsl(142, 71%, 45%, 0.3)',
                    }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <h4 className="text-sm font-semibold">{t(rec.title, lang)}</h4>
                        <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{t(rec.description, lang)}</p>
                      </div>
                      <Badge
                        className={
                          'shrink-0 ' +
                          (rec.priority === 'haute'
                            ? 'bg-red-100 text-red-700 border-red-200'
                            : rec.priority === 'moyenne'
                              ? 'bg-orange-100 text-orange-700 border-orange-200'
                              : 'bg-emerald-100 text-emerald-700 border-emerald-200')
                        }
                        variant="outline"
                      >
                        {rec.priority === 'haute' ? t('Haute', lang) : rec.priority === 'moyenne' ? t('Moyenne', lang) : t('Basse', lang)}
                      </Badge>
                    </div>
                    <ul className="mt-3 space-y-1.5">
                      {rec.actions.map((action: string, j: number) => (
                          <li key={j} className="flex items-start gap-2 text-xs text-muted-foreground">
                            <ChevronRight className="mt-0.5 h-3 w-3 shrink-0" style={{ color }} />
                            <span>{t(action, lang)}</span>
                          </li>
                        ))}
                    </ul>
                  </div>
                ))}
              </CardContent>
            </Card>
    </motion.div>
  )
      })()}
    </div>
  )
}

// ─── KPI Detail Sub-KPIs ──────────────────────────────────────────────────
function KPIDetailSubKPIs({ indicator, unit, startYear, endYear, lang }: { indicator: IndicatorData; unit: string; startYear: number; endYear: number; lang?: Lang }) {
  const pts = indicator.national.filter((p) => p.year >= startYear && p.year <= endYear)
  if (pts.length === 0) return null
  const vals = pts.map((p) => p.value)
  const current = vals[vals.length - 1]
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  const avg = vals.reduce((s, v) => s + v, 0) / vals.length
  const minYear = pts.find((p) => p.value === min)?.year
  const maxYear = pts.find((p) => p.value === max)?.year
  const first = vals[0]
  const change = current - first
  const changePct = first !== 0 ? (change / Math.abs(first)) * 100 : 0

  const boxes = [
    { label: t('Valeur actuelle', lang || 'fr'), value: formatKPIValue(current, indicator.code), sub: `${endYear}`, color: '#3b82f6', bg: 'bg-blue-50 dark:bg-blue-950/40', textColor: 'text-blue-600 dark:text-blue-400' },
    { label: t('Minimum', lang || 'fr'), value: formatKPIValue(min, indicator.code), sub: `${minYear}`, color: '#ef4444', bg: 'bg-red-50 dark:bg-red-950/40', textColor: 'text-red-600 dark:text-red-400' },
    { label: t('Maximum', lang || 'fr'), value: formatKPIValue(max, indicator.code), sub: `${maxYear}`, color: '#22c55e', bg: 'bg-emerald-50 dark:bg-emerald-950/40', textColor: 'text-emerald-600 dark:text-emerald-400' },
    { label: t('Moyenne', lang || 'fr'), value: formatKPIValue(avg, indicator.code), sub: `${startYear}–${endYear}`, color: '#a855f7', bg: 'bg-purple-50 dark:bg-purple-950/40', textColor: 'text-purple-600 dark:text-purple-400' },
    { label: t('Variation totale', lang || 'fr'), value: `${change >= 0 ? '+' : ''}${formatKPIValue(change, indicator.code)}`, sub: `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}%`, color: change >= 0 ? '#22c55e' : '#ef4444', bg: change >= 0 ? 'bg-emerald-50 dark:bg-emerald-950/40' : 'bg-red-50 dark:bg-red-950/40', textColor: change >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400' },
    { label: t('Observations', lang || 'fr'), value: `${pts.length}`, sub: t('ans', lang || 'fr'), color: '#64748b', bg: 'bg-slate-50 dark:bg-slate-800', textColor: 'text-slate-600 dark:text-slate-400' },
  ]


  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {boxes.map((b) => (
        <div key={b.label} className={`rounded-xl border border-slate-200 dark:border-slate-700 ${b.bg} p-4 text-center`}>
          <p className="text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">{b.label}</p>
          <p className={`text-2xl font-bold mt-1 ${b.textColor}`}>{b.value}</p>
          {b.sub && <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{b.sub}</p>}
        </div>
      ))}
    </div>
  )
}

// ─── CAF Champions League Detail (interactive: click region → see clubs) ────
function CAFCLDetail({ lang }: { lang?: Lang }) {
  const [selectedClubRegion, setSelectedClubRegion] = useState<string | null>(null)
  const clubsInRegion = selectedClubRegion ? FOOTBALL_CLUBS.filter(c => c.region === selectedClubRegion) : []
  const regionCFTA = selectedClubRegion ? clubsInRegion.reduce((s, c) => s + c.totalCAFTitles, 0) : 0
  const regionColors: Record<string, string> = {
    "Casablanca-Settat": "#C1272D", "Rabat-Salé-Kénitra": "#000080", "Fès-Meknès": "#0000CD",
    "Tanger-Tétouan-Al Hoceima": "#FF4500", "Oriental": "#DAA520", "Marrakech-Safi": "#006400",
    "Souss-Massa": "#FF6347", "Béni Mellal-Khénifra": "#800080", "Drâa-Tafilalet": "#A0522D",
    "Laâyoune-Sakia El Hamra": "#4B0082", "Dakhla-Oued Ed-Dahab": "#00CED1", "Guelmim-Oued Noun": "#B8860B",
  }
  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">Clubs Botola 1 & 2 par région</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Cliquez sur une région pour voir les clubs, logos et palmarès</p>
        </div>
        <div className="p-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {Object.entries(regionColors).map(([region, color]) => {
            const clubs = FOOTBALL_CLUBS.filter(c => c.region === region)
            if (clubs.length === 0) return null
            const b1 = clubs.filter(c => c.division === 'Botola 1').length
            const b2 = clubs.filter(c => c.division === 'Botola 2').length
            const cft = clubs.reduce((s, c) => s + c.totalCAFTitles, 0)
            const isActive = selectedClubRegion === region
            return (
              <button key={region} onClick={() => setSelectedClubRegion(isActive ? null : region)}
                className={`text-left rounded-lg p-3 border-2 transition-all ${isActive ? 'shadow-lg scale-[1.02]' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'}`}
                style={{ borderColor: isActive ? color : undefined, backgroundColor: isActive ? `${color}10` : undefined }}>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: color }} />
                  <span className="text-[11px] font-bold text-slate-900 dark:text-white truncate">{region}</span>
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400">
                  {b1 > 0 && <span className="font-semibold text-emerald-600 dark:text-emerald-400">{b1} B1</span>}
                  {b1 > 0 && b2 > 0 && <span> · </span>}
                  {b2 > 0 && <span className="font-semibold text-blue-600 dark:text-blue-400">{b2} B2</span>}
                </div>
                {cft > 0 && <div className="text-[10px] font-bold mt-1" style={{ color }}>{cft} titre{cft > 1 ? 's' : ''} CAF</div>}
              </button>
            )
          })}
        </div>
      </div>
      {selectedClubRegion && (
        <div className="bg-white dark:bg-slate-800 rounded-xl border-2 overflow-hidden" style={{ borderColor: regionColors[selectedClubRegion] || '#64748b' }}>
          <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
            <div className="w-4 h-4 rounded-full shrink-0" style={{ backgroundColor: regionColors[selectedClubRegion] }} />
            <div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white">{selectedClubRegion}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">{clubsInRegion.length} clubs · {regionCFTA} titre{regionCFTA !== 1 ? 's' : ''} CAF Champions League</p>
            </div>
          </div>
          <div className="p-4 space-y-3">
            {clubsInRegion.sort((a, b) => b.totalCAFTitles - a.totalCAFTitles || (a.division === 'Botola 1' ? -1 : 1)).map((club, i) => (
              <div key={i} className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3 p-3 bg-gradient-to-r from-slate-50 to-white dark:from-slate-800/50 dark:to-slate-900/50">
                  <img src={club.logo} alt={club.name} className="w-14 h-14 rounded-lg object-contain bg-white dark:bg-slate-700 p-0.5 border shrink-0" style={{ borderColor: club.color }}
                    onError={(e) => {
                      const img = e.target as HTMLImageElement
                      if (!img.dataset.fallback) {
                        img.dataset.fallback = '1'
                        img.src = `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="56" height="56"><rect width="56" height="56" fill="${club.color}" rx="8"/><text x="50%" y="55%" dominantBaseline="middle" textAnchor="middle" fill="#fff" font-size="14" font-weight="bold">${club.acronym}</text></svg>`)}`
                      }
                    }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="font-bold text-sm text-slate-900 dark:text-white">{club.name}</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full" style={{ backgroundColor: `${club.color}20`, color: club.color }}>{club.acronym}</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${club.division === 'Botola 1' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'}`}>{club.division}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">{club.city} · {club.stadium} · Fondé {club.founded}</div>
                    <div className="flex gap-3 mt-1 text-[10px]">
                      {club.botolaTitles > 0 && <span className="font-semibold text-amber-600 dark:text-amber-400">{club.botolaTitles}x Botola</span>}
                      {club.totalCAFTitles > 0 && <span className="font-semibold" style={{ color: club.color }}>{club.totalCAFTitles}x CAF CL</span>}
                    </div>
                  </div>
                </div>
                {club.cafTitles.length > 0 && (
                  <div className="px-3 pb-3">
                    <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Palmarès CAF</p>
                    <div className="space-y-1">
                      {club.cafTitles.sort((a, b) => b.year - a.year).map((t, j) => (
                        <div key={j} className="flex items-center gap-2 text-xs bg-slate-50 dark:bg-slate-800 rounded-lg px-2 py-1.5">
                          <span className="font-mono font-bold shrink-0 w-8" style={{ color: club.color }}>{t.year}</span>
                          <span className="text-slate-700 dark:text-slate-300 flex-1 truncate">vs <strong>{t.opponent}</strong></span>
                          <span className="font-mono text-[10px] text-slate-400">{t.score}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── KPI Detail Charts ────────────────────────────────────────────────────
function KPIDetailCharts({ indicator, label, unit, startYear, endYear, lang }: { indicator: IndicatorData; label: string; unit: string; startYear: number; endYear: number; lang?: Lang }) {
  const [activeChart, setActiveChart] = useState<string>('line')
  const allPts = indicator.national
  const filteredPts = allPts.filter((p) => p.year >= startYear && p.year <= endYear)
  const reg = endYear < 15 && indicator.regionalOld ? indicator.regionalOld : indicator.regional
  const regData = reg.map((r) => ({ name: r.region.length > 18 ? r.region.slice(0, 16) + '…' : r.region, fullName: r.region, value: r.value }))

  const COLORS = ['#f97316', '#22c55e', '#3b82f6', '#a855f7', '#ef4444', '#eab308', '#06b6d4', '#ec4899', '#14b8a6', '#8b5cf6', '#f43f5e', '#84cc16', '#0ea5e9', '#d946ef', '#f59e0b', '#6366f1']
  const avg = filteredPts.length > 0 ? filteredPts.reduce((s, p) => s + p.value, 0) / filteredPts.length : 0

  const tabs = [
    { key: 'line', label: t('Courbes', lang) },
    { key: 'area', label: t('Aires', lang) },
    { key: 'bar', label: t('Barres', lang) },
    { key: 'composed', label: t('Composé', lang) },
    ...(regData.length > 0 ? [
      { key: 'pie', label: t('Camembert', lang) },
      { key: 'donut', label: t('Anneau', lang) },
      { key: 'treemap', label: 'Treemap' },
    ] : []),
    { key: 'scatter', label: t('Points', lang) },
  ]

  return (
    <div className="space-y-4">
      <div className="flex gap-1 overflow-x-auto pb-1">
        {tabs.map((tr) => (
          <button key={tr.key} onClick={() => setActiveChart(tr.key)} className={`shrink-0 px-4 py-2 text-sm font-medium rounded-lg transition-all ${activeChart === tr.key ? 'bg-primary text-white shadow-md' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'}`}>{tr.label}</button>
        ))}
      </div>

      <Card className="overflow-hidden bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
        <CardContent className="p-4">
          {activeChart === 'line' && (
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={allPts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <ReferenceLine y={avg} stroke="#a855f7" strokeDasharray="5 5" label={{ value: `Moy: ${formatKPIValue(avg, indicator.code)}`, position: 'right', fill: '#a855f7', fontSize: 11 }} />
                <Line type="monotone" dataKey="value" stroke="#f97316" strokeWidth={2.5} dot={{ r: 3, fill: '#f97316' }} activeDot={{ r: 6, stroke: '#fff', strokeWidth: 2 }} name={label} />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'area' && (
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={allPts}>
                <defs><linearGradient id="gradArea" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#f97316" stopOpacity={0.3} /><stop offset="95%" stopColor="#f97316" stopOpacity={0.02} /></linearGradient></defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <Area type="monotone" dataKey="value" stroke="#f97316" fill="url(#gradArea)" strokeWidth={2} name={label} />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'bar' && (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={allPts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <Bar dataKey="value" name={label} radius={[4, 4, 0, 0]}>
                  {allPts.map((entry, i) => (<Cell key={i} fill={entry.year >= startYear && entry.year <= endYear ? '#f97316' : '#cbd5e1'} />))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'composed' && (
            <ResponsiveContainer width="100%" height={350}>
              <ComposedChart data={allPts}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                <Legend />
                <Area type="monotone" dataKey="value" fill="#f97316" fillOpacity={0.12} stroke="#f97316" name={label} />
                <Bar dataKey="value" barSize={18} fill="#3b82f6" fillOpacity={0.45} name={label} />
                <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} name={label} />
              </ComposedChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'pie' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart><Pie data={regData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={130} label={({ name, value }) => `${name}: ${formatTableValue(value)}`}>{regData.map((_, i) => (<Cell key={i} fill={COLORS[i % COLORS.length]} />))}</Pie><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></PieChart>
              </ResponsiveContainer>
              <div className="max-h-[350px] overflow-y-auto"><Table><TableHeader><TableRow className="bg-slate-100 dark:bg-slate-700"><TableHead className="text-xs font-semibold">{t('Région', lang || 'fr')}</TableHead><TableHead className="text-xs text-right font-semibold">{t('Valeur', lang || 'fr')}</TableHead></TableRow></TableHeader><TableBody>{regData.map((d, i) => (<TableRow key={i} className={i % 2 === 0 ? '' : 'bg-slate-50 dark:bg-slate-800'}><TableCell className="text-sm py-1.5"><span className="inline-block w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[i % COLORS.length] }} />{t(d.fullName, lang)}</TableCell><TableCell className="text-sm text-right font-mono font-semibold py-1.5">{formatTableValue(d.value)}</TableCell></TableRow>))}</TableBody></Table></div>
            </div>
          )}

          {activeChart === 'donut' && (
            <ResponsiveContainer width="100%" height={350}>
              <PieChart><Pie data={regData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={70} outerRadius={120} paddingAngle={2} label={({ name }) => name}>{regData.map((_, i) => (<Cell key={i} fill={COLORS[i % COLORS.length]} />))}</Pie><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></PieChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'treemap' && (
            <ResponsiveContainer width="100%" height={350}>
              <RTreemap data={regData.map((r, i) => ({ name: r.name, size: r.value, fill: COLORS[i % COLORS.length] }))} dataKey="size" nameKey="name" stroke="#fff"><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></RTreemap>
            </ResponsiveContainer>
          )}

          {activeChart === 'scatter' && (
            <ResponsiveContainer width="100%" height={350}>
              <ScatterChart><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /><XAxis type="number" dataKey="year" name={t('Année', lang || 'fr')} tick={{ fontSize: 11, fill: '#94a3b8' }} /><YAxis type="number" dataKey="value" name={t('Valeur', lang || 'fr')} tick={{ fontSize: 11, fill: '#94a3b8' }} /><ReTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} /><Scatter data={allPts} fill="#f97316" /></ScatterChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function KPIDetailTable({ indicator, unit, startYear, endYear, lang }: { indicator: IndicatorData; unit: string; startYear: number; endYear: number; lang?: Lang }) {
  return (
    <Card className="bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <FileText className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          {t('Données complètes', 'fr')} — {indicator.national.length} {t('observations', 'fr')}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="max-h-[500px] overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                <TableHead className="font-semibold">{t('Année', 'fr')}</TableHead>
                <TableHead className="text-right font-semibold">{t('Valeur', 'fr')} ({unit})</TableHead>
                <TableHead className="text-right font-semibold">{t('Variation', 'fr')}</TableHead>
                <TableHead className="text-right font-semibold">%</TableHead>
                <TableHead className="text-center font-semibold">{t('Tendance', 'fr')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {indicator.national.map((pt, idx) => {
                const prev = idx > 0 ? indicator.national[idx - 1].value : pt.value
                const curVal = pt.value ?? 0
                const prevVal = prev ?? 0
                const diff = curVal - prevVal
                const pct = prevVal !== 0 ? (diff / Math.abs(prevVal)) * 100 : 0
                const safePct = Number.isFinite(pct) ? pct : 0
                const trend = diff > 0.001 ? 'up' : diff < -0.001 ? 'down' : 'stable'
                const inRange = pt.year >= startYear && pt.year <= endYear
                return (
                  <TableRow key={pt.year} className={inRange ? (idx % 2 === 0 ? 'bg-blue-50/70 dark:bg-blue-950/30' : 'bg-blue-100/40 dark:bg-blue-950/20') : (idx % 2 === 0 ? '' : 'bg-slate-50 dark:bg-slate-800/50')}>
                    <TableCell className="font-medium text-sm py-2 text-slate-900 dark:text-slate-100">{pt.year}{inRange && startYear !== endYear && <span className="ml-1 text-[10px] text-blue-600 dark:text-blue-400">• plage</span>}</TableCell>
                    <TableCell className="text-right font-mono tabular-nums font-semibold text-sm py-2 text-slate-900 dark:text-slate-100">{formatTableValue(curVal)}</TableCell>
                    <TableCell className={`text-right font-mono tabular-nums text-sm py-2 ${diff > 0.001 ? 'text-emerald-600 dark:text-emerald-400' : diff < -0.001 ? 'text-red-500 dark:text-red-400' : 'text-amber-500 dark:text-amber-400'}`}>{idx === 0 ? '—' : `${diff > 0 ? '+' : ''}${formatTableValue(diff)}`}</TableCell>
                    <TableCell className={`text-right font-mono tabular-nums text-sm py-2 ${diff > 0.001 ? 'text-emerald-600 dark:text-emerald-400' : diff < -0.001 ? 'text-red-500 dark:text-red-400' : 'text-amber-500 dark:text-amber-400'}`}>{idx === 0 ? '—' : `${safePct > 0 ? '+' : ''}${safePct.toFixed(1)}%`}</TableCell>
                    <TableCell className="text-center py-2">{idx === 0 ? '—' : <span className={`text-sm font-medium ${trend === 'up' ? 'text-emerald-600 dark:text-emerald-400' : trend === 'down' ? 'text-red-500 dark:text-red-400' : 'text-amber-500 dark:text-amber-400'}`}>{trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}</span>}</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Main Page ──────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('Économie')
  const [lang, setLang] = useState<Lang>('fr')
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null)
  const [startYear, setStartYear] = useState(2015)
  const [endYear, setEndYear] = useState(2025)
  const [mapIndicatorIndex, setMapIndicatorIndex] = useState(() => {
    const firstRegional = ALL_MODULES.find((m) => m.name === 'Économie')?.indicators.findIndex((ind) => !ind.isNationalOnly && ind.regional.length > 0)
    return firstRegional !== undefined && firstRegional >= 0 ? firstRegional : 0
  })
  const [selectedKPI, setSelectedKPI] = useState<{ indicator: IndicatorData; label: string; unit: string } | null>(null)
  const [activeDetailIndicator, setActiveDetailIndicator] = useState<IndicatorData | null>(null)
  const [kpiStartYear, setKpiStartYear] = useState(2015)
  const [kpiEndYear, setKpiEndYear] = useState(2025)
  const [kpiActiveChart, setKpiActiveChart] = useState('line')
  const [enrichedModule, setEnrichedModule] = useState<ModuleData | null>(null)

  const staticModule = ALL_MODULES.find((m) => m.name === activeTab)!
  const activeModule = enrichedModule || staticModule

  useEffect(() => {
    enrichModule(staticModule).then(setEnrichedModule)
  }, [activeTab])
  const currentRegions = useMemo(() => getRegionsForYear(endYear), [endYear])

  const handleKPIClick = useCallback((kpi: { label: string; unit: string; indicator: IndicatorData }) => {
    setSelectedKPI(kpi)
    setKpiStartYear(MIN_YEAR)
    setKpiEndYear(MAX_YEAR)
    setKpiActiveChart('line')
    setTimeout(() => window.scrollTo({ top: 0, behavior: 'smooth' }), 50)
  }, [])

  const handleTabChange = useCallback((v: string) => {
    setActiveTab(v)
    setSelectedRegion(null)
    setMapIndicatorIndex(0)
  }, [])

  // Apply theme to html element
  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next = prev === 'light' ? 'dark' : 'light'
      document.documentElement.classList.toggle('dark', next === 'dark')
      return next
    })
  }, [])

  const toggleLang = useCallback(() => {
    setLang((prev) => prev === 'fr' ? 'en' : 'fr')
  }, [])

  const handleStartYearChange = useCallback((y: number) => {
    setStartYear(y)
    setSelectedRegion(null)
    playChangeSound()
  }, [])

  const handleEndYearChange = useCallback((y: number) => {
    setEndYear(y)
    setSelectedRegion(null)
    playChangeSound()
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-slate-900">
      {/* ─── Top Bar (always visible, compact when KPI selected) ── */}
      <div className={`sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 shadow-sm`}>
        <div className="flex h-0.5 w-full" aria-hidden="true">
          <div className="flex-1 bg-[#C1272D]" />
          <div className="flex-1 bg-[#006233]" />
          <div className="flex-1 bg-[#C1272D]" />
        </div>
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-2 flex items-center gap-3">
          {selectedKPI && (
            <button onClick={() => setSelectedKPI(null)} className="flex items-center justify-center h-8 w-8 rounded-full bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors shrink-0">
              <ArrowLeft className="h-4 w-4 text-slate-700 dark:text-slate-200" />
            </button>
          )}
          <img src="/logo.png" alt="MAROC STAT" className={`${selectedKPI ? 'h-8' : 'h-10'} w-auto object-contain shrink-0`} />
          {selectedKPI ? (
            <>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-slate-900 dark:text-white truncate">{selectedKPI.label}</p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">{selectedKPI.unit} — {selectedKPI.indicator.source || 'Source non disponible'} — {selectedKPI.indicator.national.length} {t('observations', lang)}</p>
              </div>
            </>
          ) : (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-slate-900 dark:text-white">MAROC STAT</p>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">{t('Observatoire Prédictif Multi-Domaines du Maroc', lang)}</p>
            </div>
          )}
          <button onClick={toggleLang} className="shrink-0 flex items-center gap-1 px-2.5 py-1.5 text-[10px] font-semibold rounded-lg bg-[#006233] text-white hover:bg-[#004d28] transition-colors">
            {lang === 'fr' ? 'FR' : 'EN'}
          </button>
          <button onClick={toggleTheme} className="shrink-0 flex items-center gap-1 px-2.5 py-1.5 text-[10px] font-semibold rounded-lg bg-[#C1272D] text-white hover:bg-[#8B1A1A] transition-colors">
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button onClick={() => window.location.reload()} className="shrink-0 flex items-center justify-center h-8 w-8 rounded-full bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors" title="Rafraîchir">
            <RefreshCw className="h-4 w-4 text-slate-700 dark:text-slate-200" />
          </button>
        </div>
      </div>

      {/* ─── Hero Header (only on main dashboard) ──────────────────── */}
      {!selectedKPI && (
        <header className="relative overflow-hidden bg-gradient-to-b from-white via-slate-50 to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 sm:py-10 text-center">
            <div className="inline-block rounded-2xl bg-white/90 dark:bg-white/95 p-4 shadow-lg">
              <img src="/logo.png" alt="MAROC STAT" className="mx-auto h-40 sm:h-48 lg:h-56 w-auto object-contain" />
            </div>

            <h1 className="mt-4 text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              MAROC STAT
            </h1>
            <p className="mt-1 text-sm sm:text-base text-slate-600 dark:text-slate-300 font-medium">
              {t('Observatoire Prédictif Multi-Domaines du Maroc', lang)}
            </p>

            <Separator className="mx-auto mt-5 max-w-xs bg-slate-300 dark:bg-slate-600" />

            {/* Stat Badges */}
            <div className="mt-6 flex flex-wrap items-center justify-center gap-2 sm:gap-3">
              <Badge variant="secondary" className="bg-[#006233]/10 text-[#006233] dark:bg-[#006233]/20 dark:text-emerald-300 border-[#006233]/20 gap-1.5">
                <Database className="h-3 w-3" />
                {Math.round(GLOBAL_STATS.totalLignes / 1000)}K {t('lignes', lang)}
              </Badge>
              <Badge variant="secondary" className="bg-[#C1272D]/10 text-[#C1272D] dark:bg-[#C1272D]/20 dark:text-red-300 border-[#C1272D]/20 gap-1.5">
                <BarChart3 className="h-3 w-3" />
                {GLOBAL_STATS.totalIndicateurs} {t('indicateurs', lang)}
              </Badge>
              <Badge variant="secondary" className="bg-[#FFD700]/15 text-amber-700 dark:bg-[#FFD700]/15 dark:text-amber-300 border-[#FFD700]/30 gap-1.5">
                <MapPin className="h-3 w-3" />
                {currentRegions.length} {t('régions', lang)} {endYear < 2015 ? '(1997–2015)' : '(2015–)'}
              </Badge>
              <Badge variant="secondary" className="bg-slate-200/80 text-slate-700 dark:bg-slate-700/60 dark:text-slate-300 border-slate-300 dark:border-slate-600 gap-1.5">
                <FileText className="h-3 w-3" />
                {GLOBAL_STATS.totalSources} {t('sources', lang)}
              </Badge>
              <Badge variant="secondary" className="bg-slate-200/80 text-slate-700 dark:bg-slate-700/60 dark:text-slate-300 border-slate-300 dark:border-slate-600 gap-1.5">
                <Calendar className="h-3 w-3" />
                {GLOBAL_STATS.periode}
              </Badge>
            </div>
          </div>
        </header>
      )}

      {/* ─── KPI Detail View (inline, YouTube-style) ─────────────────────── */}
      {selectedKPI && (() => {
        const ind = selectedKPI.indicator
        const pts = ind.national.filter((p) => p.year >= kpiStartYear && p.year <= kpiEndYear)
        if (pts.length === 0) return null
        const vals = pts.map((p) => p.value)
        const cur = vals[vals.length - 1]
        const mn = Math.min(...vals)
        const mx = Math.max(...vals)
        const av = vals.reduce((s, v) => s + v, 0) / vals.length
        const mnYr = pts.find((p) => p.value === mn)?.year
        const mxYr = pts.find((p) => p.value === mx)?.year
        const fir = vals[0]
        const chg = cur - fir
        const chgPct = fir !== 0 ? (chg / Math.abs(fir)) * 100 : 0
        const mc = MODULE_COLORS[activeModule.name] || '#f97316'
        const tabs = [
          { key: 'line', label: t('Courbes', lang) }, { key: 'area', label: t('Aires', lang) },
          { key: 'bar', label: t('Barres', lang) }, { key: 'composed', label: t('Composé', lang) },
          { key: 'pie', label: t('Camembert', lang) }, { key: 'donut', label: t('Anneau', lang) },
          { key: 'treemap', label: 'Treemap' }, { key: 'scatter', label: t('Points', lang) },
        ]
        const subs = [
          { label: t('Valeur actuelle', lang), value: formatKPIValue(cur, ind.code), sub: `${kpiEndYear}`, color: '#3b82f6', bg: 'bg-blue-50 dark:bg-blue-950/40' },
          { label: t('Minimum', lang), value: formatKPIValue(mn, ind.code), sub: `${mnYr}`, color: '#ef4444', bg: 'bg-red-50 dark:bg-red-950/40' },
          { label: t('Maximum', lang), value: formatKPIValue(mx, ind.code), sub: `${mxYr}`, color: '#22c55e', bg: 'bg-emerald-50 dark:bg-emerald-950/40' },
          { label: t('Moyenne', lang), value: formatKPIValue(av, ind.code), sub: `${kpiStartYear}–${kpiEndYear}`, color: '#a855f7', bg: 'bg-purple-50 dark:bg-purple-950/40' },
          { label: t('Variation totale', lang), value: `${chg >= 0 ? '+' : ''}${formatKPIValue(chg, ind.code)}`, sub: `${chgPct >= 0 ? '+' : ''}${chgPct.toFixed(1)}%`, color: chg >= 0 ? '#22c55e' : '#ef4444', bg: chg >= 0 ? 'bg-emerald-50 dark:bg-emerald-950/40' : 'bg-red-50 dark:bg-red-950/40' },
          { label: t('Observations', lang), value: `${pts.length}`, sub: t('ans', lang), color: '#64748b', bg: 'bg-slate-50 dark:bg-slate-800' },
        ]
        const rReg = kpiEndYear < 2015 && ind.regionalOld ? ind.regionalOld : ind.regional
        const rData = rReg.map((r) => ({ name: r.region.length > 18 ? r.region.slice(0, 16) + '…' : r.region, fullName: r.region, value: r.value }))
        const PC = ['#f97316','#22c55e','#3b82f6','#a855f7','#ef4444','#eab308','#06b6d4','#ec4899','#14b8a6','#8b5cf6','#f43f5e','#84cc16']
        return (
          <div className="flex-1 w-full bg-white dark:bg-slate-900">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 space-y-5">
              {/* Period Selector */}
              <div className="flex flex-wrap items-center gap-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">{t('Début', lang)}</span>
                  <select value={kpiStartYear} onChange={(e) => setKpiStartYear(Number(e.target.value))} className="px-2 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white">
                    {ALL_YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">{t('Fin', lang)}</span>
                  <select value={kpiEndYear} onChange={(e) => setKpiEndYear(Number(e.target.value))} className="px-2 py-1 text-sm rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white">
                    {ALL_YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
                  </select>
                </div>
              </div>

              {/* Interpretation Block */}
              {KPI_INTERPRETATIONS[ind.code] && (() => {
                const interp = KPI_INTERPRETATIONS[ind.code]
                const lastVal = vals[vals.length - 1]
                const isGood = (ind.code === 'TAUX_CHOMAGE' || ind.code === 'TAUX_ABANDON_PRIMAIRE' || ind.code === 'INFLATION' || ind.code === 'STRESS_HYDRIQUE') ? lastVal < 15 : lastVal > 0
                return (
                  <div className={`rounded-xl border p-5 space-y-3 ${isGood ? 'bg-emerald-50/80 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800' : 'bg-amber-50/80 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800'}`}>
                    <div className="flex items-center gap-2">
                      <div className={`h-2 w-2 rounded-full ${isGood ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">{t('Interprétation & Recommandations', lang)}</h4>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">{t('C\'est quoi ?', lang)}</p>
                        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{interp.what[lang]}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">{t('Interprétation', lang)}</p>
                        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{interp.meaning[lang]}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">{t('Situation actuelle', lang)}</p>
                        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{interp.status[lang]}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400 tracking-wider">{t('Recommandations officielles', lang)}</p>
                        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{interp.recommendation[lang]}</p>
                      </div>
                    </div>
                  </div>
                )
              })()}

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {subs.map((b) => (
                  <div key={b.label} className={`rounded-xl border border-slate-200 dark:border-slate-700 ${b.bg} p-4 text-center`}>
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">{b.label}</p>
                    <p className="text-2xl font-bold mt-1" style={{ color: b.color }}>{b.value}</p>
                    {b.sub && <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{b.sub}</p>}
                  </div>
                ))}
              </div>
              <div className="flex gap-1 overflow-x-auto pb-1">
                {tabs.map((tr) => (
                  <button key={tr.key} onClick={() => setKpiActiveChart(tr.key)} className={`shrink-0 px-4 py-2 text-sm font-medium rounded-lg transition-all ${kpiActiveChart === tr.key ? 'text-white shadow-md' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'}`} style={kpiActiveChart === tr.key ? { backgroundColor: mc } : undefined}>
                    {tr.label}
                  </button>
                ))}
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                {kpiActiveChart === 'line' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={pts}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                      <ReferenceLine y={av} stroke="#a855f7" strokeDasharray="5 5" />
                      <Line type="monotone" dataKey="value" stroke={mc} strokeWidth={2.5} dot={{ r: 3, fill: mc }} activeDot={{ r: 6 }} name={t(ind.label, lang || 'fr')} />
                    </LineChart>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'area' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={pts}>
                      <defs><linearGradient id="gK" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={mc} stopOpacity={0.3} /><stop offset="95%" stopColor={mc} stopOpacity={0.02} /></linearGradient></defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                      <Area type="monotone" dataKey="value" stroke={mc} fill="url(#gK)" strokeWidth={2} name={t(ind.label, lang || 'fr')} />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'bar' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={pts}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                      <Bar dataKey="value" name={t(ind.label, lang || 'fr')} fill={mc} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'composed' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={pts}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} />
                      <Legend />
                      <Area type="monotone" dataKey="value" fill={mc} fillOpacity={0.12} stroke={mc} name={t(ind.label, lang || 'fr')} />
                      <Bar dataKey="value" barSize={18} fill="#3b82f6" fillOpacity={0.45} name={t(ind.label, lang || 'fr')} />
                      <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} name={t(ind.label, lang || 'fr')} />
                    </ComposedChart>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'pie' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart><Pie data={rData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={150} label={({ name, value }) => `${name}: ${formatTableValue(value)}`}>{rData.map((_, i) => <Cell key={i} fill={PC[i % PC.length]} />)}</Pie><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></PieChart>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'donut' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart><Pie data={rData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={80} outerRadius={140} paddingAngle={2} label={({ name }) => name}>{rData.map((_, i) => <Cell key={i} fill={PC[i % PC.length]} />)}</Pie><ReTooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} formatter={(v: number) => formatTableValue(v)} /></PieChart>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'treemap' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <div className="grid grid-cols-3 gap-2 h-full">
                      {rData.slice(0, 9).map((r, i) => (
                        <div key={i} className="rounded-lg p-3 flex flex-col justify-end" style={{ backgroundColor: PC[i % PC.length], opacity: 0.8 }}>
                          <span className="text-white text-[10px] font-semibold truncate">{r.name}</span>
                          <span className="text-white text-lg font-bold">{formatTableValue(r.value)}</span>
                        </div>
                      ))}
                    </div>
                  </ResponsiveContainer>
                )}
                {kpiActiveChart === 'scatter' && (
                  <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /><XAxis type="number" dataKey="year" domain={[kpiStartYear, kpiEndYear]} tick={{ fontSize: 11, fill: '#94a3b8' }} /><YAxis type="number" dataKey="value" tick={{ fontSize: 11, fill: '#94a3b8' }} /><ReTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0' }} /><Scatter data={pts} fill={mc} /></ScatterChart>
                  </ResponsiveContainer>
                )}
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                  <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                    <FileText className="h-4 w-4 text-slate-500" />
                    {t('Données complètes', lang)} — {pts.length} {t('observations', lang)}
                  </h3>
                </div>
                <div className="max-h-[500px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                      <th className="text-left p-2 font-semibold">{t('Année', lang)}</th>
                      <th className="text-right p-2 font-semibold">{t('Valeur', lang)} ({ind.unit})</th>
                      <th className="text-right p-2 font-semibold">{t('Variation', lang)}</th>
                      <th className="text-right p-2 font-semibold">% Δ</th>
                      <th className="text-center p-2 font-semibold">{t('Tendance', lang)}</th>
                    </tr></thead>
                    <tbody>
                      {pts.map((pt, idx) => {
                        const prev = idx > 0 ? pts[idx - 1].value : pt.value
                        const d = pt.value - prev
                        const p = prev !== 0 ? (d / Math.abs(prev)) * 100 : 0
                        const tr = d > 0.001 ? 'up' : d < -0.001 ? 'down' : 'stable'
                        return (
                          <tr key={pt.year} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                            <td className="p-2 font-medium">{pt.year}</td>
                            <td className="p-2 text-right font-mono font-semibold">{formatTableValue(pt.value)}</td>
                            <td className={`p-2 text-right font-mono ${d > 0.001 ? 'text-emerald-600 dark:text-emerald-400' : d < -0.001 ? 'text-red-500 dark:text-red-400' : 'text-amber-500'}`}>{idx === 0 ? '—' : `${d > 0 ? '+' : ''}${formatTableValue(d)}`}</td>
                            <td className={`p-2 text-right font-mono ${p > 0.001 ? 'text-emerald-600 dark:text-emerald-400' : p < -0.001 ? 'text-red-500 dark:text-red-400' : 'text-amber-500'}`}>{idx === 0 ? '—' : `${p > 0 ? '+' : ''}${p.toFixed(1)}%`}</td>
                            <td className="p-2 text-center">{idx === 0 ? '—' : <span className={`text-sm font-medium ${tr === 'up' ? 'text-emerald-600' : tr === 'down' ? 'text-red-500' : 'text-amber-500'}`}>{tr === 'up' ? '↑' : tr === 'down' ? '↓' : '→'}</span>}</td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* ─── Detailed Data Section ──────────────────────────────── */}
              {getDetailedData(ind.code) && (() => {
                const data = getDetailedData(ind.code)
                if (!data || data.length === 0) return null

                if (ind.code === 'UNIVERSITES_COUNT' || ind.code === 'UNIVERSITES_PUBLIQUES' || ind.code === 'UNIVERSITES_PRIVEES') {
                  const unis = data as University[]
                  const filtered = unis
                  const types = ['publique', 'privée', 'semi-publique'] as const
                  const typeColors = { publique: '#006233', 'privée': '#C1272D', 'semi-publique': '#FFD700' }
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                           {t('Universités et établissements', lang)} — {filtered.length} {t('établissements', lang)}
                        </h3>
                        <div className="flex gap-2 mt-2">
                          {types.map(tp => (
                            <span key={tp} className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${typeColors[tp]}20`, color: typeColors[tp] }}>
                              {tp === 'publique' ? 'Publique' : tp === 'privée' ? 'Privée' : 'Semi-publique'} ({unis.filter(u => u.type === tp).length})
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="max-h-[600px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            <th className="text-left p-2 font-semibold">Université</th>
                            <th className="text-left p-2 font-semibold">Type</th>
                            <th className="text-left p-2 font-semibold">Région</th>
                            <th className="text-right p-2 font-semibold">Fondée</th>
                            <th className="text-right p-2 font-semibold">Étudiants</th>
                            <th className="text-left p-2 font-semibold">Facultés / Écoles</th>
                          </tr></thead>
                          <tbody>
                            {filtered.map((u, i) => (
                              <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                <td className="p-2 font-medium text-slate-900 dark:text-white">{u.name} <span className="text-slate-400 text-xs">({u.acronym})</span></td>
                                <td className="p-2"><span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${typeColors[u.type]}20`, color: typeColors[u.type] }}>{u.type === 'publique' ? 'Public' : u.type === 'privée' ? 'Privé' : 'Semi-public'}</span></td>
                                <td className="p-2 text-slate-600 dark:text-slate-400">{u.region}</td>
                                <td className="p-2 text-right font-mono">{u.founded}</td>
                                <td className="p-2 text-right font-mono font-semibold">{u.students.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-xs text-slate-500 dark:text-slate-400 max-w-xs">{u.faculties.join(' • ')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'MEDECINS') {
                  const docData = getDoctorData()
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                             {t('Médecins par spécialité', lang)} — {docData.specialties.length} {t('spécialités', lang)}
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Source : Carte Sanitaire 2025 — Ministère de la Santé et de la Protection Sociale</p>
                          <div className="flex gap-3 mt-2 text-xs">
                            <span className="text-blue-600 dark:text-blue-400">Total : {docData.specialties.reduce((s, d) => s + d.total, 0).toLocaleString('fr-FR')}</span>
                            <span className="text-emerald-600 dark:text-emerald-400">Public : {docData.specialties.reduce((s, d) => s + d.public, 0).toLocaleString('fr-FR')}</span>
                          </div>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Spécialité</th>
                              <th className="text-right p-2 font-semibold">Total</th>
                              <th className="text-right p-2 font-semibold text-emerald-600">Public</th>
                              <th className="text-right p-2 font-semibold text-blue-600">Privé</th>
                            </tr></thead>
                            <tbody>
                              {docData.specialties.map((d, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{d.specialty}{d.description && <span className="text-xs text-slate-400 ml-1">— {d.description}</span>}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{d.total.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-emerald-600 dark:text-emerald-400">{d.public.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-blue-600 dark:text-blue-400">{d.prive > 0 ? d.prive.toLocaleString('fr-FR') : '—'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                             {t('Médecins par région', lang)} — 2025
                          </h3>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Région</th>
                              <th className="text-right p-2 font-semibold">Total</th>
                              <th className="text-right p-2 font-semibold text-emerald-600">Public</th>
                              <th className="text-right p-2 font-semibold text-blue-600">Privé</th>
                              <th className="text-right p-2 font-semibold">Hab./Médecin</th>
                            </tr></thead>
                            <tbody>
                              {docData.byRegion.map((d, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{d.region}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{d.total.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-emerald-600 dark:text-emerald-400">{d.public.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-blue-600 dark:text-blue-400">{d.prive.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-slate-600 dark:text-slate-300">{d.ratioHab?.toLocaleString('fr-FR') ?? '—'}</td>
                                </tr>
                              ))}
                              <tr className="bg-slate-50 dark:bg-slate-700/50 font-semibold border-t-2 border-slate-300 dark:border-slate-600">
                                <td className="p-2 text-slate-900 dark:text-white">TOTAL</td>
                                <td className="p-2 text-right font-mono">{docData.byRegion.reduce((s, d) => s + d.total, 0).toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono text-emerald-600">{docData.byRegion.reduce((s, d) => s + d.public, 0).toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono text-blue-600">{docData.byRegion.reduce((s, d) => s + d.prive, 0).toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono">1 108</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                             {t('Médecins par province', lang)} — {docData.byProvince.length} {t('provinces', lang)}
                          </h3>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Province</th>
                              <th className="text-left p-2 font-semibold">Région</th>
                              <th className="text-right p-2 font-semibold">Médecins</th>
                            </tr></thead>
                            <tbody>
                              {docData.byProvince.map((d, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{d.province}</td>
                                  <td className="p-2 text-xs text-slate-500 dark:text-slate-400">{d.region}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{d.doctors.toLocaleString('fr-FR')}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'GRANDS_BARRAGES' || ind.code === 'REMPLISSAGE_BARRAGES') {
                  const dams = data as Dam[]
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                           {t('Grands barrages du Maroc', lang)} — {dams.length} {t('barrages', lang)}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Capacité totale : {(dams.reduce((s, d) => s + d.capacityM3, 0) / 1e9).toFixed(1)} milliards m³ — Source : ONEP / ABH</p>
                      </div>
                      <div className="max-h-[600px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            <th className="text-left p-2 font-semibold">Barrage</th>
                            <th className="text-left p-2 font-semibold">Région</th>
                            <th className="text-left p-2 font-semibold">Bassin</th>
                            <th className="text-right p-2 font-semibold">Capacité (M m³)</th>
                            <th className="text-right p-2 font-semibold">Année</th>
                            <th className="text-left p-2 font-semibold">Usages</th>
                            <th className="text-right p-2 font-semibold">Remplissage 2026</th>
                          </tr></thead>
                          <tbody>
                            {dams.map((d, i) => {
                              const filling2026 = d.annualFilling.find(f => f.year === kpiEndYear)?.percent ?? 0
                              return (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{d.name}</td>
                                  <td className="p-2 text-slate-600 dark:text-slate-400">{d.region}</td>
                                  <td className="p-2 text-slate-600 dark:text-slate-400">{d.basin}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{(d.capacityM3 / 1e6).toFixed(0)}</td>
                                  <td className="p-2 text-right font-mono">{d.yearBuilt}</td>
                                  <td className="p-2 text-xs text-slate-500 dark:text-slate-400">{d.usage.join(' • ')}</td>
                                  <td className="p-2 text-right">
                                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${filling2026 > 50 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : filling2026 > 30 ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'}`}>
                                      {filling2026}%
                                    </span>
                                  </td>
                                </tr>
                              )
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'LITS_HOPITAL' || ind.code === 'HOPITAUX_PRIVES') {
                  const hospitals = data as Hospital[]
                  const types = ['public', 'clinique', 'semi-privé', 'privé'] as const
                  const typeLabels: Record<string, string> = { public: 'Public (CHU/CH)', privé: 'Privé', 'semi-privé': 'Non-lucratif', clinique: 'Clinique' }
                  const typeColors: Record<string, string> = { public: '#006233', privé: '#C1272D', 'semi-privé': '#3b82f6', clinique: '#FFD700' }
                  const totalRevenue = hospitals.reduce((s, h) => s + h.annualRevenue, 0)
                  const totalBeds = hospitals.reduce((s, h) => s + h.capacity, 0)
                  const totalStaff = hospitals.reduce((s, h) => s + h.staff, 0)
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                           {t('Établissements hospitaliers', lang)} — {hospitals.length} {t('établissements', lang)}
                        </h3>
                        <div className="flex gap-2 mt-2 flex-wrap">
                          {types.map(tp => (
                            <span key={tp} className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${typeColors[tp]}20`, color: typeColors[tp] }}>
                              {typeLabels[tp]} ({hospitals.filter(h => h.type === tp).length})
                            </span>
                          ))}
                        </div>
                        <div className="flex gap-4 mt-2 text-xs text-slate-500 dark:text-slate-400">
                          <span>🛏️ {totalBeds.toLocaleString('fr-FR')} lits</span>
                          <span>👨‍⚕️ {totalStaff.toLocaleString('fr-FR')} employés</span>
                           <span>CA total : {(totalRevenue / 1e9).toFixed(1)} Mds MAD</span>
                        </div>
                      </div>
                      <div className="max-h-[600px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            <th className="text-left p-2 font-semibold">Hôpital / Clinique</th>
                            <th className="text-left p-2 font-semibold">Type</th>
                            <th className="text-left p-2 font-semibold">{t('Wilaya', lang)}</th>
                            <th className="text-right p-2 font-semibold">Lits</th>
                            <th className="text-right p-2 font-semibold">Personnel</th>
                            <th className="text-right p-2 font-semibold">CA annuel (MAD)</th>
                            <th className="text-right p-2 font-semibold">Population desservie</th>
                            <th className="text-left p-2 font-semibold">Spécialités</th>
                          </tr></thead>
                          <tbody>
                            {hospitals.map((h, i) => (
                              <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                <td className="p-2 font-medium text-slate-900 dark:text-white">{h.name}</td>
                                <td className="p-2"><span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${typeColors[h.type]}20`, color: typeColors[h.type] }}>{typeLabels[h.type]}</span></td>
                                <td className="p-2 text-slate-600 dark:text-slate-400 text-xs">{h.province}</td>
                                <td className="p-2 text-right font-mono font-semibold">{h.capacity.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono">{h.staff.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono font-semibold">{h.annualRevenue.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono text-xs">{h.population ? h.population.toLocaleString('fr-FR') : '—'}</td>
                                <td className="p-2 text-xs text-slate-500 dark:text-slate-400 max-w-xs">{h.specialties.join(' • ')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'INGENIEURS_DIPLOMES') {
                  const eng = data as EngineerGrad[]
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                           {t('Ingénieurs par filière', lang)} — {eng.length} {t('filières', lang)}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          Total : {eng.reduce((s, e) => s + e.count, 0).toLocaleString('fr-FR')} ingénieurs/an — Les plus recrutables : {eng.sort((a, b) => b.count - a.count).slice(0, 3).map(e => e.field).join(', ')}
                        </p>
                      </div>
                      <div className="max-h-[600px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            <th className="text-left p-2 font-semibold">Filière</th>
                            <th className="text-right p-2 font-semibold">Diplômés/an</th>
                            <th className="text-left p-2 font-semibold">Employabilité</th>
                          </tr></thead>
                          <tbody>
                            {eng.sort((a, b) => b.count - a.count).map((e, i) => (
                              <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                <td className="p-2 font-medium text-slate-900 dark:text-white">{e.field}</td>
                                <td className="p-2 text-right font-mono font-semibold">{e.count.toLocaleString('fr-FR')}</td>
                                <td className="p-2"><span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${e.employability.includes('Très élevée') ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : e.employability.includes('Élevée') ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'}`}>{e.employability}</span></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'NB_CLUBS' || ind.code === 'BOTOLA_PRO_CLUBS' || ind.code.startsWith('LICENCIES_')) {
                  const clubs = data as SportsClub[]
                  const activeSport = ind.code === 'NB_CLUBS' ? null
                    : ind.code === 'BOTOLA_PRO_CLUBS' ? 'Football'
                    : ind.code === 'LICENCIES_BASKETBALL' ? 'Basketball'
                    : ind.code === 'LICENCIES_HANDBALL' ? 'Handball'
                    : ind.code === 'LICENCIES_NATATION' ? 'Natation'
                    : ind.code === 'LICENCIES_CYCLISME' ? 'Cyclisme'
                    : ind.code === 'LICENCIES_TENNIS' ? 'Tennis'
                    : ind.code === 'LICENCIES_GOLF' ? 'Golf'
                    : ind.code === 'LICENCIES_RUGBY' ? 'Rugby'
                    : ind.code === 'LICENCIES_ESPORT' ? 'E-sport'
                    : null
                  const filtered = activeSport ? clubs.filter(c => c.sport === activeSport || c.sport.startsWith(activeSport)) : clubs
                  const sports = [...new Set(filtered.map(c => c.sport))]
                  const sportColors: Record<string, string> = { 'Football': '#006233', 'Football féminin': '#C1272D', 'Basketball': '#f97316', 'Natation': '#3b82f6', 'Judo': '#a855f7', 'Boxe': '#ef4444', 'Athlétisme': '#22c55e', 'Tennis': '#FFD700', 'Golf': '#065f46', 'Handball': '#0891b2', 'Volleyball': '#6366f1', 'Rugby': '#7c3aed', 'Tbourida': '#92400e', 'E-sport': '#ec4899' }
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                           {activeSport ? t(`Clubs ${activeSport}`, lang) || `Clubs ${activeSport}` : t('Clubs sportifs', lang)} — {filtered.length} {t('clubs', lang)}
                        </h3>
                        <div className="flex gap-2 mt-2 flex-wrap">
                          {sports.map(sp => (
                            <span key={sp} className="text-[10px] font-semibold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${sportColors[sp] || '#64748b'}20`, color: sportColors[sp] || '#64748b' }}>
                              {sp} ({filtered.filter(c => c.sport === sp).length})
                            </span>
                          ))}
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          Budget total : {(filtered.reduce((s, c) => s + c.budget, 0) / 1e6).toFixed(0)}M MAD — {filtered.reduce((s, c) => s + c.members, 0).toLocaleString('fr-FR')} membres — {filtered.reduce((s, c) => s + c.trophies, 0)} trophées
                        </p>
                      </div>
                      <div className="max-h-[600px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            <th className="text-left p-2 font-semibold">Club</th>
                            <th className="text-left p-2 font-semibold">Sport</th>
                            <th className="text-left p-2 font-semibold">Ville</th>
                            <th className="text-right p-2 font-semibold">Fondé</th>
                            <th className="text-right p-2 font-semibold">Budget (M MAD)</th>
                            <th className="text-right p-2 font-semibold">Membres</th>
                            <th className="text-right p-2 font-semibold">Trophées</th>
                            <th className="text-left p-2 font-semibold">Palmarès</th>
                          </tr></thead>
                          <tbody>
                            {filtered.sort((a, b) => b.budget - a.budget).map((c, i) => (
                              <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                <td className="p-2 font-medium text-slate-900 dark:text-white">{c.name}</td>
                                <td className="p-2"><span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ backgroundColor: `${sportColors[c.sport] || '#64748b'}20`, color: sportColors[c.sport] || '#64748b' }}>{c.sport}</span></td>
                                <td className="p-2 text-slate-600 dark:text-slate-400 text-xs">{c.city}</td>
                                <td className="p-2 text-right font-mono text-xs">{c.founded}</td>
                                <td className="p-2 text-right font-mono font-semibold">{(c.budget / 1e6).toFixed(0)}</td>
                                <td className="p-2 text-right font-mono">{c.members.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono font-semibold">{c.trophies}</td>
                                <td className="p-2 text-xs text-slate-500 dark:text-slate-400">{c.title}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'NB_PROGRAMMES_SOCIAUX' || ind.code === 'BENEFICIAIRES_SOCIAUX') {
                  const progs = data as SocialProgram[]
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                           {t('Programmes sociaux', lang)} — {progs.length} {t('programmes', lang)}
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          Budget total : {(progs.reduce((s, p) => s + p.budget, 0) / 1e9).toFixed(1)} milliards MAD — {progs.reduce((s, p) => s + p.beneficiaries, 0).toLocaleString('fr-FR')} bénéficiaires cumulés
                        </p>
                      </div>
                      <div className="max-h-[600px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            <th className="text-left p-2 font-semibold">Programme</th>
                            <th className="text-left p-2 font-semibold">Ministère</th>
                            <th className="text-right p-2 font-semibold">Budget (M MAD)</th>
                            <th className="text-right p-2 font-semibold">Bénéficiaires</th>
                            <th className="text-left p-2 font-semibold">Lancement</th>
                            <th className="text-left p-2 font-semibold">Indicateurs clés</th>
                          </tr></thead>
                          <tbody>
                            {progs.sort((a, b) => b.budget - a.budget).map((p, i) => (
                              <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                <td className="p-2">
                                  <div className="font-medium text-slate-900 dark:text-white">{p.name}</div>
                                  <div className="text-[10px] text-slate-400">{p.acronym} — {p.description.slice(0, 60)}…</div>
                                </td>
                                <td className="p-2 text-slate-600 dark:text-slate-400 text-xs">{p.ministry}</td>
                                <td className="p-2 text-right font-mono font-semibold">{(p.budget / 1e6).toFixed(0)}</td>
                                <td className="p-2 text-right font-mono font-semibold">{p.beneficiaries >= 1e6 ? `${(p.beneficiaries / 1e6).toFixed(1)}M` : p.beneficiaries.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono">{p.startDate}</td>
                                <td className="p-2 text-xs text-slate-500 dark:text-slate-400 max-w-xs">{p.indicators.join(' • ')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'COUPE_CAF_CL') {
                  return <CAFCLDetail lang={lang} />
                }

                if (ind.code === 'SMIG' || ind.code === 'SMAG') {
                  const smigData = SMIG_SMAG_DETAIL.filter(d => d.year >= kpiStartYear && d.year <= kpiEndYear)
                  const isSmig = ind.code === 'SMIG'
                  const avgSmig = smigData.length > 0 ? Math.round(smigData.reduce((s, d) => s + d.smigMonthly, 0) / smigData.length) : 0
                  const avgSmag = smigData.length > 0 ? Math.round(smigData.reduce((s, d) => s + d.smagMonthly, 0) / smigData.length) : 0
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                             {isSmig ? 'SMIG — Salaire Minimum Interprofessionnel Garanti' : 'SMAG — Salaire Minimum Agricole Garanti'}
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            Source : Bank Al-Maghrib, Ministère de l'Emploi — {smigData.length} {t('années', lang)} ({kpiStartYear}–{kpiEndYear})
                          </p>
                          <div className="flex gap-4 mt-2 text-xs">
                            <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Moyenne : {isSmig ? avgSmig.toLocaleString('fr-FR') : avgSmag.toLocaleString('fr-FR')} DH/mois</span>
                            {smigData.length > 1 && (
                              <span className="text-blue-600 dark:text-blue-400">
                                Variation : +{((smigData[smigData.length-1].smigMonthly / smigData[0].smigMonthly - 1) * 100).toFixed(1)}%
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="max-h-[600px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-center p-2 font-semibold">Année</th>
                              <th className="text-right p-2 font-semibold text-emerald-600">SMIG/h (DH)</th>
                              <th className="text-right p-2 font-semibold text-emerald-600">SMIG/mois brut</th>
                              <th className="text-right p-2 font-semibold text-emerald-600">SMIG/mois net</th>
                              <th className="text-right p-2 font-semibold text-amber-600">SMAG/jour (DH)</th>
                              <th className="text-right p-2 font-semibold text-amber-600">SMAG/mois brut</th>
                              <th className="text-right p-2 font-semibold text-amber-600">SMAG/mois net</th>
                              <th className="text-center p-2 font-semibold">SMAG/SMIG</th>
                              <th className="text-center p-2 font-semibold">IPC</th>
                              <th className="text-left p-2 font-semibold text-xs">Événement</th>
                            </tr></thead>
                            <tbody>
                              {smigData.map((d, i) => (
                                <tr key={d.year} className={`border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30 ${d.event !== '-' ? 'bg-amber-50/40 dark:bg-amber-900/10' : ''}`}>
                                  <td className="p-2 text-center font-bold text-slate-900 dark:text-white">{d.year}</td>
                                  <td className="p-2 text-right font-mono text-emerald-600 dark:text-emerald-400">{d.smigHourly.toFixed(2)}</td>
                                  <td className="p-2 text-right font-mono font-semibold text-emerald-600 dark:text-emerald-400">{d.smigMonthly.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-emerald-700 dark:text-emerald-300">{Math.round(d.smigMonthly * 0.9326).toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-amber-600 dark:text-amber-400">{d.smagDaily.toFixed(2)}</td>
                                  <td className="p-2 text-right font-mono font-semibold text-amber-600 dark:text-amber-400">{d.smagMonthly.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-amber-700 dark:text-amber-300">{Math.round(d.smagMonthly * 0.9326).toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-center font-mono text-xs">{d.smagPctOfSmig.toFixed(1)}%</td>
                                  <td className="p-2 text-center font-mono text-xs text-slate-500">{d.ipc}%</td>
                                  <td className="p-2 text-xs text-slate-500 dark:text-slate-400 max-w-xs">
                                    {d.event !== '-' ? <span className="font-semibold text-amber-600 dark:text-amber-400">{d.event}</span> : <span className="text-slate-300 dark:text-slate-600">—</span>}
                                    {d.decree !== '-' && <span className="ml-1 text-slate-400">({d.decree})</span>}
                                  </td>
                                </tr>
                              ))}
                              {smigData.length > 1 && (
                                <tr className="bg-slate-50 dark:bg-slate-700/50 font-semibold border-t-2 border-slate-300 dark:border-slate-600">
                                  <td className="p-2 text-center text-slate-900 dark:text-white">MOYENNE</td>
                                  <td className="p-2 text-right font-mono text-emerald-600">{(smigData.reduce((s, d) => s + d.smigHourly, 0) / smigData.length).toFixed(2)}</td>
                                  <td className="p-2 text-right font-mono text-emerald-600">{avgSmig.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-emerald-700">{Math.round(avgSmig * 0.9326).toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-amber-600">{(smigData.reduce((s, d) => s + d.smagDaily, 0) / smigData.length).toFixed(2)}</td>
                                  <td className="p-2 text-right font-mono text-amber-600">{avgSmag.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono text-amber-700">{Math.round(avgSmag * 0.9326).toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-center font-mono text-xs">{(smigData.reduce((s, d) => s + d.smagPctOfSmig, 0) / smigData.length).toFixed(1)}%</td>
                                  <td className="p-2 text-center font-mono text-xs">—</td>
                                  <td className="p-2 text-xs font-semibold text-blue-600 dark:text-blue-400">Moyenne {kpiStartYear}–{kpiEndYear}</td>
                                </tr>
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>
                      {isSmig && (
                        <div className="bg-blue-50 dark:bg-blue-950/30 rounded-xl border border-blue-200 dark:border-blue-800 p-4">
                          <h4 className="text-sm font-bold text-blue-800 dark:text-blue-300 mb-2">{t('C\'est quoi le SMIG ?', lang)}</h4>
                          <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
                            <li>• <strong>{t('SMIG explique', lang)}</strong></li>
                            <li>• {t('SMIG calcul', lang)}</li>
                            <li>• {t('SMIG evolution', lang)}</li>
                            <li>• {t('SMIG comparaison', lang)}</li>
                            <li>• {t('SMIG exonération', lang)}</li>
                          </ul>
                        </div>
                      )}
                      {!isSmig && (
                        <div className="bg-amber-50 dark:bg-amber-950/30 rounded-xl border border-amber-200 dark:border-amber-800 p-4">
                          <h4 className="text-sm font-bold text-amber-800 dark:text-amber-300 mb-2">{t('C\'est quoi le SMAG ?', lang)}</h4>
                          <ul className="text-xs text-amber-700 dark:text-amber-400 space-y-1">
                            <li>• {t('SMAG explique', lang)}</li>
                            <li>• {t('SMAG calcul', lang)}</li>
                            <li>• {t('SMAG ecart', lang)}</li>
                            <li>• {t('SMAG agriculture', lang)}</li>
                            <li>• {t('SMAG augmentation', lang)}</li>
                          </ul>
                        </div>
                      )}
                      <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-4">
                        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">{t('Comprendre l\'évolution du salaire minimum au Maroc', lang)}</h4>
                        <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed space-y-3">
                          <p>{t('ESSAY_PARA1', lang)}</p>
                          <p>{t('ESSAY_PARA2', lang)}</p>
                          <p>{t('ESSAY_PARA3', lang)}</p>
                          <p>{t('ESSAY_PARA4', lang)}</p>
                          <p>{t('ESSAY_PARA5', lang)}</p>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'POUVOIR_ACHAT') {
                  const smigRows = SMIG_SMAG_DETAIL.filter(d => d.year >= kpiStartYear && d.year <= kpiEndYear)
                  let cumIpc = 100
                  const rowsWithPouv = SMIG_SMAG_DETAIL.map(d => {
                    if (d.year === 1999) cumIpc = 100
                    else cumIpc *= (1 + d.ipc / 100)
                    return { ...d, ipcIndex: cumIpc, pouv: (d.smigMonthly / cumIpc) / (1660 / 100) * 100 }
                  }).filter(d => d.year >= kpiStartYear && d.year <= kpiEndYear)
                  const avgPouv = rowsWithPouv.length > 0 ? (rowsWithPouv.reduce((s, d) => s + d.pouv, 0) / rowsWithPouv.length) : 100
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
                            Pouvoir d'achat réel du SMIG — {kpiStartYear}–{kpiEndYear}
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            Indice base 100 = 1999. Calcul : SMIG nominal ÷ IPC cumulé × 100. Moyenne période : <strong>{avgPouv.toFixed(1)}</strong>
                          </p>
                        </div>
                        <div className="max-h-[500px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-center p-2 font-semibold">Année</th>
                              <th className="text-right p-2 font-semibold">SMIG/mois</th>
                              <th className="text-right p-2 font-semibold">IPC inflation</th>
                              <th className="text-right p-2 font-semibold">IPC index</th>
                              <th className="text-right p-2 font-semibold">Pouvoir d'achat</th>
                              <th className="text-center p-2 font-semibold">Tendance</th>
                            </tr></thead>
                            <tbody>
                              {rowsWithPouv.map((d, i) => {
                                const prev = i > 0 ? rowsWithPouv[i-1].pouv : 100
                                const diff = d.pouv - prev
                                return (
                                  <tr key={d.year} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                    <td className="p-2 text-center font-bold text-slate-900 dark:text-white">{d.year}</td>
                                    <td className="p-2 text-right font-mono">{d.smigMonthly.toLocaleString('fr-FR')} DH</td>
                                    <td className="p-2 text-right font-mono text-red-500">{d.ipc}%</td>
                                    <td className="p-2 text-right font-mono text-slate-500">{d.ipcIndex.toFixed(1)}</td>
                                    <td className={`p-2 text-right font-mono font-bold ${d.pouv >= 100 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
                                      {d.pouv.toFixed(1)}
                                    </td>
                                    <td className="p-2 text-center">
                                      {diff > 0.5 ? <span className="text-emerald-500 text-xs">▲ +{diff.toFixed(1)}</span>
                                        : diff < -0.5 ? <span className="text-red-500 text-xs">▼ {diff.toFixed(1)}</span>
                                        : <span className="text-slate-400 text-xs">—</span>}
                                    </td>
                                  </tr>
                                )
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                      <div className="bg-purple-50 dark:bg-purple-950/30 rounded-xl border border-purple-200 dark:border-purple-800 p-4 space-y-3">
                        <h4 className="text-sm font-bold text-purple-800 dark:text-purple-300">Comprendre le pouvoir d'achat</h4>
                        <div className="text-xs text-purple-700 dark:text-purple-400 space-y-2">
                          <p><strong>C'est quoi ?</strong> Le pouvoir d'achat mesure la <strong>quantité réelle de biens et services</strong> que peut acheter un salarié avec son SMIG. Il tient compte de la hausse des prix (inflation).</p>
                          <p><strong>Comment est-il calculé ?</strong> On divise le SMIG nominal par l'indice des prix à la consommation (IPC). Si le SMIG augmente de 5% mais l'inflation est de 6%, le pouvoir d'achat <strong>baisse</strong> de 1%.</p>
                          <p><strong>Que signifie 117,6 ?</strong> Un salarié au SMIG en 2026 peut acheter <strong>17,6% de biens en plus</strong> qu'en 1999. C'est une amélioration modeste sur 27 ans.</p>
                          <p><strong>Pourquoi a-t-il baissé en 2022-2023 ?</strong> L'inflation a atteint 6,6% (2022) et 6,1% (2023), soit les niveaux les plus élevés depuis 20 ans. La hausse du SMIG (+5%) n'a pas compensé.</p>
                          <p><strong>Comparaison internationale :</strong> Le pouvoir d'achat du SMIG marocain est faible en termes absolus (~340 USD/mois), mais le coût de la vie au Maroc est également plus bas. En parité pouvoir d'achat (PPP), le SMIG vaut environ 750 USD/mois.</p>
                          <p><strong>Recommandation FMI :</strong> Indexer le SMIG sur la productivité et l'inflation pour préserver le pouvoir d'achat réel des travailleurs les plus vulnérables.</p>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'ARRIVEES_TOURISTIQUES' || ind.code === 'NUITEES') {
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                            {t('Touristes étrangers par pays', lang) || 'Touristes étrangers par pays'}
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            {t('Source', lang) || 'Source'} : ONMT, HCP — {TOURISM_SOURCE_MARKETS.length} {t('pays', lang) || 'pays'}
                          </p>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Pays</th>
                              <th className="text-right p-2 font-semibold">Visiteurs 2024</th>
                              <th className="text-right p-2 font-semibold">Part</th>
                            </tr></thead>
                            <tbody>
                              {TOURISM_SOURCE_MARKETS.sort((a, b) => b.visitors2024 - a.visitors2024).map((m, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{m.country}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{m.visitors2024.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono">{m.sharePct.toFixed(1)}%</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'RECETTES_TOURISTIQUES') {
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                            {t('Touristes étrangers par pays', lang) || 'Touristes étrangers par pays'}
                          </h3>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Pays</th>
                              <th className="text-right p-2 font-semibold">Visiteurs 2024</th>
                              <th className="text-right p-2 font-semibold">Part</th>
                            </tr></thead>
                            <tbody>
                              {TOURISM_SOURCE_MARKETS.sort((a, b) => b.visitors2024 - a.visitors2024).map((m, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{m.country}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{m.visitors2024.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono">{m.sharePct.toFixed(1)}%</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'TOURISTES_MRE') {
                  const totalMre = TOURISM_MRE.reduce((s, m) => s + m.effectifs, 0)
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                            Touristes MRE par pays de résidence
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            {t('Source', lang) || 'Source'} : ONMT, Direction de la Migration — {totalMre.toLocaleString('fr-FR')} MRE arrivées en 2024
                          </p>
                        </div>
                        <div className="max-h-[500px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Pays de résidence</th>
                              <th className="text-right p-2 font-semibold">Effectifs</th>
                              <th className="text-right p-2 font-semibold">Part arrivées</th>
                              <th className="text-right p-2 font-semibold">Dép. moy. (DH)</th>
                              <th className="text-left p-2 font-semibold">Type de visite</th>
                            </tr></thead>
                            <tbody>
                              {TOURISM_MRE.sort((a, b) => b.effectifs - a.effectifs).map((m, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{m.pays}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{m.effectifs.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono">{m.partArrivees.toFixed(1)}%</td>
                                  <td className="p-2 text-right font-mono">{m.depensesMoyennes.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-xs text-slate-500 dark:text-slate-400">{m.typeVisite}</td>
                                </tr>
                              ))}
                              <tr className="bg-slate-50 dark:bg-slate-700/50 font-semibold border-t-2 border-slate-300 dark:border-slate-600">
                                <td className="p-2 text-slate-900 dark:text-white">TOTAL</td>
                                <td className="p-2 text-right font-mono">{totalMre.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono">100%</td>
                                <td className="p-2 text-right font-mono">{Math.round(TOURISM_MRE.reduce((s, m) => s + m.depensesMoyennes, 0) / TOURISM_MRE.length).toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-xs text-slate-500">—</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'TOURISME_INTERNE' || ind.code === 'RECETTES_TOURISME_INTERNE') {
                  const totalDom = TOURISM_DOMESTIC.reduce((s, d) => s + d.voyageurs2024, 0)
                  return (
                    <div className="space-y-4">
                      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                            Tourisme intérieur — {totalDom.toLocaleString('fr-FR')} voyageurs en 2024
                          </h3>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                            {t('Source', lang) || 'Source'} : ONMT, HCP — Répartition par type de séjour
                          </p>
                        </div>
                        <div className="max-h-[500px] overflow-y-auto">
                          <table className="w-full text-sm">
                            <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                              <th className="text-left p-2 font-semibold">Type de séjour</th>
                              <th className="text-right p-2 font-semibold">Voyageurs 2024</th>
                              <th className="text-right p-2 font-semibold">Dép. moy. (DH)</th>
                              <th className="text-left p-2 font-semibold">Destinations</th>
                              <th className="text-left p-2 font-semibold">Saison</th>
                            </tr></thead>
                            <tbody>
                              {TOURISM_DOMESTIC.sort((a, b) => b.voyageurs2024 - a.voyageurs2024).map((d, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                  <td className="p-2 font-medium text-slate-900 dark:text-white">{d.type}</td>
                                  <td className="p-2 text-right font-mono font-semibold">{d.voyageurs2024.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-right font-mono">{d.depensesMoyennes.toLocaleString('fr-FR')}</td>
                                  <td className="p-2 text-xs text-slate-500 dark:text-slate-400">{d.destinations}</td>
                                  <td className="p-2 text-xs text-slate-500 dark:text-slate-400">{d.saison}</td>
                                </tr>
                              ))}
                              <tr className="bg-slate-50 dark:bg-slate-700/50 font-semibold border-t-2 border-slate-300 dark:border-slate-600">
                                <td className="p-2 text-slate-900 dark:text-white">TOTAL</td>
                                <td className="p-2 text-right font-mono">{totalDom.toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-right font-mono">{Math.round(TOURISM_DOMESTIC.reduce((s, d) => s + d.depensesMoyennes, 0) / TOURISM_DOMESTIC.length).toLocaleString('fr-FR')}</td>
                                <td className="p-2 text-xs text-slate-500">—</td>
                                <td className="p-2 text-xs text-slate-500">—</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )
                }

                if (ind.code === 'PART_PIB_MRE') {
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                          Contribution des transferts MRE au PIB
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          {t('Source', lang) || 'Source'} : Bank Al-Maghrib, HCP
                        </p>
                      </div>
                      <div className="p-4">
                        <div className="text-xs text-slate-600 dark:text-slate-400 space-y-2">
                          <p>Les transferts des MRE (Marocains Résidant à l'Étranger) constituent l'une des premières sources de devises étrangères du Maroc, derrière le tourisme.</p>
                          <p>Les transferts financent principalement la consommation des ménages, l'investissement immobilier et le soutien familial. Ils jouent un rôle crucial dans l'équilibre de la balance des paiements.</p>
                          <p><strong>Part dans le PIB :</strong> Environ 7% du PIB, soit ~102 milliards MAD en 2025. Le ratio place le Maroc parmi les 10 premiers pays mondiaux.</p>
                        </div>
                      </div>
                    </div>
                  )
                }

                // ── Generic table for any detailed data ──
                const genericData = data as any[]
                if (genericData && genericData.length > 0 && !Array.isArray(genericData[0]?.year)) {
                  const keys = Object.keys(genericData[0] || {})
                  return (
                    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                        <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                          {t(ind.label, lang) || ind.label} — {genericData.length} entrées
                        </h3>
                        {ind.source && <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Source : {ind.source}</p>}
                      </div>
                      <div className="max-h-[500px] overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead><tr className="bg-slate-100 dark:bg-slate-700 sticky top-0 z-10">
                            {keys.filter(k => k !== 'sectorEn' && k !== 'descriptionEn' && k !== 'categoryEn' && k !== 'typeEn').slice(0, 7).map(k => (
                              <th key={k} className="text-left p-2 font-semibold capitalize">{k.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ')}</th>
                            ))}
                          </tr></thead>
                          <tbody>
                            {genericData.slice(0, 100).map((row: any, i: number) => (
                              <tr key={i} className="border-t border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30">
                                {keys.filter(k => k !== 'sectorEn' && k !== 'descriptionEn' && k !== 'categoryEn' && k !== 'typeEn').slice(0, 7).map(k => (
                                  <td key={k} className="p-2 text-xs text-slate-600 dark:text-slate-400 max-w-[200px] truncate">
                                    {typeof row[k] === 'number' ? row[k].toLocaleString('fr-FR') : String(row[k] ?? '—')}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )
                }

                return null
              })()}
            </div>
          </div>
        )
      })()}

      {/* ─── Normal Dashboard ──────────────────────────────────────────────── */}
      {!selectedKPI && (<>
      {/* ─── Main Content ──────────────────────────────────────────────── */}
      <main className="flex-1 w-full bg-white dark:bg-slate-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          {/* ─── Period Selector ──────────────────────────────────────── */}
          <PeriodSelector
            startYear={startYear}
            endYear={endYear}
            onStartChange={handleStartYearChange}
            onEndChange={handleEndYearChange}
          />

          {/* ─── Year Timeline Bar ─────────────────────────────────────────── */}
          <div className="relative mt-2">
            <div className="flex gap-1 overflow-x-auto pb-2 scrollbar-thin">
              {ALL_YEARS.map((y) => {
                const isActive = y >= startYear && y <= endYear
                const isStart = y === startYear
                const isEnd = y === endYear
                return (
                  <button
                    key={y}
                    onClick={() => {
                      if (startYear === endYear) {
                        setEndYear(y)
                        if (y < startYear) setStartYear(y)
                      } else {
                        setStartYear(y)
                        setEndYear(y)
                      }
                    }}
                    className={`shrink-0 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                      isActive
                        ? isStart || isEnd
                          ? 'bg-[#006233] text-white shadow-md scale-105'
                          : 'bg-[#006233]/15 text-[#006233]'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                  >
                    {y}
                  </button>
                )
              })}
            </div>
          </div>

          {/* ─── Synthèse Conjoncturelle ────────────────────────────── */}
          <section aria-label={t('Synthèse Conjoncturelle', lang)}>
            <Card className="overflow-hidden bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700">
              <CardHeader className="pb-3">
                <div className="flex flex-wrap items-center gap-3">
                  <CardTitle className="text-lg dark:text-white">{t('Synthèse Conjoncturelle', lang)}</CardTitle>
                  <Badge
                    className="bg-orange-100 text-orange-700 hover:bg-orange-100 border-orange-200"
                  >
                    {t('Période', lang)} {SYNTHESE.periode}
                  </Badge>
                </div>
                <CardDescription className="mt-1 text-sm leading-relaxed dark:text-slate-400">
                  {t(SYNTHESE.resume, lang)}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {SYNTHESE.pointsDeVigilance.map((point, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50/80 dark:bg-amber-900/20 px-4 py-3"
                    >
                      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                      <p className="text-sm text-amber-900 dark:text-amber-200 leading-relaxed">{t(point, lang)}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </section>

          {/* ─── Module Tabs ──────────────────────────────────────────── */}
          <section aria-label={t('Sélection du module', lang)}>
            <Tabs
              value={activeTab}
              onValueChange={handleTabChange}
              className="w-full"
            >
              <TabsList
                className="h-auto flex-wrap gap-1.5 bg-muted/60 p-1.5 border border-border/60"
                aria-label={t('Sélection du module', lang)}
              >
                {ALL_MODULES.map((m) => {
                  const mColor = MODULE_COLORS[m.name]
                  const MIcon = ICON_MAP[MODULE_ICONS[m.name]] || BarChart3
                  const isActive = activeTab === m.name
                  return (
                    <TabsTrigger
                      key={m.name}
                      value={m.name}
                      className={
                        'module-tab-trigger gap-2 rounded-full px-4 py-2.5 transition-all ' +
                        (isActive ? 'data-[state=active]:text-white data-[state=active]:shadow-md' : 'text-muted-foreground')
                      }
                      style={
                        isActive
                          ? {
                              '--tab-active-bg': mColor,
                              boxShadow: `0 2px 8px ${mColor}40`,
                            } as React.CSSProperties
                          : undefined
                      }
                      aria-label={`Module ${m.name}`}
                    >
                      <MIcon className="h-4 w-4" />
                      <span className="hidden sm:inline">{tModule(m.name, lang)}</span>
                    </TabsTrigger>
                  )
                })}
              </TabsList>
            </Tabs>

            {/* Tab Content with Animation */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25, ease: 'easeInOut' }}
                className="mt-8"
              >
                <ModuleContent
                  module={activeModule}
                  startYear={startYear}
                  endYear={endYear}
                  selectedRegion={selectedRegion}
                  setSelectedRegion={setSelectedRegion}
                  mapIndicatorIndex={mapIndicatorIndex}
                  setMapIndicatorIndex={setMapIndicatorIndex}
                  onKPIClick={handleKPIClick}
                  lang={lang}
                  activeDetailIndicator={activeDetailIndicator}
                  setActiveDetailIndicator={setActiveDetailIndicator}
                />
              </motion.div>
            </AnimatePresence>
          </section>
        </div>
      </main>

      {/* ═══════════════════════════════════════════════════════════════════════ */}
      {/* ─── Royal Section ─────────────────────────────────────────────────── */}
      {/* ═══════════════════════════════════════════════════════════════════════ */}
      <section className="relative overflow-hidden bg-gradient-to-b from-[#006233] via-[#004d28] to-[#003319]">
        {/* Moroccan pattern overlay */}
        <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.4\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")' }} />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            {/* King Portrait */}
            <div className="shrink-0">
              <div className="relative">
                <div className="absolute -inset-3 bg-gradient-to-br from-[#FFD700]/30 to-[#C1272D]/20 rounded-2xl blur-lg" />
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Mohammed_VI_of_Morocco.jpg"
                  alt="Sa Majesté le Roi Mohammed VI"
                  className="relative w-48 h-48 sm:w-56 sm:h-56 object-cover rounded-2xl border-4 border-[#FFD700]/50 shadow-2xl"
                />
                <div className="absolute -bottom-2 -right-2 bg-[#FFD700] text-[#003319] text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                  Depuis 1999
                </div>
              </div>
            </div>

            {/* Royal Info */}
            <div className="text-center lg:text-left flex-1">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-2">
                {t('Sa Majesté le Roi Mohammed VI', lang)}
              </h2>
              <p className="text-[#FFD700] text-lg font-semibold mb-4">
                {t('Roi du Maroc — Depuis le 23 juillet 1999', lang)}
              </p>
              <p className="text-white/70 text-sm leading-relaxed max-w-2xl">
                {t("Sous le règne de Sa Majesté le Roi Mohammed VI, le Maroc a connu une transformation sans précédent avec des projets structurants d'envergure nationale et internationale, faisant du Royaume un pôle économique majeur en Afrique et dans le monde méditerranéen.", lang)}
              </p>

              {/* Reign Stats */}
              <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: t('Années de règne', lang), value: '26+', icon: <Crown className="h-7 w-7 text-[#FFD700]" /> },
                    { label: t('Projets structurants', lang), value: '50+', icon: <Building2 className="h-7 w-7 text-[#FFD700]" /> },
                    { label: t('PIB par habitant', lang), value: '+68%', icon: <TrendingUp className="h-7 w-7 text-[#FFD700]" /> },
                    { label: t('Investissements', lang), value: '300 Mds MAD', icon: <Landmark className="h-7 w-7 text-[#FFD700]" /> },
                  ].map((s) => (
                  <div key={s.label} className="bg-white/10 backdrop-blur-sm rounded-xl p-3 text-center border border-white/10">
                    <div className="flex justify-center">{s.icon}</div>
                    <p className="text-xl font-bold text-[#FFD700] mt-1">{s.value}</p>
                    <p className="text-[10px] text-white/60 uppercase tracking-wider">{s.label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        {/* Gold accent bar */}
        <div className="h-1 bg-gradient-to-r from-[#FFD700] via-[#C1272D] to-[#FFD700]" />
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════ */}
      {/* ─── Infrastructure Section ────────────────────────────────────────── */}
      {/* ═══════════════════════════════════════════════════════════════════════ */}
      <section className="bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">
              {t('Infrastructures Stratégiques du Royaume', lang)}
            </h2>
            <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              {t('Des projets structurants qui font du Maroc un hub logistique et industriel de premier plan en Afrique et dans le monde', lang)}
            </p>
            <div className="mt-4 h-1 w-24 mx-auto bg-gradient-to-r from-[#006233] via-[#FFD700] to-[#C1272D] rounded-full" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Tanger Med */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="h-48 relative overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/4/40/Tanger_Med_port.jpg" alt="Tanger Med Port" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <p className="text-white/90 text-xs font-semibold">{t('Port Conteneur #1 Afrique', lang)}</p>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg text-slate-900 dark:text-white group-hover:text-[#006233] transition-colors">{lang === 'en' ? 'Tanger Med' : 'Tanger Med'}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                  {t("1er port d'Afrique et de la Méditerranée", lang)}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-[10px] font-semibold bg-[#006233]/10 text-[#006233] px-2 py-0.5 rounded-full">9M TEUs</span>
                  <span className="text-[10px] font-semibold bg-[#FFD700]/20 text-amber-700 px-2 py-0.5 rounded-full">180+ ports</span>
                  <span className="text-[10px] font-semibold bg-[#C1272D]/10 text-[#C1272D] px-2 py-0.5 rounded-full">70 pays</span>
                </div>
              </div>
            </div>

            {/* Al Boraq TGV */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="h-48 relative overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Al_Boraq_Tangier.jpg/1280px-Al_Boraq_Tangier.jpg" alt="Al Boraq TGV" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <p className="text-white/90 text-xs font-semibold">{t("Premier TGV d'Afrique", lang)}</p>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg text-slate-900 dark:text-white group-hover:text-[#C1272D] transition-colors">Al Boraq TGV</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                  {t('LGV Tanger-Casablanca', lang)}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-[10px] font-semibold bg-[#C1272D]/10 text-[#C1272D] px-2 py-0.5 rounded-full">320 km/h</span>
                  <span className="text-[10px] font-semibold bg-[#FFD700]/20 text-amber-700 px-2 py-0.5 rounded-full">2h10</span>
                  <span className="text-[10px] font-semibold bg-[#006233]/10 text-[#006233] px-2 py-0.5 rounded-full">1ère Afrique</span>
                </div>
              </div>
            </div>

            {/* Maroc Numeric */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="h-48 relative overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Casablanca_Finance_City_37.jpg/1280px-Casablanca_Finance_City_37.jpg" alt="Maroc Numérique 2030" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <p className="text-white/90 text-xs font-semibold">{t('Réseau Numérique National', lang)}</p>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg text-slate-900 dark:text-white group-hover:text-[#D4A800] transition-colors">Maroc Numérique 2030</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                  {t('Stratégie numérique nationale', lang)}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-[10px] font-semibold bg-[#FFD700]/20 text-amber-700 px-2 py-0.5 rounded-full">66% Internet</span>
                  <span className="text-[10px] font-semibold bg-[#006233]/10 text-[#006233] px-2 py-0.5 rounded-full">12 tech cities</span>
                </div>
              </div>
            </div>

            {/* Noor Ouarzazate */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="h-48 relative overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Noor_1_and_2_-_Ouarzazate_Solar_Power_Station_%2848962353822%29.jpg/1280px-Noor_1_and_2_-_Ouarzazate_Solar_Power_Station_%2848962353822%29.jpg" alt="Noor Ouarzazate Solar Complex" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <p className="text-white/90 text-xs font-semibold">{t('Plus Grand Complexe Solaire', lang)}</p>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg text-slate-900 dark:text-white group-hover:text-amber-600 transition-colors">Noor Ouarzazate</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                  {t('Complexe solaire Noor', lang)}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-[10px] font-semibold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 px-2 py-0.5 rounded-full">580 MW</span>
                  <span className="text-[10px] font-semibold bg-[#006233]/10 text-[#006233] px-2 py-0.5 rounded-full">52% ENR 2030</span>
                </div>
              </div>
            </div>

            {/* Casablanca Finance City */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="h-48 relative overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/CFC_Casa_Tower.jpg/1280px-CFC_Casa_Tower.jpg" alt="Casablanca Finance City" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <p className="text-white/90 text-xs font-semibold">{t('Hub Financier Africain', lang)}</p>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg text-slate-900 dark:text-white group-hover:text-[#1e3a5f] transition-colors">Casablanca Finance City</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                  {t('Place financière Casablanca', lang)}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-[10px] font-semibold bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 px-2 py-0.5 rounded-full">350+ entreprises</span>
                  <span className="text-[10px] font-semibold bg-[#FFD700]/20 text-amber-700 px-2 py-0.5 rounded-full">Top 50 mondial</span>
                </div>
              </div>
            </div>

            {/* Ports & Logistics */}
            <div className="group relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm hover:shadow-xl transition-all duration-300">
              <div className="h-48 relative overflow-hidden">
                <img src="https://upload.wikimedia.org/wikipedia/commons/9/93/Thermal_power_station_of_Jorf_Lasfar.jpg" alt="Réseau Portuaire" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                <div className="absolute bottom-3 left-3 right-3">
                  <p className="text-white/90 text-xs font-semibold">{t('Réseau Portuaire National', lang)}</p>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg text-slate-900 dark:text-white group-hover:text-[#006233] transition-colors">{t('Réseau Portuaire', lang)}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                  {t('Réseau portuaire marocain', lang)}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="text-[10px] font-semibold bg-[#006233]/10 text-[#006233] px-2 py-0.5 rounded-full">35 ports</span>
                  <span className="text-[10px] font-semibold bg-[#C1272D]/10 text-[#C1272D] px-2 py-0.5 rounded-full">177 Mt/an</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════ */}
      {/* ─── Footer ──────────────────────────────────────────────────────────── */}
      {/* ═══════════════════════════════════════════════════════════════════════ */}
      <footer className="relative overflow-hidden bg-gradient-to-b from-[#003319] to-[#001a0d] text-white">
        {/* Zellige pattern */}
        <div className="absolute inset-0 opacity-3" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'80\' height=\'80\' viewBox=\'0 0 80 80\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M0 0l40 40-40 40L0 40zm40 0l40 40-40 40V0z\' fill=\'%23ffffff\' fill-opacity=\'0.03\'/%3E%3C/svg%3E")' }} />

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <img src="/logo.png" alt="MAROC STAT" className="h-12 w-12 rounded-lg object-contain bg-white/10 p-1" />
                <div>
                  <p className="font-bold text-lg text-[#FFD700]">MAROC STAT</p>
                  <p className="text-xs text-white/50">{t('Statistiques & Analyses Nationales', lang)}</p>
                </div>
              </div>
              <p className="text-sm text-white/60 leading-relaxed">
                {t("Plateforme d'analyse prédictive multi-domaines du Royaume du Maroc.", lang)}<br/>
                {t('Données officielles : HCP, BAM, MESRS.', lang)}
              </p>
            </div>

            {/* Sources */}
            <div>
              <h4 className="font-semibold text-[#FFD700] mb-4 text-sm uppercase tracking-wider">{t('Sources Officielles', lang)}</h4>
              <ul className="space-y-2 text-sm text-white/60">
                <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[#006233]" /> {t('Haut-Commissariat au Plan (HCP)', lang)}</li>
                <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[#C1272D]" /> {t('Bank Al-Maghrib (BAM)', lang)}</li>
                <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-[#FFD700]" /> {t("Ministère de l'Éducation", lang)}</li>
                <li className="flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-white/40" /> {t('Open Data Maroc (data.gov.ma)', lang)}</li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="font-semibold text-[#FFD700] mb-4 text-sm uppercase tracking-wider">{t('Informations', lang)}</h4>
              <ul className="space-y-2 text-sm text-white/60">
                <li>{t('Données sous Licence Ouverte', lang)}</li>
                <li>Version 1.0 — Juillet 2026</li>
                <li>{t('Développé par Youssef Amarzou', lang)}</li>
              </ul>
              <div className="mt-4 flex gap-2">
                <div className="h-1 w-8 rounded-full bg-[#C1272D]" />
                <div className="h-1 w-8 rounded-full bg-[#006233]" />
                <div className="h-1 w-8 rounded-full bg-[#FFD700]" />
              </div>
            </div>
          </div>

          <div className="border-t border-white/10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-white/40">
            <p>© 2026 MAROC STAT — {t('Tous droits réservés', lang)}</p>
            <p className="flex items-center gap-1">{t('Fait avec ❤️ pour le Maroc 🇲🇦', lang)}</p>
          </div>
        </div>
      </footer>
      </>)}
    </div>
  )
}
