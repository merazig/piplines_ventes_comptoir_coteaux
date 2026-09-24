-- Chiffre d'affaire

COPY (
    SELECT
        product_id,
        sku,
        price,
        total_sales,
        price * total_sales AS revenue
    FROM read_parquet(
        's3://comptoir-coteaux/parquet/{{PERIOD}}/silver/merged.parquet'
    )
)
TO 's3://comptoir-coteaux/parquet/{{PERIOD}}/gold/sales.parquet'
(FORMAT PARQUET);
