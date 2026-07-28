#!/usr/bin/env node
// ============================================================================
// generate-data-json.js
// Generates per-year JSON files in data/{domaine}/{year}.json
// and data/regions.json for the RASD-Maroc project.
// Run: node scripts/generate-data-json.js
// ============================================================================

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const DATA_DIR = path.join(ROOT, "data");

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function writeJSON(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n", "utf8");
}

const YEARS = [];
for (let y = 2015; y <= 2026; y++) YEARS.push(y);

// ============================================================================
// ÉCONOMIE
// ============================================================================
const economieData = {
  PIB:    { 2015:1.1, 2016:1.1, 2017:4.8, 2018:3.1, 2019:2.3, 2020:-7.2, 2021:8.0, 2022:1.3, 2023:3.0, 2024:3.8, 2025:4.6, 2026:4.8 },
  IPC:    { 2015:1.6, 2016:1.5, 2017:0.8, 2018:1.9, 2019:0.8, 2020:0.6, 2021:2.3, 2022:6.6, 2023:6.1, 2024:0.9, 2025:1.0, 2026:1.9 },
  CHOMAGE:{ 2015:10.1, 2016:10.5, 2017:10.3, 2018:10.0, 2019:10.6, 2020:11.9, 2021:12.3, 2022:11.8, 2023:13.0, 2024:13.3, 2025:13.0, 2026:10.8 },
  BAM:    { 2015:3.0, 2016:2.75, 2017:2.5, 2018:2.5, 2019:2.5, 2020:2.0, 2021:2.0, 2022:2.5, 2023:3.0, 2024:2.75, 2025:2.5, 2026:2.25 },
  DETTE:  { 2015:63.5, 2016:65.7, 2017:68.6, 2018:65.4, 2019:65.7, 2020:77.6, 2021:71.2, 2022:71.8, 2023:74.3, 2024:78.0, 2025:78.6, 2026:79.0 },
  RESERVES:{ 2015:6.0, 2016:5.5, 2017:4.5, 2018:5.3, 2019:6.0, 2020:5.5, 2021:6.5, 2022:5.2, 2023:5.0, 2024:5.5, 2025:5.2, 2026:5.3 },
  IDE:    { 2015:33.5, 2016:30.1, 2017:27.6, 2018:23.5, 2019:22.5, 2020:17.5, 2021:23.5, 2022:21.8, 2023:25.5, 2024:32.4, 2025:34.0, 2026:36.5 },
  DEFICIT:{ 2015:-3.7, 2016:-3.5, 2017:-3.5, 2018:-3.1, 2019:-3.6, 2020:-7.7, 2021:-6.4, 2022:-5.3, 2023:-4.7, 2024:-4.5, 2025:-4.2, 2026:-3.9 },
};

const economieKpis = [
  { code: "PIB_CROISSANCE",  label: "Croissance du PIB",        unit: "%" },
  { code: "IPC_GLISSEMENT",  label: "Inflation IPC",            unit: "%" },
  { code: "CHOMAGE",         label: "Taux de chômage",          unit: "%" },
  { code: "TAUX_DIRECTEUR",  label: "Taux directeur BAM",       unit: "%" },
  { code: "DETTE_PUBLIQUE",  label: "Dette publique / PIB",     unit: "% PIB" },
  { code: "RESERVES_CHANGE", label: "Réserves de change",       unit: "mois" },
  { code: "IDE_FLUX",        label: "Flux d'IDE",               unit: "MM MAD" },
  { code: "DEFICIT_BUDGET",  label: "Déficit budgétaire",       unit: "% PIB" },
];

const economieValues = {
  PIB_CROISSANCE:  economieData.PIB,
  IPC_GLISSEMENT:  economieData.IPC,
  CHOMAGE:         economieData.CHOMAGE,
  TAUX_DIRECTEUR:  economieData.BAM,
  DETTE_PUBLIQUE:  economieData.DETTE,
  RESERVES_CHANGE: economieData.RESERVES,
  IDE_FLUX:        economieData.IDE,
  DEFICIT_BUDGET:  economieData.DEFICIT,
};

