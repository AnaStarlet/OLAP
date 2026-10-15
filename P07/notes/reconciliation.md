# Сверка DuckDB — ClickHouse

## Метод

- Источник: `P03/data/raw/*.csv` (одни и те же файлы).
- DuckDB: файл `P03/warehouse.duckdb`, обычные MergeTree-таблицы.
- ClickHouse: база `olap`, движок ReplacingMergeTree.
- Для ClickHouse используется `FINAL` — он схлопывает версии строк и считает уникальные.

## Count по таблицам

| Таблица | DuckDB | ClickHouse (FINAL) | Совпадает |
|---|---|---|---|
| dim_store | 30 | 30 | да |
| dim_warehouse | 6 | 6 | да |
| dim_supplier | 300 | 300 | да |
| dim_product | 35 000 | 35 000 | да |
| dim_customer | 25 000 | 25 000 | да |
| dim_employee | 300 | 300 | да |
| dim_date | 2 466 | 2 466 | да |
| fact_visits | 150 000 | 150 000 | да |
| fact_interest | 200 000 | 200 000 | да |
| fact_sales | 100 000 | 100 000 | да |
| fact_loyalty | 60 000 | 60 000 | да |
| fact_logistics | 50 000 | 50 000 | да |
| fact_inventory | 120 000 | 120 000 | да |

## Главная метрика

Запрос: `SELECT SUM(total_amount) FROM fact_sales` (в ClickHouse — с `FINAL`).

| База | Значение |
|---|---|
| DuckDB | 3 557 661 372.99 |
| ClickHouse | 3 557 661 372.99 |

Совпадает до копейки.

## Повторная загрузка

Загрузка инкрементальная, без `TRUNCATE`. Просто `INSERT`.
Дедупликация делается движком `ReplacingMergeTree` по ключу сортировки:

- `fact_sales` — `sale_id`
- `fact_visits` — `visit_id`
- `fact_interest` — `interest_id`
- `fact_loyalty` — `loyalty_id`
- `fact_logistics` — `shipment_id`
- `fact_inventory` — `inventory_id`
- все `dim_*` — по своему id.

Доказательство: загрузка запущена **дважды подряд**. После второго прогона:
- `count(*) FINAL` = 100 000, не 200 000
- `sum(total_amount) FINAL` = 3 557 661 372.99, не изменилась.
