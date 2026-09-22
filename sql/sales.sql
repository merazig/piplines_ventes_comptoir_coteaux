-- Chiffre d'affaire

COPY (
    SELECT
        product_id,
        sku,
        price,
        total_sales,
        price * total_sales AS revenue
    FROM read_parquet('work/parquet/merged.parquet')
)
TO 'work/parquet/sales.parquet'
(FORMAT PARQUET);
