-- ============================================================
-- З03. DDL для DuckDB. Ювелирная сеть Республики Беларусь.
-- 7 измерений + 6 фактов = 13 таблиц.
-- Данные: 2020-01-01 … 2026-10-01.
-- Деньги — DECIMAL(14,2), не FLOAT.
-- ============================================================

-- ------------------------------------------------------------
-- ИЗМЕРЕНИЯ
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_store (
    store_id            INTEGER PRIMARY KEY,
    store_name          VARCHAR NOT NULL,
    network             VARCHAR,
    city                VARCHAR,
    region              VARCHAR,
    country             VARCHAR,
    address             VARCHAR,
    store_format        VARCHAR,
    area_m2             INTEGER,
    opening_date        DATE,
    logistics_center    VARCHAR,
    warehouse_id        INTEGER,
    employees_count     INTEGER,
    consultants_count   INTEGER,
    manager_name        VARCHAR,
    working_hours       VARCHAR,
    status              VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_warehouse (
    warehouse_id        INTEGER PRIMARY KEY,
    warehouse_name      VARCHAR NOT NULL,
    warehouse_type      VARCHAR,
    city                VARCHAR,
    region              VARCHAR,
    country             VARCHAR,
    address             VARCHAR,
    area_m2             INTEGER,
    capacity_units      INTEGER,
    logistics_center    VARCHAR,
    manager_name        VARCHAR,
    status              VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_supplier (
    supplier_id         INTEGER PRIMARY KEY,
    supplier_name       VARCHAR NOT NULL,
    supplier_type       VARCHAR,
    country             VARCHAR,
    city                VARCHAR,
    address             VARCHAR,
    contact             VARCHAR,
    contract_number     VARCHAR,
    contract_date       DATE,
    payment_terms       VARCHAR,
    delivery_days       INTEGER,
    supplier_rating     DECIMAL(3,2),
    status              VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id          INTEGER PRIMARY KEY,
    article             VARCHAR NOT NULL,
    product_name        VARCHAR NOT NULL,
    category            VARCHAR,
    subcategory         VARCHAR,
    item_type           VARCHAR,
    material            VARCHAR,
    metal_color         VARCHAR,
    assay               INTEGER,
    weight_g            DECIMAL(6,2),
    size                VARCHAR,
    stone               VARCHAR,
    stone_count         INTEGER,
    cut                 VARCHAR,
    stone_color         VARCHAR,
    clarity             VARCHAR,
    collection          VARCHAR,
    season              VARCHAR,
    target_gender       VARCHAR,
    purpose             VARCHAR,
    manufacturer_name   VARCHAR,
    supplier_id         INTEGER,
    cost_price          DECIMAL(14,2),
    retail_price        DECIMAL(14,2),
    currency            VARCHAR,
    release_date        DATE,
    status              VARCHAR,
    FOREIGN KEY (supplier_id) REFERENCES dim_supplier(supplier_id)
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id         INTEGER PRIMARY KEY,
    full_name           VARCHAR NOT NULL,
    birth_date          DATE,
    age                 INTEGER,
    age_group           VARCHAR,
    gender              VARCHAR,
    city                VARCHAR,
    region              VARCHAR,
    country             VARCHAR,
    registration_date   DATE,
    loyalty_card        VARCHAR,
    loyalty_level       VARCHAR,
    loyalty_join_date   DATE,
    bonus_balance       DECIMAL(10,2),
    purchases_count     INTEGER,
    total_purchases     DECIMAL(14,2),
    avg_check           DECIMAL(10,2),
    last_purchase_date  DATE,
    purchase_frequency  VARCHAR,
    preferred_material  VARCHAR,
    preferred_category  VARCHAR,
    acquisition_channel VARCHAR,
    status              VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_employee (
    employee_id         INTEGER PRIMARY KEY,
    full_name           VARCHAR NOT NULL,
    position            VARCHAR,
    store_id            INTEGER,
    store_name          VARCHAR,
    department          VARCHAR,
    hire_date           DATE,
    experience_years    INTEGER,
    shift               VARCHAR,
    region              VARCHAR,
    country             VARCHAR,
    status              VARCHAR,
    FOREIGN KEY (store_id) REFERENCES dim_store(store_id)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id             INTEGER PRIMARY KEY,
    date                DATE NOT NULL,
    day                 INTEGER,
    weekday             VARCHAR,
    week                INTEGER,
    month               VARCHAR,
    month_num           INTEGER,
    quarter             INTEGER,
    year                INTEGER,
    season              VARCHAR,
    is_workday          VARCHAR,
    is_holiday          VARCHAR
);

-- ------------------------------------------------------------
-- ФАКТЫ
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_visits (
    visit_id            INTEGER PRIMARY KEY,
    date_id             INTEGER,
    time_id             INTEGER,
    customer_id         INTEGER,
    store_id            INTEGER,
    employee_id         INTEGER,
    entry_time          VARCHAR,
    exit_time           VARCHAR,
    duration_min        INTEGER,
    visit_purpose       VARCHAR,
    new_customer        VARCHAR,
    has_loyalty_card    VARCHAR,
    got_consultation    VARCHAR,
    products_viewed     INTEGER,
    products_selected   INTEGER,
    purchase_made       VARCHAR,
    purchase_amount     DECIMAL(14,2),
    currency            VARCHAR,
    FOREIGN KEY (date_id)     REFERENCES dim_date(date_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (store_id)    REFERENCES dim_store(store_id),
    FOREIGN KEY (employee_id) REFERENCES dim_employee(employee_id)
);

CREATE TABLE IF NOT EXISTS fact_interest (
    interest_id         INTEGER PRIMARY KEY,
    visit_id            INTEGER,
    customer_id         INTEGER,
    product_id          INTEGER,
    store_id            INTEGER,
    employee_id         INTEGER,
    date_id             INTEGER,
    time_id             INTEGER,
    view_minutes        INTEGER,
    tried_on            VARCHAR,
    got_consultation    VARCHAR,
    asked_question      VARCHAR,
    added_to_selection  VARCHAR,
    interest_reason     VARCHAR,
    product_price       DECIMAL(14,2),
    discount_pct        INTEGER,
    purchased           VARCHAR,
    currency            VARCHAR,
    FOREIGN KEY (visit_id)    REFERENCES fact_visits(visit_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id)  REFERENCES dim_product(product_id),
    FOREIGN KEY (store_id)    REFERENCES dim_store(store_id),
    FOREIGN KEY (employee_id) REFERENCES dim_employee(employee_id),
    FOREIGN KEY (date_id)     REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id             INTEGER PRIMARY KEY,
    date_id             INTEGER,
    time_id             INTEGER,
    customer_id         INTEGER,
    product_id          INTEGER,
    store_id            INTEGER,
    employee_id         INTEGER,
    quantity            INTEGER,
    unit_price          DECIMAL(14,2),
    discount_pct        INTEGER,
    bonus_used          DECIMAL(10,2),
    total_amount        DECIMAL(14,2),
    cost_amount         DECIMAL(14,2),
    profit_amount       DECIMAL(14,2),
    payment_method      VARCHAR,
    sale_type           VARCHAR,
    receipt_number      VARCHAR,
    currency            VARCHAR,
    FOREIGN KEY (date_id)     REFERENCES dim_date(date_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id)  REFERENCES dim_product(product_id),
    FOREIGN KEY (store_id)    REFERENCES dim_store(store_id),
    FOREIGN KEY (employee_id) REFERENCES dim_employee(employee_id)
);

CREATE TABLE IF NOT EXISTS fact_loyalty (
    loyalty_id          INTEGER PRIMARY KEY,
    customer_id         INTEGER,
    date_id             INTEGER,
    sale_id             INTEGER,
    operation           VARCHAR,
    accrued             DECIMAL(10,2),
    spent               DECIMAL(10,2),
    balance             DECIMAL(10,2),
    reason              VARCHAR,
    customer_level      VARCHAR,
    currency            VARCHAR,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (date_id)     REFERENCES dim_date(date_id),
    FOREIGN KEY (sale_id)     REFERENCES fact_sales(sale_id)
);

CREATE TABLE IF NOT EXISTS fact_logistics (
    shipment_id         INTEGER PRIMARY KEY,
    product_id          INTEGER,
    supplier_id         INTEGER,
    warehouse_id        INTEGER,
    store_id            INTEGER,
    dispatch_date       DATE,
    arrival_date        DATE,
    quantity            INTEGER,
    weight_g            DECIMAL(12,2),
    transport_type      VARCHAR,
    invoice_number      VARCHAR,
    delivery_cost       DECIMAL(14,2),
    delivery_days       INTEGER,
    status              VARCHAR,
    delay_reason        VARCHAR,
    certificate_number  VARCHAR,
    verification_result VARCHAR,
    currency            VARCHAR,
    FOREIGN KEY (product_id)   REFERENCES dim_product(product_id),
    FOREIGN KEY (supplier_id)  REFERENCES dim_supplier(supplier_id),
    FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id),
    FOREIGN KEY (store_id)     REFERENCES dim_store(store_id)
);

CREATE TABLE IF NOT EXISTS fact_inventory (
    inventory_id        INTEGER PRIMARY KEY,
    date_id             INTEGER,
    product_id          INTEGER,
    store_id            INTEGER,
    warehouse_id        INTEGER,
    opening_stock       INTEGER,
    received            INTEGER,
    sold                INTEGER,
    returns             INTEGER,
    moved               INTEGER,
    closing_stock       INTEGER,
    reserved            INTEGER,
    storage_days        INTEGER,
    FOREIGN KEY (date_id)      REFERENCES dim_date(date_id),
    FOREIGN KEY (product_id)   REFERENCES dim_product(product_id),
    FOREIGN KEY (store_id)     REFERENCES dim_store(store_id),
    FOREIGN KEY (warehouse_id) REFERENCES dim_warehouse(warehouse_id)
);