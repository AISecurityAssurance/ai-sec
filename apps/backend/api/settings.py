"""
Settings API routes
Manages application settings including model configurations
"""
from typing import Dict, Any, Optional
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from core.services.settings_service import settings_service
from config.settings import ModelProvider, AuthMethod

logger = logging.getLogger(__name__)

router = APIRouter()


class ModelSettingsRequest(BaseModel):
    """Request to save model settings"""
    provider: ModelProvider
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model: str
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(4096, ge=1, le=32000)
    auth_method: AuthMethod = AuthMethod.API_KEY
    is_enabled: bool = True


class ModelSettingsResponse(BaseModel):
    """Response with model settings"""
    provider: ModelProvider
    api_key: Optional[str] = None  # Masked for security
    api_endpoint: Optional[str] = None
    model: str
    temperature: float
    max_tokens: int
    auth_method: AuthMethod
    is_enabled: bool


class ActiveProviderRequest(BaseModel):
    """Request to set active provider"""
    provider: ModelProvider


@router.get("/models", response_model=Dict[str, ModelSettingsResponse])
async def get_model_settings(db: AsyncSession = Depends(get_db)):
    """Get all configured model settings"""
    providers = [
        ModelProvider.ANTHROPIC,
        ModelProvider.OPENAI,
        ModelProvider.GROQ,
        ModelProvider.GEMINI,
        ModelProvider.OLLAMA
    ]
    
    settings = {}
    for provider in providers:
        config = await settings_service.get_model_config(provider, db)
        if config:
            settings[provider.value] = ModelSettingsResponse(
                provider=provider,
                api_key="*" * 8 if config.api_key else None,  # Mask API key
                api_endpoint=config.api_endpoint,
                model=config.model or "",
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                auth_method=config.auth_method,
                is_enabled=config.is_enabled
            )
    
    return settings


@router.get("/models/{provider}", response_model=Optional[ModelSettingsResponse])
async def get_model_settings_by_provider(
    provider: ModelProvider,
    db: AsyncSession = Depends(get_db)
):
    """Get settings for a specific model provider"""
    config = await settings_service.get_model_config(provider, db)
    
    if not config:
        return None
    
    return ModelSettingsResponse(
        provider=provider,
        api_key="*" * 8 if config.api_key else None,  # Mask API key
        api_endpoint=config.api_endpoint,
        model=config.model or "",
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        auth_method=config.auth_method,
        is_enabled=config.is_enabled
    )


@router.post("/models/{provider}", response_model=ModelSettingsResponse)
async def save_model_settings(
    provider: ModelProvider,
    request: ModelSettingsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Save model settings"""
    # Validate provider matches
    if provider != request.provider:
        raise HTTPException(status_code=400, detail="Provider mismatch")
    
    # Validate required fields based on provider
    if provider == ModelProvider.OLLAMA:
        if not request.api_endpoint:
            raise HTTPException(
                status_code=400,
                detail="API endpoint is required for Ollama"
            )
    else:
        if not request.api_key:
            raise HTTPException(
                status_code=400,
                detail="API key is required for this provider"
            )
    
    # Prepare config dict
    config_dict = {
        "api_key": request.api_key,
        "api_endpoint": request.api_endpoint,
        "model": request.model,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "auth_method": request.auth_method.value,
        "is_enabled": request.is_enabled
    }
    
    # Save to database
    saved_config = await settings_service.save_model_config(provider, config_dict, db)
    
    # Clear LLM manager cache to reload with new settings
    from core.utils.llm_client import llm_manager
    llm_manager.clients.clear()
    llm_manager._db_checked = False
    
    return ModelSettingsResponse(
        provider=provider,
        api_key="*" * 8 if saved_config.api_key else None,
        api_endpoint=saved_config.api_endpoint,
        model=saved_config.model or "",
        temperature=saved_config.temperature,
        max_tokens=saved_config.max_tokens,
        auth_method=saved_config.auth_method,
        is_enabled=saved_config.is_enabled
    )


@router.get("/active-provider", response_model=Optional[str])
async def get_active_provider(db: AsyncSession = Depends(get_db)):
    """Get the currently active model provider"""
    provider = await settings_service.get_active_provider(db)
    return provider.value if provider else None


@router.post("/active-provider")
async def set_active_provider(
    request: ActiveProviderRequest,
    db: AsyncSession = Depends(get_db)
):
    """Set the active model provider"""
    # Verify the provider has configuration
    config = await settings_service.get_model_config(request.provider, db)
    if not config:
        raise HTTPException(
            status_code=400,
            detail=f"Provider {request.provider.value} is not configured"
        )
    
    await settings_service.set_active_provider(request.provider, db)
    
    # Clear LLM manager cache
    from core.utils.llm_client import llm_manager
    llm_manager.clients.clear()
    llm_manager._db_checked = False
    
    return {"message": f"Active provider set to {request.provider.value}"}


@router.post("/test-connection/{provider}")
async def test_model_connection(
    provider: ModelProvider,
    db: AsyncSession = Depends(get_db)
):
    """Test connection to a model provider"""
    config = await settings_service.get_model_config(provider, db)
    
    if not config:
        raise HTTPException(
            status_code=400,
            detail=f"Provider {provider.value} is not configured"
        )
    
    # Test the connection
    from core.utils.llm_client import llm_manager
    
    try:
        # Force reload
        await llm_manager._ensure_clients()
        
        # Try a simple test prompt
        response = await llm_manager.generate(
            "Hello, please respond with 'Connection successful!'",
            max_tokens=20
        )
        
        return {
            "success": True,
            "message": "Connection successful",
            "response": response.content[:100]  # First 100 chars
        }
    except Exception as e:
        logger.error(f"Connection test failed for {provider.value}: {e}")
        return {
            "success": False,
            "message": str(e)
        }