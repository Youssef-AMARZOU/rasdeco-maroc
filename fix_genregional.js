const fs = require('fs');
let data = fs.readFileSync('src/lib/rasd-data.ts', 'utf8');

// Fix all genRegional calls for indicators that have isNationalOnly: true
// Pattern: regional: genRegional(...),\n      regionalOld: genRegionalOld(...),\n      isNationalOnly: true,
const pattern = /(\s+)regional: genRegional\([^)]+\),\n\1      regionalOld: genRegionalOld\([^)]+\),\n\1      isNationalOnly: true,/g;
data = data.replace(pattern, '$1regional: [],\n$1      regionalOld: [],\n$1      isNationalOnly: true,');

fs.writeFileSync('src/lib/rasd-data.ts', data);
console.log('Fixed national-only indicators');