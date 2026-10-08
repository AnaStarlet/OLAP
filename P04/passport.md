# Паспорт витрины

**ФИО:** Сакович Анастасия, Потапчик Анастасия, Журавская Полина  
**Группа:** СДП-ИИ-231  
**Дата:** 10.10.2026  
**Домен:** Розничная торговля — ювелирный магазин

---

## 1. Бизнес-цель витрины (1–2 предложения)

Витрина показывает продажи ювелирного магазина: оборот, количество проданных единиц и структуру продаж по товарам, категориям, магазинам, клиентам и времени. Нужна, чтобы отвечать на вопросы «что и где продаётся лучше», «как меняется выручка по месяцам», «какие категории дают основной оборот».

---

## 2. Grain (одна фраза)

**Одна строка факта `fact_sales` = одна позиция в чеке** (один товар в одной продаже с количеством и суммой).

---

## 3. Fact-таблица(ы)

| Имя | Grain | Примечание |
|---|---|---|
| `fact_sales` | одна строка = одна позиция чека (`sale_id` + `product_id`) | В сырье `fact_sales.csv` уже одна строка на товарную позицию. |

---

## 4. Меры

| Мера | sum ok? | Определение |
|---|---|---|
| `total_amount` | да | Сумма продажи по позиции (`quantity * unit_price`), в сырье уже посчитана |
| `quantity` | да | Количество единиц товара в позиции |
| `cost_amount` | да | Себестоимость позиции |
| `profit_amount` | да | Прибыль по позиции |
| `unit_price` | нет | Цена за единицу; только avg/min/max |
| `sales_count` | count | `COUNT(*)` — число позиций |

---

## 5. Измерения

| Dim | Ключ | Важные атрибуты | SCD |
|---|---|---|---|
| `dim_product` | `product_id` | `product_name`, `category`, `subcategory`, `material`, `retail_price`, `supplier_id` | SCD2 по `category`, `retail_price` |
| `dim_store` | `store_id` | `store_name`, `network`, `city`, `region`, `address`, `store_format` | SCD1 |
| `dim_customer` | `customer_id` | `full_name`, `gender`, `age`, `age_group`, `city`, `loyalty_card`, `loyalty_level` | SCD1 |
| `dim_date` | `date_id` | `date`, `month`, `month_num`, `quarter`, `year`, `weekday` | нет |
| `dim_employee` | `employee_id` | `full_name`, `position`, `store_id` | SCD1 |
| `dim_supplier` | `supplier_id` | `supplier_name`, `supplier_type`, `country` | SCD1 |
| `dim_warehouse` | `warehouse_id` | `warehouse_name`, `warehouse_type`, `city` | SCD1 |

---

## 6. Три бизнес-вопроса

1. Какой общий оборот по магазинам за январь 2024 года?
2. Какие категории товаров дают наибольший оборот за квартал?
3. Как меняется средний чек по месяцам и способам оплаты?

---

## 7. Эталонный SQL одной метрики

**Главная метрика:** оборот без возвратов = `SUM(total_amount)` по `fact_sales`.  
Возвратов в сырье нет, поэтому «оборот без возвратов» совпадает с обычным оборотом.

```sql
-- sql/canonical_metric.sql
SELECT SUM(total_amount) AS revenue_byn
FROM fact_sales;
```

**Зафиксированное значение:** `3 557 661 372.99 BYN`.

**Пример разреза: оборот по месяцам за 2024 год**

```sql
SELECT
    d.year,
    d.month_num,
    SUM(f.total_amount) AS revenue_byn
FROM fact_sales f
JOIN dim_date d ON d.date_id = f.date_id
WHERE d.year = 2024
GROUP BY d.year, d.month_num
ORDER BY d.year, d.month_num;
```

---

## 8. Риски / cut

- **Возвратов нет в сырье** — в `fact_sales.csv` нет признака `is_return`, поэтому «оборот без возвратов» совпадает с обычным оборотом.
- **Справочник `dim_store`** — в сырье `store_id` есть в факте, но атрибутов магазина изначально не было; справочник заполнен вручную.
- **`dim_product` и `dim_customer`** — требуют очистки и приведения типов при загрузке.
- **SCD2 по товарам** — в сырье только текущее состояние `dim_product`, для истории нужна отдельная таблица с `valid_from` / `valid_to`.
- **`dim_payment` не выделен в отдельную таблицу** — `payment_method` хранится прямо в `fact_sales` как `VARCHAR` (значения: `Наличные`, `Безналичные`). При необходимости фильтрации по способу оплаты используется это поле.
- **6 фактов, а не 1** — витрина строится вокруг `fact_sales` (главный факт), остальные пять (`fact_visits`, `fact_interest`, `fact_loyalty`, `fact_logistics`, `fact_inventory`) — сопутствующие, для кросс-анализа поведения клиента и остатков.
- **ClickHouse / Kafka / ML** — не делаем, выносим в cut с описанием, чем это грозит отчётам.\*\* — не делаем, выносим в cut с описанием, чем это грозит отчётам.

