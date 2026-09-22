-- clean liason
COPY (
    SELECT *
    FROM read_parquet('work/parquet/liaison.parquet')
    WHERE id_web IS NOT NULL
)
TO 'work/parquet/liaison_clean.parquet'
(FORMAT PARQUET);

-- clean web
COPY (
    SELECT *
    FROM read_parquet('work/parquet/web.parquet')
    WHERE sku IS NOT NULL
        AND post_type = 'product'
)
TO 'work/parquet/web_clean.parquet'
(FORMAT PARQUET);