// ============================================================================
// AGRICULTURE
// ============================================================================
const agricultureData = {
  CEREALES: { 2015:75.6, 2016:43.5, 2017:54.7, 2018:65.5, 2019:45.2, 2020:36.3, 2021:33.0, 2022:31.2, 2023:32.8, 2024:44.0, 2025:44.0, 2026:90.0 },
  VA_AGRICOLE: {
    2015: 66.0, 2016: 72.0, 2017: 82.0, 2018: 91.0, 2019: 98.0,
    2020: 85.0, 2021: 95.0, 2022: 100.0, 2023: 110.0, 2024: 118.0, 2025: 124.0, 2026: 130.5,
  },
  SUPERFICIE: {
    2015: 8.5, 2016: 8.7, 2017: 8.9, 2018: 9.1, 2019: 9.3,
    2020: 9.4, 2021: 9.5, 2022: 9.6, 2023: 9.8, 2024: 10.0, 2025: 10.0, 2026: 10.2,
  },
  EXPORT_AGRICOLE: {
    2015: 25.0, 2016: 28.0, 2017: 32.0, 2018: 38.0, 2019: 42.0,
    2020: 38.0, 2021: 48.0, 2022: 52.0, 2023: 58.0, 2024: 65.0, 2025: 66.0, 2026: 68.0,
  },
  RENDEMENT_CEREALIER: {
    2015: 12.0, 2016: 10.5, 2017: 11.5, 2018: 13.0, 2019: 10.8,
    2020: 10.2, 2021: 10.0, 2022: 9.8, 2023: 10.5, 2024: 14.0, 2025: 14.5, 2026: 18.2,
  },
  REMPLISSAGE_BARRAGES: {
    2015: 58, 2016: 30, 2017: 40, 2018: 52, 2019: 48,
    2020: 35, 2021: 60, 2022: 28, 2023: 32, 2024: 55, 2025: 42, 2026: 68,
  },
};

const agricultureKpis = [
  { code: "PROD_CEREALIERE",       label: "Production céréalière",       unit: "M qx" },
  { code: "VA_AGRICOLE",           label: "Valeur ajoutée agricole",     unit: "MM MAD" },
  { code: "SUPERFICIE_CULTIVEE",   label: "Superficie cultivée",         unit: "M ha" },
  { code: "EXPORT_AGRICOLE",       label: "Exportations agricoles",      unit: "MM MAD" },
  { code: "RENDEMENT_CEREALIER",   label: "Rendement céréalier moyen",   unit: "qx/ha" },
  { code: "REMPLISSAGE_BARRAGES",  label: "Remplissage des barrages",    unit: "%" },
];

const agricultureValues = {
  PROD_CEREALIERE:      agricultureData.CEREALES,
  VA_AGRICOLE:          agricultureData.VA_AGRICOLE,
  SUPERFICIE_CULTIVEE:  agricultureData.SUPERFICIE,
  EXPORT_AGRICOLE:      agricultureData.EXPORT_AGRICOLE,
  RENDEMENT_CEREALIER:  agricultureData.RENDEMENT_CEREALIER,
  REMPLISSAGE_BARRAGES: agricultureData.REMPLISSAGE_BARRAGES,
};

// ============================================================================
// EDUCATION
// ============================================================================
const educationData = {
  SCOLARISATION_PRIMAIRE: {
    2015: 96.5, 2016: 97.0, 2017: 97.2, 2018: 97.5, 2019: 97.8,
    2020: 98.0, 2021: 98.2, 2022: 98.5, 2023: 98.8, 2024: 99.0, 2025: 99.1, 2026: 99.2,
  },
  SCOLARISATION_COLLEGE: {
    2015: 68.0, 2016: 70.0, 2017: 72.0, 2018: 74.0, 2019: 76.0,
    2020: 78.0, 2021: 80.0, 2022: 82.0, 2023: 84.0, 2024: 85.9, 2025: 86.5, 2026: 87.5,
  },
  ENSEIGNANTS: {
    2015: 200.0, 2016: 205.0, 2017: 210.0, 2018: 215.0, 2019: 220.0,
    2020: 224.0, 2021: 228.0, 2022: 232.0, 2023: 237.0, 2024: 242.1, 2025: 245.0, 2026: 248.5,
  },
  ETABLISSEMENTS: {
    2015: 12.5, 2016: 12.8, 2017: 13.1, 2018: 13.5, 2019: 13.9,
    2020: 14.2, 2021: 14.6, 2022: 15.0, 2023: 15.5, 2024: 15.9, 2025: 16.0, 2026: 16.2,
  },
  ABANDON_PRIMAIRE: {
    2015: 7.0, 2016: 6.5, 2017: 6.0, 2018: 5.5, 2019: 5.2,
    2020: 5.0, 2021: 4.8, 2022: 4.5, 2023: 4.2, 2024: 3.8, 2025: 3.5, 2026: 3.2,
  },
  ETUDIANTS_TOTAL: {
    2015: 850, 2016: 900, 2017: 950, 2018: 1000, 2019: 1050,
    2020: 1080, 2021: 1120, 2022: 1160, 2023: 1200, 2024: 1250, 2025: 1280, 2026: 1300,
  },
};

