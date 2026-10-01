import subprocess
from pathlib import Path

sql = Path("checks.sql").read_text(encoding="utf-8")
r = subprocess.run(
    ["duckdb", "warehouse.duckdb"],
    input=sql.encode("utf-8"),
    capture_output=True,
)
with open("checks.txt", "ab") as f:
    f.write(r.stdout)
print("checks.txt written (UTF-8, appended)")
