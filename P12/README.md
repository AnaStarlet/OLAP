# Проект OLAP

**Предметная область:** розничная торговля — сеть ювелирных магазинов.

Репозиторий содержит полный аналитический пайплайн для розничной сети ювелирных магазинов: от исходных CSV-файлов до аналитической витрины в ClickHouse и интерактивного дашборда в Metabase.

## Требования

Перед началом убедитесь, что у вас установлены:
* **Docker Desktop** — [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
* **Python 3.9+** — [https://www.python.org/downloads/](https://www.python.org/downloads/) (при установке на Windows обязательно отметьте галочку **Add Python to PATH**)
* **Git** (если планируете скачивать через консоль)

---

## Как запустить проект

### 1. Скачать проект

Через Git (в терминале):
```bash
git clone https://github.com/AnaStarlet/OLAP.git OLAP-project
cd OLAP-project
```
*(Или скачайте ZIP прямо на GitHub: нажмите зеленую кнопку **Code → Download ZIP** и распакуйте архив).*

### 2. Запустить базы данных через Docker

**Запуск ClickHouse (важно указать пароль `1234`):**
```bash
docker run -d --name clickhouse-olap -p 8123:8123 -p 9000:9000 -v clickhouse_data:/var/lib/clickhouse -e CLICKHOUSE_PASSWORD=1234 clickhouse/clickhouse-server:latest
```

**Запуск Metabase:**
```bash
docker run -d --name metabase-olap -p 3000:3000 metabase/metabase:latest
```

### 3. Установить драйвер ClickHouse для Metabase
Metabase «из коробки» не умеет работать с ClickHouse, нужен плагин.
1. Скачайте файл `clickhouse.metabase-driver.jar` по ссылке: [https://github.com/clickhouse/metabase-clickhouse-driver/releases/latest](https://github.com/clickhouse/metabase-clickhouse-driver/releases/latest)
2. Откройте терминал/CMD в папке, куда скачался файл, и скопируйте его в контейнер:
```bash
docker cp clickhouse.metabase-driver.jar metabase-olap:/plugins/
docker restart metabase-olap
```

### 4. Подготовить базу данных и таблицы (выполняется один раз)
*Скрипт загрузки не создает базу сам, поэтому выполните это перед первым запуском:*
```bash
docker exec -it clickhouse-olap clickhouse-client --user default --password 1234 --query "CREATE DATABASE IF NOT EXISTS olap"
docker exec -i clickhouse-olap clickhouse-client --user default --password 1234 --multiquery < P07/sql/ddl_clickhouse.sql
```

### 5. Установить зависимости и загрузить данные в ClickHouse
Установите Python-библиотеки:
```bash
pip install clickhouse-driver pandas
```
Запустите скрипт загрузки данных:
```bash
cd P07
python etl/load_all.py
```

### 6. Проверить эталонную метрику в ClickHouse
Выполните запрос в терминале (или в любом SQL-клиенте):
```sql
SELECT sum(total_amount) FROM olap.fact_sales FINAL;
```
Либо прямо через Docker:
```bash
docker exec -it clickhouse-olap clickhouse-client --user default --password 1234 --query "SELECT sum(total_amount) FROM olap.fact_sales FINAL"
```
**Ожидаемый результат:** `3 557 661 372.99`

### 7. Открыть дашборд
1. Перейдите по адресу [http://localhost:3000](http://localhost:3000).
2. Пройдите первичную настройку (создайте аккаунт администратора).
3. В меню **Admin Settings → Databases → Add database** добавьте базу:
   * **Тип:** ClickHouse
   * **Host:** `localhost`
   * **Port:** `8123`
   * **Username:** `default`
   * **Password:** `1234`
4. Нажмите **Save**. Metabase просканирует таблицы. Откройте дашборд `Дашборд OLAP`.

### 8. Проверить логи при возникновении ошибок
```bash
docker logs clickhouse-olap
docker logs metabase-olap
```

---

## Повторный запуск (после перезагрузки компьютера)

Создавать контейнеры заново не нужно, просто запустите их:
```bash
docker start clickhouse-olap metabase-olap
```
Данные сохраняются в томе `clickhouse_data`.

---

## Путь данных

1. **Источник данных:** CSV-файлы в каталоге `P03/data/raw/`.
2. **Загрузка данных:** скрипт `P07/etl/load_all.py` загружает данные в ClickHouse.
3. **Обработка данных:** используется движок `ReplacingMergeTree` с ключом `ORDER BY (sale_id)` для обработки повторных записей.
4. **Аналитическая витрина:** 13 таблиц, включая 7 справочников и 6 таблиц фактов. Сводная таблица `sales_by_store_month` используется для построения графиков.
5. **Расчёт метрики:** эталонный SQL-запрос находится в `P10/dashboards/widget1_metric.sql` и рассчитывает сумму `total_amount`.
6. **Визуализация:** Metabase подключается к ClickHouse и отображает аналитические показатели на дашборде.
7. **Проверка результатов:** сверка показателей SQL и BI выполняется в каталоге `P11`.

> **Гранулярность факта:** одна строка таблицы `fact_sales` соответствует одной позиции в чеке.

> **Главная мера:** `total_amount` — оборот в белорусских рублях (BYN).

---

## Структура проекта

| Каталог | Назначение |
|---|---|
| `P03–P05` | Загрузка данных в DuckDB и проверка результатов |
| `P06` | Реализация SCD2 для истории справочника товаров |
| `P07–P09` | Загрузка данных в ClickHouse, работа с партициями и сводными таблицами |
| `P10` | Создание дашборда в Metabase |
| `P11` | Сверка результатов SQL и BI |
| `P12` | Финальная сборка проекта |

---

## Ограничения проекта (Cut)

| Ограничение | Обоснование и последствия |
|---|---|
| Кластер ClickHouse | Используется один сервер ClickHouse. Горизонтальное масштабирование и отказоустойчивость кластера не реализованы. |
| Kafka и потоковая загрузка | Данные загружаются пакетно из CSV-файлов. Обновление показателей в реальном времени не реализовано. |
| ML-прогнозирование спроса | Витрина предназначена для анализа исторических данных. Прогнозирование будущих продаж и автоматическое планирование закупок не реализованы. |
| Учёт возвратов | В исходных данных отсутствует признак `is_return`, поэтому отдельный расчёт оборота за вычетом возвратов не реализован. |
| Праздники в `dim_date` | Сезонность анализируется по месяцам и кварталам без отдельного учёта праздничных дней. |

---

## Технологический стек

* **Python** — генерация, подготовка и загрузка данных.
* **SQL** — создание таблиц, аналитические запросы и проверка метрик.
* **CSV** — хранение исходных данных.
* **DuckDB** — локальная аналитическая база данных.
* **ClickHouse** — аналитическая СУБД для обработки данных.
* **Docker** — запуск сервисов.
* **Metabase** — визуализация показателей и создание дашборда.

---

## Итог

Проект демонстрирует полный цикл построения OLAP-решения: подготовку исходных данных, загрузку в аналитическую СУБД, создание аналитических витрин, расчёт контрольных метрик и визуализацию результатов в BI-системе.