const educationKpis = [
  { code: "SCOLARISATION_PRIMAIRE", label: "Taux de scolarisation (6-11 ans)", unit: "%" },
  { code: "SCOLARISATION_COLLEGE",  label: "Taux de scolarisation (12-14 ans)", unit: "%" },
  { code: "ENSEIGNANTS",            label: "Nombre d'enseignants",             unit: "K" },
  { code: "ETABLISSEMENTS",         label: "Établissements scolaires",         unit: "K" },
  { code: "ABANDON_PRIMAIRE",       label: "Taux d'abandon primaire",          unit: "%" },
  { code: "ETUDIANTS_TOTAL",        label: "Étudiants inscrits (supérieur)",   unit: "K" },
];

const educationValues = {
  SCOLARISATION_PRIMAIRE: educationData.SCOLARISATION_PRIMAIRE,
  SCOLARISATION_COLLEGE:  educationData.SCOLARISATION_COLLEGE,
  ENSEIGNANTS:            educationData.ENSEIGNANTS,
  ETABLISSEMENTS:         educationData.ETABLISSEMENTS,
  ABANDON_PRIMAIRE:       educationData.ABANDON_PRIMAIRE,
  ETUDIANTS_TOTAL:        educationData.ETUDIANTS_TOTAL,
};

// ============================================================================
// SANTÉ
// ============================================================================
const santeData = {
  LITS_HOPITAL: {
    2015: 20.5, 2016: 21.0, 2017: 21.8, 2018: 22.5, 2019: 23.2,
    2020: 24.0, 2021: 24.8, 2022: 25.5, 2023: 26.5, 2024: 27.8, 2025: 28.0, 2026: 28.4,
  },
  MEDECINS: {
    2015: 12.0, 2016: 13.5, 2017: 15.0, 2018: 17.0, 2019: 19.0,
    2020: 21.0, 2021: 23.0, 2022: 25.5, 2023: 28.0, 2024: 30.5, 2025: 31.5, 2026: 32.8,
  },
  RATIO_MEDECINS: {
    2015: 3.6, 2016: 4.0, 2017: 4.4, 2018: 5.0, 2019: 5.5,
    2020: 6.0, 2021: 6.6, 2022: 7.2, 2023: 7.8, 2024: 8.2, 2025: 8.5, 2026: 8.8,
  },
  COUVERTURE_MEDICALE: {
    2015: 35.0, 2016: 38.0, 2017: 42.0, 2018: 46.0, 2019: 50.0,
    2020: 52.0, 2021: 55.0, 2022: 58.0, 2023: 62.0, 2024: 66.1, 2025: 69.0, 2026: 72.4,
  },
  ESPERANCE_VIE: {
    2015: 73.5, 2016: 73.8, 2017: 74.2, 2018: 74.5, 2019: 74.8,
    2020: 75.0, 2021: 75.5, 2022: 76.0, 2023: 76.4, 2024: 76.8, 2025: 77.0, 2026: 77.1,
  },
};

const santeKpis = [
  { code: "LITS_HOPITAL",       label: "Lits d'hôpital",                 unit: "K" },
  { code: "MEDECINS",           label: "Médecins",                       unit: "K" },
  { code: "RATIO_MEDECINS",     label: "Ratio médecins/1000 hab",        unit: "‰" },
  { code: "COUVERTURE_MEDICALE", label: "Taux de couverture médicale",   unit: "%" },
  { code: "ESPERANCE_VIE",      label: "Espérance de vie",               unit: "ans" },
];

const santeValues = {
  LITS_HOPITAL:       santeData.LITS_HOPITAL,
  MEDECINS:           santeData.MEDECINS,
  RATIO_MEDECINS:     santeData.RATIO_MEDECINS,
  COUVERTURE_MEDICALE: santeData.COUVERTURE_MEDICALE,
  ESPERANCE_VIE:      santeData.ESPERANCE_VIE,
};

