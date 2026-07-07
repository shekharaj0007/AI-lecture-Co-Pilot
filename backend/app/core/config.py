from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    groq_api_key: str = ""
    voyage_api_key: str = ""
    pipeline_mode: str = "local"  # local | docker | production

    storage_backend: str = "local"  # local | s3
    local_data_dir: str = str(DATA_DIR)

    database_url: str = f"sqlite+aiosqlite:///{(DATA_DIR / 'lecture_copilot.db').as_posix()}"
    redis_url: str = "redis://localhost:6379/0"
    celery_eager: bool = True

    s3_endpoint_url: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "lecture-videos"

    whisper_model: str = "base"
    scene_threshold: float = 0.75
    frame_sample_fps: float = 1.0

    auth_secret: str = "dev-secret"

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        extra="ignore",
    )

    @field_validator("local_data_dir", mode="before")
    @classmethod
    def resolve_data_dir(cls, value: str) -> str:
        path = Path(value)
        if not path.is_absolute():
            path = ROOT_DIR / path
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @field_validator("database_url", mode="before")
    @classmethod
    def resolve_database_url(cls, value: str) -> str:
        if value.startswith("sqlite") and ":///" in value:
            raw = value.split("///", 1)[1]
            db_path = Path(raw)
            if not db_path.is_absolute():
                db_path = ROOT_DIR / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path.as_posix()}"
        return value

    @property
    def uploads_dir(self) -> Path:
        path = Path(self.local_data_dir) / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def frames_dir(self) -> Path:
        path = Path(self.local_data_dir) / "frames"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


settings = Settings()
