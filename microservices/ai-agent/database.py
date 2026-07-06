from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import get_settings

Base = declarative_base()


def _make_engine():
    settings = get_settings()
    return create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,   # detecta conexiones muertas
        pool_size=5,
        max_overflow=10,
    )


# El engine se crea lazy — si DATABASE_URL no apunta a una BD accesible,
# el servidor arranca igual; el error solo ocurre en el primer query.
engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency que provee una sesión de BD por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
