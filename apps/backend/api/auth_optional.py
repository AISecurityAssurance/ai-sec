"""Optional authentication for development"""
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from core.database import get_db
from core.models.database import User
from api.auth import get_current_user as get_authenticated_user, security

# Mock user for development
MOCK_USER = User(
    id="dev-user-001",
    email="dev@example.com",
    name="Developer",
    is_active=True
)

async def get_current_user_optional(
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user or return mock user for development"""
    # For now, always return mock user
    # Later we can add auth check here
    return MOCK_USER

# For easier migration later
get_current_user = get_current_user_optional