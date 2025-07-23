"""
Authentication API routes
Handles user authentication and authorization
"""
from typing import Optional
from datetime import datetime, timedelta
import logging
import secrets

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from jose import jwt
from passlib.context import CryptContext

from core.database import get_db
from core.models.database import User
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT settings
JWT_SECRET = settings.secret_key or secrets.token_urlsafe(32)
JWT_ALGORITHM = settings.jwt_algorithm
JWT_EXPIRATION_HOURS = 24


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request model"""
    email: EmailStr
    password: str
    name: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: str
    role: str
    created_at: datetime
    is_active: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        name=request.name,
        role="user",
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""
    # Find user
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should discard token)"""
    # In a more complex system, we might blacklist the token
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh access token"""
    access_token = create_access_token(data={"sub": str(current_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user={
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role
        }
    )