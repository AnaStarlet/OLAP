# OLAP-проект

**ФИО:** Сакович Анастасия, Потапчик Анастасия, Журавская Полина  
**Группа:** СДП-ИИ-231  
**Домен:** Розничная торговля — продуктовый магазин

## Как поднять ClickHouse

Из корня проекта:

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

| Файл | Строк | Поля |
|------|-------|------|
| `dim_product.csv` | 25 000 | product_id, product_name, category, brand, unit, price, supplier_id |
| `dim_customer.csv` | 25 000 | customer_id, full_name, gender, age, city, loyalty_card, register_date |
| `fact_sales.csv` | 25 000 | sale_id, sale_datetime, customer_id, product_id, quantity, unit_price, total_amount, payment_type, store_id |
