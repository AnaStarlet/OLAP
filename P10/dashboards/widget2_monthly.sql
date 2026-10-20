SELECT
    concat(toString(year), '-', leftPad(toString(month_num), 2, '0')) AS month,
    sum(amount_sum) AS revenue
FROM olap.sales_by_store_month FINAL
GROUP BY year, month_num
ORDER BY year, month_num
