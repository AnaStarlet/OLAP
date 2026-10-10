"""Create tables in ClickHouse by sending one statement at a time."""
import re
from pathlib import Path
from clickhouse_driver import Client

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "1234"

DDL_FILE = Path("sql/ddl_clickhouse.sql")


def split_sql(sql: str):
    """Split SQL by semicolons, ignore comments and empty lines."""
    sql = re.sub(r"--[^\n]*", "", sql)  # strip line comments
    parts = [p.strip() for p in sql.split(";")]
    return [p for p in parts if p]


def main():
    client = Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )
    sql = DDL_FILE.read_text(encoding="utf-8")
    for stmt in split_sql(sql):
        first_line = stmt.splitlines()[0][:70]
        print(f"-> {first_line}")
        client.execute(stmt)
    print("Done. All tables created.")


if __name__ == "__main__":
    main()
