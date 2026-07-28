const XLSX = require('xlsx');
const path = require('path');

// ============================================================
// DATA: Complete SMIG / SMAG / IPC / Pouvoir d'achat 1999-2026
// Source: Bank Al-Maghrib, Ministère de l'Emploi, Décrets officiels
// ============================================================

const ROWS = [
  { a:1999, smig_h:7.98, smig_m:1660, smig_a:19920, smag_j:41.36, smag_m:1075, smag_a:12900, ipc:0.8,   ev:'Stable depuis juil. 1996', evt:'-' },
  { a:2000, smig_h:8.78, smig_m:1826, smig_a:21912, smag_j:45.50, smag_m:1183, smag_a:14196, ipc:1.2,   ev:'+10% (juil. 2000)', evt:'Accord social 2000' },
  { a:2001, smig_h:8.78, smig_m:1826, smig_a:21912, smag_j:45.50, smag_m:1183, smag_a:14196, ipc:0.8,   ev:'-', evt:'-' },
  { a:2002, smig_h:8.78, smig_m:1826, smig_a:21912, smag_j:45.50, smag_m:1183, smag_a:14196, ipc:2.8,   ev:'-', evt:'-' },
  { a:2003, smig_h:8.78, smig_m:1826, smig_a:21912, smag_j:45.50, smag_m:1183, smag_a:14196, ipc:1.2,   ev:'-', evt:'-' },
  { a:2004, smig_h:9.66, smig_m:1845, smig_a:22140, smag_j:50.00, smag_m:1300, smag_a:15600, ipc:1.5,   ev:'+10% + 208h→191h', evt:'Décret, réforme durée travail' },
  { a:2005, smig_h:9.66, smig_m:1845, smig_a:22140, smag_j:50.00, smag_m:1300, smag_a:15600, ipc:2.4,   ev:'-', evt:'-' },
  { a:2006, smig_h:9.66, smig_m:1845, smig_a:22140, smag_j:50.00, smag_m:1300, smag_a:15600, ipc:3.3,   ev:'-', evt:'-' },
  { a:2007, smig_h:9.66, smig_m:1845, smig_a:22140, smag_j:50.00, smag_m:1300, smag_a:15600, ipc:3.3,   ev:'-', evt:'-' },
  { a:2008, smig_h:10.14, smig_m:1937, smig_a:23244, smag_j:52.50, smag_m:1365, smag_a:16380, ipc:3.7,   ev:'+5% (juin 2008)', evt:'Décret 2-08-205' },
  { a:2009, smig_h:10.64, smig_m:2032, smig_a:24384, smag_j:55.12, smag_m:1433, smag_a:17196, ipc:1.7,   ev:'+5% (juil. 2009)', evt:'Décret 2-09-271' },
  { a:2010, smig_h:10.64, smig_m:2032, smig_a:24384, smag_j:55.12, smag_m:1433, smag_a:17196, ipc:2.0,   ev:'-', evt:'-' },
  { a:2011, smig_h:11.70, smig_m:2235, smig_a:26820, smag_j:60.63, smag_m:1576, smag_a:18912, ipc:2.1,   ev:'+10% (sep. 2011)', evt:'Accord social 2011' },
  { a:2012, smig_h:12.24, smig_m:2338, smig_a:28056, smag_j:63.39, smag_m:1648, smag_a:19776, ipc:1.3,   ev:'+5% (juin 2012)', evt:'Décret 2-12-91' },
  { a:2013, smig_h:12.24, smig_m:2338, smig_a:28056, smag_j:63.39, smag_m:1648, smag_a:19776, ipc:1.9,   ev:'-', evt:'-' },
  { a:2014, smig_h:12.85, smig_m:2454, smig_a:29448, smag_j:66.56, smag_m:1731, smag_a:20772, ipc:1.5,   ev:'+5% (juin 2014)', evt:'Décret 2-14-130' },
  { a:2015, smig_h:13.46, smig_m:2571, smig_a:30852, smag_j:69.73, smag_m:1813, smag_a:21756, ipc:1.6,   ev:'+5% (juil. 2015)', evt:'Décret 2-15-53' },
  { a:2016, smig_h:13.46, smig_m:2571, smig_a:30852, smag_j:69.73, smag_m:1813, smag_a:21756, ipc:1.5,   ev:'-', evt:'-' },
  { a:2017, smig_h:13.46, smig_m:2571, smig_a:30852, smag_j:69.73, smag_m:1813, smag_a:21756, ipc:0.8,   ev:'-', evt:'-' },
  { a:2018, smig_h:13.46, smig_m:2571, smig_a:30852, smag_j:69.73, smag_m:1813, smag_a:21756, ipc:1.9,   ev:'-', evt:'-' },
  { a:2019, smig_h:14.13, smig_m:2699, smig_a:32388, smag_j:73.22, smag_m:1904, smag_a:22848, ipc:0.8,   ev:'+5% (juil. 2019)', evt:'Décret 2-19-562' },
  { a:2020, smig_h:14.81, smig_m:2829, smig_a:33948, smag_j:76.70, smag_m:1994, smag_a:23928, ipc:0.6,   ev:'+5% (juil. 2020)', evt:'Décret 2-20-470' },
  { a:2021, smig_h:14.81, smig_m:2829, smig_a:33948, smag_j:76.70, smag_m:1994, smag_a:23928, ipc:2.3,   ev:'-', evt:'-' },
  { a:2022, smig_h:15.55, smig_m:2970, smig_a:35640, smag_j:84.37, smag_m:2194, smag_a:26328, ipc:6.6,   ev:'+5% (sep. 2022)', evt:'Accord tripartite avril 2022' },
  { a:2023, smig_h:16.29, smig_m:3111, smig_a:37332, smag_j:88.58, smag_m:2303, smag_a:27636, ipc:6.1,   ev:'+5% (sep. 2023)', evt:'Phase 2 accord 2022' },
  { a:2024, smig_h:16.29, smig_m:3111, smig_a:37332, smag_j:88.58, smag_m:2303, smag_a:27636, ipc:0.9,   ev:'-', evt:'-' },
  { a:2025, smig_h:17.10, smig_m:3266, smig_a:39192, smag_j:93.00, smag_m:2418, smag_a:29016, ipc:1.0,   ev:'+5% jan.(SMIG) / +5% avr.(SMAG)', evt:'Accord tripartite avril 2024' },
  { a:2026, smig_h:17.92, smig_m:3423, smig_a:41076, smag_j:97.44, smag_m:2533, smag_a:30396, ipc:1.9,   ev:'+5% jan.(SMIG) / +5% avr.(SMAG)', evt:'Phase 2 accord 2024, Décret 2-25-983' },
];

