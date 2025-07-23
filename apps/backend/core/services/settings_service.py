"""
Settings Service
Manages model configurations with database-first approach
"""
from typing import Dict, Optional, Any
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models.database import Setting
from config.settings import ModelProvider, ModelConfig, AuthMethod

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing application settings with database persistence"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._model_configs: Dict[str, ModelConfig] = {}
    
    async def get_model_config(
        self, 
        provider: ModelProvider, 
        db: AsyncSession
    ) -> Optional[ModelConfig]:
        """
        Get model configuration with priority:
        1. Database (from UI settings)
        2. Environment variables
        3. None (show message to configure)
        """
        # Check cache first
        cache_key = f"model_config_{provider.value}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Check database
        db_config = await self._get_db_model_config(provider, db)
        if db_config:
            self._cache[cache_key] = db_config
            return db_config
        
        # Check environment variables
        env_config = self._get_env_model_config(provider)
        if env_config:
            self._cache[cache_key] = env_config
            return env_config
        
        # No configuration found
        logger.info(f"No configuration found for {provider.value}. User needs to configure in Settings.")
        return None
    
    async def save_model_config(
        self,
        provider: ModelProvider,
        config: Dict[str, Any],
        db: AsyncSession
    ) -> ModelConfig:
        """Save model configuration to database"""
        # Store each config field as a separate setting
        for key, value in config.items():
            setting_key = f"model_{provider.value}_{key}"
            
            # Check if setting exists
            result = await db.execute(
                select(Setting).where(Setting.key == setting_key)
            )
            setting = result.scalar_one_or_none()
            
            if setting:
                setting.value = str(value)
            else:
                setting = Setting(
                    key=setting_key,
                    value=str(value),
                    category="model_config",
                    description=f"{provider.value} {key}"
                )
                db.add(setting)
        
        await db.commit()
        
        # Clear cache
        cache_key = f"model_config_{provider.value}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        # Return the new config
        return await self.get_model_config(provider, db)
    
    async def get_active_provider(self, db: AsyncSession) -> Optional[ModelProvider]:
        """Get the active model provider"""
        # Check database first
        result = await db.execute(
            select(Setting).where(Setting.key == "active_provider")
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            try:
                return ModelProvider(setting.value)
            except ValueError:
                logger.warning(f"Invalid provider in database: {setting.value}")
        
        # Check environment variable
        env_provider = os.getenv("ACTIVE_PROVIDER")
        if env_provider:
            try:
                return ModelProvider(env_provider.lower())
            except ValueError:
                logger.warning(f"Invalid provider in environment: {env_provider}")
        
        # Default to None - user must configure
        return None
    
    async def set_active_provider(
        self,
        provider: ModelProvider,
        db: AsyncSession
    ):
        """Set the active model provider"""
        result = await db.execute(
            select(Setting).where(Setting.key == "active_provider")
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = provider.value
        else:
            setting = Setting(
                key="active_provider",
                value=provider.value,
                category="model_config",
                description="Active model provider"
            )
            db.add(setting)
        
        await db.commit()
        
        # Clear cache
        if "active_provider" in self._cache:
            del self._cache["active_provider"]
    
    async def _get_db_model_config(
        self,
        provider: ModelProvider,
        db: AsyncSession
    ) -> Optional[ModelConfig]:
        """Get model configuration from database"""
        # Query all settings for this provider
        prefix = f"model_{provider.value}_"
        result = await db.execute(
            select(Setting).where(Setting.key.startswith(prefix))
        )
        settings = result.scalars().all()
        
        if not settings:
            return None
        
        # Build config from settings
        config_dict = {
            "provider": provider,
            "auth_method": AuthMethod.API_KEY,  # Default
            "is_enabled": True
        }
        
        for setting in settings:
            key = setting.key.replace(prefix, "")
            value = setting.value
            
            # Convert types as needed
            if key in ["temperature"]:
                config_dict[key] = float(value)
            elif key in ["max_tokens"]:
                config_dict[key] = int(value)
            elif key == "auth_method":
                try:
                    config_dict[key] = AuthMethod(value)
                except ValueError:
                    config_dict[key] = AuthMethod.API_KEY
            elif key == "is_enabled":
                config_dict[key] = value.lower() == "true"
            else:
                config_dict[key] = value
        
        # Validate required fields based on provider
        if provider == ModelProvider.OLLAMA:
            if "api_endpoint" not in config_dict:
                return None
        else:
            if "api_key" not in config_dict:
                return None
        
        try:
            return ModelConfig(**config_dict)
        except Exception as e:
            logger.error(f"Failed to create ModelConfig from database: {e}")
            return None
    
    def _get_env_model_config(self, provider: ModelProvider) -> Optional[ModelConfig]:
        """Get model configuration from environment variables"""
        if provider == ModelProvider.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return None
            
            return ModelConfig(
                provider=provider,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        elif provider == ModelProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            
            return ModelConfig(
                provider=provider,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        elif provider == ModelProvider.GROQ:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return None
            
            return ModelConfig(
                provider=provider,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                model=os.getenv("GROQ_MODEL", "llama2-70b-4096"),
                temperature=float(os.getenv("GROQ_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        elif provider == ModelProvider.GEMINI:
            api_key = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY"))
            if not api_key:
                return None
            
            return ModelConfig(
                provider=provider,
                auth_method=AuthMethod.API_KEY,
                api_key=api_key,
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        elif provider == ModelProvider.OLLAMA:
            endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            
            return ModelConfig(
                provider=provider,
                auth_method=AuthMethod.NONE,
                api_endpoint=endpoint,
                model=os.getenv("OLLAMA_MODEL", "mistral:instruct"),
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        return None
    
    def clear_cache(self):
        """Clear the settings cache"""
        self._cache.clear()
        self._model_configs.clear()


# Global settings service instance
settings_service = SettingsService()