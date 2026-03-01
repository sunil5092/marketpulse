"""
database.py — SQLAlchemy setup: engine, session factory, and declarative base.

Usage:
    from app.database import get_db, Base, engine

    # In FastAPI route:
    def my_route(db: Session = Depends(get_db)):
        ...
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# ── Engine ─────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # test connections before using them
    pool_size=5,
    max_overflow=10,
    echo=False,              # set True to log all SQL queries (debug)
)

# ── Session factory ────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── Base class for all ORM models ──────────────────────────────
Base = declarative_base()


# ── Dependency for FastAPI routes ──────────────────────────────
def get_db():
    """Yields a database session and ensures it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in ORM models. Called at app startup."""
    Base.metadata.create_all(bind=engine)