// IPC cumulative index (base 1999 = 100)
let ipcIdx = 100;
const rows = ROWS.map(r => {
  ipcIdx = r.a === 1999 ? 100 : ipcIdx * (1 + r.ipc / 100);
  const smig_real = r.smig_m / ipcIdx * 100;
  const smig_ny_ratio = (17.92 * 8 * 30) / 3423; // SMIC NY monthly / SMIG MA
  const pouv = (r.smig_m / ipcIdx) / (1660 / 100) * 100;
  const smag_smig = (r.smag_m / r.smig_m * 100);
  const smig_mensuel_net = Math.round(r.smig_m * 0.9326); // after CNSS ~6.74%
  const smag_mensuel_net = Math.round(r.smag_m * 0.9326);
  return {
    Annee: r.a,
    'SMIG horaire (DH)': r.smig_h,
    'SMIG mensuel brut (DH)': r.smig_m,
    'SMIG mensuel net (DH)': smig_mensuel_net,
    'SMIG annuel brut (DH)': r.smig_a,
    'SMAG journalier (DH)': r.smag_j,
    'SMAG mensuel brut (DH)': r.smag_m,
    'SMAG mensuel net (DH)': smag_mensuel_net,
    'SMAG annuel brut (DH)': r.smag_a,
    'SMAG/SMIG (%)': Math.round(smag_smig * 10) / 10,
    'IPC inflation (%)': r.ipc,
    'IPC index (1999=100)': Math.round(ipcIdx * 100) / 100,
    'Pouvoir d\'achat (base 100)': Math.round(pouv * 10) / 10,
    'SMIG net NY comparaison': Math.round(smig_mensuel_net * smig_ny_ratio),
    'Ratio SMIG MA / SMIC NY': '1:' + Math.round(smig_ny_ratio),
    Evenement: r.ev,
    'Source / Décret': r.evt,
  };
});

