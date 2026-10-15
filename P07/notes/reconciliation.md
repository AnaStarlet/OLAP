# Сверка DuckDB ↔ ClickHouse

Одни и те же CSV, две базы. В ClickHouse используется `FINAL`
(схлопывает версии строк по ключу).

## Count

| Таблица | DuckDB | ClickHouse (FINAL) |
|---|---|---|
| dim_store | 30 | 30 |
| dim_warehouse | 6 | 6 |
| dim_supplier | 300 | 300 |
| dim_product | 35 000 | 35 000 |
| dim_customer | 25 000 | 25 000 |
| dim_employee | 300 | 300 |
| dim_date | 2 466 | 2 466 |
| fact_visits | 150 000 | 150 000 |
| fact_interest | 200 000 | 200 000 |
| fact_sales | 100 000 | 100 000 |
| fact_loyalty | 60 000 | 60 000 |
| fact_logistics | 50 000 | 50 000 |
| fact_inventory | 120 000 | 120 000 |

Все 13 таблиц совпадают.

## Главная метрика

    SELECT SUM(total_amount) FROM fact_sales;         -- DuckDB
    SELECT SUM(total_amount) FROM fact_sales FINAL;   -- ClickHouse

| База | Значение |
|---|---|
| DuckDB | 3 557 661 372.99 |
| ClickHouse | 3 557 661 372.99 |

Совпадает до копейки.

## Повторная загрузка

Загрузка выполнена дважды подряд. Лог обоих прогонов — в `notes/load_log.txt`.
После второго прогона числа не изменились: `fact_sales = 100 000` (не 200 000),
метрика `3 557 661 372.99`. Дубли удаляются движком `ReplacingMergeTree` по ключу.
