# Сверка DuckDB — ClickHouse

## Метод

Для каждой из 13 таблиц сравнили `count(*)` в обеих базах.
Для главной метрики сравнили `sum(total_amount)` по `fact_sales`.

## Count по таблицам

| Таблица | DuckDB | ClickHouse | Совпадает |
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

Файл: `sql/canonical_metric.sql`, запрос: `SELECT SUM(total_amount) FROM fact_sales`.

| База | Значение |
|---|---|
| DuckDB | 3 557 661 372.99 |
| ClickHouse | 3 557 661 372.99 |

Совпадает до копейки. Расхождений нет.

## Повторная загрузка

`etl/load_all.py` перед каждой таблицей выполняет `TRUNCATE TABLE olap.{table}`,
затем заливает CSV заново. Поэтому повторный запуск не удваивает данные.

Проверено двумя прогонами подряд — лог в `notes/load_log.txt`.
`fact_sales` в обоих прогонах = 100 000 строк, метрика не меняется.
