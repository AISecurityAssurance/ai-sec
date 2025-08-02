"""System Description Agent for STPA-Sec Step 1.

This agent creates a comprehensive system description that serves as the primary
input for Step 2 control structure analysis. It synthesizes information from
the input documents and other Step 1 artifacts to create a clear, structured
description of the system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .base_step1 import BaseStep1Agent, CognitiveStyle, AgentResult


class SystemDescriptionAgent(BaseStep1Agent):
    """Creates a comprehensive system description for use in Step 2 analysis."""
    
    def get_agent_type(self) -> str:
        return "system_description"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive system description.
        
        Args:
            context: Contains system description and other Step 1 results
            
        Returns:
            Dict containing the structured system description
        """
        await self.log_activity("Starting system description generation")
        
        try:
            # Extract system information
            system_desc = context.get('system_description', '')
            mission_data = context.get('mission_analyst', {})
            boundary_data = context.get('system_boundaries', {})
            stakeholder_data = context.get('stakeholder_analyst', {})
            
            # Build the prompt
            prompt = self._build_prompt(
                system_desc, 
                mission_data, 
                boundary_data,
                stakeholder_data
            )
            
            # Get response from model using base class method
            response = await self.call_llm(prompt)
            
            # Parse and validate response
            result_data = self._parse_response(response)
            
            await self.log_activity("System description generation complete")
            
            return result_data
            
        except Exception as e:
            await self.log_activity(f"System description analysis failed: {str(e)}", is_error=True)
            raise
    
    def _build_prompt(
        self, 
        system_desc: str,
        mission_data: Dict[str, Any],
        boundary_data: Dict[str, Any],
        stakeholder_data: Dict[str, Any]
    ) -> str:
        """Build the prompt for system description generation."""
        
        # Include mission context if available
        mission_context = ""
        if mission_data.get('mission'):
            mission_context = f"""
Mission Statement: {mission_data['mission']['statement']}
Primary Objectives:
{json.dumps(mission_data['mission'].get('objectives', []), indent=2)}
"""

        # Include boundary context if available
        boundary_context = ""
        if boundary_data.get('system_boundaries'):
            boundaries = boundary_data['system_boundaries']
            boundary_context = "System Boundaries:\n"
            for boundary in boundaries:
                boundary_context += f"- {boundary['boundary_name']}: {boundary['description']}\n"

        # Include stakeholder context if available
        stakeholder_context = ""
        if stakeholder_data.get('stakeholders'):
            stakeholder_context = "Key Stakeholders:\n"
            for sh in stakeholder_data['stakeholders'][:5]:  # Top 5 stakeholders
                stakeholder_context += f"- {sh['name']} ({sh['stakeholder_type']})\n"

        return f"""You are a systems engineering expert specializing in creating comprehensive system descriptions for STPA-Sec analysis.

Your task is to create a detailed system description that will serve as the primary input for control structure analysis. This description should provide a clear understanding of:
1. The system's purpose and functionality
2. The system's architecture and major components
3. How components interact and communicate
4. The control hierarchy and decision-making structure
5. Key operational flows and processes

CONTEXT FROM STEP 1 ANALYSIS:
{mission_context}
{boundary_context}
{stakeholder_context}

SYSTEM INFORMATION:
{system_desc}

Create a comprehensive system description following this EXACT JSON structure:

{{
  "system_overview": {{
    "name": "string - formal name of the system",
    "type": "string - type of system (e.g., 'distributed network', 'cloud platform', 'embedded system')",
    "purpose": "string - primary purpose and function",
    "scope": "string - what is included/excluded from analysis",
    "operational_context": "string - where and how the system operates"
  }},
  "architecture": {{
    "architectural_pattern": "string - overall pattern (e.g., 'client-server', 'microservices', 'layered')",
    "layers": [
      {{
        "name": "string - layer name",
        "purpose": "string - what this layer does",
        "components": ["list of major components in this layer"]
      }}
    ],
    "key_technologies": ["list of core technologies used"]
  }},
  "components": [
    {{
      "identifier": "string - unique identifier (e.g., 'COMP-001')",
      "name": "string - component name",
      "type": "string - component type (e.g., 'service', 'database', 'interface')",
      "purpose": "string - what this component does",
      "responsibilities": ["list of key responsibilities"],
      "interfaces": ["list of interfaces this component exposes"],
      "dependencies": ["list of components this depends on"]
    }}
  ],
  "interactions": [
    {{
      "identifier": "string - unique identifier (e.g., 'INT-001')",
      "name": "string - interaction name",
      "from_component": "string - source component identifier",
      "to_component": "string - target component identifier",
      "type": "string - interaction type (e.g., 'data flow', 'control', 'query')",
      "protocol": "string - communication protocol if applicable",
      "description": "string - what this interaction accomplishes"
    }}
  ],
  "control_hierarchy": {{
    "description": "string - overview of control structure",
    "levels": [
      {{
        "level": "number - hierarchy level (1 = highest)",
        "name": "string - level name",
        "controllers": ["list of controllers at this level"],
        "authority": "string - what control authority this level has"
      }}
    ]
  }},
  "operational_flows": [
    {{
      "identifier": "string - unique identifier (e.g., 'FLOW-001')",
      "name": "string - flow name",
      "type": "string - flow type (e.g., 'data processing', 'authentication', 'transaction')",
      "trigger": "string - what initiates this flow",
      "steps": [
        {{
          "step": "number",
          "component": "string - component identifier",
          "action": "string - what happens at this step"
        }}
      ],
      "outcome": "string - expected result"
    }}
  ],
  "key_characteristics": {{
    "scalability": "string - how the system scales",
    "reliability": "string - reliability mechanisms",
    "security": "string - security approach",
    "performance": "string - performance characteristics",
    "distribution": "string - how system is distributed"
  }}
}}

Important:
- Focus on DESCRIBING the system, not analyzing risks or hazards
- Be comprehensive but concise
- Use clear, technical language
- Ensure all identifiers are unique and follow the pattern shown
- Include enough detail for someone unfamiliar with the system to understand it
- Do NOT include analysis of unsafe conditions or security issues - just describe what IS

Start your response with {{ and end with }}.
"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate the model response."""
        try:
            # Clean up response
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            data = json.loads(cleaned)
            
            # Validate required fields
            required_fields = [
                'system_overview', 'architecture', 'components', 
                'interactions', 'control_hierarchy', 'operational_flows',
                'key_characteristics'
            ]
            
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add metadata
            data['generated_at'] = datetime.now().isoformat()
            data['description_version'] = "1.0"
            
            return data
            
        except json.JSONDecodeError as e:
            # Failed to parse JSON response
            # Return a minimal valid structure
            return {
                "system_overview": {
                    "name": "Unknown System",
                    "type": "unknown",
                    "purpose": "Failed to parse system description",
                    "scope": "unknown",
                    "operational_context": "unknown"
                },
                "architecture": {
                    "architectural_pattern": "unknown",
                    "layers": [],
                    "key_technologies": []
                },
                "components": [],
                "interactions": [],
                "control_hierarchy": {
                    "description": "unknown",
                    "levels": []
                },
                "operational_flows": [],
                "key_characteristics": {
                    "scalability": "unknown",
                    "reliability": "unknown", 
                    "security": "unknown",
                    "performance": "unknown",
                    "distribution": "unknown"
                },
                "parse_error": str(e),
                "raw_response": response[:1000]
            }
    
    def validate_abstraction_level(self, content: str) -> bool:
        """
        Validate that content maintains Step 1 abstraction level.
        
        Step 1 system descriptions should focus on WHAT the system does,
        not HOW it implements those functions.
        
        Args:
            content: Content to validate
            
        Returns:
            True if content maintains proper abstraction level
        """
        # Convert to lowercase for easier checking
        content_lower = content.lower()
        
        # Check for appropriate Step 1 language patterns
        step1_indicators = [
            'system', 'component', 'purpose', 'function', 'responsibility',
            'interface', 'interaction', 'hierarchy', 'flow', 'architecture'
        ]
        
        # Check for inappropriate Step 2+ language patterns
        step2_indicators = [
            'control action', 'feedback mechanism', 'process model',
            'algorithm', 'state machine', 'specific implementation',
            'code', 'protocol details', 'configuration parameters'
        ]
        
        # Count indicators
        step1_count = sum(1 for indicator in step1_indicators if indicator in content_lower)
        step2_count = sum(1 for indicator in step2_indicators if indicator in content_lower)
        
        # Content should have more Step 1 indicators than Step 2 indicators
        # and should have at least some Step 1 indicators
        return step1_count > 0 and step1_count >= step2_count