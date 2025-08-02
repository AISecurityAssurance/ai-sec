from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from enum import Enum
import os
from pathlib import Path


class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelProvider(str, Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    CUSTOM = "custom"
    MOCK = "mock"


class AuthMethod(str, Enum):
    """Authentication methods for providers"""
    API_KEY = "api-key"
    OAUTH = "oauth"
    NONE = "none"


class ModelConfig(BaseSettings):
    """Configuration for a specific model provider"""
    provider: ModelProvider
    auth_method: AuthMethod
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    is_enabled: bool = False

    model_config = {
        "env_prefix": "MODEL_",
        "extra": "ignore"  # Ignore extra environment variables
    }


class DatabaseConfig(BaseSettings):
    """Database configuration"""
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: str = Field("security_analyst", env="POSTGRES_DB")
    postgres_user: str = Field("sa_user", env="POSTGRES_USER")
    postgres_password: str = Field("sa_password", env="POSTGRES_PASSWORD")
    
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    neo4j_uri: str = Field("bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field("neo4j", env="NEO4J_USER")
    neo4j_password: str = Field("neo4j_password", env="NEO4J_PASSWORD")
    
    model_config = {
        "extra": "ignore"  # Ignore extra environment variables
    }

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"


class Settings(BaseSettings):
    """Application settings"""
    # Application
    app_name: str = Field("Security Analyst", env="APP_NAME")
    environment: Environment = Field(Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    
    # API
    api_prefix: str = Field("/api/v1", env="API_PREFIX")
    port: int = Field(8000, env="PORT")
    cors_origins: List[str] = Field(
        ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Database
    database: DatabaseConfig = DatabaseConfig()
    
    # Model Providers
    model_providers: Dict[str, ModelConfig] = Field(default_factory=dict)
    active_provider: Optional[ModelProvider] = Field(None, env="ACTIVE_PROVIDER")
    enable_fallback: bool = Field(False, env="ENABLE_MODEL_FALLBACK")
    fallback_order: List[ModelProvider] = Field(
        [ModelProvider.ANTHROPIC, ModelProvider.OPENAI, ModelProvider.GROQ],
        env="MODEL_FALLBACK_ORDER"
    )
    
    # Performance
    max_concurrent_analyses: int = Field(10, env="MAX_CONCURRENT_ANALYSES")
    analysis_timeout_seconds: int = Field(300, env="ANALYSIS_TIMEOUT_SECONDS")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    cache_ttl_seconds: int = Field(3600, env="CACHE_TTL_SECONDS")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    prompts_dir: Path = base_dir / "core" / "prompts"
    artifacts_dir: Path = base_dir / "artifacts"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "protected_namespaces": ("settings_",),
        "extra": "ignore"  # Ignore extra environment variables
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_model_providers()
        self._ensure_directories()
    
    def _load_model_providers(self):
        """Load model provider configurations from environment variables"""
        # Azure OpenAI first (takes highest precedence)
        if (azure_key := os.getenv("AZURE_OPENAI_API_KEY")) and (azure_base := os.getenv("AZURE_OPENAI_API_BASE")):
            self.model_providers["openai"] = ModelConfig(
                provider=ModelProvider.OPENAI,
                auth_method=AuthMethod.API_KEY,
                api_key=azure_key,
                api_endpoint=azure_base,
                model=os.getenv("AZURE_OPENAI_API_MODEL", "gpt-4-turbo"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
                is_enabled=True
            )
            # Set active provider to OpenAI when Azure is configured
            self.active_provider = ModelProvider.OPENAI
        # Standard OpenAI
        elif openai_key := os.getenv("OPENAI_API_KEY"):
            self.model_providers["openai"] = ModelConfig(
                provider=ModelProvider.OPENAI,
                auth_method=AuthMethod.API_KEY,
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        # Anthropic
        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            self.model_providers["anthropic"] = ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                auth_method=AuthMethod.API_KEY,
                api_key=anthropic_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        # Groq
        if groq_key := os.getenv("GROQ_API_KEY"):
            self.model_providers["groq"] = ModelConfig(
                provider=ModelProvider.GROQ,
                auth_method=AuthMethod.API_KEY,
                api_key=groq_key,
                model=os.getenv("GROQ_MODEL", "llama2-70b-4096"),
                temperature=float(os.getenv("GROQ_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        # Gemini
        if gemini_key := os.getenv("GEMINI_API_KEY"):
            self.model_providers["gemini"] = ModelConfig(
                provider=ModelProvider.GEMINI,
                auth_method=AuthMethod.API_KEY,
                api_key=gemini_key,
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
                temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "4096")),
                is_enabled=True
            )
        
        # Ollama - only configure if explicitly requested
        if os.getenv("OLLAMA_ENABLED", "").lower() == "true":
            ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
            self.model_providers["ollama"] = ModelConfig(
                provider=ModelProvider.OLLAMA,
                auth_method=AuthMethod.NONE,
                api_endpoint=ollama_endpoint,
                model=os.getenv("OLLAMA_MODEL", "llama2"),
                temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", "4096")),
                is_enabled=True
            )
            
        # Mock provider - for testing without real API calls
        if os.getenv("USE_MOCK_PROVIDER", "").lower() == "true":
            self.model_providers["mock"] = ModelConfig(
                provider=ModelProvider.MOCK,
                auth_method=AuthMethod.NONE,
                api_key="mock-key",
                model="mock-model",
                temperature=0.0,
                max_tokens=4096,
                is_enabled=True
            )
            # Override active provider to use mock
            self.active_provider = ModelProvider.MOCK
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    def get_active_model_config(self) -> Optional[ModelConfig]:
        """Get the configuration for the active model provider"""
        return self.model_providers.get(self.active_provider.value)
    
    def get_available_providers(self) -> List[ModelProvider]:
        """Get list of available (configured) providers"""
        return [
            ModelProvider(provider_id)
            for provider_id, config in self.model_providers.items()
            if config.is_enabled
        ]


# Global settings instance
settings = Settings()


# Performance metrics helper
class PerformanceMetrics:
    """Helper class for tracking performance metrics"""
    def __init__(self):
        self.analysis_times: Dict[str, List[float]] = {}
        self.token_usage: Dict[str, Dict[str, int]] = {}
        self.cache_hits: int = 0
        self.cache_misses: int = 0
    
    def record_analysis_time(self, analysis_type: str, duration: float):
        """Record time taken for an analysis"""
        if analysis_type not in self.analysis_times:
            self.analysis_times[analysis_type] = []
        self.analysis_times[analysis_type].append(duration)
    
    def record_token_usage(self, provider: str, input_tokens: int, output_tokens: int):
        """Record token usage for a provider"""
        if provider not in self.token_usage:
            self.token_usage[provider] = {"input": 0, "output": 0, "total": 0}
        self.token_usage[provider]["input"] += input_tokens
        self.token_usage[provider]["output"] += output_tokens
        self.token_usage[provider]["total"] += input_tokens + output_tokens
    
    def get_average_analysis_time(self, analysis_type: str) -> Optional[float]:
        """Get average time for an analysis type"""
        times = self.analysis_times.get(analysis_type, [])
        return sum(times) / len(times) if times else None
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


# Global metrics instance
metrics = PerformanceMetrics()