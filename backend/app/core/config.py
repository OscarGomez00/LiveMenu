from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from app.core import secrets


class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "LiveMenu"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "dev"

    # Database
    POSTGRES_USER: str = "livemenu"
    POSTGRES_PASSWORD: str = "livemenu123"
    POSTGRES_DB: str = "livemenu_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DB_SSL_MODE: str = "prefer"
    DB_SSL_ROOT_CERT: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        c = secrets.get_db_credentials()
        return f"postgresql+asyncpg://{c['username']}:{c['password']}@{c['host']}:{c['port']}/{c['dbname']}"

    @property
    def DATABASE_CONNECT_ARGS(self) -> dict:
        if self.APP_ENV.lower() in {"prod", "production", "staging"}:
            if self.DB_SSL_ROOT_CERT:
                import ssl
                return {"ssl": ssl.create_default_context(cafile=self.DB_SSL_ROOT_CERT)}
            return {"ssl": True}
        return {}

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def refresh_jwt(self) -> None:
        jwt_conf = secrets.get_jwt_secret()
        if jwt_conf.get("SECRET_KEY"):
            self.SECRET_KEY = jwt_conf["SECRET_KEY"]
        self.ALGORITHM = jwt_conf.get("ALGORITHM", self.ALGORITHM)

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Storage & Images
    STORAGE_BACKEND: str = "local"
    S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    CDN_BASE_URL: Optional[str] = None
    S3_KMS_KEY_ID: Optional[str] = None

    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]
    IMAGE_QUALITY: int = 80
    IMAGE_SIZES: dict = {
        "thumbnail": (150, 150),
        "medium": (400, 400),
        "large": (800, 800),
    }

    IMAGE_WORKERS: int = 2
    IMAGE_QUEUE_SIZE: int = 20

    FORCE_HTTPS: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

try:
    settings.refresh_jwt()
except Exception:
    pass
