import os
from contextlib import contextmanager
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    # Lightweight SQLite migration: add viability columns if missing
    try:
        with engine.connect() as conn:
            res = conn.exec_driver_sql("PRAGMA table_info(project)")
            cols = {row[1] for row in res.fetchall()}  # type: ignore[index]
            alters = []
            if "mvp_viability" not in cols:
                alters.append("ALTER TABLE project ADD COLUMN mvp_viability TEXT")
            if "viability_score" not in cols:
                alters.append("ALTER TABLE project ADD COLUMN viability_score REAL")
            if "viability_reason" not in cols:
                alters.append("ALTER TABLE project ADD COLUMN viability_reason TEXT")
            for stmt in alters:
                conn.exec_driver_sql(stmt)
    except Exception:
        # Best-effort; ignore in environments that aren't SQLite
        pass


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
