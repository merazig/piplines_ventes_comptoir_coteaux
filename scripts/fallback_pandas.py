"""Solution qui remplace duckdb."""

from pathlib import Path

import pandas as pd


PARQUET_DIR = Path("work/parquet")


def clean_web() -> None:
    """Remove web records with a missing SKU."""
    input_path = PARQUET_DIR / "web.parquet"
    output_path = PARQUET_DIR / "web_clean.parquet"

    df = pd.read_parquet(input_path)
    df = df[df["sku"].notna()].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Nettoyage Web terminé : {output_path}")


def deduplicate_web() -> None:
    """Keep only product records from the cleaned web data."""
    input_path = PARQUET_DIR / "web_clean.parquet"
    output_path = PARQUET_DIR / "web_deduplicated.parquet"

    df = pd.read_parquet(input_path)
    df = df[df["post_type"] == "product"].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Dédoublonnage Web terminé : {output_path}")


def merge_data() -> None:
    """Merge ERP, liaison, and web data using product identifiers."""
    erp_path = PARQUET_DIR / "erp.parquet"
    liaison_path = PARQUET_DIR / "liaison.parquet"
    web_path = PARQUET_DIR / "web_deduplicated.parquet"
    output_path = PARQUET_DIR / "merged.parquet"

    erp = pd.read_parquet(erp_path)
    liaison = pd.read_parquet(liaison_path)
    web = pd.read_parquet(web_path)

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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(output_path, index=False)

    print(f"Fusion terminée : {output_path}")


def calculate_sales() -> None:
    """Calculate revenue for each product."""
    input_path = PARQUET_DIR / "merged.parquet"
    output_path = PARQUET_DIR / "sales.parquet"

    df = pd.read_parquet(input_path)

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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"Calcul du chiffre d'affaires terminé : {output_path}")


def main() -> None:
    """Execute the complete pandas fallback pipeline."""
    clean_web()
    deduplicate_web()
    merge_data()
    calculate_sales()


if __name__ == "__main__":
    main()
