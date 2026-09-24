"""Calcule z-scores des vins et genere CSV."""

from io import BytesIO

from pathlib import Path

import pandas as pd


from scripts.minio_client import read_object, get_s3_client, S3_BUCKET

PARQUET_DIR = Path("parquet")
OUTPUT_DIR = Path("output")


def main() -> None:
    """Calcule z-scores and genere output CSV."""
    period = pd.Timestamp.today().strftime("%Y-%m")
    
    input_path = f"{PARQUET_DIR}/{period}/gold/sales.parquet"
    premium_path = f"{OUTPUT_DIR}/{period}/vins_premium.csv"
    ordinary_path = f"{OUTPUT_DIR}/{period}/vins_ordinaires.csv"
    
    df = pd.read_parquet(read_object(input_path))

    mean_price = df["price"].mean()
    std_price = df["price"].std()

    df["z_score"] = round((df["price"] - mean_price) / std_price, 3)

    premium = df[df["z_score"] > 2]
    ordinary = df[df["z_score"] <= 2]

    client = get_s3_client()
    
    premium_buffer = BytesIO()
    premium.to_csv(premium_buffer, index=False)
    premium_buffer.seek(0)

    client.upload_fileobj(
        premium_buffer,
        S3_BUCKET,
        premium_path,
    )

    ordinary_buffer = BytesIO()
    ordinary.to_csv(ordinary_buffer, index=False)
    ordinary_buffer.seek(0)

    client.upload_fileobj(
        ordinary_buffer,
        S3_BUCKET,
        ordinary_path,
    )

    print(f"Vins premium détectés : {len(premium)}")


if __name__ == "__main__":
    main()
