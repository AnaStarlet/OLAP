# P03/load_data.py
"""
Load CSV from P01/data/raw/*.csv into P03/warehouse.duckdb.

Idempotent: tables are cleared (DELETE FROM) before loading,
so a repeated run does not duplicate rows.

Console output is ASCII-only to avoid Windows PowerShell encoding issues.
"""
import duckdb
import csv
import os
import sys
from datetime import datetime

# --- Paths relative to repo root OLAP/ ---
HERE = os.path.dirname(os.path.abspath(__file__))          # .../P03
ROOT = os.path.dirname(HERE)                                # .../OLAP
RAW_DIR = os.path.join(ROOT, "P01", "data", "raw")

DB_FILE = os.path.join(HERE, "warehouse.duckdb")
DDL_FILE = os.path.join(HERE, "sql", "ddl_duckdb.sql")

CUSTOMER_CSV = os.path.join(RAW_DIR, "dim_customer.csv")
PRODUCT_CSV = os.path.join(RAW_DIR, "dim_product.csv")
FACT_CSV = os.path.join(RAW_DIR, "fact_sales.csv")
STORE_CSV = os.path.join(HERE, "data", "dim_store.csv")


def apply_ddl(con):
    if not os.path.exists(DDL_FILE):
        print(f"[ERROR] DDL file not found: {DDL_FILE}")
        sys.exit(1)
    with open(DDL_FILE, "r", encoding="utf-8") as f:
        con.execute(f.read())
    print(f"[OK] DDL applied: {DDL_FILE}")


def clear_tables(con):
    for t in ["fact_sales", "dim_customer", "dim_product",
              "dim_store", "dim_date", "dim_payment"]:
        try:
            con.execute(f"DELETE FROM {t};")
        except Exception:
            pass
    print("[OK] Tables cleared (DELETE FROM).")


