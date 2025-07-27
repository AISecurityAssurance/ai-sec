"""
Synchronous database session for STPA-Sec routes
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Deferred engine creation to avoid import-time database connection
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create the synchronous database engine"""
    global _engine, _SessionLocal
    if _engine is None:
        # Use environment variable if available
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://sa_user:sa_password@localhost:5432/security_analyst')
        # Convert async URL to sync URL
        SYNC_DATABASE_URL = DATABASE_URL.replace('+asyncpg', '')
        _engine = create_engine(SYNC_DATABASE_URL)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine, _SessionLocal


def get_sync_db():
    """Get synchronous database session for STPA-Sec routes"""
    _, SessionLocal = get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()