# P03. Загрузка данных в DuckDB

## Структура

```
OLAP/
├── P01/data/raw/               # исходное сырьё
│   ├── dim_customer.csv
│   ├── dim_product.csv
│   └── fact_sales.csv
└── P03/
    ├── data/
    │   └── dim_store.csv       # справочник магазинов
    ├── sql/ddl_duckdb.sql
    ├── load_data.py
    ├── checks.txt              # сохранённый вывод проверок
    └── warehouse.duckdb        # создаётся скриптом, не коммитим
```

## Как загрузить

### 1. Установить DuckDB (один раз)

```powershell
python -m pip install duckdb
```

### 2. Запустить скрипт из папки P03

```powershell
python load_data.py
```

Скрипт:

- создаёт таблицы из `sql/ddl_duckdb.sql`;
- очищает таблицы (`DELETE FROM`) — повторный запуск не удваивает данные;
- грузит `dim_customer.csv` и `dim_product.csv` из `P01/data/raw/`;
- грузит `dim_store.csv` из `P03/data/`
- грузит `fact_sales.csv`, попутно заполняя `dim_date` и `dim_payment`;
- печатает проверки (строки, пустые ключи, суммы).

**Весь вывод скрипта — на английском (ASCII).** Это сделано специально,
чтобы избежать проблем с кодировкой в Windows PowerShell.

### 3. Сохранить вывод проверок

```powershell
python load_data.py *>&1 | Tee-Object -FilePath checks.txt
```

Результат — в `checks.txt`. Он же в репозитории как доказательство
выполнения пункта «Проверки» из задания.

## Повторный запуск

`python load_data.py` можно запускать сколько угодно раз.
Скрипт каждый раз делает `DELETE FROM` по таблицам и грузит CSV заново —
**данные не удваиваются**.

## О таблицах

| Таблица | Источник |
|---------|----------|-------|
| `dim_customer` | `P01/data/raw/dim_customer.csv` |
| `dim_product`  | `P01/data/raw/dim_product.csv` |
| `dim_store`    | `P03/data/dim_store.csv` |
| `dim_date`     | генерируется из `fact_sales.sale_datetime`|
| `dim_payment`  | генерируется из `fact_sales.payment_type` |
| `fact_sales`   | `P01/data/raw/fact_sales.csv` |

Grain факта: **одна строка = одна позиция в чеке** (`sale_id` + `product_id`).
