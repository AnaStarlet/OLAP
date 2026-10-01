## Как поднять ClickHouse

Из папки `P01/`:

    cd P01
    docker compose up -d
    chmod +x scripts/init_ch.sh
    ./scripts/init_ch.sh
    curl http://localhost:8123/ping     # → Ok.

## Порты

| Сервис | Порт |
|--------|------|
| ClickHouse | 8123 |
| ClickHouse | 9000 |
| Metabase | 3000 |

## Сырьё

### Сводная таблица

| Файл | Строк | Поля |
|------|-------|------|
| `dim_product.csv` | 25 000 | product_id, product_name, category, brand, unit, price, supplier_id |
| `dim_customer.csv` | 25 000 | customer_id, full_name, gender, age, city, loyalty_card, register_date |
| `fact_sales.csv` | 25 000 | sale_id, sale_datetime, customer_id, product_id, quantity, unit_price, total_amount, payment_type, store_id |

---

### dim_customer.csv

| Поле | Расшифровка | Тип |
|------|-------------|-----|
| `customer_id` | Уникальный идентификатор покупателя | INT (PK) |
| `full_name` | ФИО покупателя | VARCHAR |
| `gender` | Пол покупателя | VARCHAR |
| `age` | Возраст покупателя | INT |
| `city` | Город покупателя | VARCHAR |
| `loyalty_card` | Наличие карты лояльности | VARCHAR |
| `register_date` | Дата регистрации покупателя | DATE |

---

### dim_product.csv

| Поле | Расшифровка | Тип |
|------|-------------|-----|
| `product_id` | Уникальный идентификатор товара | INT (PK) |
| `product_name` | Название товара | VARCHAR |
| `category` | Категория товара | VARCHAR |
| `brand` | Бренд производителя | VARCHAR |
| `unit` | Единица измерения | VARCHAR |
| `price` | Справочная цена товара | DECIMAL |
| `supplier_id` | Идентификатор поставщика | INT (FK) |

---

### fact_sales.csv

| Поле | Расшифровка | Тип |
|------|-------------|-----|
| `sale_id` | Уникальный идентификатор продажи | INT (PK) |
| `sale_datetime` | Дата и время продажи | DATETIME |
| `customer_id` | Идентификатор покупателя | INT (FK) |
| `product_id` | Идентификатор товара | INT (FK) |
| `quantity` | Количество проданных единиц | INT |
| `unit_price` | Фактическая цена за единицу | DECIMAL |
| `total_amount` | Итоговая сумма продажи | DECIMAL |
| `payment_type` | Способ оплаты | VARCHAR |
| `store_id` | Идентификатор магазина | INT (FK) |

---
