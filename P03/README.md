\# P03. Загрузка данных в DuckDB



\## Структура



```

OLAP/

├── P01/data/raw/          # исходное сырьё

│   ├── dim\_customer.csv

│   ├── dim\_product.csv

│   └── fact\_sales.csv

└── P03/

&#x20;   ├── sql/ddl\_duckdb.sql # создание таблиц

&#x20;   ├── load\_data.py       # скрипт загрузки

&#x20;   └── warehouse.duckdb   # БД (создаётся скриптом)

```



\## Как загрузить



\### 1. Установить DuckDB (один раз)



```powershell

python -m pip install duckdb

```



\### 2. Запустить скрипт из папки `P03`



```powershell

python load\_data.py

```



Скрипт:



\- создаёт таблицы из `sql/ddl\_duckdb.sql`;

\- очищает таблицы (`DELETE FROM`) — повторный запуск не дублирует данные;

\- грузит CSV из `P01/data/raw/` в таблицы `dim\_customer`, `dim\_product`, `fact\_sales`;

\- заполняет `dim\_date` и `dim\_payment` из факта;

\- печатает проверки (строки, пустые ключи, сумму).



\### 3. Проверить



```powershell

duckdb warehouse.duckdb "SELECT COUNT(\*) FROM fact\_sales;"

duckdb warehouse.duckdb "SELECT SUM(total\_amount) FROM fact\_sales;"

```



\## Повторный запуск



`python load\_data.py` можно запускать много раз — данные не удваиваются

(перед загрузкой таблицы очищаются).

