"""Tests for the sales pipeline."""

import duckdb

import pandas as pd

def test_erp_count() -> None:
    """Check the number of ERP rows."""
    result = duckdb.sql("""
        SELECT COUNT(*)
        FROM read_parquet('work/parquet/erp.parquet')
    """).fetchone()

    assert result is not None
    assert result[0] == 825


def test_liaison_count() -> None:
    """Check the number of liaison rows."""
    result = duckdb.sql("""
        SELECT COUNT(*)
        FROM read_parquet('work/parquet/liaison.parquet')
    """).fetchone()

    assert result is not None
    assert result[0] == 825


def test_web_clean_count() -> None:
    """Check the number of rows after Web cleaning."""
    result = duckdb.sql("""
        SELECT COUNT(*)
        FROM read_parquet('work/parquet/web_clean.parquet')
    """).fetchone()

    assert result is not None
    assert result[0] == 1428


def test_web_deduplicated_count() -> None:
    """Check the number of Web products after deduplication."""
    result = duckdb.sql("""
        SELECT COUNT(*)
        FROM read_parquet('work/parquet/web_deduplicated.parquet')
    """).fetchone()

    assert result is not None
    assert result[0] == 714


def test_merged_count() -> None:
    """Check the number of rows in the merged dataset."""
    result = duckdb.sql("""
        SELECT COUNT(*)
        FROM read_parquet('work/parquet/merged.parquet')
    """).fetchone()

    assert result is not None
    assert result[0] == 714


def test_total_revenue() -> None:
    """Check the reference total revenue."""
    result = duckdb.sql("""
        SELECT SUM(revenue)
        FROM read_parquet('work/parquet/sales.parquet')
    """).fetchone()

    assert result is not None
    assert result[0] == 70568.6

def test_premium_wines() -> None:
    """Check the number of premium wines."""
    df = pd.read_csv("outputs/vins_premium.csv")

    assert len(df) == 30
