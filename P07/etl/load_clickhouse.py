"""P07. Load CSV from P03/data/raw/ into ClickHouse.

- TRUNCATE before insert (re-run safe, no duplicates).
- Convert types per column: Int32, Decimal, Date, String.
"""
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from clickhouse_driver import Client

CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "1234"

RAW = Path("../P03/data/raw")   # запускать из папки P07

TYPES = {
    "dim_store": {
        "store_id": "i", "area_m2": "d", "opening_date": "t",
        "warehouse_id": "i", "employees_count": "i", "consultants_count": "i",
    },
    "dim_warehouse": {
        "warehouse_id": "i", "area_m2": "d", "capacity_units": "i",
    },
    "dim_supplier": {
        "supplier_id": "i", "contract_date": "t", "delivery_days": "i",
        "supplier_rating": "d",
    },
    "dim_product": {
        "product_id": "i", "assay": "i", "weight_g": "d",
        "stone_count": "i", "supplier_id": "i",
        "cost_price": "d", "retail_price": "d", "release_date": "t",
    },
    "dim_customer": {
        "customer_id": "i", "birth_date": "t", "age": "i",
        "registration_date": "t", "loyalty_join_date": "t",
        "bonus_balance": "d", "purchases_count": "i",
        "total_purchases": "d", "avg_check": "d", "last_purchase_date": "t",
    },
    "dim_employee": {
        "employee_id": "i", "store_id": "i", "hire_date": "t",
        "experience_years": "i",
    },
    "dim_date": {
        "date_id": "i", "date": "t", "day": "i", "week": "i",
        "month_num": "i", "quarter": "i", "year": "i",
        "is_workday": "u", "is_holiday": "u",
    },
    "fact_sales": {
        "sale_id": "i", "date_id": "i", "time_id": "i",
        "customer_id": "i", "product_id": "i", "store_id": "i",
        "employee_id": "i", "quantity": "i", "unit_price": "d",
        "discount_pct": "i", "bonus_used": "d", "total_amount": "d",
        "cost_amount": "d", "profit_amount": "d",
    },
    "fact_visits": {
        "visit_id": "i", "date_id": "i", "time_id": "i",
        "customer_id": "i", "store_id": "i", "employee_id": "i",
        "duration_min": "i", "new_customer": "u", "has_loyalty_card": "u",
        "got_consultation": "u", "products_viewed": "i",
        "products_selected": "i", "purchase_made": "u", "purchase_amount": "d",
    },
    "fact_interest": {
        "interest_id": "i", "visit_id": "i", "customer_id": "i",
        "product_id": "i", "store_id": "i", "employee_id": "i",
        "date_id": "i", "time_id": "i", "view_minutes": "i",
        "tried_on": "u", "got_consultation": "u", "asked_question": "u",
        "added_to_selection": "u", "product_price": "d",
        "discount_pct": "i", "purchased": "u",
    },
    "fact_loyalty": {
        "loyalty_id": "i", "customer_id": "i", "date_id": "i",
        "sale_id": "i", "accrued": "d", "spent": "d", "balance": "d",
    },
    "fact_logistics": {
        "shipment_id": "i", "product_id": "i", "supplier_id": "i",
        "warehouse_id": "i", "store_id": "i",
        "dispatch_date": "t", "arrival_date": "t",
        "quantity": "i", "weight_g": "d", "delivery_cost": "d",
        "delivery_days": "i",
    },
    "fact_inventory": {
        "inventory_id": "i", "date_id": "i", "product_id": "i",
        "store_id": "i", "warehouse_id": "i",
        "opening_stock": "i", "received": "i", "sold": "i",
        "returns": "i", "moved": "i", "closing_stock": "i",
        "reserved": "i", "storage_days": "i",
    },
}

DIMENSIONS = [
    "dim_store", "dim_warehouse", "dim_supplier",
    "dim_product", "dim_customer", "dim_employee", "dim_date",
]
FACTS = [
    "fact_visits", "fact_interest", "fact_sales",
    "fact_loyalty", "fact_logistics", "fact_inventory",
]
TABLES = DIMENSIONS + FACTS


def convert(value, kind):
    if value is None or value == "":
        return None
    if kind in ("i", "u"):
        return int(value)
    if kind == "d":
        return Decimal(value)
    if kind == "t":
        value = value.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None
    return value


def main():
    client = Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
    )

    for table in TABLES:
        csv_file = RAW / f"{table}.csv"
        if not csv_file.exists():
            print(f"SKIP: {csv_file} not found")
            continue

        client.execute(f"TRUNCATE TABLE olap.{table}")

        types = TYPES.get(table, {})

        with csv_file.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            rows = []
            for r in reader:
                row = []
                for col in header:
                    kind = types.get(col, "s")
                    row.append(convert(r.get(col, ""), kind))
                rows.append(tuple(row))

        cols = ", ".join(header)
        client.execute(
            f"INSERT INTO olap.{table} ({cols}) VALUES",
            rows,
            types_check=True,
        )

        n = client.execute(f"SELECT count(*) FROM olap.{table}")[0][0]
        print(f"{table:<16} {n:>10,} rows")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
