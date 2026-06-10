from contextlib import contextmanager

from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def ensure_database_schema() -> None:
    """Small SQLite compatibility migration for older local installs."""
    if not settings.database_url.startswith("sqlite"):
        return
    with engine.begin() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).scalars().all()
        if "tasks" in tables:
            columns = {row[1] for row in conn.execute(text("PRAGMA table_info(tasks)")).fetchall()}
            additions = {
                "request_id": "ALTER TABLE tasks ADD COLUMN request_id VARCHAR(120)",
                "retry_count": "ALTER TABLE tasks ADD COLUMN retry_count INTEGER DEFAULT 0",
                "timeout_seconds": "ALTER TABLE tasks ADD COLUMN timeout_seconds INTEGER DEFAULT 300",
                "requires_confirmation": "ALTER TABLE tasks ADD COLUMN requires_confirmation BOOLEAN DEFAULT 0",
                "confirmed": "ALTER TABLE tasks ADD COLUMN confirmed BOOLEAN DEFAULT 0",
                "safe_to_retry": "ALTER TABLE tasks ADD COLUMN safe_to_retry BOOLEAN DEFAULT 1",
                "user_id": "ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id)",
            }
            for column, statement in additions.items():
                if column not in columns:
                    conn.execute(text(statement))
        if "agents" in tables:
            columns = {row[1] for row in conn.execute(text("PRAGMA table_info(agents)")).fetchall()}
            additions = {
                "hostname": "ALTER TABLE agents ADD COLUMN hostname VARCHAR(160) DEFAULT ''",
                "username": "ALTER TABLE agents ADD COLUMN username VARCHAR(160) DEFAULT ''",
                "os_name": "ALTER TABLE agents ADD COLUMN os_name VARCHAR(160) DEFAULT ''",
                "public_ip": "ALTER TABLE agents ADD COLUMN public_ip VARCHAR(120) DEFAULT ''",
                "connection_ip": "ALTER TABLE agents ADD COLUMN connection_ip VARCHAR(120) DEFAULT ''",
                "camera_enabled": "ALTER TABLE agents ADD COLUMN camera_enabled BOOLEAN DEFAULT 0",
                "video_enabled": "ALTER TABLE agents ADD COLUMN video_enabled BOOLEAN DEFAULT 0",
                "user_id": "ALTER TABLE agents ADD COLUMN user_id INTEGER REFERENCES users(id)",
            }
            for column, statement in additions.items():
                if column not in columns:
                    conn.execute(text(statement))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
