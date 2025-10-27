import os
from typing import Optional

try:
    import boto3  # type: ignore
    from botocore.client import Config  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None
    Config = None  # type: ignore


class S3Storage:
    def __init__(self) -> None:
        self.bucket = os.getenv("S3_BUCKET")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not boto3:
                raise RuntimeError("boto3 is not installed")
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                config=Config(signature_version="s3v4") if Config else None,
            )
        return self._client

    def save_bytes(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        extra = {"ACL": "public-read"}
        if content_type:
            extra["ContentType"] = content_type
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
        return self.public_url(key)

    def public_url(self, key: str) -> str:
        # Assuming public bucket or public-read ACL
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

