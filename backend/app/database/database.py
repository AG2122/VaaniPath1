"""VaniPath Backend - Database Configuration

Supports:
- SQLite (local development / offline fallback)
- PostgreSQL via Supabase shared session pooler (production)

Automatically detects the engine from DATABASE_URL.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
import os

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

from app.config import settings

# --- Engine Selection --------------------------------------------------------
connect_args = {}

if settings.is_postgresql:
    # PostgreSQL: no check_same_thread; use SSL if Supabase
    connect_args = {}
    ssl_mode = os.getenv("PGSSLMODE", "require")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
else:
    # SQLite fallback
    connect_args["check_same_thread"] = False
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (testing only)."""
    Base.metadata.drop_all(bind=engine)


def reset_tables():
    """Drop and recreate all tables (testing only)."""
    drop_tables()
    create_tables()
