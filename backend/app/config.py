from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://swinglens:swinglens@localhost:5432/swinglens"

    # Redis (Celery broker)
    redis_url: str = "redis://localhost:6379/0"

    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = "swinglens-media"
    aws_s3_region: str = "ap-south-1"

    # Claude API
    anthropic_api_key: str = ""

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_expiry_minutes: int = 1440

    # OTP
    otp_api_key: str = ""
    otp_template_id: str = ""

    # Firebase
    firebase_credentials_path: str = ""

    # App
    app_env: str = "development"
    api_base_url: str = "http://localhost:8000"


settings = Settings()