// ============================================================================
// SOCIAL
// ============================================================================
const socialData = {
  PAUVRETE: {
    2015: 8.0, 2016: 7.5, 2017: 7.0, 2018: 6.5, 2019: 6.0,
    2020: 5.5, 2021: 5.2, 2022: 4.8, 2023: 4.5, 2024: 4.2, 2025: 4.0, 2026: 3.9,
  },
  COUVERTURE_AMO: {
    2015: 5.0, 2016: 8.0, 2017: 12.0, 2018: 18.0, 2019: 25.0,
    2020: 30.0, 2021: 38.0, 2022: 45.0, 2023: 52.0, 2024: 58.4, 2025: 60.0, 2026: 62.8,
  },
  GINI: {
    2015: 0.410, 2016: 0.408, 2017: 0.406, 2018: 0.404, 2019: 0.402,
    2020: 0.400, 2021: 0.399, 2022: 0.398, 2023: 0.397, 2024: 0.398, 2025: 0.396, 2026: 0.395,
  },
  POP_ACTIVE: {
    2015: 10.5, 2016: 10.7, 2017: 10.9, 2018: 11.1, 2019: 11.3,
    2020: 11.5, 2021: 11.6, 2022: 11.8, 2023: 12.0, 2024: 12.1, 2025: 12.2, 2026: 12.4,
  },
  URBANISATION: {
    2015: 59.0, 2016: 59.5, 2017: 60.0, 2018: 60.5, 2019: 61.0,
    2020: 61.5, 2021: 62.0, 2022: 62.5, 2023: 63.0, 2024: 63.5, 2025: 63.8, 2026: 64.1,
  },
};

const socialKpis = [
  { code: "PAUVRETE",       label: "Taux de pauvreté",       unit: "%" },
  { code: "COUVERTURE_AMO", label: "Taux de couverture AMO",  unit: "%" },
  { code: "GINI",           label: "Indice de Gini",          unit: "" },
  { code: "POP_ACTIVE",     label: "Population active",       unit: "M" },
  { code: "URBANISATION",   label: "Taux d'urbanisation",     unit: "%" },
];

const socialValues = {
  PAUVRETE:       socialData.PAUVRETE,
  COUVERTURE_AMO: socialData.COUVERTURE_AMO,
  GINI:           socialData.GINI,
  POP_ACTIVE:     socialData.POP_ACTIVE,
  URBANISATION:   socialData.URBANISATION,
};

// ============================================================================
// SPORT
// ============================================================================
const sportData = {
  LICENCIES: {
    2015: 0.80, 2016: 0.90, 2017: 1.05, 2018: 1.20, 2019: 1.40,
    2020: 1.30, 2021: 1.60, 2022: 2.00, 2023: 2.40, 2024: 2.90, 2025: 3.10, 2026: 3.20,
  },
  INSTALLATIONS: {
    2015: 8.0, 2016: 8.5, 2017: 9.0, 2018: 9.5, 2019: 10.0,
    2020: 10.5, 2021: 11.0, 2022: 12.0, 2023: 13.0, 2024: 14.2, 2025: 14.5, 2026: 14.8,
  },
  FEDERATIONS: {
    2015: 60, 2016: 62, 2017: 64, 2018: 66, 2019: 68,
    2020: 70, 2021: 72, 2022: 74, 2023: 76, 2024: 78, 2025: 80, 2026: 82,
  },
  BUDGET_SPORT: {
    2015: 0.18, 2016: 0.20, 2017: 0.22, 2018: 0.24, 2019: 0.26,
    2020: 0.27, 2021: 0.29, 2022: 0.32, 2023: 0.35, 2024: 0.38, 2025: 0.40, 2026: 0.42,
  },
  CLASSEMENT_FIFA: {
    2015: 42, 2016: 38, 2017: 35, 2018: 30, 2019: 28,
    2020: 26, 2021: 22, 2022: 18, 2023: 14, 2024: 13, 2025: 12, 2026: 12,
  },
  MEDAILLES: {
    2015: 25, 2016: 30, 2017: 35, 2018: 45, 2019: 55,
    2020: 50, 2021: 65, 2022: 80, 2023: 100, 2024: 128, 2025: 138, 2026: 145,
  },
};

const sportKpis = [
  { code: "LICENCIES",          label: "Licenciés sportifs",          unit: "M" },
  { code: "INSTALLATIONS",      label: "Installations sportives",     unit: "K" },
  { code: "FEDERATIONS",        label: "Fédérations affiliées",       unit: "" },
  { code: "BUDGET_SPORT",       label: "Budget sport / PIB",          unit: "% PIB" },
  { code: "CLASSEMENT_FIFA",    label: "Classement mondial (foot)",   unit: "e place" },
  { code: "MEDAILLES",          label: "Médailles internationales",   unit: "" },
];

