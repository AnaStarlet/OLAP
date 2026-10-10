import subprocess
from pathlib import Path

RAW = Path("../P03/data/raw")
TABLES = ["dim_date", "fact_visits", "fact_interest"]


def main():
    for t in TABLES:
        csv_file = (RAW / f"{t}.csv").resolve()
        print(f"loading {t} ...")

        subprocess.run([
            "docker", "exec", "clickhouse-olap",
            "clickhouse-client", "--user", "default", "--password", "1234",
            "--query", f"TRUNCATE TABLE olap.{t}",
        ], check=True)

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
            print(r.stderr.decode(errors="replace"))
            continue

        r = subprocess.run([
            "docker", "exec", "clickhouse-olap",
            "clickhouse-client", "--user", "default", "--password", "1234",
            "--query", f"SELECT count(*) FROM olap.{t}",
        ], capture_output=True, text=True)
        print(f"{t:<16} {r.stdout.strip():>10} rows")


if __name__ == "__main__":
    main()