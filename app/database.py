import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _resolve_sqlite_url(url: str) -> str:
    """For SQLite absolute paths, ensure the parent dir exists.
    Falls back to a local relative path if the directory cannot be created
    (e.g. Render free plan without a persistent disk attached)."""
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url
    raw = url[len(prefix):]
    if not raw.startswith("/"):
        return url  # relative path — SQLite creates the file automatically
    db_path = Path(raw)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        fallback = "sqlite:///./quote_generator.db"
        print(
            f"WARNING: Cannot create SQLite dir {db_path.parent}, "
            f"falling back to {fallback}",
            flush=True,
        )
        return fallback
    return url


DATABASE_URL = _resolve_sqlite_url(
    normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///./quote_generator.db")
    )
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
