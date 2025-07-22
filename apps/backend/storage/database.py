from typing import AsyncGenerator, Any, Optional
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase

from config.settings import settings
from core.models.analysis import Base

# PostgreSQL setup
engine = create_async_engine(
    settings.database.postgres_url,
    echo=settings.debug,
    pool_pre_ping=True,
    poolclass=NullPool,  # Use NullPool for async
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Redis setup
redis_pool = redis.ConnectionPool.from_url(
    settings.database.redis_url,
    decode_responses=True,
)
redis_client = redis.Redis(connection_pool=redis_pool)

# Neo4j setup
neo4j_driver = None


async def init_neo4j():
    """Initialize Neo4j connection"""
    global neo4j_driver
    try:
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.database.neo4j_uri,
            auth=(settings.database.neo4j_user, settings.database.neo4j_password)
        )
        # Test connection
        async with neo4j_driver.session() as session:
            await session.run("RETURN 1")
        print("Neo4j connection established")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        neo4j_driver = None


async def close_neo4j():
    """Close Neo4j connection"""
    global neo4j_driver
    if neo4j_driver:
        await neo4j_driver.close()
        neo4j_driver = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get PostgreSQL session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    return redis_client


@asynccontextmanager
async def get_neo4j_session():
    """Get Neo4j session"""
    if not neo4j_driver:
        raise RuntimeError("Neo4j not initialized")
    
    async with neo4j_driver.session() as session:
        yield session


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Neo4j
    await init_neo4j()
    
    # Test Redis
    try:
        await redis_client.ping()
        print("Redis connection established")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    await redis_client.close()
    await close_neo4j()


# Cache helpers
class CacheManager:
    """Redis cache manager"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = settings.cache_ttl_seconds
    
    async def get(self, key: str) -> Any:
        """Get value from cache"""
        value = await self.redis.get(key)
        if value:
            import json
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        import json
        ttl = ttl or self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0
    
    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern"""
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break


# Global cache instance
cache = CacheManager(redis_client)