-- P07. DDL for ClickHouse (MergeTree engine).
-- ORDER BY uses ONLY non-Nullable columns (ClickHouse requirement).
-- Money — Decimal, not Float.
-- Yes/No flags stored as String because CSV uses Russian "Да"/"Нет".

CREATE DATABASE IF NOT EXISTS olap;

-- Dimensions (7)

CREATE TABLE IF NOT EXISTS olap.dim_store (
    store_id Int32, store_name String, network String, city String, region String,
    country String, address String, store_format String, area_m2 Nullable(Float64),
    opening_date Nullable(Date), logistics_center String, warehouse_id Nullable(Int32),
    employees_count Nullable(Int32), consultants_count Nullable(Int32),
    manager_name String, working_hours String, status String
) ENGINE = MergeTree ORDER BY (store_id);

CREATE TABLE IF NOT EXISTS olap.dim_warehouse (
    warehouse_id Int32, warehouse_name String, warehouse_type String, city String,
    region String, country String, address String, area_m2 Nullable(Float64),
    capacity_units Nullable(Int32), logistics_center String, manager_name String, status String
) ENGINE = MergeTree ORDER BY (warehouse_id);

CREATE TABLE IF NOT EXISTS olap.dim_supplier (
    supplier_id Int32, supplier_name String, supplier_type String, country String,
    city String, address String, contact String, contract_number String,
    contract_date Nullable(Date), payment_terms String, delivery_days Nullable(Int32),
    supplier_rating Nullable(Float64), status String
) ENGINE = MergeTree ORDER BY (supplier_id);

CREATE TABLE IF NOT EXISTS olap.dim_product (
    product_id Int32, article String, product_name String, category String,
    subcategory String, item_type String, material String, metal_color String,
    assay Nullable(Int32), weight_g Nullable(Decimal(14,2)), size String, stone String,
    stone_count Nullable(Int32), cut String, stone_color String, clarity String,
    collection String, season String, target_gender String, purpose String,
    manufacturer_name String, supplier_id Nullable(Int32),
    cost_price Nullable(Decimal(14,2)), retail_price Nullable(Decimal(14,2)),
    currency String, release_date Nullable(Date), status String
) ENGINE = MergeTree ORDER BY (product_id);

CREATE TABLE IF NOT EXISTS olap.dim_customer (
    customer_id Int32, full_name String, birth_date Nullable(Date), age Nullable(Int32),
    age_group String, gender String, city String, region String, country String,
    registration_date Nullable(Date), loyalty_card String, loyalty_level String,
    loyalty_join_date Nullable(Date), bonus_balance Nullable(Decimal(14,2)),
    purchases_count Nullable(Int32), total_purchases Nullable(Decimal(14,2)),
    avg_check Nullable(Decimal(14,2)), last_purchase_date Nullable(Date),
    purchase_frequency String, preferred_material String, preferred_category String,
    acquisition_channel String, status String
) ENGINE = MergeTree ORDER BY (customer_id);

CREATE TABLE IF NOT EXISTS olap.dim_employee (
    employee_id Int32, full_name String, position String, store_id Nullable(Int32),
    store_name String, department String, hire_date Nullable(Date),
    experience_years Nullable(Int32), shift String, region String, country String, status String
) ENGINE = MergeTree ORDER BY (employee_id);

CREATE TABLE IF NOT EXISTS olap.dim_date (
    date_id Int32, date Date, day Nullable(Int32), weekday String, week Nullable(Int32),
    month String, month_num Nullable(Int32), quarter Nullable(Int32), year Nullable(Int32),
    season String, is_workday String, is_holiday String
) ENGINE = MergeTree ORDER BY (date_id);

-- Facts (6)

CREATE TABLE IF NOT EXISTS olap.fact_sales (
    sale_id Int32, date_id Int32, time_id Nullable(Int32), customer_id Nullable(Int32),
    product_id Nullable(Int32), store_id Nullable(Int32), employee_id Nullable(Int32),
    quantity Nullable(Int32), unit_price Nullable(Decimal(14,2)),
    discount_pct Nullable(Int32), bonus_used Nullable(Decimal(14,2)),
    total_amount Nullable(Decimal(14,2)), cost_amount Nullable(Decimal(14,2)),
    profit_amount Nullable(Decimal(14,2)), payment_method String, sale_type String,
    receipt_number String, currency String
) ENGINE = MergeTree ORDER BY (date_id);

CREATE TABLE IF NOT EXISTS olap.fact_visits (
    visit_id Int32, date_id Int32, time_id Nullable(Int32), customer_id Nullable(Int32),
    store_id Nullable(Int32), employee_id Nullable(Int32), entry_time String, exit_time String,
    duration_min Nullable(Int32), visit_purpose String,
    new_customer String, has_loyalty_card String, got_consultation String,
    products_viewed Nullable(Int32), products_selected Nullable(Int32),
    purchase_made String, purchase_amount Nullable(Decimal(14,2)), currency String
) ENGINE = MergeTree ORDER BY (date_id);

CREATE TABLE IF NOT EXISTS olap.fact_interest (
    interest_id Int32, visit_id Nullable(Int32), customer_id Nullable(Int32),
    product_id Nullable(Int32), store_id Nullable(Int32), employee_id Nullable(Int32),
    date_id Int32, time_id Nullable(Int32), view_minutes Nullable(Int32),
    tried_on String, got_consultation String, asked_question String,
    added_to_selection String, interest_reason String,
    product_price Nullable(Decimal(14,2)), discount_pct Nullable(Int32),
    purchased String, currency String
) ENGINE = MergeTree ORDER BY (date_id);

CREATE TABLE IF NOT EXISTS olap.fact_loyalty (
    loyalty_id Int32, customer_id Nullable(Int32), date_id Int32, sale_id Nullable(Int32),
    operation String, accrued Nullable(Decimal(14,2)), spent Nullable(Decimal(14,2)),
    balance Nullable(Decimal(14,2)), reason String, customer_level String, currency String
) ENGINE = MergeTree ORDER BY (date_id);

CREATE TABLE IF NOT EXISTS olap.fact_logistics (
    shipment_id Int32, product_id Nullable(Int32), supplier_id Nullable(Int32),
    warehouse_id Nullable(Int32), store_id Nullable(Int32), dispatch_date Nullable(Date),
    arrival_date Nullable(Date), quantity Nullable(Int32), weight_g Nullable(Decimal(14,2)),
    transport_type String, invoice_number String, delivery_cost Nullable(Decimal(14,2)),
    delivery_days Nullable(Int32), status String, delay_reason String,
    certificate_number String, verification_result String, currency String
) ENGINE = MergeTree ORDER BY (shipment_id);

CREATE TABLE IF NOT EXISTS olap.fact_inventory (
    inventory_id Int32, date_id Int32, product_id Nullable(Int32), store_id Nullable(Int32),
    warehouse_id Nullable(Int32), opening_stock Nullable(Int32), received Nullable(Int32),
    sold Nullable(Int32), returns Nullable(Int32), moved Nullable(Int32),
    closing_stock Nullable(Int32), reserved Nullable(Int32), storage_days Nullable(Int32)
) ENGINE = MergeTree ORDER BY (date_id);