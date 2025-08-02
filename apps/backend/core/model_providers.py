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
    
    async def generate_structured(self, messages: List[Dict[str, str]], 
                                 response_format: Dict[str, Any],
                                 temperature: float = 0.7,
                                 max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate a structured response from the model with JSON schema validation"""
        # Default implementation falls back to regular generation
        # Subclasses can override to use native structured output support
        return await self.generate(messages, temperature, max_tokens)


class OpenAIClient(BaseModelClient):
    """OpenAI API client (supports both OpenAI and Azure)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", api_endpoint: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.api_endpoint = api_endpoint
        
        # Determine if this is Azure or standard OpenAI
        if api_endpoint:
            # Azure OpenAI
            self.is_azure = True
            self.base_url = api_endpoint.rstrip('/')
        else:
            # Standard OpenAI
            self.is_azure = False
            self.base_url = "https://api.openai.com/v1"
        
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate response using OpenAI API"""
        
        if self.is_azure:
            # Azure OpenAI uses different headers and URL structure
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            # Azure expects the deployment name, not the model name in the URL
            # Use newer API version that supports structured outputs
            url = f"{self.base_url}/openai/deployments/{self.model}/chat/completions?api-version=2024-10-21"
        else:
            # Standard OpenAI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            url = f"{self.base_url}/chat/completions"
        
        data = {
            "messages": messages,
            "temperature": temperature,
        }
        
        # Only include model for standard OpenAI (not Azure)
        if not self.is_azure:
            data["model"] = self.model
        
        if max_tokens:
            data["max_tokens"] = max_tokens
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
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
    
    async def generate_structured(self, messages: List[Dict[str, str]], 
                                 response_format: Dict[str, Any],
                                 temperature: float = 0.7,
                                 max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate structured response using OpenAI's structured output feature"""
        
        if self.is_azure:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            # Use API version that supports structured outputs
            url = f"{self.base_url}/openai/deployments/{self.model}/chat/completions?api-version=2024-10-21"
        else:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            url = f"{self.base_url}/chat/completions"
        
        data = {
            "messages": messages,
            "temperature": temperature,
            "response_format": response_format
        }
        
        if not self.is_azure:
            data["model"] = self.model
        
        if max_tokens:
            data["max_tokens"] = max_tokens
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=120.0
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Parse the structured content
                content = result["choices"][0]["message"]["content"]
                
                # If content is a string, try to parse as JSON
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON
                
                return ModelResponse(
                    content=content,
                    model=result["model"],
                    usage=result.get("usage"),
                    raw_response=result
                )
            except httpx.HTTPStatusError as e:
                # If structured output not supported, fall back to regular generation
                if e.response.status_code == 400 and "response_format" in str(e.response.text):
                    return await self.generate(messages, temperature, max_tokens)
                raise


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
    
    def _generate_mock_json_response(self, user_message: str) -> str:
        """Generate a mock JSON response based on the prompt context."""
        import json
        
        # Check for Step 2 agent contexts
        if "control structure" in user_message.lower():
            return json.dumps({
                "components": {
                    "controllers": [
                        {
                            "identifier": "CTRL-1",
                            "name": "System Administrator",
                            "type": "human",
                            "description": "Primary system admin",
                            "authority_level": "high",
                            "hierarchical_level": "system"
                        }
                    ],
                    "controlled_processes": [
                        {
                            "identifier": "PROC-1",
                            "name": "System Configuration",
                            "type": "configuration",
                            "description": "System settings management",
                            "criticality": "high"
                        },
                        {
                            "identifier": "PROC-2",
                            "name": "Access Control",
                            "type": "security",
                            "description": "User access management",
                            "criticality": "critical"
                        }
                    ],
                    "control_hierarchy": []
                },
                "summary": "Basic control structure"
            })
        elif "control action" in user_message.lower():
            return json.dumps({
                "control_actions": {
                    "control_actions": [
                        {
                            "identifier": "CA-1",
                            "controller_id": "CTRL-1",
                            "controlled_process_id": "PROC-1",
                            "action_name": "Update Configuration",
                            "action_type": "configuration",
                            "authority_level": "mandatory"
                        }
                    ]
                },
                "completeness_check": {
                    "controllers_without_actions": [],
                    "processes_without_control": ["PROC-2"],
                    "orphan_components": [],
                    "coverage_assessment": "Partial coverage"
                }
            })
        elif "feedback" in user_message.lower():
            return json.dumps({
                "feedback_mechanisms": [
                    {
                        "identifier": "FB-1",
                        "feedback_name": "Status Report",
                        "source_process_id": "PROC-1",
                        "target_controller_id": "CTRL-1",
                        "information_type": "status"
                    }
                ],
                "feedback_adequacy": []
            })
        elif "trust boundar" in user_message.lower():
            return json.dumps({
                "trust_boundaries": [
                    {
                        "identifier": "TB-1",
                        "boundary_name": "Admin Interface",
                        "boundary_type": "interface",
                        "component_a_id": "CTRL-1",
                        "component_b_id": "PROC-1"
                    }
                ],
                "trust_mechanisms": {
                    "authentication_protocols": ["password"],
                    "authorization_schemes": ["role-based"],
                    "data_protection": ["TLS"],
                    "trust_establishment": ["manual"],
                    "trust_maintenance": ["session"]
                }
            })
        elif "process model" in user_message.lower():
            return json.dumps({
                "process_models": [
                    {
                        "identifier": "PM-1",
                        "controller_id": "CTRL-1",
                        "process_id": "PROC-1",
                        "state_variables": ["config_version", "last_update"],
                        "assumptions": ["Config changes are atomic"],
                        "staleness_risk": "low"
                    }
                ],
                "control_algorithms": [],
                "insights": {}
            })
        elif "control context" in user_message.lower() or "operational mode" in user_message.lower():
            return json.dumps({
                "control_contexts": [
                    {
                        "control_action_id": "CA-1",
                        "execution_context": {
                            "triggers": ["Admin request"],
                            "preconditions": ["Valid auth"],
                            "environmental_factors": [],
                            "timing_requirements": {}
                        },
                        "decision_logic": {
                            "inputs_evaluated": ["Request validity"],
                            "decision_criteria": "Authorization check",
                            "priority": "high",
                            "conflict_resolution": "First come first serve"
                        },
                        "process_model": {
                            "state_beliefs": ["System is stable"],
                            "key_assumptions": ["Admin is authorized"],
                            "update_sources": ["Auth system"],
                            "tracked_variables": ["session_id"],
                            "staleness_handling": "Revalidate",
                            "model_reality_gaps": []
                        },
                        "applicable_modes": ["normal"]
                    }
                ],
                "operational_modes": [
                    {
                        "mode_name": "normal",
                        "description": "Normal operation",
                        "entry_conditions": ["System startup"],
                        "exit_conditions": ["Shutdown command"],
                        "active_controllers": ["CTRL-1"],
                        "available_actions": ["CA-1"],
                        "mode_constraints": []
                    }
                ],
                "mode_transitions": []
            })
        else:
            # Default response
            return json.dumps({
                "result": "Mock response",
                "status": "success"
            })
    
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate mock response based on message content"""
        
        # Get the last user message to determine response type
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        # Import the mock provider for sophisticated responses
        try:
            from core.model_providers.mock_provider import MockModelProvider
            mock = MockModelProvider()
            response = await mock.query(user_message)
            return ModelResponse(
                content=response.content,
                model=response.model,
                usage=response.usage,
                raw_response={"mock": True, "finish_reason": response.finish_reason}
            )
        except:
            # Fallback to simple JSON response based on context
            mock_response = self._generate_mock_json_response(user_message)
            return ModelResponse(
                content=mock_response,
                model="mock",
                usage={"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60}
            )


def get_model_client() -> BaseModelClient:
    """Get the configured model client"""
    
    active_provider = settings.active_provider
    
    # If no active provider set, use the first available one
    if not active_provider:
        if settings.model_providers:
            # Get the first configured provider
            first_provider = next(iter(settings.model_providers.values()))
            active_provider = first_provider.provider
        else:
            raise ValueError(
                "No model provider configured. Please set up one of:\n"
                "  • Azure OpenAI: Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_BASE, AZURE_OPENAI_API_MODEL\n"
                "  • OpenAI: Set OPENAI_API_KEY\n"
                "  • Ollama: Set OLLAMA_ENABLED=true"
            )
    
    # Convert string provider to enum if needed
    if isinstance(active_provider, str):
        try:
            active_provider = ModelProvider(active_provider)
        except ValueError:
            raise ValueError(f"Invalid provider: {active_provider}")
    
    # Look for the provider by value
    config = None
    for provider_key, provider_config in settings.model_providers.items():
        if provider_config.provider == active_provider:
            config = provider_config
            break
    
    if not config:
        raise ValueError(
            f"No configuration found for provider: {active_provider}. "
            f"Available providers: {list(settings.model_providers.keys())}"
        )
    
    if not config.is_enabled:
        raise ValueError(f"Provider {active_provider} is not enabled")
    
    if config.provider == ModelProvider.OPENAI:
        if not config.api_key:
            raise ValueError("OpenAI API key not configured")
        
        return OpenAIClient(
            api_key=config.api_key, 
            model=config.model,
            api_endpoint=config.api_endpoint
        )
        
    elif config.provider == ModelProvider.OLLAMA:
        return OllamaClient(
            api_endpoint=config.api_endpoint or "http://localhost:11434",
            model=config.model
        )
        
    elif config.provider == ModelProvider.MOCK:
        return MockModelClient()
        
    else:
        raise ValueError(f"Unknown provider: {config.provider}")