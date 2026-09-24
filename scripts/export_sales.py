"""Chiffre d'affaires."""

from pathlib import Path

import pandas as pd

from scripts.minio_client import read_object, upload_file


def export_sales() -> None:
    """Generate the sales report in Excel format and upload it to MinIO."""
    period = pd.Timestamp.today().strftime("%Y-%m")

    input_path = Path(f"parquet/{period}/gold/sales.parquet")
    output_path = Path("outputs/rapport_ca.xlsx")

    df = pd.read_parquet(read_object(str(input_path)))

    total_revenue = df["revenue"].sum()

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="CA par produit", index=False)

        pd.DataFrame({"CA total": [total_revenue]}).to_excel(
            writer,
            sheet_name="CA total",
            index=False,
        )

    upload_file(
        str(output_path),
        f"output/{period}/rapport_ca.xlsx",
    )

    print(f"Rapport CA généré : output/{period}/rapport_ca.xlsx")
