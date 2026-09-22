"""Convert to parquet."""

from pathlib import Path
import pandas as pd


DATA_DIR = Path("data")
OUTPUT_DIR = Path("work/parquet")


def convert_excel_to_parquet(filename: str, output_name: str) -> None:
    """Excel to parquet."""
    input_path = DATA_DIR / filename
    output_path = OUTPUT_DIR / output_name

    df = pd.read_excel(input_path)

    if filename == "fichier_liaison.xlsx":
        df["id_web"] = df["id_web"].astype("string")

    if filename == "Fichier_web.xlsx":
        df["sku"] = df["sku"].astype("string")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    print(f"{filename} : {len(df)} lignes -> {output_path}")


def main() -> None:
    """Main."""
    convert_excel_to_parquet("Fichier_erp.xlsx", "erp.parquet")

    convert_excel_to_parquet("fichier_liaison.xlsx", "liaison.parquet")

    convert_excel_to_parquet("Fichier_web.xlsx", "web.parquet")


if __name__ == "__main__":
    main()
