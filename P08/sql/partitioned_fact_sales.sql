CREATE TABLE IF NOT EXISTS olap.fact_sales_partitioned (
    sale_id Int32, date_id Int32, time_id Nullable(Int32), customer_id Nullable(Int32),
    product_id Nullable(Int32), store_id Nullable(Int32), employee_id Nullable(Int32),
    quantity Nullable(Int32), unit_price Nullable(Decimal(14,2)),
    discount_pct Nullable(Int32), bonus_used Nullable(Decimal(14,2)),
    total_amount Nullable(Decimal(14,2)), cost_amount Nullable(Decimal(14,2)),
    profit_amount Nullable(Decimal(14,2)), payment_method String, sale_type String,
    receipt_number String, currency String
) ENGINE = ReplacingMergeTree
PARTITION BY intDiv(date_id, 100)
ORDER BY (sale_id);

INSERT INTO olap.fact_sales_partitioned
SELECT * FROM olap.fact_sales FINAL;

SELECT
    partition,
    rows,
    formatReadableSize(bytes_on_disk) AS size
FROM system.parts
WHERE database = 'olap' AND table = 'fact_sales_partitioned' AND active
ORDER BY partition;