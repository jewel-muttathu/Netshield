from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # =========================
    # Application
    # =========================
    APP_NAME: str = "NetShield API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # =========================
    # Database
    # =========================
    DATABASE_URL: str = "sqlite:///./netshield.db"

    # =========================
    # Frontend / CORS
    # =========================
    FRONTEND_URL: str = "http://localhost:5173"

    # =========================
    # File Storage
    # =========================
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"

    # =========================
    # LUCID / ML Model
    # =========================
    MODEL_DIR: Path = BASE_DIR / "models"

    MODEL_PATH: Path = MODEL_DIR / "lucid_cnn.h5"

    LUCID_SCRIPT: Path = MODEL_DIR / "lucid_cnn.py"

    LUCID_DATASET_PARSER: Path = (
        MODEL_DIR / "lucid_dataset_parser.py"
    )

    # =========================
    # Environment Configuration
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# Make sure upload directory exists
settings.UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)