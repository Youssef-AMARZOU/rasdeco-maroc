import polars as pl

pf = r"C:\Users\youss\OneDrive\Desktop\Yoyo\data\curated\economie\fact_indicateurs.parquet"
df = pl.read_parquet(pf)

print("=== FINAL PARQUET VERIFICATION ===")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns}")
print()

print("=== code_indicateur (37 unique) ===")
for c in sorted(df["code_indicateur"].unique().to_list()):
    n = df.filter(pl.col("code_indicateur") == c).height
    print(f"  {c:<35s} {n:>5d} rows")

print()
print("=== unite (standardized) ===")
for u in sorted(df["unite"].unique().to_list()):
    print(f"  {repr(u)}")

print()
print("=== domaine_code ===")
for d in sorted(df["domaine_code"].unique().to_list()):
    n = df.filter(pl.col("domaine_code") == d).height
    print(f"  {d:<12s} {n:>5d} rows")

print()
print("=== source_code ===")
for s in sorted(df["source_code"].unique().to_list()):
    n = df.filter(pl.col("source_code") == s).height
    print(f"  {s:<10s} {n:>5d} rows")

print()
print("=== Any Arabic still present? ===")
import unicodedata
for col in ["code_indicateur", "unite", "domaine_code", "date_label"]:
    vals = df[col].drop_nulls().unique().to_list()
    for v in vals:
        s = str(v)
        has_arabic = any(0x0600 <= ord(ch) <= 0x06FF for ch in s)
        if has_arabic:
            print(f"  ARABIC in {col}: {repr(s[:80])}")
print("  (check done)")
