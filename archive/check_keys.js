const fs = require('fs');
const data = fs.readFileSync('src/lib/rasd-data.ts', 'utf8');

const codes = ['SMIG', 'SMAG', 'POUVOIR_ACHAT', 'CHOMAGE', 'RECETTES_TOURISME_INTERNE', 'RECETTES_TOURISME', 'ARRIVEES_TOURISTIQUES'];

codes.forEach(code => {
  const pattern = new RegExp('code: "' + code + '"[\\s\\S]*?national: ts\\(([\\s\\S]*?)\\)');
  const m = data.match(pattern);
  if (m) {
    const vals = m[1].match(/\[\d+, [\d.]+\]/g) || [];
    console.log(code + ': ' + vals[0] + ' -> ' + vals[vals.length-1]);
  } else {
    console.log(code + ': NOT FOUND');
  }
});