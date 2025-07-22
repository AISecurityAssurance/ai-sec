from typing import Dict, List, Optional, Any, AsyncGenerator
from abc import ABC, abstractmethod
import asyncio
import time
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
        
        message = await self.client.messages.create(
            model=self.config.model or "claude-3-opus-20240229",
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = LLMResponse(
            content=message.content[0].text,
            model=message.model,
            provider=self.provider,
            usage={
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.input_tokens + message.usage.output_tokens
            },
            latency=time.time() - start_time
        )
        
        self._record_metrics(response)
        return response
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
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


class OpenAIClient(BaseLLMClient):
    """OpenAI (GPT) client"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        if not openai:
            raise ImportError("openai package not installed")
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


class LLMManager:
    """Manager for LLM clients with fallback support"""
    
    def __init__(self):
        self.clients: Dict[ModelProvider, BaseLLMClient] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize configured LLM clients"""
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
                    self.clients[config.provider] = client_class(config)
            except Exception as e:
                print(f"Failed to initialize {provider_id} client: {e}")
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response with fallback support"""
        providers = [settings.active_provider]
        
        if settings.enable_fallback:
            providers.extend([
                p for p in settings.fallback_order 
                if p != settings.active_provider and p in self.clients
            ])
        
        last_error = None
        for provider in providers:
            if provider not in self.clients:
                continue
            
            try:
                return await self.clients[provider].generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                print(f"Provider {provider} failed: {e}")
                continue
        
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response with fallback support"""
        providers = [settings.active_provider]
        
        if settings.enable_fallback:
            providers.extend([
                p for p in settings.fallback_order 
                if p != settings.active_provider and p in self.clients
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
        
        raise Exception(f"All providers failed. Last error: {last_error}")


# Global LLM manager instance
llm_manager = LLMManager()