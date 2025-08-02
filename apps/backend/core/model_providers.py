"""
Model provider abstraction for LLM integration
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import os
import httpx
import json
import logging
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
    
    def __init__(self):
        self.supports_structured_output = False
    
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
        if self.supports_structured_output:
            # Subclasses should override this method if they support structured output
            return await self.generate(messages, temperature, max_tokens)
        else:
            # Fallback: Enhance prompt for JSON output
            enhanced_messages = self._enhance_messages_for_json(messages, response_format)
            # Use lower temperature for more consistent JSON output
            json_temperature = min(temperature, 0.3)
            if json_temperature < temperature:
                logger = logging.getLogger(__name__)
                logger.debug(f"Lowered temperature from {temperature} to {json_temperature} for JSON consistency")
            response = await self.generate(enhanced_messages, json_temperature, max_tokens)
            
            # Try to parse JSON if response is a string
            if isinstance(response.content, str):
                try:
                    parsed_content = json.loads(response.content)
                    return ModelResponse(
                        content=parsed_content,
                        model=response.model,
                        usage=response.usage,
                        raw_response=response.raw_response
                    )
                except json.JSONDecodeError:
                    # Log but don't fail - let the agent's parser handle it
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Could not parse JSON in base fallback: {response.content[:100]}...")
            
            return response
    
    def _enhance_messages_for_json(self, messages: List[Dict[str, str]], 
                                  response_format: Dict[str, Any]) -> List[Dict[str, str]]:
        """Enhance messages to encourage JSON output when structured output not supported."""
        enhanced = messages.copy()
        
        # Extract schema if present
        schema = None
        if isinstance(response_format, dict) and 'json_schema' in response_format:
            schema = response_format['json_schema'].get('schema', {})
        
        # Add JSON instruction to system message
        json_instruction = "\n\nIMPORTANT: You MUST respond with valid JSON only. Do not include any markdown formatting, explanations, or text outside of the JSON object."
        
        if schema:
            json_instruction += f"\n\nYour response must conform to this JSON schema:\n{json.dumps(schema, indent=2)}"
        
        # Find and enhance system message
        system_msg_found = False
        for i, msg in enumerate(enhanced):
            if msg['role'] == 'system':
                enhanced[i] = {
                    'role': 'system',
                    'content': msg['content'] + json_instruction
                }
                system_msg_found = True
                break
        
        # If no system message, add one
        if not system_msg_found:
            enhanced.insert(0, {
                'role': 'system',
                'content': 'You are a helpful assistant.' + json_instruction
            })
        
        # Also add reminder in the last user message
        for i in range(len(enhanced) - 1, -1, -1):
            if enhanced[i]['role'] == 'user':
                enhanced[i] = {
                    'role': 'user',
                    'content': enhanced[i]['content'] + '\n\nRemember: Respond with valid JSON only.'
                }
                break
        
        return enhanced


class OpenAIClient(BaseModelClient):
    """OpenAI API client (supports both OpenAI and Azure)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", api_endpoint: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.api_endpoint = api_endpoint
        
        # Determine if this is Azure or standard OpenAI
        if api_endpoint:
            # Azure OpenAI
            self.is_azure = True
            self.base_url = api_endpoint.rstrip('/')
            # Azure OpenAI with 2024-10-21 API version supports structured output
            self.supports_structured_output = True
        else:
            # Standard OpenAI
            self.is_azure = False
            self.base_url = "https://api.openai.com/v1"
            # OpenAI supports structured output with certain models
            self.supports_structured_output = True
        
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
        
        # First, try with native structured output support
        if self.supports_structured_output:
            try:
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
                # If structured output not supported, disable it and fall back
                if e.response.status_code == 400 and "response_format" in str(e.response.text):
                    self.supports_structured_output = False
                    logging.getLogger(__name__).info("Structured output not supported, falling back to enhanced prompting")
                else:
                    raise
        
        # Fallback to enhanced prompting - use base class method which handles everything
        return await super().generate_structured(messages, response_format, temperature, max_tokens)


class OllamaClient(BaseModelClient):
    """Ollama local model client"""
    
    def __init__(self, api_endpoint: str = "http://localhost:11434", 
                 model: str = "mixtral:instruct"):
        super().__init__()
        self.api_endpoint = api_endpoint
        self.model = model
        # Ollama doesn't support structured output natively
        self.supports_structured_output = False
        
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


