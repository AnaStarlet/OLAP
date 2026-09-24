# OLAP-проект

**ФИО:** Сакович Анастасия, Потапчик Анастасия, Журавская Полина
**Группа:** СДП-ИИ-231
**Домен:** онлайн-продажи электроники

## Как поднять ClickHouse

Из корня проекта:

```bash
docker compose up -d
chmod +x scripts/init_ch.sh
./scripts/init_ch.sh
curl http://localhost:8123/ping     # → Ok.
```

## Порты

| Сервис | Порт |
|---|---|
| ClickHouse | 8123 |
| ClickHouse | 9000 |
| Metabase | 3000 |

## Сырьё

Папка `data/raw/`:

| Файл | Поля |
|---|---|
| dim_customer.csv | customer_id, customer_name, city, segment |
| dim_product.csv | product_id, product_name, category, brand |
| dim_date.csv | date_id, full_date, year, month, month_name, day_of_week |
| fact_orders.csv | order_id, date_id, customer_id, product_id, qty, amount |

---