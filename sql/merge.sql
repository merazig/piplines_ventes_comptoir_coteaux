-- Jointure des donnees ERP et Web

COPY (
    SELECT
        e.product_id,
        e.onsale_web,
        e.price,
        e.stock_quantity,
        e.stock_status,
        l.id_web,
        w.sku,
        w.total_sales,
        w.post_title,
        w.post_status
    FROM read_parquet(
        's3://comptoir-coteaux/parquet/{{PERIOD}}/bronze/erp.parquet'
    ) AS e
    INNER JOIN read_parquet(
        's3://comptoir-coteaux/parquet/{{PERIOD}}/bronze/liaison.parquet'
    ) AS l
        ON e.product_id = l.product_id
    INNER JOIN read_parquet(
        's3://comptoir-coteaux/parquet/{{PERIOD}}/silver/web_deduplicated.parquet'
    ) AS w
        ON CAST(l.id_web AS VARCHAR) = w.sku
)
TO 's3://comptoir-coteaux/parquet/{{PERIOD}}/silver/merged.parquet'
(FORMAT PARQUET);