class AnthropicClient(BaseModelClient):
    """Anthropic Claude API client"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        # Anthropic doesn't support structured output yet
        self.supports_structured_output = False
        
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate response using Anthropic API"""
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Convert messages to Anthropic format
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        data = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4000
        }
        
        if system_message:
            data["system"] = system_message
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=120.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract content from Anthropic's response format
            content = ""
            for content_block in result.get("content", []):
                if content_block.get("type") == "text":
                    content += content_block.get("text", "")
            
            return ModelResponse(
                content=content,
                model=result.get("model", self.model),
                usage={
                    "prompt_tokens": result.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": result.get("usage", {}).get("output_tokens", 0),
                    "total_tokens": (result.get("usage", {}).get("input_tokens", 0) + 
                                   result.get("usage", {}).get("output_tokens", 0))
                },
                raw_response=result
            )


class MockModelClient(BaseModelClient):
    """Mock client for testing without real LLM calls"""
    
    def __init__(self):
        super().__init__()
        # Mock client simulates no structured output support for testing fallback
        self.supports_structured_output = False
    
    def _generate_mock_json_response(self, user_message: str) -> str:
        """Generate a mock JSON response based on the prompt context."""
        import json
        
        # Log the type of request for debugging
        logger = logging.getLogger("MockModelClient")
        logger.debug(f"Mock request type detection for message length: {len(user_message)}")
        
        # Check for Step 2 agent contexts
        if "control structure" in user_message.lower():
            return json.dumps({
                "controllers": [
                    {
                        "identifier": "CTRL-1",
                        "name": "System Administrator",
                        "type": "human",
                        "description": "Primary system admin",
                        "authority_level": "high",
                        "hierarchical_level": "system",
                        "controls": ["System configuration", "Access control"]
                    }
                ],
                "controlled_processes": [
                    {
                        "identifier": "PROC-1",
                        "name": "System Configuration",
                        "type": "computational",
                        "description": "System settings management",
                        "criticality": "high",
                        "capabilities": ["Store configuration", "Apply settings"]
                    },
                    {
                        "identifier": "PROC-2",
                        "name": "Access Control",
                        "type": "computational",
                        "description": "User access management",
                        "criticality": "high",
                        "capabilities": ["Authenticate users", "Authorize actions"]
                    }
                ],
                "dual_role_components": [],
                "control_hierarchy": [],
                "analysis_notes": "Basic mock control structure for testing"
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
        elif ("quality" in user_message.lower() and "assess" in user_message.lower()) or \
             ("methodology" in user_message.lower() and "stpa" in user_message.lower()) or \
             ("quality_level" in user_message and "methodology_compliance" in user_message):
            # Quality assessment response for expert agent
            return json.dumps({
                "quality_level": "acceptable",
                "overall_score": 8.0,
                "methodology_compliance": {
                    "control_structure_identified": True,
                    "hierarchical_levels_clear": True,
                    "all_components_typed": True,
                    "relationships_mapped": True
                },
                "issues": [],
                "recommendations": [],
                "strengths": ["Clear structure", "Good coverage"],
                "weaknesses": []
            })
        elif "refinement" in user_message.lower() and "guidance" in user_message.lower():
            # Refinement guidance response
            return json.dumps({
                "priority_fixes": [],
                "specific_requirements": [],
                "avoid_patterns": [],
                "example_corrections": []
            })
        elif "step 2" in user_message.lower() or "stpa-sec step 2" in user_message.lower():
            # Generic Step 2 response
            return json.dumps({
                "quality_level": "acceptable",
                "overall_score": 0.8,
                "methodology_compliance": {
                    "follows_stpa_principles": True,
                    "meets_step_requirements": True,
                    "appropriate_abstraction": True,
                    "complete_control_loops": True
                },
                "issues": [],
                "recommendations": [],
                "strengths": ["Good structure"],
                "weaknesses": []
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
        
    elif config.provider == ModelProvider.ANTHROPIC:
        if not config.api_key:
            raise ValueError("Anthropic API key not configured")
        
        return AnthropicClient(
            api_key=config.api_key,
            model=config.model
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