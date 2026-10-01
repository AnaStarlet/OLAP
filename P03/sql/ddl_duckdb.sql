-- 03. DDL витрины "Розничная торговля — продуктовый магазин"
-- Grain факта: одна строка = одна позиция в чеке (sale_id + product_id)

CREATE TABLE IF NOT EXISTS dim_product (
    product_id    INTEGER PRIMARY KEY,
    product_name  VARCHAR NOT NULL,
    category      VARCHAR NOT NULL,
    brand         VARCHAR,
    unit          VARCHAR,
    price         DECIMAL(12, 2),
    supplier_id   INTEGER
);

CREATE TABLE IF NOT EXISTS dim_store (
    store_id    INTEGER PRIMARY KEY,
    store_name  VARCHAR NOT NULL,
    region      VARCHAR,
    city        VARCHAR,
    address     VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id     INTEGER PRIMARY KEY,
    full_name       VARCHAR NOT NULL,
    gender          VARCHAR(1),
    age             INTEGER,
    city            VARCHAR,
    loyalty_card    BOOLEAN,
    register_date   DATE
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key   DATE PRIMARY KEY,
    year       INTEGER NOT NULL,
    month      INTEGER NOT NULL,
    quarter    INTEGER NOT NULL,
    weekday    VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_payment (
    payment_type VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id        INTEGER NOT NULL,
    product_id     INTEGER NOT NULL,
    store_id       INTEGER NOT NULL,
    customer_id    INTEGER,
    sale_datetime  TIMESTAMP NOT NULL,
    payment_type   VARCHAR,
    quantity       INTEGER NOT NULL,
    unit_price     DECIMAL(12, 2) NOT NULL,
    total_amount   DECIMAL(14, 2) NOT NULL,
    PRIMARY KEY (sale_id, product_id),
    FOREIGN KEY (product_id)   REFERENCES dim_product(product_id),
    FOREIGN KEY (store_id)     REFERENCES dim_store(store_id),
    FOREIGN KEY (customer_id)  REFERENCES dim_customer(customer_id),
    FOREIGN KEY (payment_type) REFERENCES dim_payment(payment_type)
);