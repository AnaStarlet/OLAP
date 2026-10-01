.mode csv
-- Z03. Post-load checks. Belarus jewelry chain.

-- 1. Row counts per table
SELECT 'dim_store'      AS table_name, COUNT(*) AS rows FROM dim_store
UNION ALL SELECT 'dim_warehouse',  COUNT(*) FROM dim_warehouse
UNION ALL SELECT 'dim_supplier',   COUNT(*) FROM dim_supplier
UNION ALL SELECT 'dim_product',    COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_customer',   COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_employee',   COUNT(*) FROM dim_employee
UNION ALL SELECT 'dim_date',       COUNT(*) FROM dim_date
UNION ALL SELECT 'fact_visits',    COUNT(*) FROM fact_visits
UNION ALL SELECT 'fact_interest',  COUNT(*) FROM fact_interest
UNION ALL SELECT 'fact_sales',     COUNT(*) FROM fact_sales
UNION ALL SELECT 'fact_loyalty',   COUNT(*) FROM fact_loyalty
UNION ALL SELECT 'fact_logistics', COUNT(*) FROM fact_logistics
UNION ALL SELECT 'fact_inventory', COUNT(*) FROM fact_inventory
ORDER BY table_name;

-- 2. Null keys in fact_sales (should be 0)
SELECT
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer,
    SUM(CASE WHEN product_id  IS NULL THEN 1 ELSE 0 END) AS null_product,
    SUM(CASE WHEN store_id    IS NULL THEN 1 ELSE 0 END) AS null_store,
    SUM(CASE WHEN date_id     IS NULL THEN 1 ELSE 0 END) AS null_date
FROM fact_sales;

-- 3. Main measure: total sales
SELECT
    COUNT(*)           AS sales_rows,
    SUM(quantity)      AS total_quantity,
    SUM(total_amount)  AS total_revenue_byn,
    SUM(cost_amount)   AS total_cost_byn,
    SUM(profit_amount) AS total_profit_byn
FROM fact_sales;

-- 4. Average check
SELECT ROUND(AVG(total_amount), 2) AS avg_check_byn
FROM fact_sales;

-- 5. Payment methods (only 2 expected)
SELECT payment_method, COUNT(*) AS cnt
FROM fact_sales
GROUP BY payment_method
ORDER BY payment_method;

-- 6. Date range
SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM dim_date;

-- 7. Top-5 stores by revenue
SELECT s.store_name, SUM(f.total_amount) AS revenue
FROM fact_sales f
JOIN dim_store s USING (store_id)
GROUP BY s.store_name
ORDER BY revenue DESC
LIMIT 5;
