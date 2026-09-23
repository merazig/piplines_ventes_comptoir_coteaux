"""Calculate wine price z-scores and generate reports."""

from pathlib import Path

import pandas as pd


INPUT = Path("work/parquet/sales.parquet")
OUTPUT_DIR = Path("outputs")


def main() -> None:
    """Calculate z-scores and generate output files."""
    df = pd.read_parquet(INPUT)

    mean_price = df["price"].mean()
    std_price = df["price"].std()

    df["z_score"] = round((df["price"] - mean_price) / std_price, 3)

    premium = df[df["z_score"] > 2]
    non_premium = df[df["z_score"] <= 2]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    premium.to_csv(OUTPUT_DIR / "vins_premium.csv", index=False)
    non_premium.to_csv(OUTPUT_DIR / "vins_non_premium.csv", index=False)

    print(f"Vins premium détectés : {len(premium)}")


if __name__ == "__main__":
    main()
