"""
Synchronous database session for STPA-Sec routes
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings

# Create synchronous engine for STPA-Sec
DATABASE_URL = settings.database.postgres_url.replace('+asyncpg', '')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_sync_db():
    """Get synchronous database session for STPA-Sec routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()