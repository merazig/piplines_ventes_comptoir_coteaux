"""Exécute les traitements SQL avec DuckDB."""

from pathlib import Path

import duckdb


SQL_DIR = Path("sql")


def execute_sql(filename: str) -> None:
    """Exécute un fichier SQL avec DuckDB."""
    sql_path = SQL_DIR / filename
    sql = sql_path.read_text(encoding="utf-8")

    connection = duckdb.connect()

    connection.execute(sql)
    
    connection.close()

    print(f"Script SQL exécuté : {sql_path}")


if __name__ == "__main__":
    execute_sql("sales.sql")
    

