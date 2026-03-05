"""
Alembic environment configuration for AgentCanvas.

Uses the async recipe with asyncpg so migrations run in the same async
context as the application.  DATABASE_URL is read from app.core.config.settings
— never hardcoded (Coding Standard 10).

Offline mode is provided for generating migration SQL without a live DB.
Online mode runs the migration against the real PostgreSQL instance.
"""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import settings before any model so the DB URL is available
from app.core.config import settings

# Import Base and all models so Alembic autogenerate can detect every table.
# The models __init__ does the per-model imports — one import here covers all.
from app.db.base import Base
import app.models  # noqa: F401  — registers all ORM metadata on Base

# Alembic Config object — gives access to .ini file values
config = context.config

# Override sqlalchemy.url with the value from pydantic-settings.
# This means the .ini file must NOT have a sqlalchemy.url line (or it is
# ignored).  No credentials ever appear in alembic.ini (Coding Standard 10).
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata object that Alembic autogenerate compares against the DB
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL to stdout without connecting to a database.
    Useful for review-before-apply workflows in CI/CD.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Apply pending migrations using an existing synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Compare server defaults so Alembic detects added/removed defaults
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Create an async engine and run migrations.

    NullPool is used here — migration runs are short-lived one-shot
    processes, so a pool would be wasteful.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online mode — wraps the async runner in asyncio.run."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
