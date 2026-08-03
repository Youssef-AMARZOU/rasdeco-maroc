import re

with open('src/lib/rasd-data.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all indicator code references
indicators = set()
for match in re.finditer(r'code:\s*"([^"]+)"', content):
    indicators.add(match.group(1))

# Check which ts_data keys are referenced
ts_keys = {"BALANCE.COMMERCIALE", "BAM.OPCVM.ENCOURS", "CHANGE.USD", "CHOMAGE.TAUX",
           "DEFICIT.BUDGET", "DEPENSES.TOTAL", "DETTE.PUBLIQUE", "EMPLOI.VOLUME",
           "EXPORT.MANUFACTURES", "IDE.FLUX", "IMPORT.ENERGIE", "INDICATEUR.HCP.GENERIQUE",
           "INVESTISSEMENT.PUBLIC", "IPC.INDICE", "PIB.TRIM.VOL", "RECETTES.FISCALES",
           "RESERVES.CHANGE"}

print("=== Indicator codes in rasd-data.ts ===")
for code in sorted(indicators):
    print(f"  {code}")
print(f"\nTotal: {len(indicators)}")

print("\n=== ts_data keys referenced in indicators ===")
for key in sorted(ts_keys):
    found = key in indicators
    print(f"  {key:30s} {'REFERENCED' if found else 'NOT REFERENCED'}")
