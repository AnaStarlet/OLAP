-- sql/canonical_metric.sql
-- Главная метрика: оборот без возвратов
-- Возвратов в сырье нет, поэтому "оборот без возвратов" = обычный оборот
SELECT SUM(total_amount) AS revenue_byn
FROM fact_sales;
