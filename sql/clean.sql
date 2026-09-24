-- clean web

COPY (
    SELECT *
    FROM read_parquet(
        's3://comptoir-coteaux/parquet/{{PERIOD}}/bronze/web.parquet'
    )
    WHERE sku IS NOT NULL
)
TO 's3://comptoir-coteaux/parquet/{{PERIOD}}/silver/web_clean.parquet'
(FORMAT PARQUET);
