-- clean web
COPY (
    SELECT *
    FROM read_parquet('work/parquet/web.parquet')
    WHERE sku IS NOT NULL
)
TO 'work/parquet/web_clean.parquet'
(FORMAT PARQUET);

