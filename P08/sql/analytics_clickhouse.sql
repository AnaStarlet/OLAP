-- P08. Analytics queries in ClickHouse.

-- ============================================================
-- Canonical metric: total revenue
-- ============================================================
SELECT sum(total_amount) AS revenue_byn
FROM olap.fact_sales FINAL;


-- ============================================================
-- Question 1: revenue by store for January 2024
-- ============================================================
SELECT
    s.store_name,
    sum(f.total_amount) AS revenue_byn
FROM olap.fact_sales f FINAL
JOIN olap.dim_store s ON s.store_id = f.store_id
JOIN olap.dim_date  d ON d.date_id  = f.date_id
WHERE d.year = 2024 AND d.month_num = 1
GROUP BY s.store_name
ORDER BY revenue_byn DESC;


-- ============================================================
-- Question 2: top categories for Q1 2024
-- window function: share_pct + rank
-- ============================================================
WITH q AS (
    SELECT
        p.category,
        sum(f.total_amount) AS revenue_byn
    FROM olap.fact_sales f FINAL
    JOIN olap.dim_product p ON p.product_id = f.product_id
    JOIN olap.dim_date    d ON d.date_id    = f.date_id
    WHERE d.year = 2024 AND d.quarter = 1
    GROUP BY p.category
)
SELECT
    category,
    revenue_byn,
    round(100.0 * revenue_byn / sum(revenue_byn) OVER (), 2) AS share_pct,
    rank() OVER (ORDER BY revenue_byn DESC)                  AS rank_in_quarter
FROM q
ORDER BY revenue_byn DESC;


-- ============================================================
-- Question 3: avg check by month and payment method
-- ============================================================
SELECT
    d.year,
    d.month_num,
    f.payment_method,
    avg(f.total_amount) AS avg_check_byn,
    count(*)            AS sales_count
FROM olap.fact_sales f FINAL
JOIN olap.dim_date d ON d.date_id = f.date_id
WHERE d.year = 2024
GROUP BY d.year, d.month_num, f.payment_method
ORDER BY d.month_num, f.payment_method;