"""P07
Groups:
  sales      fact_sales + dim_store, dim_product, dim_customer, dim_date
  behavior   fact_visits, fact_interest + dim_employee
  logistics  fact_logistics, fact_inventory + dim_warehouse, dim_supplier
  loyalty    fact_loyalty
"""
import subprocess
import sys
from pathlib import Path

RAW = Path("../P03/data/raw")

GROUPS = {
    "sales":     ["dim_store", "dim_product", "dim_customer", "dim_date", "fact_sales"],
    "behavior":  ["dim_employee", "fact_visits", "fact_interest"],
    "logistics": ["dim_warehouse", "dim_supplier", "fact_logistics", "fact_inventory"],
    "loyalty":   ["fact_loyalty"],
}


def load(table):
    csv = (RAW / f"{table}.csv").resolve()
    if not csv.exists():
        print(f"{table:<16} SKIP")
        return

    with csv.open("rb") as f:
        r = subprocess.run(
            ["docker", "exec", "-i", "clickhouse-olap",
             "clickhouse-client", "--user", "default", "--password", "1234",
             "--query", f"INSERT INTO olap.{table} FORMAT CSVWithNames"],
            stdin=f, capture_output=True,
        )
    if r.returncode != 0:
        print(f"{table:<16} FAIL: {r.stderr.decode(errors='replace')[:120]}")
        return

    r = subprocess.run(
        ["docker", "exec", "clickhouse-olap",
         "clickhouse-client", "--user", "default", "--password", "1234",
         "--query", f"SELECT count(*) FROM olap.{table} FINAL"],
        capture_output=True, text=True,
    )
    print(f"{table:<16} {r.stdout.strip():>10} rows (FINAL)")


def main():
    targets = [sys.argv[1]] if len(sys.argv) > 1 else list(GROUPS)
    for g in targets:
        print(f"--- group: {g} ---")
        for t in GROUPS[g]:
            load(t)
    print("Done.")


if __name__ == "__main__":
    main()