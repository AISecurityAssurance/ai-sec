"""
Model provider abstraction for LLM integration
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import os
import httpx
import json
from dataclasses import dataclass

from config.settings import settings, ModelProvider


@dataclass
class ModelResponse:
    """Response from a model provider"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseModelClient(ABC):
    """Base class for model provider clients"""
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate a response from the model"""
        pass


class OpenAIClient(BaseModelClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate response using OpenAI API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=120.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            return ModelResponse(
                content=result["choices"][0]["message"]["content"],
                model=result["model"],
                usage=result.get("usage"),
                raw_response=result
            )


class OllamaClient(BaseModelClient):
    """Ollama local model client"""
    
    def __init__(self, api_endpoint: str = "http://localhost:11434", 
                 model: str = "mixtral:instruct"):
        self.api_endpoint = api_endpoint
        self.model = model
        
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate response using Ollama API"""
        
        # Convert messages to Ollama format
        prompt = self._format_messages(messages)
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            data["options"]["num_predict"] = max_tokens
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_endpoint}/api/generate",
                json=data,
                timeout=300.0  # Ollama can be slow
            )
            response.raise_for_status()
            
            result = response.json()
            
            return ModelResponse(
                content=result["response"],
                model=self.model,
                usage={
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                },
                raw_response=result
            )
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Ollama prompt"""
        formatted = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
                
        # Add final prompt indicator
        formatted.append("Assistant:")
        
        return "\n\n".join(formatted)


class MockModelClient(BaseModelClient):
    """Mock client for testing without real LLM calls"""
    
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate mock response"""
        
        # Return a simple mock response
        return ModelResponse(
            content="Mock response for testing",
            model="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        )


def get_model_client() -> BaseModelClient:
    """Get the configured model client"""
    
    active_provider = settings.active_provider
    
    if active_provider not in settings.model_providers:
        raise ValueError(f"No configuration found for provider: {active_provider}")
    
    config = settings.model_providers[active_provider]
    
    if not config.is_enabled:
        raise ValueError(f"Provider {active_provider} is not enabled")
    
    if config.provider == ModelProvider.OPENAI:
        if not config.api_key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIClient(api_key=config.api_key, model=config.model)
        
    elif config.provider == ModelProvider.OLLAMA:
        return OllamaClient(
            api_endpoint=config.api_endpoint or "http://localhost:11434",
            model=config.model
        )
        
    elif config.provider == ModelProvider.MOCK:
        return MockModelClient()
        
    else:
        raise ValueError(f"Unknown provider: {config.provider}")