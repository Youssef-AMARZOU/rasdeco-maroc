t = open('src/lib/rasd-data.ts', encoding='utf-8').read()
i = t.find('code: "PIB_CROISSANCE"')
if i == -1:
    print("PIB_CROISSANCE NOT FOUND!")
    # Try other patterns
    for q in ["'", '"']:
        i = t.find(f'code: {q}PIB_CROISSANCE{q}')
        if i >= 0:
            print(f"Found with quote: {q} at {i}")
else:
    print(f"PIB_CROISSANCE found at pos {i}")
    print(f"Context: {t[i-20:i+60]}")

# Count economie indicators
count = 0
for code in ['PIB_CROISSANCE','IPC_GLISSEMENT','CHOMAGE','TAUX_DIRECTEUR','DETTE_PUBLIQUE','RESERVES_CHANGE','IDE_FLUX','DEFICIT_BUDGET','PIB_PAR_HAB','BALANCE_COURANTE','SMIG','SMAG','POUVOIR_ACHAT','TRANSFERTS_MRE','PART_PIB_MRE','POPULATION','EXPORTATIONS','IMPORTATIONS','INVESTISSEMENT']:
    for q in ["'", '"']:
        if f'code: {q}{code}{q}' in t:
            count += 1
            break
    else:
        print(f"MISSING: {code}")

print(f"\nEconomie indicators found: {count}/19")