def load_customers(con):
    if not os.path.exists(CUSTOMER_CSV):
        print(f"[WARN] Missing {CUSTOMER_CSV} - skipped.")
        return 0
    with open(CUSTOMER_CSV, "r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r)
        idx = {name: i for i, name in enumerate(header)}
        rows = []
        for row in r:
            if not row:
                continue
            # CSV uses Russian "yes"/"no" (da/net) in loyalty_card column
            raw = row[idx["loyalty_card"]].strip().lower()
            loyalty = raw in ("да", "da", "yes", "true", "1")
            rows.append((
                int(row[idx["customer_id"]]),
                row[idx["full_name"]],
                row[idx["gender"]],
                int(row[idx["age"]]),
                row[idx["city"]],
                loyalty,
                row[idx["register_date"]],
            ))
    con.executemany(
        "INSERT INTO dim_customer (customer_id, full_name, gender, age, city, loyalty_card, register_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    print(f"[OK] dim_customer: {len(rows)} rows.")
    return len(rows)


def load_products(con):
    if not os.path.exists(PRODUCT_CSV):
        print(f"[WARN] Missing {PRODUCT_CSV} - skipped.")
        return 0
    with open(PRODUCT_CSV, "r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        rows, skipped = [], 0
        for row in r:
            if not row:
                continue
            if len(row) < 7 or row[6].strip() == "":
                skipped += 1
                continue
            rows.append((int(row[0]), row[1], row[2], row[3], row[4],
                         float(row[5]), int(row[6])))
    con.executemany(
        "INSERT INTO dim_product (product_id, product_name, category, brand, unit, price, supplier_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
    print(f"[OK] dim_product: {len(rows)} rows, skipped {skipped} broken.")
    return len(rows)


def load_stores(con):
    if not os.path.exists(STORE_CSV):
        print(f"[WARN] Missing {STORE_CSV} - skipped.")
        return 0
    with open(STORE_CSV, "r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)  # header
        rows = []
        for row in r:
            if not row:
                continue
            rows.append((int(row[0]), row[1], row[2], row[3], row[4]))
    con.executemany(
        "INSERT INTO dim_store (store_id, store_name, region, city, address) "
        "VALUES (?, ?, ?, ?, ?)", rows)
    print(f"[OK] dim_store: {len(rows)} rows.")
    return len(rows)


def load_facts(con):
    if not os.path.exists(FACT_CSV):
        print(f"[WARN] Missing {FACT_CSV} - skipped.")
        return 0

    with open(FACT_CSV, "r", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r)
        idx = {name: i for i, name in enumerate(header)}

        rows = []
        dates = set()
        payments = set()
        for row in r:
            if not row:
                continue
            sale_dt_str = row[idx["sale_datetime"]]
            try:
                sale_dt = datetime.fromisoformat(sale_dt_str)
            except ValueError:
                sale_dt = datetime.strptime(sale_dt_str, "%Y-%m-%d %H:%M:%S")
            dates.add(sale_dt.date())

            pt = row[idx["payment_type"]]
            payments.add(pt)

            cust_raw = row[idx["customer_id"]]
            customer_id = int(cust_raw) if cust_raw.strip() != "" else None

            rows.append((
                int(row[idx["sale_id"]]),
                sale_dt,
                customer_id,
                int(row[idx["product_id"]]),
                int(row[idx["quantity"]]),
                float(row[idx["unit_price"]]),
                float(row[idx["total_amount"]]),
                pt,
                int(row[idx["store_id"]]),
            ))

    con.executemany(
        "INSERT INTO fact_sales (sale_id, sale_datetime, customer_id, product_id, "
        "quantity, unit_price, total_amount, payment_type, store_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    print(f"[OK] fact_sales: {len(rows)} rows.")

    con.executemany(
        "INSERT INTO dim_payment (payment_type) VALUES (?) "
        "ON CONFLICT (payment_type) DO NOTHING",
        [(p,) for p in payments])
    print(f"[OK] dim_payment: {len(payments)} payment types loaded.")

    date_rows = [(d, d.year, d.month, (d.month - 1)//3 + 1, d.strftime("%A"))
                 for d in dates]
    con.executemany(
        "INSERT INTO dim_date (date_key, year, month, quarter, weekday) "
        "VALUES (?, ?, ?, ?, ?) ON CONFLICT (date_key) DO NOTHING",
        date_rows)
    print(f"[OK] dim_date: {len(date_rows)} dates loaded.")

    return len(rows)


def run_checks(con):
    print("\n--- CHECKS ---")

    print("\n[1] Row counts:")
    for t in ["dim_customer", "dim_product", "dim_store",
              "dim_date", "dim_payment", "fact_sales"]:
        try:
            cnt = con.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
            print(f"    {t:15s} = {cnt}")
        except Exception as e:
            print(f"    {t:15s} - {e}")

    print("\n[2] Null keys:")
    for tbl, key in [("dim_customer", "customer_id"),
                     ("dim_product", "product_id"),
                     ("fact_sales", "sale_id"),
                     ("fact_sales", "product_id"),
                     ("fact_sales", "store_id")]:
        try:
            cnt = con.execute(
                f"SELECT COUNT(*) FROM {tbl} WHERE {key} IS NULL;"
            ).fetchone()[0]
            print(f"    {tbl}.{key}: {cnt}")
        except Exception:
            pass

    print("\n[3] Main measure sums:")
    for tbl, col in [("fact_sales", "total_amount"),
                     ("fact_sales", "quantity")]:
        try:
            s = con.execute(
                f"SELECT COALESCE(SUM({col}), 0) FROM {tbl};"
            ).fetchone()[0]
            print(f"    SUM({tbl}.{col}) = {s}")
        except Exception as e:
            print(f"    {tbl}.{col}: {e}")

    print("\n[4] Consistency with source CSV:")
    try:
        cust_csv = sum(1 for _ in open(CUSTOMER_CSV, encoding="utf-8-sig")) - 1
        prod_csv = sum(1 for _ in open(PRODUCT_CSV, encoding="utf-8-sig")) - 1
        fact_csv = sum(1 for _ in open(FACT_CSV, encoding="utf-8-sig")) - 1
        print(f"    rows in CSV dim_customer = {cust_csv}")
        print(f"    rows in CSV dim_product  = {prod_csv}")
        print(f"    rows in CSV fact_sales   = {fact_csv}")
    except Exception as e:
        print(f"    Could not count CSV: {e}")


def main():
    print(f"[INFO] Repo root:   {ROOT}")
    print(f"[INFO] Source data: {RAW_DIR}")
    print(f"[INFO] DuckDB file: {DB_FILE}")
    con = duckdb.connect(DB_FILE)
    apply_ddl(con)
    clear_tables(con)
    load_customers(con)
    load_products(con)
    load_stores(con)
    load_facts(con)
    run_checks(con)
    con.close()
    print("\n[DONE]")


if __name__ == "__main__":
    main()