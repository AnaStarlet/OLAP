# P03. Загрузка данных в DuckDB

## Структура

```text
OLAP/
│
└── P03/
    ├── data/
    │   └── raw/                  # CSV
    │       ├── dim_store.csv
    │       ├── dim_warehouse.csv
    │       ├── dim_supplier.csv
    │       ├── dim_product.csv
    │       ├── dim_customer.csv
    │       ├── dim_employee.csv
    │       ├── dim_date.csv
    │       ├── fact_visits.csv
    │       ├── fact_interest.csv
    │       ├── fact_sales.csv
    │       ├── fact_loyalty.csv
    │       ├── fact_logistics.csv
    │       └── fact_inventory.csv
    ├── sql/ddl_duckdb.sql        # создание таблиц
    ├── load_data.py              # загрузка CSV → DuckDB
    ├── checks.sql                # проверочные запросы
    ├── checks.txt                # сохранённый вывод проверок
    ├── README.md
    └── warehouse.duckdb          # создаётся скриптом
```
