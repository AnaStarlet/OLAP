"""P07. Load CSV into ClickHouse via clickhouse-client inside Docker.

Docker container parses CSV itself using the table schema.
No Python type conversion needed.
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


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    for t in TABLES:
        csv_file = (RAW / f"{t}.csv").resolve()
        if not csv_file.exists():
            print(f"SKIP: {csv_file} not found")
            continue

        # 1. TRUNCATE
        r = run([
            "docker", "exec", "clickhouse-olap",
            "clickhouse-client", "--user", "default", "--password", "1234",
            "--query", f"TRUNCATE TABLE olap.{t}",
        ])
        if r.returncode != 0:
            print(f"TRUNCATE {t} failed: {r.stderr}")
            continue

        # 2. INSERT via clickhouse-client reading from stdin
        with csv_file.open("rb") as f:
            r = subprocess.run(
                [
                    "docker", "exec", "-i", "clickhouse-olap",
                    "clickhouse-client", "--user", "default", "--password", "1234",
                    "--query",
                    f"INSERT INTO olap.{t} FORMAT CSVWithNames",
                ],
                stdin=f,
                capture_output=True,
            )
        if r.returncode != 0:
            print(f"INSERT {t} failed: {r.stderr.decode(errors='replace')}")
            continue

        # 3. COUNT
        r = run([
            "docker", "exec", "clickhouse-olap",
            "clickhouse-client", "--user", "default", "--password", "1234",
            "--query", f"SELECT count(*) FROM olap.{t}",
        ])
        n = r.stdout.strip()
        print(f"{t:<16} {n:>10} rows")

    print()
    print("Done.")


if __name__ == "__main__":
    main()