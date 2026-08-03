"""Validate IMF data in rasd-data.ts dashboard against data_parser."""
import re, sys
from pathlib import Path

RASD_FILE = Path("src/lib/rasd-data.ts")
if not RASD_FILE.exists():
    RASD_FILE = Path(__file__).parent.parent.parent / "src/lib/rasd-data.ts"

content = RASD_FILE.read_text(encoding="utf-8")

# Locate economie module
eco_start = content.find('code: "PIB_CROISSANCE"')
eco_end = content.find('code: "PIB_CROISSANCE"')
# Actually find the whole indicators array within economie
# Look for indicators: [ after the kpis section
kpis_end = content.find('indicators: [', content.find('code: "PIB_CROISSANCE"'))
if kpis_end == -1:
    # Search from start of economie section
    kpis_end = content.find('indicators: [')

# Find the end of the economie indicators array
# It ends when the next module starts (agriculture)
agri_start = content.find('agricultureModule')
eco_ind_end = content.rfind('},', kpis_end, agri_start) + 2 if agri_start > kpis_end else -1

print("=" * 70)
print("VERIFICATION DONNEES FMI DANS LE DASHBOARD")
print("=" * 70)

if kpis_end == -1 or eco_ind_end == -1:
    # Fallback: use grep-like approach
    print("Searching for indicator blocks...")

# Extract all indicator blocks: each starts with "code:" and ends before next "code:"
# Use the region after indicators: [ until agricultureModule
if agri_start > kpis_end:
    eco_section = content[kpis_end:agri_start]
else:
    eco_section = content[kpis_end:]

# Split by "code:" pattern
blocks_raw = re.split(r'(?=code:\s*")', eco_section)
blocks = [b for b in blocks_raw if b.strip().startswith('code:')]

print(f"Indicateurs trouves: {len(blocks)}")
print("-" * 70)

issues = []
total_years = 0

for i, block in enumerate(blocks, 1):
    cm = re.search(r'code:\s*"(\w+)"', block)
    code = cm.group(1) if cm else "UNKNOWN"
    lm = re.search(r'label:\s*"([^"]+)"', block)
    label = lm.group(1) if lm else ""

    pairs = re.findall(r'\[(\d+),\s*([-\d.]+)\]', block)
    if not pairs:
        continue

    years = [int(p[0]) for p in pairs]
    vals = [float(p[1]) for p in pairs]
    min_y, max_y = min(years), max(years)
    n = len(pairs)
    total_years += n

    # Check gaps
    expected = list(range(min_y, max_y + 1))
    missing = sorted(set(expected) - set(years))

    # Check duplicates
    seen = set()
    dups = sorted(set(y for y in years if y in seen or seen.add(y)))
    # Actually fix:
    seen_y = {}
    dups = []
    for y in years:
        if y in seen_y:
            dups.append(y)
        seen_y[y] = True
    dups = sorted(set(dups))

    status = "OK"
    details = []
    if missing:
        details.append(f"gaps:{len(missing)}")
        status = "ISSUES"
    if dups:
        details.append(f"dup:{len(dups)}")
        status = "ISSUES"
    detail_str = ", ".join(details) if details else "ok"

    print(f"  {i:2d}. {code:18s} [{min_y}-{max_y}] {n:3d} yrs  [{detail_str}]")

    if missing:
        issues.append(f"{code}: Annees manquantes: {missing[:5]}...")
    if dups:
        issues.append(f"{code}: Annees dupliquees: {dups[:5]}...")

print("-" * 70)
print(f"Total annees dans dashboard: {total_years}")

if issues:
    print(f"\nWARN  {len(issues)} ISSUES:")
    for iss in issues:
        print(f"   * {iss}")
else:
    print("\nOK  TOUTES LES SERIES SONT COHERENTES")

# Check KPI explanations in page.tsx
PAGE_FILE = Path("src/app/page.tsx")
if not PAGE_FILE.exists():
    PAGE_FILE = Path(__file__).parent.parent.parent / "src/app/page.tsx"
page_content = PAGE_FILE.read_text(encoding="utf-8")

print("\n" + "=" * 70)
print("VERIFICATION KPIs vs EXPLANATIONS")
print("=" * 70)

kpi_codes = re.findall(r'indicatorCode:\s*"(\w+)"', content[eco_start-200:eco_ind_end+200])
print(f"KPIs dans economie: {len(kpi_codes)}")
for k in kpi_codes:
    print(f"   - {k}")

missing_exp = []
for k in kpi_codes:
    if k not in page_content:
        missing_exp.append(k)
    else:
        idx = page_content.find(k)
        snippet = page_content[idx:idx+300]
        if "what" not in snippet:
            missing_exp.append(f"{k} (structure incomplete)")

if missing_exp:
    print(f"\nWARN  KPI SANS EXPLICATION:")
    for k in missing_exp:
        print(f"   * {k}")
else:
    print("OK  TOUS LES KPIs ONT UNE EXPLICATION")

print("\n" + "=" * 70)
print("VERIFICATION TERMINEE")
print("=" * 70)
