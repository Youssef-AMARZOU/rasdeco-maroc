const fs = require('fs');
let data = fs.readFileSync('src/lib/rasd-data.ts', 'utf8');

// Fix specific lines that have genRegional but should be empty since they have isNationalOnly
// These are economy indicators at lines ~612, 628, 659, 675, 690, 705, 720, 738, 756, 774, 790, 806
// and agriculture at line 949, 1112

const fixes = [
  // PIB_CROISSANCE
  { find: '      regional: genRegional(2.5, 0.25),\n      regionalOld: genRegionalOld(2.5, 0.25),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // IPC_GLISSEMENT
  { find: '      regional: genRegional(1.1, 0.15),\n      regionalOld: genRegionalOld(1.1, 0.15),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // TAUX_DIRECTEUR
  { find: '      regional: genRegional(2.25, 0),\n      regionalOld: genRegionalOld(2.25, 0),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // DETTE_PUBLIQUE
  { find: '      regional: genRegional(75, 0.1),\n      regionalOld: genRegionalOld(75, 0.1),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // RESERVES_CHANGE
  { find: '      regional: genRegional(5.3, 0.08),\n      regionalOld: genRegionalOld(5.3, 0.08),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // IDE_FLUX
  { find: '      regional: genRegional(30, 0.3),\n      regionalOld: genRegionalOld(30, 0.3),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // DEFICIT_BUDGET
  { find: '      regional: genRegional(-3.9, 0.15),\n      regionalOld: genRegionalOld(-3.9, 0.15),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // SMIG
  { find: '      regional: genRegional(3423, 0.05),\n      regionalOld: genRegionalOld(3423, 0.05),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // SMAG
  { find: '      regional: genRegional(2533, 0.05),\n      regionalOld: genRegionalOld(2533, 0.05),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // POUVOIR_ACHAT
  { find: '      regional: genRegional(117, 0.05),\n      regionalOld: genRegionalOld(117, 0.05),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // TRANSFERTS_MRE
  { find: '      regional: genRegional(108.5, 0.08),\n      regionalOld: genRegionalOld(108.5, 0.08),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
  // BALANCE_COMMERCIALE
  { find: '      regional: genRegional(7.1, 0.05),\n      regionalOld: genRegionalOld(7.1, 0.05),\n      isNationalOnly: true,', replace: '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,' },
];

fixes.forEach(f => {
  if (data.includes(f.find)) {
    data = data.replace(f.find, f.replace);
    console.log('Fixed one');
  } else {
    console.log('NOT FOUND:', f.find.substring(0, 40));
  }
});

// Agriculture PROD_CEREALIERE
const agriFind = '      regional: genRegional(7.5, 0.4),\n      regionalOld: genRegionalOld(7.5, 0.4),';
const agriReplace = '      regional: genRegionalFromShares(AGRI_PRODUCTION_12, 7.5, true),\n      regionalOld: genRegionalFromShares(AGRI_PRODUCTION_12, 7.5, true),';
if (data.includes(agriFind)) {
  data = data.replace(agriFind, agriReplace);
  console.log('Fixed PROD_CEREALIERE');
} else {
  console.log('PROD_CEREALIERE not found');
}

// GRANDS_BARRAGES
const barFind = '      regional: genRegional(14, 0.4, true),\n      regionalOld: genRegionalOld(14, 0.4, true),';
const barReplace = '      regional: [],\n      regionalOld: [],\n      isNationalOnly: true,';
if (data.includes(barFind)) {
  data = data.replace(barFind, barReplace);
  console.log('Fixed GRANDS_BARRAGES');
} else {
  console.log('GRANDS_BARRAGES not found');
}

fs.writeFileSync('src/lib/rasd-data.ts', data);
console.log('Done');