const fs = require('fs');
const data = fs.readFileSync('src/lib/rasd-data.ts', 'utf8');

function extractIndicator(code) {
  const pattern = new RegExp('code: "' + code + '"[\\s\\S]*?national: ts\\((\\[[\\s\\S]*?\\])\\)');
  const match = data.match(pattern);
  if (!match) return null;
  return match[1].trim().split('],').map(s => s.trim() + ']').filter(s => s.includes('['));
}

const indicators = [
  'CHOMAGE', 'PIB_CROISSANCE', 'IPC_GLISSEMENT', 'DETTE_PUBLIQUE',
  'PAUVRETE', 'COUVERTURE_AMO', 'GINI', 'POP_ACTIVE', 'URBANISATION', 'IDH',
  'SCOLARISATION_PRIMAIRE', 'SCOLARISATION_COLLEGE', 'ABANDON_PRIMAIRE',
  'RATIO_MEDECINS', 'COUVERTURE_MEDICALE', 'ESPERANCE_VIE',
  'VA_AGRICOLE', 'SUPERFICIE_CULTIVEE', 'EXPORT_AGRICOLE', 'RENDEMENT_CEREALIER',
  'PRODUCTION_FRUITS', 'CHEPTEL_BOVIN', 'CHEPTEL_OVIN', 'SUPERFICIE_ARBRES_FRUITERS',
  'EAU_POTABLE', 'CAPACITE_DESSALEMENT', 'EAU_TRAITEE_ONEP', 'ACCES_EAU_POTABLE', 'STRESS_HYDRIQUE',
  'ARRIVEES_TOURISTIQUES', 'RECETTES_TOURISME', 'NUITEES', 'TAUX_OCCUPATION',
  'CAPACITE_HOTELIERE', 'EMPLOI_TOURISME', 'DEPENSE_MOYENNE_TOURISTE',
  'PASSAGERS_AEROPORT', 'TOURISTES_MRE', 'TOURISME_INTERNE', 'RECETTES_TOURISME_INTERNE',
  'SMIG_MENSUEL', 'SMAG_MENSUEL', 'POUVOIR_ACHAT'
];

console.log('=== VERIFICATION INDICATEURS CLES ===\n');
indicators.forEach(code => {
  const vals = extractIndicator(code);
  if (vals) {
    const first = vals[0];
    const last = vals[vals.length-1];
    console.log(code + ': ' + first + ' -> ' + last + ' (' + vals.length + ' pts)');
  } else {
    console.log(code + ': NOT FOUND');
  }
});

console.log('\n=== VALEURS 2024/2026 ===');
const keyCodes = ['CHOMAGE', 'PIB_CROISSANCE', 'PAUVRETE', 'ARRIVEES_TOURISTIQUES', 'RECETTES_TOURISME', 'SMIG_MENSUEL', 'SMAG_MENSUEL', 'POUVOIR_ACHAT'];
keyCodes.forEach(code => {
  const vals = extractIndicator(code);
  if (vals) {
    const v2024 = vals.find(v => v.includes('[2024'));
    const v2026 = vals.find(v => v.includes('[2026'));
    console.log(code + ' 2024: ' + (v2024 || 'N/A') + ' | 2026: ' + (v2026 || 'N/A'));
  }
});

console.log('\n=== SPORT INDICATORS ===');
const sportCodes = ['COUPE_CAF_CL', 'COUPE_CAF_CONF', 'MEDAILLES_OLYMPIQUES', 'MEDAILLES_PARALYMPIQUES', 
  'LICENCIES_SPORTIFS', 'INSTALLATIONS_SPORTIVES', 'BUDGET_SPORT', 'FEDERATIONS', 
  'LIGUES_REGIONALES', 'ASSOCIATIONS_SPORTIVES', 'SCOLAIRE_SPORT', 'REVENUS_SPORT_PRIVE', 'PRATIQUANTS_INFORMELS'];
sportCodes.forEach(code => {
  const vals = extractIndicator(code);
  if (vals) {
    const first = vals[0];
    const last = vals[vals.length-1];
    console.log(code + ': ' + first + ' -> ' + last);
  }
});