"""P07 v2. Incremental load with ReplacingMergeTree.

No TRUNCATE — just INSERT.
Duplicates are removed by ClickHouse engine on merge, by sorting key.

Tables are grouped by business meaning:
  sales      - fact_sales + its dimensions
  behavior   - fact_visits, fact_interest + dim_employee
  logistics  - fact_logistics, fact_inventory + dim_warehouse, dim_supplier
  loyalty    - fact_loyalty

You can load a single group with:  python load_all.py sales
Load all groups:                    python load_all.py
"""
import subprocess
import sys
from pathlib import Path

RAW = Path("../P03/data/raw")

GROUPS = {
    "sales": [
        "dim_store", "dim_product", "dim_customer", "dim_date",
        "fact_sales",
    ],
    "behavior": [
        "dim_employee",
        "fact_visits", "fact_interest",
    ],
    "logistics": [
        "dim_warehouse", "dim_supplier",
        "fact_logistics", "fact_inventory",
    ],
    "loyalty": [
        "fact_loyalty",
    ],
}


def load_table(table: str):
    csv_file = (RAW / f"{table}.csv").resolve()
    if not csv_file.exists():
        print(f"{table:<16} SKIP — {csv_file} not found")
        return

    # INSERT into ClickHouse via client inside Docker
    # ReplacingMergeTree removes duplicates by sorting key.
    with csv_file.open("rb") as f:
        r = subprocess.run(
            [
                "docker", "exec", "-i", "clickhouse-olap",
                "clickhouse-client", "--user", "default", "--password", "1234",
                "--query",
                f"INSERT INTO olap.{table} FORMAT CSVWithNames",
            ],
            stdin=f, capture_output=True,
        )
    if r.returncode != 0:
        print(f"{table:<16} FAIL — {r.stderr.decode(errors='replace')[:120]}")
        return

    # COUNT with FINAL — merges versions and counts unique rows
    r = subprocess.run([
        "docker", "exec", "clickhouse-olap",
        "clickhouse-client", "--user", "default", "--password", "1234",
        "--query", f"SELECT count(*) FROM olap.{table} FINAL",
    ], capture_output=True, text=True)
    print(f"{table:<16} {r.stdout.strip():>10} rows (FINAL)")


def load_group(name: str):
    print(f"--- group: {name} ---")
    for t in GROUPS[name]:
        load_table(t)


def main():
    if len(sys.argv) > 1:
        group = sys.argv[1]
        if group not in GROUPS:
            print(f"Unknown group: {group}")
            print(f"Available: {list(GROUPS)}")
            sys.exit(1)
        load_group(group)
    else:
        for g in GROUPS:
            load_group(g)
    print()
    print("Done.")


if __name__ == "__main__":
    main()