// Monthly breakdown for each year (for the monthly sheet)
const monthlyRows = [];
for (const r of ROWS) {
  for (let m = 1; m <= 12; m++) {
    const netSmig = Math.round(r.smig_m * 0.9326);
    const netSmag = Math.round(r.smag_m * 0.9326);
    monthlyRows.push({
      Annee: r.a,
      Mois: m,
      'Nom du mois': ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'][m-1],
      'SMIG/h (DH)': r.smig_h,
      'SMIG mensuel brut': r.smig_m,
      'SMIG mensuel net': netSmig,
      'SMAG/j (DH)': r.smag_j,
      'SMAG mensuel brut': r.smag_m,
      'SMAG mensuel net': netSmag,
    });
  }
}

// Historical rate changes (the 10 revalorisations)
const revalorisations = [
  { Date:'01/07/1996', 'SMIG/h':7.98, 'SMAG/j':41.36, 'SMIG mensuel':1660, 'SMAG mensuel':1075, 'Taux SMIG':'Base', 'Taux SMAG':'Base', Commentaire:'Dernière revalorisation de la décennie 90' },
  { Date:'01/07/2000', 'SMIG/h':8.78, 'SMAG/j':45.50, 'SMIG mensuel':1826, 'SMAG mensuel':1183, 'Taux SMIG':'+10%', 'Taux SMAG':'+10%', Commentaire:'Accord social tripartite' },
  { Date:'01/07/2004', 'SMIG/h':9.66, 'SMAG/j':50.00, 'SMIG mensuel':1845, 'SMAG mensuel':1300, 'Taux SMIG':'+10% (h)', 'Taux SMAG':'+10%', Commentaire:'Passage de 208h à 191h/mois → hausse mensuelle = +1% seulement' },
  { Date:'01/06/2008', 'SMIG/h':10.14, 'SMAG/j':52.50, 'SMIG mensuel':1937, 'SMAG mensuel':1365, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-08-205' },
  { Date:'01/07/2009', 'SMIG/h':10.64, 'SMAG/j':55.12, 'SMIG mensuel':2032, 'SMAG mensuel':1433, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-09-271' },
  { Date:'01/09/2011', 'SMIG/h':11.70, 'SMAG/j':60.63, 'SMIG mensuel':2235, 'SMAG mensuel':1576, 'Taux SMIG':'+10%', 'Taux SMAG':'+10%', Commentaire:'Accord social post-Arab Spring' },
  { Date:'01/06/2012', 'SMIG/h':12.24, 'SMAG/j':63.39, 'SMIG mensuel':2338, 'SMAG mensuel':1648, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-12-91' },
  { Date:'01/06/2014', 'SMIG/h':12.85, 'SMAG/j':66.56, 'SMIG mensuel':2454, 'SMAG mensuel':1731, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-14-130' },
  { Date:'01/07/2015', 'SMIG/h':13.46, 'SMAG/j':69.73, 'SMIG mensuel':2571, 'SMAG mensuel':1813, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-15-53' },
  { Date:'01/07/2019', 'SMIG/h':14.13, 'SMAG/j':73.22, 'SMIG mensuel':2699, 'SMAG mensuel':1904, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-19-562' },
  { Date:'01/07/2020', 'SMIG/h':14.81, 'SMAG/j':76.70, 'SMIG mensuel':2829, 'SMAG mensuel':1994, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Décret 2-20-470' },
  { Date:'01/09/2022', 'SMIG/h':15.55, 'SMAG/j':84.37, 'SMIG mensuel':2970, 'SMAG mensuel':2194, 'Taux SMIG':'+5%', 'Taux SMAG':'+10%', Commentaire:'Accord tripartite avril 2022 - Phase 1' },
  { Date:'01/09/2023', 'SMIG/h':16.29, 'SMAG/j':88.58, 'SMIG mensuel':3111, 'SMAG mensuel':2303, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Phase 2 accord 2022' },
  { Date:'01/01/2025', 'SMIG/h':17.10, 'SMAG/j':93.00, 'SMIG mensuel':3266, 'SMAG mensuel':2418, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Accord tripartite avril 2024 - Phase 1' },
  { Date:'01/01/2026', 'SMIG/h':17.92, 'SMAG/j':97.44, 'SMIG mensuel':3423, 'SMAG mensuel':2533, 'Taux SMIG':'+5%', 'Taux SMAG':'+5%', Commentaire:'Phase 2 accord 2024 - Décret 2-25-983' },
];

// NY Comparison sheet
const NY_SMIC_HOURLY_USD = 16; // ~$16/hr NY SMIC 2026
const NY_SMIC_MONTHLY_USD = NY_SMIC_HOURLY_USD * 173.33; // ~2773 USD
const MAD_USD_2026 = 0.10; // ~10 MAD = 1 USD
const nyComp = ROWS.map(r => {
  const smigUSD = r.smig_m * MAD_USD_2026;
  const ratio = NY_SMIC_MONTHLY_USD / smigUSD;
  return {
    Annee: r.a,
    'SMIG Maroc (DH)': r.smig_m,
    'SMIG Maroc (USD)': Math.round(smigUSD),
    'SMIC NY (USD)': Math.round(NY_SMIC_MONTHLY_USD),
    'SMIC NY (DH)': Math.round(NY_SMIC_MONTHLY_USD / MAD_USD_2026),
    'Ratio NY/MA': '1:' + Math.round(ratio),
    'Pouvoir d\'achat Maroc (PPP)': Math.round(smigUSD * 3.6), // PPP multiplier
    'Pouvoir d\'achat NY (USD)': Math.round(NY_SMIC_MONTHLY_USD),
  };
});

// ============================================================
// BUILD WORKBOOK
// ============================================================

const wb = XLSX.utils.book_new();

// Sheet 1: Annuel complet
const ws1 = XLSX.utils.json_to_sheet(rows);
ws1['!cols'] = [
  { wch:8 }, { wch:16 }, { wch:20 }, { wch:18 }, { wch:18 },
  { wch:18 }, { wch:20 }, { wch:18 }, { wch:18 }, { wch:14 },
  { wch:14 }, { wch:20 }, { wch:20 }, { wch:22 }, { wch:20 },
  { wch:40 }, { wch:40 },
];
XLSX.utils.book_append_sheet(wb, ws1, 'SMIG-SMAG Annuel');

// Sheet 2: Mensuel complet (336 rows)
const ws2 = XLSX.utils.json_to_sheet(monthlyRows);
ws2['!cols'] = [
  { wch:8 }, { wch:6 }, { wch:12 }, { wch:14 }, { wch:18 },
  { wch:18 }, { wch:14 }, { wch:18 }, { wch:18 },
];
XLSX.utils.book_append_sheet(wb, ws2, 'SMIG-SMAG Mensuel');

// Sheet 3: Revalorisations historiques
const ws3 = XLSX.utils.json_to_sheet(revalorisations);
ws3['!cols'] = [
  { wch:12 }, { wch:10 }, { wch:10 }, { wch:14 }, { wch:14 },
  { wch:14 }, { wch:14 }, { wch:60 },
];
XLSX.utils.book_append_sheet(wb, ws3, 'Revalorisations');

// Sheet 4: Comparaison NY
const ws4 = XLSX.utils.json_to_sheet(nyComp);
ws4['!cols'] = [
  { wch:8 }, { wch:16 }, { wch:16 }, { wch:16 }, { wch:16 },
  { wch:14 }, { wch:22 }, { wch:22 },
];
XLSX.utils.book_append_sheet(wb, ws4, 'Comparaison NY');

// ============================================================
// ADD COLORS via sheet formatting
// ============================================================

function colorSheet(ws, headerColor, dataStartRow, altColor1, altColor2) {
  const range = XLSX.utils.decode_range(ws['!ref']);
  // Header row: bold + colored bg
  for (let c = range.s.c; c <= range.e.c; c++) {
    const cell = XLSX.utils.encode_cell({ r: 0, c });
    if (ws[cell]) {
      ws[cell].s = {
        font: { bold: true, color: { rgb: 'FFFFFF' }, sz: 11 },
        fill: { fgColor: { rgb: headerColor } },
        alignment: { horizontal: 'center', vertical: 'center', wrapText: true },
        border: {
          top: { style: 'thin', color: { rgb: '000000' } },
          bottom: { style: 'thin', color: { rgb: '000000' } },
          left: { style: 'thin', color: { rgb: '000000' } },
          right: { style: 'thin', color: { rgb: '000000' } },
        },
      };
    }
  }
  // Data rows: alternating colors
  for (let r = dataStartRow; r <= range.e.r; r++) {
    const color = (r - dataStartRow) % 2 === 0 ? altColor1 : altColor2;
    for (let c = range.s.c; c <= range.e.c; c++) {
      const cell = XLSX.utils.encode_cell({ r, c });
      if (ws[cell]) {
        ws[cell].s = {
          fill: { fgColor: { rgb: color } },
          border: {
            top: { style: 'thin', color: { rgb: 'D0D0D0' } },
            bottom: { style: 'thin', color: { rgb: 'D0D0D0' } },
            left: { style: 'thin', color: { rgb: 'D0D0D0' } },
            right: { style: 'thin', color: { rgb: 'D0D0D0' } },
          },
        };
      }
    }
  }
}

// Apply colors
colorSheet(ws1, '006233', 1, 'F0FFF0', 'FFFFFF');   // Green header, light green alternating
colorSheet(ws2, 'C1272D', 1, 'FFF0F0', 'FFFFFF');   // Red header, light red alternating
colorSheet(ws3, 'FFD700', 1, 'FFFFF0', 'FFFFFF');    // Gold header, light yellow alternating (fix: text color black for gold)
colorSheet(ws4, '1B4F72', 1, 'F0F4FF', 'FFFFFF');   // Blue header, light blue alternating

// Fix gold header text color (black on gold)
for (let c = 0; c <= 7; c++) {
  const cell = XLSX.utils.encode_cell({ r: 0, c });
  if (ws3[cell] && ws3[cell].s) {
    ws3[cell].s.font = { bold: true, color: { rgb: '000000' }, sz: 11 };
  }
}

// ============================================================
// WRITE FILE
// ============================================================
const filePath = path.join(__dirname, '..', 'docs', 'SMIG_SMAG_Maroc_Complet_1999_2026.xlsx');
XLSX.writeFile(wb, filePath);
console.log('✅ Excel complet créé:', filePath);
console.log('   - Feuille 1: SMIG-SMAG Annuel (28 lignes, 17 colonnes)');
console.log('   - Feuille 2: SMIG-SMAG Mensuel (336 lignes, 9 colonnes)');
console.log('   - Feuille 3: Revalorisations historiques (15 événements)');
console.log('   - Feuille 4: Comparaison NY');
