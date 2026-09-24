"""Execute the SQL pipeline."""

from datetime import date
from pathlib import Path
import os

import duckdb
from dotenv import load_dotenv

from scripts.export_sales import export_sales


load_dotenv()

SQL_DIR = Path("sql")

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
S3_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
S3_BUCKET = os.getenv("MINIO_BUCKET", "comptoir-coteaux")


def execute_sql(filename: str) -> None:
    """Execute a SQL file with DuckDB."""
    sql_path = SQL_DIR / filename
    sql = sql_path.read_text(encoding="utf-8")

    period = date.today().strftime("%Y-%m")
    sql = sql.replace("{{PERIOD}}", period)

    duckdb.sql("INSTALL httpfs;")
    duckdb.sql("LOAD httpfs;")

    duckdb.sql(
        f"""
        CREATE OR REPLACE SECRET minio_secret (
            TYPE S3,
            KEY_ID '{S3_ACCESS_KEY}',
            SECRET '{S3_SECRET_KEY}',
            ENDPOINT '{S3_ENDPOINT.removeprefix("http://").removeprefix("https://")}',
            URL_STYLE 'path',
            USE_SSL false
        );
        """
    )

    duckdb.sql(sql)

    print(f"Script SQL exécuté : {sql_path}")


def main() -> None:
    """Execute SQL scripts in pipeline order."""
    execute_sql("clean.sql")
    execute_sql("deduplicate.sql")
    execute_sql("merge.sql")
    execute_sql("sales.sql")

    export_sales()


if __name__ == "__main__":
    main()
