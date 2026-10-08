-- P06. SCD2 demo: change category for one product.

-- Step 1: initial versions of 5 products.
INSERT INTO dim_product_scd2
SELECT
    product_id,
    product_name,
    category,
    subcategory,
    material,
    retail_price,
    supplier_id,
    DATE '2020-01-01' AS valid_from,
    DATE '9999-12-31' AS valid_to,
    TRUE              AS is_current
FROM dim_product
LIMIT 5;

-- Step 2: change category for product_id = 1.
-- 2a. Close old version.
UPDATE dim_product_scd2
SET valid_to   = DATE '2024-02-01',
    is_current = FALSE
WHERE product_id = 1
  AND is_current = TRUE;

-- 2b. Insert new version.
INSERT INTO dim_product_scd2
SELECT
    product_id,
    product_name,
    'NEW_CATEGORY' AS category,
    subcategory,
    material,
    retail_price,
    supplier_id,
    DATE '2024-02-01' AS valid_from,
    DATE '9999-12-31' AS valid_to,
    TRUE              AS is_current
FROM dim_product
WHERE product_id = 1;

-- Step 3: show TWO versions of product_id = 1.
SELECT
    product_id,
    category,
    valid_from,
    valid_to,
    is_current
FROM dim_product_scd2
WHERE product_id = 1
ORDER BY valid_from;