const sportValues = {
  LICENCIES:          sportData.LICENCIES,
  INSTALLATIONS:      sportData.INSTALLATIONS,
  FEDERATIONS:        sportData.FEDERATIONS,
  BUDGET_SPORT:       sportData.BUDGET_SPORT,
  CLASSEMENT_FIFA:    sportData.CLASSEMENT_FIFA,
  MEDAILLES:          sportData.MEDAILLES,
};

// ============================================================================
// DOMAIN CONFIGURATIONS
// ============================================================================
const DOMAINS = [
  {
    key: "economie",
    domaine: "Économie",
    source: "HCP/BAM",
    kpis: economieKpis,
    values: economieValues,
  },
  {
    key: "agriculture",
    domaine: "Agriculture",
    source: "HCP/MINA",
    kpis: agricultureKpis,
    values: agricultureValues,
  },
  {
    key: "education",
    domaine: "Éducation",
    source: "MESRS/HCP",
    kpis: educationKpis,
    values: educationValues,
  },
  {
    key: "sante",
    domaine: "Santé",
    source: "HCP/DGS",
    kpis: santeKpis,
    values: santeValues,
  },
  {
    key: "social",
    domaine: "Social",
    source: "HCP/MDJS",
    kpis: socialKpis,
    values: socialValues,
  },
  {
    key: "sport",
    domaine: "Sport",
    source: "HCP/AMSED",
    kpis: sportKpis,
    values: sportValues,
  },
];

// ============================================================================
// REGIONS
// ============================================================================
const regions = {
  pre2015: [
    "Chaouia-Ouardigha",
    "Doukkala-Abda",
    "Fès-Boulemane",
    "Gharb-Chrarda-Beni Hssen",
    "Grand Casablanca",
    "Guelmim-Es Semara",
    "Laâyoune-Boujdour-Sakia el Hamra",
    "Marrakech-Tensift-Al Haouz",
    "Meknès-Tafilalet",
    "L'Oriental",
    "Oued ed Dahab-Lagouira",
    "Rabat-Salé-Zemmour-Zaër",
    "Souss-Massa-Drâa",
    "Tadla-Azilal",
    "Tanger-Tétouan",
    "Taza-Al Hoceïma-Taounate",
  ],
  post2015: [
    "Tanger-Tétouan-Al Hoceima",
    "Oriental",
    "Fès-Meknès",
    "Rabat-Salé-Kénitra",
    "Béni Mellal-Khénifra",
    "Casablanca-Settat",
    "Marrakech-Safi",
    "Drâa-Tafilalet",
    "Souss-Massa",
    "Guelmim-Oued Noun",
    "Laâyoune-Sakia El Hamra",
    "Dakhla-Oued Ed-Dahab",
  ],
};

// ============================================================================
// GENERATE FILES
// ============================================================================
let totalFiles = 0;

for (const domain of DOMAINS) {
  const domainDir = path.join(DATA_DIR, domain.key);
  ensureDir(domainDir);

  for (const year of YEARS) {
    const prevYear = year - 1;

    const kpis = domain.kpis.map((kpi) => {
      const yearValues = domain.values[kpi.code];
      const value = yearValues[year] ?? 0;
      const previousValue = prevYear >= 2015 ? (yearValues[prevYear] ?? value) : value;
      return {
        label: kpi.label,
        value,
        unit: kpi.unit,
      };
    });

    const indicators = {};
    for (const kpi of domain.kpis) {
      indicators[kpi.code] = domain.values[kpi.code][year] ?? 0;
    }

    const fileData = {
      year,
      domaine: domain.domaine,
      kpis,
      indicators,
      source: domain.source,
    };

    const filePath = path.join(domainDir, `${year}.json`);
    writeJSON(filePath, fileData);
    totalFiles++;
  }
}

// regions.json
const regionsPath = path.join(DATA_DIR, "regions.json");
writeJSON(regionsPath, regions);
totalFiles++;

// ============================================================================
// SUMMARY
// ============================================================================
console.log(`\n✅ Generated ${totalFiles} JSON files in data/\n`);
console.log("Domains:");
for (const domain of DOMAINS) {
  console.log(`  ${domain.key}/  → 2015.json .. 2026.json (${domain.kpis.length} indicators each)`);
}
console.log(`  regions.json  → pre2015: ${regions.pre2015.length} regions, post2015: ${regions.post2015.length} regions`);
console.log(`\nTotal: ${DOMAINS.length} domains × ${YEARS.length} years = ${DOMAINS.length * YEARS.length} year files + 1 regions.json = ${totalFiles} files\n`);
