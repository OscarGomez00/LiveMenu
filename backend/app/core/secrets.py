from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _in_aws() -> bool:
    return os.getenv("APP_ENV", "dev").lower() in {"prod", "production", "staging"}


@lru_cache(maxsize=16)
def _fetch_secret(secret_id: str) -> Dict[str, Any]:
    import boto3

    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
    raw = client.get_secret_value(SecretId=secret_id).get("SecretString") or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"value": raw}


def get_db_credentials() -> Dict[str, Any]:
    if _in_aws() and os.getenv("DB_SECRET_ARN"):
        secret = _fetch_secret(os.environ["DB_SECRET_ARN"])
        return {
            "username": secret.get("username") or secret.get("user"),
            "password": secret.get("password"),
            "host": secret.get("host") or os.getenv("POSTGRES_HOST"),
            "port": int(secret.get("port") or os.getenv("POSTGRES_PORT", 5432)),
            "dbname": secret.get("dbname") or secret.get("database") or os.getenv("POSTGRES_DB"),
        }

    return {
        "username": os.getenv("POSTGRES_USER", "livemenu"),
        "password": os.getenv("POSTGRES_PASSWORD", "livemenu123"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "dbname": os.getenv("POSTGRES_DB", "livemenu_db"),
    }


def get_jwt_secret() -> Dict[str, str]:
    if _in_aws() and os.getenv("JWT_SECRET_ARN"):
        secret = _fetch_secret(os.environ["JWT_SECRET_ARN"])
        return {
            "SECRET_KEY": secret.get("SECRET_KEY") or secret.get("value"),
            "ALGORITHM": secret.get("ALGORITHM", "HS256"),
        }

    return {
        "SECRET_KEY": os.getenv(
            "SECRET_KEY",
            "your-secret-key-change-this-in-production-min-32-chars",
        ),
        "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
    }


def invalidate_cache() -> None:
    _fetch_secret.cache_clear()
