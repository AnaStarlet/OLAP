-- ============================================================
-- З04. Аналитический SQL
-- Три запроса под три бизнес-вопроса из паспорта
-- ============================================================


-- ------------------------------------------------------------
-- Вопрос 1: Какой общий оборот по магазинам за январь 2024 года?
-- WHERE + GROUP BY
-- ------------------------------------------------------------
SELECT
    s.store_name,
    SUM(f.total_amount) AS revenue_byn
FROM fact_sales f
JOIN dim_store s ON s.store_id = f.store_id
JOIN dim_date  d ON d.date_id  = f.date_id
WHERE d.year = 2024 AND d.month_num = 1
GROUP BY s.store_name
ORDER BY revenue_byn DESC;


-- ------------------------------------------------------------
-- Вопрос 2: Какие категории товаров дают наибольший оборот за квартал?
-- GROUP BY + ОКОННАЯ ФУНКЦИЯ (доля категории + место в рейтинге)
-- ------------------------------------------------------------
WITH q AS (
    SELECT
        p.category,
        SUM(f.total_amount) AS revenue_byn
    FROM fact_sales f
    JOIN dim_product p ON p.product_id = f.product_id
    JOIN dim_date    d ON d.date_id    = f.date_id
    WHERE d.year = 2024 AND d.quarter = 1
    GROUP BY p.category
)
SELECT
    category,
    revenue_byn,
    ROUND(100.0 * revenue_byn / SUM(revenue_byn) OVER (), 2) AS share_pct,
    RANK() OVER (ORDER BY revenue_byn DESC)                  AS rank_in_quarter
FROM q
ORDER BY revenue_byn DESC;


-- ------------------------------------------------------------
-- Вопрос 3: Как меняется средний чек по месяцам и способам оплаты?
-- GROUP BY по двум разрезам
-- ------------------------------------------------------------
SELECT
    d.year,
    d.month_num,
    f.payment_method,
    AVG(f.total_amount) AS avg_check_byn,
    COUNT(*)            AS sales_count
FROM fact_sales f
JOIN dim_date d ON d.date_id = f.date_id
WHERE d.year = 2024
GROUP BY d.year, d.month_num, f.payment_method
ORDER BY d.month_num, f.payment_method;
