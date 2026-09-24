"""Convert Excel files to Parquet."""

import os
from pathlib import Path

import pandas as pd

from scripts.minio_client import read_object, upload_file

from datetime import date

period = date.today().strftime("%Y-%m")

DATA_DIR = Path(os.getenv("DATA_DIR", "input/"))
OUTPUT_DIR = Path(
    os.getenv("OUTPUT_DIR", f"parquet/bronze/{period}/")
)


def convert_excel_to_parquet(
    filename: str,
    output_name: str,
) -> None:
    """Read an Excel file from MinIO and save it as Parquet."""
    object_name = f"input/{filename}"

    df = pd.read_excel(
        read_object(object_name),
        engine="calamine",
    )

    output_path = OUTPUT_DIR / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if filename == "fichier_liaison.xlsx":
        df["id_web"] = df["id_web"].astype("string")

    if filename == "Fichier_web.xlsx":
        df["sku"] = df["sku"].astype("string")

    df.to_parquet(output_path, index=False)

    upload_file(
        str(output_path),
        f"parquet/bronze/{period}/{output_name}",
    )

    print(f"{filename} : {len(df)} lignes -> {output_path}")


def main() -> None:
    """Main."""
    convert_excel_to_parquet("Fichier_erp.xlsx", "erp.parquet")

    convert_excel_to_parquet("fichier_liaison.xlsx", "liaison.parquet")

    convert_excel_to_parquet("Fichier_web.xlsx", "web.parquet")


if __name__ == "__main__":
    main()
