"""Pandas fallback for the sales pipeline."""

from datetime import datetime

import pandas as pd

from scripts.minio_client import read_object, upload_file
from scripts.export_sales import export_sales

from pathlib import Path
import tempfile


def read_parquet(period: str, layer: str, name: str) -> pd.DataFrame:
    """Read a Parquet file from MinIO."""
    path = f"parquet/{period}/{layer}/{name}.parquet"
    return pd.read_parquet(read_object(path))


def write_parquet(df: pd.DataFrame, object_name: str) -> None:
    """Write Parquet."""
    with tempfile.TemporaryDirectory() as tmp:
        file_path = Path(tmp) / "output.parquet"
        df.to_parquet(file_path, index=False)
        upload_file(str(file_path), object_name)


def clean_web(period: str) -> None:
    """Remove web records with a missing SKU."""
    df = read_parquet(period, "bronze", "web")
    df = df[df["sku"].notna()].copy()

    write_parquet(
        df,
        f"parquet/{period}/silver/web_clean.parquet",
    )


def deduplicate_web(period: str) -> None:
    """Keep only product records from the cleaned web data."""
    df = read_parquet(period, "silver", "web_clean")
    df = df[df["post_type"] == "product"].copy()

    write_parquet(
        df,
        f"parquet/{period}/silver/web_deduplicated.parquet",
    )


def merge_data(period: str) -> None:
    """Merge ERP, liaison, and web data."""
    erp = read_parquet(period, "bronze", "erp")
    liaison = read_parquet(period, "bronze", "liaison")
    web = read_parquet(period, "silver", "web_deduplicated")

    merged = erp.merge(
        liaison,
        on="product_id",
        how="inner",
    )

    merged["id_web"] = merged["id_web"].astype("string")
    web["sku"] = web["sku"].astype("string")

    merged = merged.merge(
        web,
        left_on="id_web",
        right_on="sku",
        how="inner",
    )

    merged = merged[
        [
            "product_id",
            "onsale_web",
            "price",
            "stock_quantity",
            "stock_status",
            "id_web",
            "sku",
            "total_sales",
            "post_title",
            "post_status",
        ]
    ]

    write_parquet(
        merged,
        f"parquet/{period}/silver/merged.parquet",
    )


def calculate_sales(period: str) -> None:
    """Calculate revenue for each product."""
    df = read_parquet(period, "silver", "merged")

    df["revenue"] = df["price"] * df["total_sales"]

    df = df[
        [
            "product_id",
            "sku",
            "price",
            "total_sales",
            "revenue",
        ]
    ]

    write_parquet(
        df,
        f"parquet/{period}/gold/sales.parquet",
    )


def main() -> None:
    """Execute the complete Pandas fallback pipeline."""
    period = datetime.now().strftime("%Y-%m")

    clean_web(period)
    deduplicate_web(period)
    merge_data(period)
    calculate_sales(period)

    export_sales()


if __name__ == "__main__":
    main()
