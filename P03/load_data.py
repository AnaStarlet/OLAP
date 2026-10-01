"""
Z03. Load CSV from data/raw/ into DuckDB.
Jewelry retail chain, Belarus. 13 tables.

Re-run safe:
- first DELETE FROM (facts -> dimensions),
- then COPY.
So re-run does NOT double the fact rows.
"""
import duckdb
from pathlib import Path

DB  = "warehouse.duckdb"
RAW = Path("data/raw")
DDL = Path("sql/ddl_duckdb.sql")

TABLES = [
    # dimensions
    "dim_store", "dim_warehouse", "dim_supplier",
    "dim_product", "dim_customer", "dim_employee", "dim_date",
    # facts
    "fact_visits", "fact_interest", "fact_sales",
    "fact_loyalty", "fact_logistics", "fact_inventory",
]

def main():
    if not RAW.exists():
        raise SystemExit(f"No folder {RAW}. Put 13 CSV into data/raw/")

    if not DDL.exists():
        raise SystemExit(f"No file {DDL}. Put DDL first.")

    con = duckdb.connect(DB)

    # 1. DDL
    print("1) Creating tables from sql/ddl_duckdb.sql ...")
    con.execute(DDL.read_text(encoding="utf-8"))

    # 2. Clear tables (facts -> dimensions)
    print("2) Clearing tables (DELETE FROM) ...")
    for t in reversed(TABLES):
        con.execute(f"DELETE FROM {t};")

    # 3. Load CSV
    print("3) Loading CSV ...")
    for t in TABLES:
        csv = RAW / f"{t}.csv"
        if not csv.exists():
            print(f"   SKIP: {csv} not found")
            continue
        con.execute(f"""
            COPY {t} FROM '{csv.as_posix()}'
            (HEADER, DELIMITER ',', QUOTE '"', ENCODING 'UTF-8');
        """)
        n = con.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        print(f"   {t:<16} {n:>10,} rows")

    # 4. Summary
    print()
    print("=" * 60)
    print("TOTAL:")
    for t in TABLES:
        n = con.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        print(f"  {t:<16} {n:>10,}")

    con.close()
    print()
    print(f"Done. DB: {DB}")

if __name__ == "__main__":
    main()