import os
import sqlite3
from pathlib import Path
from typing import Optional

LEGACY_STATUS_MAP = {
    "utkast": "draft",
    "skickad": "sent",
    "accepterad": "accepted",
    "avvisad": "rejected",
}


def resolve_sqlite_path(database_url: str) -> Optional[Path]:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return None

    raw_path = database_url[len(prefix):]
    if raw_path.startswith("/"):
        db_path = Path(raw_path)
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Can't create the directory (e.g. no disk on Render free plan);
            # fall back to a local relative path so the app can still start.
            return Path.cwd() / "quote_generator.db"
        return db_path
    return Path.cwd() / raw_path


def migrate_statuses(database_path: Path) -> int:
    if not database_path.exists():
        return 0

    connection = sqlite3.connect(database_path)
    try:
        try:
            connection.execute("SELECT 1 FROM quotes LIMIT 1")
        except sqlite3.OperationalError:
            return 0

        updated_rows = 0
        for old_status, new_status in LEGACY_STATUS_MAP.items():
            cursor = connection.execute(
                "UPDATE quotes SET status = ? WHERE status = ?",
                (new_status, old_status),
            )
            updated_rows += cursor.rowcount
        connection.commit()
        return updated_rows
    finally:
        connection.close()


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./quote_generator.db")
    database_path = resolve_sqlite_path(database_url)
    if database_path is None:
        print("Skipping migration: non-SQLite DATABASE_URL detected")
        return
    updated_rows = migrate_statuses(database_path)
    print(f"Migrated {updated_rows} legacy quote status rows in {database_path}")


if __name__ == "__main__":
    main()
