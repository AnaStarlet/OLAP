-- P09. Summary table for chart: revenue by store by month.
-- One row = one month + one store.
-- Same metric as canonical_metric.sql: SUM(total_amount).

CREATE TABLE IF NOT EXISTS olap.sales_by_store_month (
    year       Int32,
    month_num  Int32,
    store_id   Int32,
    store_name String,
    amount_sum Decimal(18,2)
) ENGINE = ReplacingMergeTree
ORDER BY (year, month_num, store_id);