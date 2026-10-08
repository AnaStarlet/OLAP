-- P06. SCD2 table for dim_product.
-- Adds three technical columns:
--   valid_from  - when this version starts
--   valid_to    - when it ends (9999-12-31 for current)
--   is_current  - TRUE for the actual version only

DROP TABLE IF EXISTS dim_product_scd2;

CREATE TABLE dim_product_scd2 (
    product_id    INTEGER,
    product_name  VARCHAR,
    category      VARCHAR,
    subcategory   VARCHAR,
    material      VARCHAR,
    retail_price  DECIMAL(14,2),
    supplier_id   INTEGER,
    valid_from    DATE,
    valid_to      DATE,
    is_current    BOOLEAN
);
