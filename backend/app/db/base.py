"""
SQLAlchemy declarative base and shared mixins.

Using DeclarativeBase (SQLAlchemy 2.0 style) instead of the legacy
declarative_base() function for better type safety and mypy support.
"""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at to any model.

    server_default=func.now() ensures the DB clock sets the timestamp —
    avoids timezone drift between the application server and the DB.
    onupdate=func.now() on updated_at works alongside the DB trigger for
    double-safety (DB trigger is authoritative).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
