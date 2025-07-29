from typing import Dict, List, Optional, Any, AsyncGenerator
from abc import ABC, abstractmethod
import asyncio
import time
import os
from contextlib import asynccontextmanager

# LLM Provider imports
try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

import httpx
import json
from pydantic import BaseModel

from config.settings import settings, ModelProvider, ModelConfig, metrics
from core.services.settings_service import settings_service
from core.database import get_db
import warnings


class LLMResponse(BaseModel):
    """Standard response from LLM providers"""
    content: str
    model: str
    provider: ModelProvider
    usage: Dict[str, int]  # input_tokens, output_tokens, total_tokens
    latency: float  # seconds
    cached: bool = False


class BaseLLMClient(ABC):
    """Base class for LLM provider clients"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.provider = config.provider
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream a response from the LLM"""
        pass
    
    def _record_metrics(self, response: LLMResponse):
        """Record performance metrics"""
        metrics.record_token_usage(
            self.provider.value,
            response.usage.get("input_tokens", 0),
            response.usage.get("output_tokens", 0)
        )


class AnthropicClient(BaseLLMClient):
    """Anthropic (Claude) client"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if not anthropic:
            raise ImportError("anthropic package not installed")
        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        try:
            # Try new API (anthropic >= 0.18.0)
            message = await self.client.messages.create(
                model=self.config.model or "claude-3-opus-20240229",
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
        except AttributeError:
            # Fall back to old API (anthropic < 0.18.0)
            message = await self.client.completions.create(
                model=self.config.model or "claude-3-opus-20240229",
                max_tokens_to_sample=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:"
            )
        
        # Parse response based on API version
        if hasattr(message, 'content'):
            # New API
            content = message.content[0].text
            model = message.model
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
        else:
            # Old API
            content = message.completion
            model = self.config.model or "claude-3-opus-20240229"
            # Estimate tokens for old API
            input_tokens = len(prompt.split()) * 1.3
            output_tokens = len(content.split()) * 1.3
        
        response = LLMResponse(
            content=content,
            model=model,
            provider=self.provider,
            usage={
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens)
            },
            latency=time.time() - start_time
        )
        
        self._record_metrics(response)
        return response
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            # Try new API
            stream = await self.client.messages.create(
                model=self.config.model or "claude-3-opus-20240229",
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.delta.text:
                    yield chunk.delta.text
        except AttributeError:
            # Fall back to non-streaming for old API
            response = await self.generate(prompt, **kwargs)
            yield response.content


class OpenAIClient(BaseLLMClient):
    """OpenAI (GPT) client - supports both OpenAI and Azure OpenAI"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if not openai:
            raise ImportError("openai package not installed")
        
        # Check if this is Azure OpenAI (config has api_endpoint)
        if config.api_endpoint:
            # Use Azure OpenAI
            self.client = openai.AsyncAzureOpenAI(
                api_key=config.api_key,
                azure_endpoint=config.api_endpoint,
                api_version="2024-02-01"  # Latest stable API version
            )
        else:
            # Use standard OpenAI
            self.client = openai.AsyncOpenAI(api_key=config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        response = await self.client.chat.completions.create(
            model=self.config.model or "gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature)
        )
        
        result = LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.provider,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            latency=time.time() - start_time
        )
        
        self._record_metrics(result)
        return result
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.config.model or "gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class GroqClient(BaseLLMClient):
    """Groq client"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if not Groq:
            raise ImportError("groq package not installed")
        self.client = Groq(api_key=config.api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        # Groq SDK doesn't have async support yet, so we run in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.config.model or "llama2-70b-4096",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature)
            )
        )
        
        result = LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.provider,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            latency=time.time() - start_time
        )
        
        self._record_metrics(result)
        return result
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        # Groq doesn't support streaming yet
        response = await self.generate(prompt, **kwargs)
        yield response.content


class GeminiClient(BaseLLMClient):
    """Google Gemini client"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if not genai:
            raise ImportError("google-generativeai package not installed")
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model or "gemini-pro")
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        # Gemini SDK doesn't have async support yet
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    temperature=kwargs.get("temperature", self.config.temperature)
                )
            )
        )
        
        # Estimate tokens for Gemini (it doesn't provide token counts)
        input_tokens = len(prompt.split()) * 1.3  # rough estimate
        output_tokens = len(response.text.split()) * 1.3
        
        result = LLMResponse(
            content=response.text,
            model=self.config.model or "gemini-pro",
            provider=self.provider,
            usage={
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens)
            },
            latency=time.time() - start_time
        )
        
        self._record_metrics(result)
        return result
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        # Gemini doesn't support async streaming yet
        response = await self.generate(prompt, **kwargs)
        yield response.content


class OllamaClient(BaseLLMClient):
    """Ollama (local) client"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.base_url = config.api_endpoint or "http://localhost:11434"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        response = await self.client.post(
            "/api/generate",
            json={
                "model": self.config.model or "llama2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Estimate tokens for Ollama
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(data["response"].split()) * 1.3
        
        result = LLMResponse(
            content=data["response"],
            model=data["model"],
            provider=self.provider,
            usage={
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens)
            },
            latency=time.time() - start_time
        )
        
        self._record_metrics(result)
        return result
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        async with self.client.stream(
            "POST",
            "/api/generate",
            json={
                "model": self.config.model or "llama2",
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if not data.get("done", False):
                        yield data.get("response", "")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for when no providers are configured"""
    
    def __init__(self):
        self.provider = ModelProvider.CUSTOM
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate a mock response"""
        return LLMResponse(
            content="⚠️ No LLM provider configured. Please go to Settings → Models to configure a model provider (e.g., Ollama for local models).",
            model="mock",
            provider=ModelProvider.CUSTOM,
            usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            latency=0.0
        )
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream a mock response"""
        yield "⚠️ No LLM provider configured. Please configure a model in Settings."


