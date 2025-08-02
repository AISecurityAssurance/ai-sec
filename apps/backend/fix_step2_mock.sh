#!/bin/bash
# Fix Step 2 mock provider responses

echo "Fixing Step 2 mock provider..."

# Check if mock_provider.py exists, if not create a basic one
if [ ! -f "/app/core/model_providers/mock_provider.py" ]; then
    echo "Creating mock_provider.py..."
    cat > /app/core/model_providers/mock_provider.py << 'EOF'
"""Mock model provider for testing without API keys."""
import json
import asyncio
from typing import Dict, Any, List, Optional
from core.model_providers.base import ModelProvider, ModelResponse


class MockModelProvider(ModelProvider):
    """Mock provider that returns pre-defined responses for testing."""
    
    def __init__(self, api_key: str = "mock", **kwargs):
        super().__init__(api_key, **kwargs)
        self.name = "mock"
        
    async def query(self, prompt: str, system_prompt: Optional[str] = None, 
                   temperature: float = 0.7, max_tokens: int = 4000) -> ModelResponse:
        """Return mock responses based on prompt content."""
        await asyncio.sleep(0.1)
        
        prompt_lower = prompt.lower()
        
        # Default response with controllers and processes
        response = json.dumps({
            "components": {
                "controllers": [
                    {
                        "identifier": "CTRL-1",
                        "name": "SD-WAN Controller",
                        "type": "orchestrator",
                        "description": "Central management system",
                        "responsibilities": ["Policy management", "Traffic routing"]
                    }
                ],
                "controlled_processes": [
                    {
                        "identifier": "PROC-1",
                        "name": "Network Traffic Flow",
                        "type": "data_flow",
                        "description": "Enterprise data traffic"
                    }
                ]
            },
            "hierarchy": {
                "levels": [
                    {
                        "level": 1,
                        "name": "Orchestration Layer",
                        "controllers": ["CTRL-1"]
                    }
                ]
            },
            "control_actions": [
                {
                    "identifier": "CA-1",
                    "controller_identifier": "CTRL-1",
                    "process_identifier": "PROC-1",
                    "action_name": "Route Traffic",
                    "description": "Direct traffic through optimal path"
                }
            ],
            "trust_boundaries": [
                {
                    "identifier": "TB-1",
                    "name": "Internet Perimeter",
                    "type": "network",
                    "description": "Enterprise network boundary"
                }
            ],
            "feedback_mechanisms": [
                {
                    "identifier": "FB-1",
                    "from_component": "PROC-1",
                    "to_component": "CTRL-1",
                    "type": "performance_metrics",
                    "description": "Network telemetry"
                }
            ]
        })
        
        return ModelResponse(
            content=response,
            usage={"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60},
            model="mock-model",
            finish_reason="stop"
        )
    
    async def verify_connection(self) -> bool:
        """Always return True for mock provider."""
        return True
EOF
fi

# Update MockModelClient in model_providers.py to use the mock responses properly
echo "Updating MockModelClient..."
python3 -c "
import re

# Read the file
with open('/app/core/model_providers.py', 'r') as f:
    content = f.read()

# Find and update the MockModelClient class
pattern = r'class MockModelClient\(BaseModelClient\):.*?(?=\n\nclass|\n\ndef|\Z)'
replacement = '''class MockModelClient(BaseModelClient):
    \"\"\"Mock client for testing without real LLM calls\"\"\"
    
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        \"\"\"Generate mock response based on message content\"\"\"
        
        # Get the last user message
        user_message = \"\"
        for msg in reversed(messages):
            if msg[\"role\"] == \"user\":
                user_message = msg[\"content\"]
                break
        
        # Generate appropriate mock response
        prompt_lower = user_message.lower()
        
        # Default comprehensive response
        response = json.dumps({
            \"components\": {
                \"controllers\": [{
                    \"identifier\": \"CTRL-1\",
                    \"name\": \"SD-WAN Controller\",
                    \"type\": \"orchestrator\",
                    \"description\": \"Central management\"
                }],
                \"controlled_processes\": [{
                    \"identifier\": \"PROC-1\",
                    \"name\": \"Network Traffic\",
                    \"type\": \"data_flow\",
                    \"description\": \"Data traffic flow\"
                }]
            },
            \"control_actions\": [{
                \"identifier\": \"CA-1\",
                \"controller_identifier\": \"CTRL-1\",
                \"process_identifier\": \"PROC-1\",
                \"action_name\": \"Route Traffic\",
                \"description\": \"Traffic routing control\"
            }],
            \"trust_boundaries\": [{
                \"identifier\": \"TB-1\",
                \"name\": \"Network Perimeter\",
                \"type\": \"network\",
                \"description\": \"External boundary\"
            }],
            \"feedback_mechanisms\": [{
                \"identifier\": \"FB-1\",
                \"from_component\": \"PROC-1\",
                \"to_component\": \"CTRL-1\",
                \"type\": \"telemetry\",
                \"description\": \"Performance metrics\"
            }]
        })
        
        return ModelResponse(
            content=response,
            model=\"mock\",
            usage={\"prompt_tokens\": 10, \"completion_tokens\": 50, \"total_tokens\": 60}
        )'''

# Replace the class
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('/app/core/model_providers.py', 'w') as f:
    f.write(content)

print('MockModelClient updated')
"

echo "Step 2 mock provider fixes applied!"