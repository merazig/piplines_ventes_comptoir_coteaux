"""Execute the SQL pipeline."""

from pathlib import Path

import duckdb


SQL_DIR = Path("sql")


def execute_sql(filename: str) -> None:
    """Execute a SQL file with DuckDB."""
    sql_path = SQL_DIR / filename
    sql = sql_path.read_text(encoding="utf-8")
    duckdb.sql(sql)
    print(f"Script SQL exécuté : {sql_path}")


def main() -> None:
    """Execute SQL scripts in pipeline order."""
    execute_sql("clean.sql")
    execute_sql("deduplicate.sql")
    execute_sql("merge.sql")
    execute_sql("sales.sql")


if __name__ == "__main__":
    main()
