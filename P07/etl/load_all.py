"""P07. Load all 13 CSV into ClickHouse via clickhouse-client in Docker.

- TRUNCATE before each table -> re-run safe, no duplicates.
- ClickHouse parses CSV itself using table schema.
"""
import subprocess
from pathlib import Path

RAW = Path("../P03/data/raw")

DIMENSIONS = [
    "dim_store", "dim_warehouse", "dim_supplier",
    "dim_product", "dim_customer", "dim_employee", "dim_date",
]
FACTS = [
    "fact_visits", "fact_interest", "fact_sales",
    "fact_loyalty", "fact_logistics", "fact_inventory",
]
TABLES = DIMENSIONS + FACTS


def main():
    for t in TABLES:
        csv_file = (RAW / f"{t}.csv").resolve()
        if not csv_file.exists():
            print(f"SKIP: {csv_file} not found")
            continue

        # 1. TRUNCATE
        subprocess.run([
            "docker", "exec", "clickhouse-olap",
            "clickhouse-client", "--user", "default", "--password", "1234",
            "--query", f"TRUNCATE TABLE olap.{t}",
        ], check=True)

        # 2. INSERT
        with csv_file.open("rb") as f:
            r = subprocess.run(
                [
                    "docker", "exec", "-i", "clickhouse-olap",
                    "clickhouse-client", "--user", "default", "--password", "1234",
                    "--query", f"INSERT INTO olap.{t} FORMAT CSVWithNames",
                ],
                stdin=f, capture_output=True,
            )
        if r.returncode != 0:
            print(f"{t}: FAIL — {r.stderr.decode(errors='replace')[:200]}")
            continue

        # 3. COUNT
        r = subprocess.run([
            "docker", "exec", "clickhouse-olap",
            "clickhouse-client", "--user", "default", "--password", "1234",
            "--query", f"SELECT count(*) FROM olap.{t}",
        ], capture_output=True, text=True)
        print(f"{t:<16} {r.stdout.strip():>10} rows")

    print()
    print("Done.")


if __name__ == "__main__":
    main()