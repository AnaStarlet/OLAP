-- P09. Fill summary: revenue by store by month.
-- Full refresh: TRUNCATE + INSERT SELECT.

TRUNCATE TABLE olap.sales_by_store_month;

INSERT INTO olap.sales_by_store_month
SELECT
    d.year,
    d.month_num,
    f.store_id,
    s.store_name,
    sum(f.total_amount) AS amount_sum
FROM olap.fact_sales f FINAL
JOIN olap.dim_store s ON s.store_id = f.store_id
JOIN olap.dim_date  d ON d.date_id  = f.date_id
GROUP BY d.year, d.month_num, f.store_id, s.store_name;