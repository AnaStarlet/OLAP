# Проект OLAP: от CSV до дашборда

Этот репозиторий содержит полный пайплайн аналитической витрины для розничной сети ювелирных магазинов.

## Как запустить проект (5 шагов)

1. **Запустить базы данных (Docker):**
   ```bash
   docker start clickhouse-olap metabase-olap
Загрузить данные в ClickHouse:

bash
cd P07
python etl/load_all.py
Проверить эталонную метрику (ClickHouse):

sql
SELECT sum(total_amount) FROM olap.fact_sales FINAL;
-- Ожидаемый результат: 3 557 661 372.99
Открыть дашборд:
Перейди на http://localhost:3000 (Metabase) и открой «Дашборд OLAP».

Если что-то красное:
Смотри логи: docker logs clickhouse-olap или docker logs metabase-olap.

Путь данных (для устного ответа)
Источник: CSV-файлы в P03/data/raw/.

Загрузка и проверки: Скрипт P07/etl/load_all.py загружает данные в ClickHouse. Используется движок ReplacingMergeTree и ключ ORDER BY (sale_id) для инкрементальной загрузки без дублей.

Витрина: 13 таблиц (7 справочников, 6 фактов). Сводная таблица sales_by_store_month используется для графиков.

Метрика: Эталонный расчет в P10/dashboards/widget1_metric.sql (SUM(total_amount)).

Дашборд: Metabase подключается к ClickHouse. Числа совпадают с SQL-запросом (сверка в папке P11).

Одна строка факта: fact_sales = одна позиция в чеке.
Главная мера: total_amount (оборот в BYN).

Структура
P03-P05: Загрузка в DuckDB и проверки.

P06: SCD2 (история справочника).

P07-P09: ClickHouse (партиции, сводные таблицы).

P10: Дашборд Metabase.

P11: Сверка чисел SQL и BI.

Отказы (Cut)
Возвратов в сырье нет, поэтому оборот = обычный оборот.

Справочник dim_store собран вручную.

Materialized View не используется (выбран полный пересчёт через TRUNCATE + INSERT).
