CREATE DATABASE IF NOT EXISTS retail_dw;

CREATE TABLE IF NOT EXISTS retail_dw.dim_product
(
    product_id UInt32,
    product_name String,
    category String,
    brand String,
    unit String,
    price Float64,
    supplier_id UInt32
)
ENGINE = MergeTree
ORDER BY product_id;

CREATE TABLE IF NOT EXISTS retail_dw.dim_customer
(
    customer_id UInt32,
    full_name String,
    gender String,
    age UInt8,
    city String,
    loyalty_card String,
    register_date Date
)
ENGINE = MergeTree
ORDER BY customer_id;

CREATE TABLE IF NOT EXISTS retail_dw.fact_sales
(
    sale_id UInt64,
    sale_datetime DateTime,
    customer_id UInt32,
    product_id UInt32,
    quantity UInt8,
    unit_price Float64,
    total_amount Float64,
    payment_type String,
    store_id UInt8
)
ENGINE = MergeTree
ORDER BY (sale_datetime, store_id, product_id);