"""Tests for the sales pipeline."""

from io import BytesIO
import pandas as pd

from scripts.minio_client import S3_BUCKET, get_s3_client

from datetime import date


def read_parquet(object_name: str) -> pd.DataFrame:
    """Read a Parquet file from MinIO."""
    client = get_s3_client()
    response = client.get_object(
        Bucket=S3_BUCKET,
        Key=object_name,
    )
    return pd.read_parquet(BytesIO(response["Body"].read()))


def read_csv(object_name: str) -> pd.DataFrame:
    """Read a CSV file from MinIO."""
    client = get_s3_client()
    response = client.get_object(
        Bucket=S3_BUCKET,
        Key=object_name,
    )
    return pd.read_csv(BytesIO(response["Body"].read()))


def test_missing_values(period: str) -> None:
    """Check that the cleaned Web dataset contains no missing values."""
    path = f"parquet/{period}/silver/web_clean.parquet"

    df = read_parquet(path)

    assert df["sku"].notna().all(), "Valeurs manquantes détectées dans la clé sku de web_clean"


def test_duplicates(period: str) -> None:
    """Check that primary keys are unique after deduplication."""
    path = f"parquet/{period}/silver/web_deduplicated.parquet"
    key = "sku"

    df = read_parquet(path)

    assert df[key].is_unique, f"Doublons détectés dans la clé {key} de web"


def test_join_consistency(period: str) -> None:
    """Check that the merged dataset contains consistent identifiers."""
    df = read_parquet(f"parquet/{period}/silver/merged.parquet")

    assert not df.empty, "Le fichier fusionné est vide"
    assert df["product_id"].notna().all(), "product_id contient des valeurs manquantes"
    assert df["id_web"].notna().all(), "id_web contient des valeurs manquantes"
    assert df["sku"].notna().all(), "sku contient des valeurs manquantes"

    assert df["id_web"].astype("string").equals(df["sku"].astype("string")), (
        "id_web et sku ne correspondent pas"
    )


def test_revenue_consistency(period: str) -> None:
    """Check that revenue is correctly calculated."""
    df = read_parquet(f"parquet/{period}/gold/sales.parquet")
    expected_revenue = df["price"] * df["total_sales"]

    assert df["revenue"].notna().all(), "Le chiffre d'affaires contient des valeurs manquantes"

    assert (df["revenue"].round(2) == expected_revenue.round(2)).all(), (
        "Le chiffre d'affaires par produit est incorrect"
    )


def test_z_score(period: str) -> None:
    """Check the z-score calculation and premium classification."""
    df = read_parquet(f"parquet/{period}/gold/sales.parquet")
    premium = read_csv(f"output/{period}/vins_premium.csv")
    ordinary = read_csv(f"output/{period}/vins_ordinaires.csv")

    mean_price = df["price"].mean()
    std_price = df["price"].std()

    expected_z_score = ((df["price"] - mean_price) / std_price).round(3)

    premium_ids = set(df.loc[expected_z_score > 2, "product_id"])
    ordinary_ids = set(df.loc[expected_z_score <= 2, "product_id"])

    assert set(premium["product_id"]) == premium_ids, "La liste des vins premium est incorrecte"

    assert set(ordinary["product_id"]) == ordinary_ids, (
        "La liste des vins ordinaires est incorrecte"
    )

    assert premium_ids.isdisjoint(ordinary_ids), "Un produit apparaît dans les deux catégories"

    assert len(premium_ids | ordinary_ids) == len(df), (
        "Les catégories premium et ordinaires ne couvrent pas tous les produits"
    )


def main() -> None:
    """Run the five pipeline tests."""
    period = date.today().strftime("%Y-%m")

    test_missing_values(period)
    print("✓ Test valeurs manquantes")

    test_duplicates(period)
    print("✓ Test doublons")

    test_join_consistency(period)
    print("✓ Test cohérence des jointures")

    test_revenue_consistency(period)
    print("✓ Test cohérence du chiffre d'affaires")

    test_z_score(period)
    print("✓ Test z-score")

    print("\nTous les tests sont passés avec succès !")


if __name__ == "__main__":
    main()
