"""
З03. Загрузка CSV из data/raw/ в DuckDB.
Ювелирная сеть Республики Беларусь.
"""
import duckdb
from pathlib import Path

DB  = "warehouse.duckdb"
RAW = Path("data/raw")
DDL = Path("sql/ddl_duckdb.sql")

# порядок важен: сначала справочники, потом факты
TABLES = [
    # справочники
    "dim_store", "dim_warehouse", "dim_supplier",
    "dim_product", "dim_customer", "dim_employee", "dim_date",
    # факты
    "fact_visits", "fact_interest", "fact_sales",
    "fact_loyalty", "fact_logistics", "fact_inventory",
]

def main():
    if not RAW.exists():
        raise SystemExit(f"Нет папки {RAW}. Положи 13 CSV в data/raw/")

    if not DDL.exists():
        raise SystemExit(f"Нет файла {DDL}. Сначала положи DDL.")

    con = duckdb.connect(DB)

    # 1. DDL — создаём таблицы
    print("1) Создаю таблицы из sql/ddl_duckdb.sql ...")
    con.execute(DDL.read_text(encoding="utf-8"))

    # 2. Очистка — чтобы повторная загрузка не удваивала факты
    print("2) Очищаю таблицы (DELETE FROM) ...")
    for t in reversed(TABLES):          # факты первыми, потом справочники
        con.execute(f"DELETE FROM {t};")

    # 3. Загрузка CSV
    print("3) Загружаю CSV ...")
    for t in TABLES:
        csv = RAW / f"{t}.csv"
        if not csv.exists():
            print(f"   ПРОПУСК: нет {csv}")
            continue
        con.execute(f"""
            COPY {t} FROM '{csv.as_posix()}'
            (HEADER, DELIMITER ',', QUOTE '"', ENCODING 'UTF-8');
        """)
        n = con.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        print(f"   {t:<16} {n:>10,} строк")

    # 4. Итоговая сводка
    print()
    print("=" * 60)
    print("ИТОГО:")
    for t in TABLES:
        n = con.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        print(f"  {t:<16} {n:>10,}")

    con.close()
    print()
    print(f"Готово. База: {DB}")

if __name__ == "__main__":
    main()