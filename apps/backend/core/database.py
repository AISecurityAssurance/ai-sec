"""
Database connection and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config.settings import settings
import os

# Get database URL from env or use settings
database_url = os.getenv("DATABASE_URL", settings.database.postgres_url)

# Create async engine with different settings based on database type
if database_url.startswith("sqlite"):
    # SQLite doesn't support some pool options
    engine = create_async_engine(
        database_url,
        echo=False,  # Always disable echo, use logging instead
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL and other databases
    engine = create_async_engine(
        database_url,
        echo=False,  # Always disable echo, use logging instead
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables)"""
    # Import models to ensure they're registered
    from core.models.database import (
        User, Project, Analysis, AnalysisResult, 
        ChatMessage, Artifact, SystemComponent, Setting
    )
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization warning: {str(e)}")
        # Continue anyway - tables might already exist


async def close_db():
    """Close database connections"""
    await engine.dispose()


async def create_database_pool(database_url: str):
    """Create a database connection pool"""
    # For asyncpg, we just return the connection string
    # The actual pool is managed by asyncpg.create_pool
    return database_url


async def run_migrations(database_url: str):
    """Run database migrations"""
    import asyncpg
    from pathlib import Path
    
    # Connect to the database
    conn = await asyncpg.connect(database_url)
    
    try:
        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / "migrations"
        
        # Run migrations in order
        if migrations_dir.exists():
            migration_files = sorted(migrations_dir.glob("*.sql"))
            for migration_file in migration_files:
                print(f"Running migration: {migration_file.name}")
                with open(migration_file, 'r') as f:
                    sql = f.read()
                    await conn.execute(sql)
        
        print("All migrations completed successfully")
    finally:
        await conn.close()