from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, Protocol

logger = logging.getLogger(__name__)


class ObjectStorage(Protocol):
    def put_bytes(self, key: str, data: bytes, content_type: str) -> str: ...
    def delete(self, key: str) -> None: ...
    def public_url(self, key: str) -> str: ...


class LocalStorage:
    def __init__(self, base_dir: str, public_prefix: str = "/uploads") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.public_prefix = public_prefix.rstrip("/")

    def put_bytes(self, key: str, data: bytes, content_type: str) -> str:
        path = self.base_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        return self.public_url(key)

    def delete(self, key: str) -> None:
        path = self.base_dir / key
        if path.exists():
            path.unlink()

    def public_url(self, key: str) -> str:
        return f"{self.public_prefix}/{key.lstrip('/')}"


class S3Storage:
    def __init__(
        self,
        bucket: str,
        region: str,
        public_base_url: Optional[str] = None,
        kms_key_id: Optional[str] = None,
    ) -> None:
        import boto3

        self.bucket = bucket
        self.region = region
        self.public_base_url = (public_base_url or "").rstrip("/")
        self.kms_key_id = kms_key_id
        self.client = boto3.client("s3", region_name=region)

    def put_bytes(self, key: str, data: bytes, content_type: str) -> str:
        extra = {
            "ContentType": content_type,
            "CacheControl": "public, max-age=31536000, immutable",
        }
        if self.kms_key_id:
            extra["ServerSideEncryption"] = "aws:kms"
            extra["SSEKMSKeyId"] = self.kms_key_id
        else:
            extra["ServerSideEncryption"] = "AES256"

        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
        return self.public_url(key)

    def delete(self, key: str) -> None:
        # Con versionado habilitado genera un delete-marker (soft-delete).
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def public_url(self, key: str) -> str:
        key = key.lstrip("/")
        if self.public_base_url:
            return f"{self.public_base_url}/{key}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"


def build_storage_from_env() -> ObjectStorage:
    if os.getenv("STORAGE_BACKEND", "local").lower() == "s3":
        return S3Storage(
            bucket=os.environ["S3_BUCKET"],
            region=os.getenv("AWS_REGION", "us-east-1"),
            public_base_url=os.getenv("CDN_BASE_URL"),
            kms_key_id=os.getenv("S3_KMS_KEY_ID"),
        )
    from app.core.config import settings
    return LocalStorage(base_dir=settings.UPLOAD_DIR)


_storage: Optional[ObjectStorage] = None


def get_storage() -> ObjectStorage:
    global _storage
    if _storage is None:
        _storage = build_storage_from_env()
    return _storage
