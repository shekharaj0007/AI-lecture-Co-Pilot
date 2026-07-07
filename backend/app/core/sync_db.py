from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

if settings.is_sqlite:
    sync_database_url = settings.database_url.replace("+aiosqlite", "")
else:
    sync_database_url = settings.database_url.replace("+asyncpg", "+psycopg2")

sync_engine = create_engine(sync_database_url, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
