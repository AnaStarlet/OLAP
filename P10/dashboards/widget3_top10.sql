SELECT
    s.store_name,
    sum(f.total_amount) AS revenue
FROM olap.fact_sales f FINAL
JOIN olap.dim_store s ON s.store_id = f.store_id
GROUP BY s.store_name
ORDER BY revenue DESC
LIMIT 10
