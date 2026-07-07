from sqlalchemy import text

from app.core.config import settings
from app.core.db import engine
from app.models.db_models import Base


async def _sqlite_migrations(conn) -> None:
    result = await conn.execute(text("PRAGMA table_info(videos)"))
    columns = {row[1] for row in result.fetchall()}
    if "source_url" not in columns:
        await conn.execute(text("ALTER TABLE videos ADD COLUMN source_url VARCHAR"))
    if "language" not in columns:
        await conn.execute(text("ALTER TABLE videos ADD COLUMN language VARCHAR DEFAULT 'en'"))


async def init_db() -> None:
    async with engine.begin() as conn:
        if not settings.is_sqlite:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        if settings.is_sqlite:
            await _sqlite_migrations(conn)
