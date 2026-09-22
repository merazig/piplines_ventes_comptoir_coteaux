-- Suprimer les doublons

COPY (
    SELECT *
    FROM read_parquet('work/parquet/web_clean.parquet')
    WHERE post_type = 'product'
)
TO 'work/parquet/web_deduplicated.parquet'
(FORMAT PARQUET);
