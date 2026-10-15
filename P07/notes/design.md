# Дизайн загрузки: группы и ключи дедупликации

## Группы таблиц

13 таблиц разбиты на 4 бизнес-группы. При загрузке новой партии
обновляется только та группа, куда пришли данные — остальные не трогаются.

| Группа | Таблицы |
|---|---|
| sales | fact_sales, dim_store, dim_product, dim_customer, dim_date |
| behavior | fact_visits, fact_interest, dim_employee |
| logistics | fact_logistics, fact_inventory, dim_warehouse, dim_supplier |
| loyalty | fact_loyalty |

Грузить одну группу: `python load_all.py sales`.
Грузить всё: `python load_all.py`.

## Ключи дедупликации

Каждая таблица — на движке `ReplacingMergeTree`. `ORDER BY` — ключ дедупликации,
он же играет роль индекса в ClickHouse.

| Таблица | Ключ |
|---|---|
| dim_store, dim_warehouse, dim_supplier, dim_product, dim_customer, dim_employee, dim_date | свой id |
| fact_sales | sale_id |
| fact_visits | visit_id |
| fact_interest | interest_id |
| fact_loyalty | loyalty_id |
| fact_logistics | shipment_id |
| fact_inventory | inventory_id |

Ключ — первичный id: уникален по смыслу («одна строка = одна сущность / событие»),
используется в JOIN, не Nullable (ClickHouse требует этого для ключа).

## Как работает дедупликация

Загрузка — только `INSERT`, без `TRUNCATE`.
При вставке строки с уже существующим ключом ClickHouse при мерже
оставляет одну, самую новую. Дубли удаляются автоматически.

Чтобы увидеть актуальный результат сразу — `FINAL`:

    SELECT count(*) FROM olap.fact_sales FINAL;

## Проверка

Загрузка запущена дважды. Результат — в `notes/reconciliation.md` и `notes/load_log.txt`.
