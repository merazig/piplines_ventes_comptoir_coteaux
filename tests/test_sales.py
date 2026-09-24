"""Display sales pipeline control values."""

from datetime import datetime

import pandas as pd

from scripts.minio_client import read_object


def read_parquet(period: str, layer: str, name: str) -> pd.DataFrame:
    """Read a Parquet file from MinIO."""
    path = f"parquet/{period}/{layer}/{name}.parquet"
    return pd.read_parquet(read_object(path))


def main() -> None:
    """Display sales pipeline control values."""
    period = datetime.now().strftime("%Y-%m")

    erp = read_parquet(period, "bronze", "erp")
    liaison = read_parquet(period, "bronze", "liaison")
    web_clean = read_parquet(period, "silver", "web_clean")
    web_deduplicated = read_parquet(period, "silver", "web_deduplicated")
    merged = read_parquet(period, "silver", "merged")
    sales = read_parquet(period, "gold", "sales")

    premium = pd.read_csv(read_object(f"output/{period}/vins_premium.csv"))

    print(f"ERP après dédoublonnage : {len(erp)} lignes")
    print(f"Liaison après dédoublonnage : {len(liaison)} lignes")
    print(f"Web après nettoyage : {len(web_clean)} lignes")
    print(f"Web après dédoublonnage : {len(web_deduplicated)} lignes")
    print(f"Fichier fusionné : {len(merged)} lignes")
    print(
        f"Chiffre d'affaires total : {sales['revenue'].sum():,.2f} €".replace(",", " ").replace(
            ".", ","
        )
    )
    print(f"Vins premium détectés (z > 2) : {len(premium)}")


if __name__ == "__main__":
    main()
