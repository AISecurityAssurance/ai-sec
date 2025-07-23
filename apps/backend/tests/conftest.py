"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

from core.database import Base, get_db
from core.models.database import Project, Analysis, User
from core.models.schemas import FrameworkType, AnalysisStatus
from config.settings import settings
from main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests"""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override database dependency"""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create test project"""
    project = Project(
        id=uuid4(),
        name="Test Project",
        description="Test project description",
        owner_id=test_user.id,
        metadata={"test": True}
    )
    db_session.add(project)
    await db_session.commit()
    return project


@pytest.fixture
async def test_analysis(db_session: AsyncSession, test_project: Project) -> Analysis:
    """Create test analysis"""
    analysis = Analysis(
        id=uuid4(),
        project_id=test_project.id,
        system_description="Test banking system with authentication and payment processing",
        frameworks=[FrameworkType.STPA_SEC, FrameworkType.STRIDE],
        status=AnalysisStatus.PENDING,
        metadata={}
    )
    db_session.add(analysis)
    await db_session.commit()
    return analysis


@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    class MockResponse:
        def __init__(self, content: str, model: str = "gpt-4"):
            self.content = content
            self.model = model
            self.usage = {"total_tokens": 100}
    
    return MockResponse


@pytest.fixture
def sample_system_description() -> str:
    """Sample system description for testing"""
    return """
    Modern Digital Banking Platform
    
    The system is a cloud-based banking platform that provides:
    - User authentication and authorization
    - Account management and transactions
    - Payment processing and transfers
    - Fraud detection using ML models
    - Mobile and web interfaces
    - Integration with third-party services
    
    Key components:
    1. Frontend applications (web and mobile)
    2. API Gateway for request routing
    3. Microservices for business logic
    4. Database cluster for data persistence
    5. Message queue for async processing
    6. ML pipeline for fraud detection
    """
