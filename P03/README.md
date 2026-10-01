# P03. Загрузка данных в DuckDB

## Структура

```
OLAP/
├── P01/data/raw/
│   ├── dim_customer.csv
│   ├── dim_product.csv
│   └── fact_sales.csv
└── P03/
    ├── sql/ddl_duckdb.sql
    ├── load_data.py
    ├── checks.txt          # сохранённый вывод проверок
    └── warehouse.duckdb    # создаётся скриптом, не коммитим
```

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
- грузит CSV из `P01/data/raw/` в `dim_customer`, `dim_product`, `fact_sales`;
- заполняет `dim_date` и `dim_payment`;
- печатает проверки (строки, пустые ключи, суммы).

**Весь вывод скрипта — на английском (ASCII).** Это сделано специально,
чтобы избежать проблем с кодировкой в Windows PowerShell.

### 3. Сохранить вывод проверок

```powershell
python load_data.py *>&1 | Tee-Object -FilePath checks.txt
```

Результат — в `checks.txt`. Он же в репозитории как доказательство
выполнения пункта «Проверки» из задания.

## Повторный запуск

`python load_data.py` можно запускать сколько угодно раз.
Скрипт каждый раз делает `DELETE FROM` по таблицам и грузит CSV заново —
**данные не удваиваются**.
