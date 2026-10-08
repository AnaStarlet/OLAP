"""
P05. Load CSV from data/raw/ into DuckDB with quality checks.
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

    # 5. Quality checks
    print()
    print("=" * 60)
    print("QUALITY CHECKS:")

    # 5.1 Null keys in fact_sales
    nulls = con.execute("""
        SELECT
            SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer,
            SUM(CASE WHEN product_id  IS NULL THEN 1 ELSE 0 END) AS null_product,
            SUM(CASE WHEN store_id    IS NULL THEN 1 ELSE 0 END) AS null_store,
            SUM(CASE WHEN date_id     IS NULL THEN 1 ELSE 0 END) AS null_date
        FROM fact_sales
    """).fetchone()
    if any(nulls):
        raise SystemExit(f"FAIL: null keys in fact_sales: {nulls}")
    print("   OK: null keys in fact_sales = 0")

    # 5.2 Bad range
    bad_range = con.execute("""
        SELECT COUNT(*) FROM fact_sales
        WHERE quantity < 0 OR total_amount < 0
    """).fetchone()[0]
    if bad_range > 0:
        raise SystemExit(f"FAIL: negative quantity/total_amount: {bad_range} rows")
    print("   OK: quantity and total_amount >= 0")

    # 5.3 Duplicate sale_id
    dup = con.execute("""
        SELECT COUNT(*) FROM (
            SELECT sale_id FROM fact_sales GROUP BY sale_id HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    if dup > 0:
        raise SystemExit(f"FAIL: duplicate sale_id: {dup}")
    print("   OK: sale_id is unique")

    # 5.4 Orphans: store_id from fact must exist in dim_store
    orphans = con.execute("""
        SELECT COUNT(*) FROM fact_sales f
        LEFT JOIN dim_store s ON s.store_id = f.store_id
        WHERE s.store_id IS NULL
    """).fetchone()[0]
    if orphans > 0:
        raise SystemExit(f"FAIL: {orphans} rows in fact_sales with unknown store_id")
    print("   OK: all store_id from fact exist in dim_store")

    # 5.5 Orphans: product_id from fact must exist in dim_product
    orphans = con.execute("""
        SELECT COUNT(*) FROM fact_sales f
        LEFT JOIN dim_product p ON p.product_id = f.product_id
        WHERE p.product_id IS NULL
    """).fetchone()[0]
    if orphans > 0:
        raise SystemExit(f"FAIL: {orphans} rows in fact_sales with unknown product_id")
    print("   OK: all product_id from fact exist in dim_product")

    # 6. Canonical metric
    metric = con.execute("SELECT SUM(total_amount) FROM fact_sales").fetchone()[0]
    rows = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    print()
    print(f"CANONICAL METRIC: SUM(total_amount) = {metric}")
    print(f"fact_sales rows:  {rows}")

    con.close()
    print()
    print(f"Done. DB: {DB}")


if __name__ == "__main__":
    main()