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
    FROM read_parquet('work/parquet/erp.parquet') AS e
    INNER JOIN read_parquet('work/parquet/liaison_clean.parquet') AS l
        ON e.product_id = l.product_id
    INNER JOIN read_parquet('work/parquet/web_clean.parquet') AS w
        ON CAST(l.id_web AS VARCHAR) = w.sku
)
TO 'work/parquet/merged.parquet'
(FORMAT PARQUET);