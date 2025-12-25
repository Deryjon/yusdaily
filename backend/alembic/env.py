from logging.config import fileConfig
import os

from sqlalchemy import create_engine, pool
from alembic import context

from backend.app.db.base import Base


db_url = os.getenv("DATABASE_URL_SYNC") or os.getenv("DATABASE_URL")

# если вдруг в DATABASE_URL остался asyncpg, принудительно заменим
db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

connectable = create_engine(db_url, pool_pre_ping=True)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL is required for migrations")
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _get_sync_url() -> str:
    db_url = os.getenv("DATABASE_URL_SYNC") or os.getenv("DATABASE_URL") or ""
    if not db_url:
        raise RuntimeError("DATABASE_URL or DATABASE_URL_SYNC is required for migrations")
    return db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

def run_migrations_online() -> None:
    connectable = create_engine(_get_sync_url(), poolclass=pool.NullPool, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
