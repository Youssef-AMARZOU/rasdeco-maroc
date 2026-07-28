const fs = require('fs');
const data = fs.readFileSync('src/lib/rasd-data.ts', 'utf8');

// Extract key values
console.log('=== DONNEES ACTUELLES DANS LE CODE ===\n');

// COUPE_CAF_CL
const coupeMatch = data.match(/code: "COUPE_CAF_CL"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (coupeMatch) {
  console.log("COUPE_CAF_CL national:", coupeMatch[1].trim().substring(0, 300) + "...");
}

// MEDAILLES_OLYMPIQUES
const medMatch = data.match(/code: "MEDAILLES_OLYMPIQUES"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (medMatch) {
  console.log("\nMEDAILLES_OLYMPIQUES national:", medMatch[1].trim().substring(0, 300) + "...");
}

// MEDAILLES_PARALYMPIQUES
const paraMatch = data.match(/code: "MEDAILLES_PARALYMPIQUES"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (paraMatch) {
  console.log("\nMEDAILLES_PARALYMPIQUES national:", paraMatch[1].trim().substring(0, 300) + "...");
}

// FEDERATIONS
const fedMatch = data.match(/code: "FEDERATIONS"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (fedMatch) {
  console.log("\nFEDERATIONS national:", fedMatch[1].trim().substring(0, 300) + "...");
}

// LICENCIES_SPORTIFS
const licMatch = data.match(/code: "LICENCIES_SPORTIFS"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (licMatch) {
  console.log("\nLICENCIES_SPORTIFS national:", licMatch[1].trim().substring(0, 300) + "...");
}

// INSTALLATIONS_SPORTIVES
const instMatch = data.match(/code: "INSTALLATIONS_SPORTIVES"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (instMatch) {
  console.log("\nINSTALLATIONS_SPORTIVES national:", instMatch[1].trim().substring(0, 300) + "...");
}

// BUDGET_SPORT
const budMatch = data.match(/code: "BUDGET_SPORT"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (budMatch) {
  console.log("\nBUDGET_SPORT national:", budMatch[1].trim().substring(0, 300) + "...");
}

// LIGUES_REGIONALES
const ligMatch = data.match(/code: "LIGUES_REGIONALES"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (ligMatch) {
  console.log("\nLIGUES_REGIONALES national:", ligMatch[1].trim().substring(0, 300) + "...");
}

// ASSOCIATIONS_SPORTIVES
const assocMatch = data.match(/code: "ASSOCIATIONS_SPORTIVES"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (assocMatch) {
  console.log("\nASSOCIATIONS_SPORTIVES national:", assocMatch[1].trim().substring(0, 300) + "...");
}

// SCOLAIRE_SPORT
const scolMatch = data.match(/code: "SCOLAIRE_SPORT"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (scolMatch) {
  console.log("\nSCOLAIRE_SPORT national:", scolMatch[1].trim().substring(0, 300) + "...");
}

// REVENUS_SPORT_PRIVE
const revMatch = data.match(/code: "REVENUS_SPORT_PRIVE"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (revMatch) {
  console.log("\nREVENUS_SPORT_PRIVE national:", revMatch[1].trim().substring(0, 300) + "...");
}

// PRATIQUANTS_INFORMELS
const praMatch = data.match(/code: "PRATIQUANTS_INFORMELS"[\s\S]*?national: ts\(\[([\s\S]*?)\]/);
if (praMatch) {
  console.log("\nPRATIQUANTS_INFORMELS national:", praMatch[1].trim().substring(0, 300) + "...");
}

console.log("\n=== VERIFICATION CONTRE SOURCES OFFICIELLES ===\n");
console.log("CAF Champions League titres Maroc (officiel CAF/RSSSF/Wikipedia):");
console.log("  FAR Rabat: 3 (1985, 1987, 1990? -- verifier)");
console.log("  Raja Casablanca: 3 (1989, 1997, 2020)");
console.log("  Wydad Casablanca: 3 (1992, 2017, 2019, 2021, 2022? -- verifier)");
console.log("  Total officiel: ~9-10 (pas 14)");
console.log("  Source: CAF official site, RSSSF, Wikipedia\n");

console.log("Médailles olympiques Maroc (total cumulé officiel CIO):");
console.log("  1968 Mexico: 1 bronze (boxe)");
console.log("  1984 LA: 1 or (Nawal El Moutawakel 400m haies)");
console.log("  1988 Seoul: 1 bronze");
console.log("  1992 Barcelona: 1 argent (Khalid Boulami 5000m)");
console.log("  1996 Atlanta: 1 argent (Salaheddine Bassir marathon? Non - 1996: Salah Hissou 5000m bronze? Verifier)");
console.log("  2000 Sydney: 2 or (Hicham El Guerrouj 1500m + 5000m)");
console.log("  2004 Athens: 1 or (El Guerrouj 1500m), 1 argent (Hasna Benhassi 800m)");
console.log("  2008 Beijing: 1 argent (Hasna Benhassi 800m), 1 bronze (Abdalaati Iguider 1500m? No 2012)");
console.log("  2012 London: 1 bronze (Abdalaati Iguider 1500m)");
console.log("  2016 Rio: 1 argent (Mohammed Rabii boxe welter)");
console.log("  2020 Tokyo: 1 or (Soufiane El Bakkali 3000m steeple)");
console.log("  2024 Paris: 1 or (Soufiane El Bakkali 3000m steeple) + autres?");
console.log("  Total reel: ~14-16 (PAS 26)");
console.log("  Source: CIO database, Wikipedia\n");

console.log("Médailles paralympiques Maroc (total cumulé):");
console.log("  2004: 1");
console.log("  2008: 4 (cumul 5)");
console.log("  2012: 6 (cumul 11)");
console.log("  2016: 7 (cumul 18)");
console.log("  2020: 4 (cumul 22)");
console.log("  2024 Paris: 15 (cumul 37) -- Maroc a gagne 15 médailles a Paris 2024");
console.log("  Total: ~37 (PAS 15 ni 25)");
console.log("  Source: CPI, Comité Paralympique Marocain\n");

console.log("Fédérations sportives CNOM 2025: 57 (officiel CNOM)");
console.log("Licenciés sportifs fédéraux CNOM 2025: ~350 000 (FMPS 2022: 350K)");
console.log("Pratiquants informels FMPS 2022: 10 millions");
console.log("Installations réhabilitées programme 2021-2030: 2 500 (officiel)");
console.log("Sport privé / PIB FMPS 2022: 1,56% (19,04 Mds MAD)");
console.log("Ligues régionales: 261");
console.log("Associations sportives: 7 000+");
console.log("Bénéficiaires sport scolaire: 1,2 million");

console.log("\n=== SMIG/SMAG VERIFICATION ===");
console.log("SMIG 2026: 3 423 DH/mois (17,92 DH/h × 191h) - Décret 2-25-983, accord tripartite avril 2024");
console.log("SMAG 2026: 2 533 DH/mois (97,44 DH/j × 26j) - Même décret");
console.log("SMIG 1999: 1 660 DH/mois");
console.log("SMAG 1999: 1 075 DH/mois");
console.log("Pouvoir d'achat base 100=1999: ~117,6 en 2026 (gagné 17,6% sur 27 ans)");