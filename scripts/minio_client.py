"""S3-compatible storage utilities."""

import os
from io import BytesIO

import boto3

from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
S3_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
S3_BUCKET = os.getenv("MINIO_BUCKET", "comptoir-coteaux")


def get_s3_client():
    """Create an S3 client connected to MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
    )


def read_object(object_name: str) -> BytesIO:
    """Read an object from S3-compatible storage."""
    client = get_s3_client()

    response = client.get_object(
        Bucket=S3_BUCKET,
        Key=object_name,
    )

    return BytesIO(response["Body"].read())


def upload_file(file_path: str, object_name: str) -> None:
    """Upload a local file to S3-compatible storage."""
    client = get_s3_client()

    client.upload_file(
        file_path,
        S3_BUCKET,
        object_name,
    )
