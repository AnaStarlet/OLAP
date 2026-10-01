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
# Схема: 7 измерений + 6 фактов

## Измерения

| Таблица | Одна строка = | Ключ | Источник |
|---------|---------------|------|----------|
| `dim_store` | один магазин сети | `store_id` | `data/raw/dim_store.csv` |
| `dim_warehouse` | один склад / ЛЦ | `warehouse_id` | `data/raw/dim_warehouse.csv` |
| `dim_supplier` | один поставщик / производитель | `supplier_id` | `data/raw/dim_supplier.csv` |
| `dim_product` | одна товарная позиция | `product_id` | `data/raw/dim_product.csv` |
| `dim_customer` | один клиент | `customer_id` | `data/raw/dim_customer.csv` |
| `dim_employee` | один сотрудник | `employee_id` | `data/raw/dim_employee.csv` |
| `dim_date` | один календарный день | `date_id` | `data/raw/dim_date.csv` |

## Факты

| Таблица | Одна строка = | Ключ | Источник |
|---------|---------------|------|----------|
| `fact_visits` | одно посещение магазина | `visit_id` | `data/raw/fact_visits.csv` |
| `fact_interest` | один интерес к товару | `interest_id` | `data/raw/fact_interest.csv` |
| `fact_sales` | одна позиция продажи | `sale_id` | `data/raw/fact_sales.csv` |
| `fact_loyalty` | одна операция по бонусам | `loyalty_id` | `data/raw/fact_loyalty.csv` |
| `fact_logistics` | одна поставка товара | `shipment_id` | `data/raw/fact_logistics.csv` |
| `fact_inventory` | один остаток товара на дату | `inventory_id` | `data/raw/fact_inventory.csv` |

## Описание измерений

### `dim_store` — магазины
Одна строка = один магазин сети в РБ.  
Поля: `store_id`, `store_name`, `network`, `city`, `region`, `country`,
`address`, `store_format`, `area_m2`, `opening_date`, `logistics_center`,
`warehouse_id`, `employees_count`, `consultants_count`, `manager_name`,
`working_hours`, `status`.

### `dim_warehouse` — склады и логистические центры
Одна строка = один склад или ЛЦ.  
Поля: `warehouse_id`, `warehouse_name`, `warehouse_type`, `city`, `region`,
`country`, `address`, `area_m2`, `capacity_units`, `logistics_center`,
`manager_name`, `status`.

### `dim_supplier` — поставщики
Одна строка = один поставщик / производитель / импортёр.  
Поля: `supplier_id`, `supplier_name`, `supplier_type`, `country`, `city`,
`address`, `contact`, `contract_number`, `contract_date`, `payment_terms`,
`delivery_days`, `supplier_rating`, `status`.

### `dim_product` — товары
Одна строка = одна товарная позиция каталога.  
Поля: `product_id`, `article`, `product_name`, `category`, `subcategory`,
`item_type`, `material`, `metal_color`, `assay`, `weight_g`, `size`,
`stone`, `stone_count`, `cut`, `stone_color`, `clarity`, `collection`,
`season`, `target_gender`, `purpose`, `manufacturer_name`, `supplier_id`,
`cost_price`, `retail_price`, `currency`, `release_date`, `status`.

### `dim_customer` — клиенты
Одна строка = один клиент.  
Поля: `customer_id`, `full_name`, `birth_date`, `age`, `age_group`, `gender`,
`city`, `region`, `country`, `registration_date`, `loyalty_card`,
`loyalty_level`, `loyalty_join_date`, `bonus_balance`, `purchases_count`,
`total_purchases`, `avg_check`, `last_purchase_date`, `purchase_frequency`,
`preferred_material`, `preferred_category`, `acquisition_channel`, `status`.

### `dim_employee` — сотрудники
Одна строка = один сотрудник магазина.  
Поля: `employee_id`, `full_name`, `position`, `store_id`, `store_name`,
`department`, `hire_date`, `experience_years`, `shift`, `region`,
`country`, `status`.

### `dim_date` — календарь
Одна строка = один календарный день (2020-01-01 … 2026-10-01).  
Поля: `date_id`, `date`, `day`, `weekday`, `week`, `month`, `month_num`,
`quarter`, `year`, `season`, `is_workday`, `is_holiday`.

## Описание фактов

### `fact_visits` — посещения магазина
Одна строка = одно посещение магазина клиентом.  
Поля: `visit_id`, `date_id`, `time_id`, `customer_id`, `store_id`,
`employee_id`, `entry_time`, `exit_time`, `duration_min`, `visit_purpose`,
`new_customer`, `has_loyalty_card`, `got_consultation`, `products_viewed`,
`products_selected`, `purchase_made`, `purchase_amount`, `currency`.

### `fact_interest` — интерес к товару
Одна строка = один факт интереса клиента к товару в рамках посещения.  
Поля: `interest_id`, `visit_id`, `customer_id`, `product_id`, `store_id`,
`employee_id`, `date_id`, `time_id`, `view_minutes`, `tried_on`,
`got_consultation`, `asked_question`, `added_to_selection`,
`interest_reason`, `product_price`, `discount_pct`, `purchased`, `currency`.

### `fact_sales` — продажи
Одна строка = одна позиция продажи.  
Поля: `sale_id`, `date_id`, `time_id`, `customer_id`, `product_id`,
`store_id`, `employee_id`, `quantity`, `unit_price`, `discount_pct`,
`bonus_used`, `total_amount`, `cost_amount`, `profit_amount`,
`payment_method`, `sale_type`, `receipt_number`, `currency`.  
Способы оплаты: только `Наличные` и `Безналичные`.

### `fact_loyalty` — лояльность
Одна строка = одна операция по бонусам клиента.  
Поля: `loyalty_id`, `customer_id`, `date_id`, `sale_id`, `operation`,
`accrued`, `spent`, `balance`, `reason`, `customer_level`, `currency`.

### `fact_logistics` — логистика и сертификация
Одна строка = одна поставка товара.  
Поля: `shipment_id`, `product_id`, `supplier_id`, `warehouse_id`, `store_id`,
`dispatch_date`, `arrival_date`, `quantity`, `weight_g`, `transport_type`,
`invoice_number`, `delivery_cost`, `delivery_days`, `status`, `delay_reason`,
`certificate_number`, `verification_result`, `currency`.

### `fact_inventory` — остатки
Одна строка = остаток одного товара в одном магазине/складе на одну дату.  
Поля: `inventory_id`, `date_id`, `product_id`, `store_id`, `warehouse_id`,
`opening_stock`, `received`, `sold`, `returns`, `moved`, `closing_stock`,
`reserved`, `storage_days`.

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
- грузит CSV из `data/raw/`;
- печатает проверки (строки по каждой таблице).

### 3. Проверки
```powershell
duckdb warehouse.duckdb < checks.sql
```

### 4. Сохранить вывод проверок
```powershell
python load_data.py *>&1 | Tee-Object -FilePath checks.txt
duckdb warehouse.duckdb < checks.sql *>&1 | Tee-Object -FilePath checks.txt -Append
```

Результат — в `checks.txt`. Он же в репозитории как доказательство выполнения пункта «Проверки» из задания.

## Повторный запуск

`python load_data.py` можно запускать сколько угодно раз.
