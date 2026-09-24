-- Supprimer les doublons

COPY (
    SELECT *
    FROM read_parquet(
        's3://comptoir-coteaux/parquet/{{PERIOD}}/silver/web_clean.parquet'
    )
    WHERE post_type = 'product'
)
TO 's3://comptoir-coteaux/parquet/{{PERIOD}}/silver/web_deduplicated.parquet'
(FORMAT PARQUET);

