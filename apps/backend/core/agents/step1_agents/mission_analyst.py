"""
Mission Analyst Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List
import re
import json

from .base_step1 import BaseStep1Agent, CognitiveStyle
# Removed - using base class call_llm method instead


class MissionAnalystAgent(BaseStep1Agent):
    """
    Analyzes and structures the system's mission
    
    Responsibilities:
    - Extract PURPOSE (what the system does)
    - Extract METHOD (how it achieves purpose - abstract)
    - Extract GOALS (why it matters)
    - Ensure mission-level language
    """
    
    def get_agent_type(self) -> str:
        return "mission_analyst"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system mission from description"""
        await self.log_activity("Starting mission analysis")
        
        system_description = context.get('system_description', '')
        
        # Always use LLM for analysis
        mission_data = await self._analyze_mission_with_llm(system_description)
        
        # Extract components from mission data
        problem_statement = mission_data.get('problem_statement', {})
        mission_context = mission_data.get('mission_context', {})
        operational_constraints = mission_data.get('operational_constraints', [])
        environmental_assumptions = mission_data.get('environmental_assumptions', {})
        
        results = {
            "problem_statement": problem_statement,
            "mission_context": mission_context,
            "operational_constraints": operational_constraints,
            "environmental_assumptions": environmental_assumptions,
            "abstraction_validated": True,
            "cognitive_style": self.cognitive_style.value
        }
        
        # Validate abstraction level
        for key, value in problem_statement.items():
            if isinstance(value, str) and self.is_implementation_detail(value):
                results["abstraction_warnings"] = results.get("abstraction_warnings", [])
                results["abstraction_warnings"].append(f"{key} contains implementation details")
                results["abstraction_validated"] = False
        
        await self.save_results(results)
        await self.log_activity("Completed mission analysis", results)
        
        return results
    
    async def _analyze_mission_with_llm(self, description: str) -> Dict[str, Any]:
        """Use LLM to analyze mission based on cognitive style"""
        # Get cognitive style prompt modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Build the prompt
        prompt = f"""{style_modifier}

You are a security analyst performing STPA-Sec Step 1 mission analysis.

System Description:
{description}

Analyze the system's mission and provide:

1. Problem Statement with:
   - PURPOSE (WHAT the system does - mission level)
   - METHOD (HOW it achieves purpose - abstract, not implementation)
   - GOALS (WHY it matters - strategic objectives)
   - Full statement: "A System to [PURPOSE] by means of [METHOD] in order to [GOALS]"

2. Mission Context:
   - Domain (e.g., financial_services, healthcare, infrastructure)
   - Criticality (catastrophic, major, moderate, minor)
   - Operational tempo (continuous, scheduled, on_demand)
   - Key capabilities (abstract capabilities, not features)

3. Operational Constraints:
   - Regulatory frameworks and compliance requirements
   - Business constraints (SLAs, transaction volumes)
   - Organizational constraints (risk appetite, maturity)

4. Environmental Assumptions:
   - User behavior patterns
   - Threat landscape
   - Infrastructure dependencies
   - Trust relationships

Provide your response as a JSON object with the following structure:
{{
  "problem_statement": {{
    "purpose_what": "purpose description",
    "method_how": "method description",
    "goals_why": "goals description",
    "full_statement": "A System to..."
  }},
  "mission_context": {{
    "domain": "domain_type",
    "criticality": "catastrophic|major|moderate|minor",
    "operational_tempo": {{
      "pattern": "continuous|scheduled|on_demand",
      "peak_periods": ["period1", "period2"],
      "availability_requirement": "percentage or description"
    }},
    "key_capabilities": ["capability1", "capability2"]
  }},
  "operational_constraints": {{
    "regulatory": {{
      "frameworks": ["framework1", "framework2"],
      "audit_frequency": "periodic|continuous",
      "change_approval": "required|standard"
    }},
    "business": {{
      "availability_requirement": "SLA percentage",
      "transaction_volume": "volume description",
      "legacy_integration": "required|optional|none"
    }},
    "organizational": {{
      "risk_appetite": "low|moderate|high",
      "security_maturity": "initial|developing|defined|managed|optimizing",
      "change_capacity": "low|moderate|high"
    }}
  }},
  "environmental_assumptions": {{
    "user_behavior": ["assumption1", "assumption2"],
    "threat_landscape": ["threat1", "threat2"],
    "infrastructure": ["dependency1", "dependency2"],
    "trust_relationships": ["relationship1", "relationship2"]
  }}
}}

IMPORTANT: Maintain mission-level abstraction. Avoid implementation details, technical specifications, or prevention-focused language."""
        
        try:
            # Call LLM
            response = await self.call_llm(prompt)
            
            # Parse JSON response
            content = response.strip()
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            mission_data = json.loads(content)
            
            # Validate structure
            required_keys = ["problem_statement", "mission_context", "operational_constraints", "environmental_assumptions"]
            for key in required_keys:
                if key not in mission_data:
                    raise ValueError(f"Missing required key: {key}")
            
            return mission_data
            
        except Exception as e:
            await self.log_activity(f"LLM mission analysis failed: {e}", {"error": str(e)})
            # Re-raise the exception - analysis should fail if LLM fails
            raise
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate mission-level abstraction"""
        # Check for implementation details
        if self.is_implementation_detail(content):
            return False
        
        # Check for prevention language
        if self.is_prevention_language(content):
            return False
            
        return True