class LLMManager:
    """Manager for LLM clients with fallback support"""
    
    def __init__(self):
        self.clients: Dict[ModelProvider, BaseLLMClient] = {}
        self._db_checked = False
        self._no_llm_warning_shown = False
    
    async def _ensure_clients(self):
        """Ensure clients are initialized, checking DB first"""
        if self.clients and self._db_checked:
            return
        
        # Try environment variables first (for CLI mode)
        self._initialize_clients_from_env()
        
        # If no clients from env, try database
        if not self.clients:
            try:
                async for db in get_db():
                    await self._initialize_clients_from_db(db)
                    break
            except Exception as e:
                # Database not available, that's OK for CLI mode
                pass
        
        self._db_checked = True
        
        # If still no clients, add mock client
        if not self.clients:
            self.clients[ModelProvider.CUSTOM] = MockLLMClient()
            if not self._no_llm_warning_shown:
                warnings.warn(
                    "No LLM providers configured. Please configure a model in Settings → Models. "
                    "For local models, you can use Ollama with mistral:instruct.",
                    UserWarning
                )
                self._no_llm_warning_shown = True
    
    async def _initialize_clients_from_db(self, db):
        """Initialize clients from database settings"""
        providers = [
            ModelProvider.ANTHROPIC,
            ModelProvider.OPENAI,
            ModelProvider.GROQ,
            ModelProvider.GEMINI,
            ModelProvider.OLLAMA
        ]
        
        for provider in providers:
            try:
                config = await settings_service.get_model_config(provider, db)
                if config and config.is_enabled:
                    client_class = {
                        ModelProvider.ANTHROPIC: AnthropicClient,
                        ModelProvider.OPENAI: OpenAIClient,
                        ModelProvider.GROQ: GroqClient,
                        ModelProvider.GEMINI: GeminiClient,
                        ModelProvider.OLLAMA: OllamaClient,
                    }.get(provider)
                    
                    if client_class:
                        self.clients[provider] = client_class(config)
            except Exception as e:
                print(f"Failed to initialize {provider.value} client from DB: {e}")
    
    def reinitialize(self):
        """Force reinitialization of clients"""
        self.clients = {}
        self._db_checked = False
        self._initialize_clients_from_env()
    
    def _initialize_clients_from_env(self):
        """Initialize clients from environment variables"""
        for provider_id, config in settings.model_providers.items():
            if not config.is_enabled:
                continue
            
            try:
                client_class = {
                    ModelProvider.ANTHROPIC: AnthropicClient,
                    ModelProvider.OPENAI: OpenAIClient,
                    ModelProvider.GROQ: GroqClient,
                    ModelProvider.GEMINI: GeminiClient,
                    ModelProvider.OLLAMA: OllamaClient,
                }.get(config.provider)
                
                if client_class:
                    try:
                        self.clients[config.provider] = client_class(config)
                    except Exception as client_error:
                        print(f"Failed to initialize {provider_id} client: {client_error}")
                        raise
            except Exception as e:
                print(f"Failed to initialize {provider_id} client from env: {e}")
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response with fallback support"""
        # Ensure clients are initialized
        await self._ensure_clients()
        
        # Get active provider from DB or settings
        active_provider = settings.active_provider
        try:
            async for db in get_db():
                db_provider = await settings_service.get_active_provider(db)
                if db_provider:
                    active_provider = db_provider
                break
        except:
            pass
        
        providers = [active_provider] if active_provider else list(self.clients.keys())
        
        last_error = None
        for provider in providers:
            if provider not in self.clients:
                continue
            
            try:
                return await self.clients[provider].generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if "401" in str(e) or "403" in str(e):
                    print(f"Authentication failed for {provider}: {e}")
                else:
                    print(f"Provider {provider} failed: {e}")
                continue
        
        # If all providers failed, return mock response
        if ModelProvider.CUSTOM in self.clients:
            return await self.clients[ModelProvider.CUSTOM].generate(prompt, **kwargs)
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response with fallback support"""
        # Ensure clients are initialized
        await self._ensure_clients()
        
        # Get active provider from DB or settings
        active_provider = settings.active_provider
        try:
            async for db in get_db():
                db_provider = await settings_service.get_active_provider(db)
                if db_provider:
                    active_provider = db_provider
                break
        except:
            pass
        
        providers = [active_provider] if active_provider else list(self.clients.keys())
        
        if settings.enable_fallback and active_provider:
            providers.extend([
                p for p in settings.fallback_order 
                if p != active_provider and p in self.clients
            ])
        
        last_error = None
        for provider in providers:
            if provider not in self.clients:
                continue
            
            try:
                async for chunk in self.clients[provider].stream(prompt, **kwargs):
                    yield chunk
                return
            except Exception as e:
                last_error = e
                print(f"Provider {provider} failed: {e}")
                continue
        
        # If all providers failed, stream mock response
        if ModelProvider.CUSTOM in self.clients:
            async for chunk in self.clients[ModelProvider.CUSTOM].stream(prompt, **kwargs):
                yield chunk
            return
        
        raise Exception(f"All providers failed. Last error: {last_error}")


# Global LLM manager instance
llm_manager = LLMManager()