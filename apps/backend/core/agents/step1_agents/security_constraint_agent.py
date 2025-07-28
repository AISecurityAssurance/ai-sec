"""
Security Constraint Agent for STPA-Sec Step 1
Derives security constraints from identified hazards and losses
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_step1 import BaseStep1Agent, CognitiveStyle


class SecurityConstraintAgent(BaseStep1Agent):
    """Agent responsible for deriving security constraints from hazards"""
    
    def __init__(self, cognitive_style: CognitiveStyle = CognitiveStyle.BALANCED):
        super().__init__(cognitive_style)
        self.agent_type = "security_constraints"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derive security constraints from hazards and losses
        
        Args:
            context: Dictionary containing:
                - hazards: List of identified hazards
                - losses: List of identified losses
                - system_description: System being analyzed
                
        Returns:
            Dictionary containing security constraints and mappings
        """
        hazards = context.get('hazards', [])
        losses = context.get('losses', [])
        system_description = context.get('system_description', '')
        
        # Generate prompt for constraint derivation
        prompt = self._create_constraint_prompt(hazards, losses, system_description)
        
        # Call LLM with cognitive style modifier
        response = await self.call_llm(prompt)
        
        # Parse and structure the response
        constraints = self._parse_constraint_response(response)
        
        # Generate constraint-hazard mappings
        mappings = self._generate_mappings(constraints, hazards)
        
        # Create summary statistics
        summary = self._create_summary(constraints, mappings)
        
        return {
            "security_constraints": constraints,
            "constraint_hazard_mappings": mappings,
            "constraint_count": len(constraints),
            "constraint_types": summary["types"],
            "cognitive_style": self.cognitive_style.value,
            "analysis_metadata": {
                "agent_type": self.agent_type,
                "analysis_id": context.get('analysis_id', 'unknown'),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0"
            }
        }
    
    def _create_constraint_prompt(self, hazards: List[Dict], losses: List[Dict], 
                                system_description: str) -> str:
        """Create prompt for constraint generation"""
        
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Format hazards and losses for the prompt
        hazards_text = "\n".join([
            f"- {h['identifier']}: {h['description']}"
            for h in hazards
        ])
        
        losses_text = "\n".join([
            f"- {l['identifier']}: {l['description']}"
            for l in losses
        ])
        
        prompt = f"""You are a security analyst performing STPA-Sec Step 1 analysis.
{style_modifier}

Given these mission-level hazards and losses, derive security constraints that prevent, detect, or mitigate the hazards.

SYSTEM DESCRIPTION:
{system_description}

IDENTIFIED HAZARDS:
{hazards_text}

IDENTIFIED LOSSES:
{losses_text}

INSTRUCTIONS:
1. For each hazard, identify one or more constraints that would address it
2. Constraints must be at mission level (WHAT not HOW)
3. Use "The system shall..." format
4. Each constraint must be verifiable and enforceable
5. Consider:
   - Preventive constraints (eliminate hazards)
   - Detective constraints (identify when hazards occur)
   - Corrective constraints (respond to hazards)
   - Compensating constraints (reduce impact)

Generate constraints in this JSON format:
{{
  "constraints": [
    {{
      "identifier": "SC-1",
      "constraint_statement": "The system shall...",
      "rationale": "Why this constraint is needed",
      "constraint_type": "preventive|detective|corrective|compensating",
      "enforcement_level": "mandatory|recommended|optional",
      "addresses_hazards": ["H-1", "H-2"],
      "prevents_losses": ["L-1"],
      "mission_impact_if_violated": {{
        "losses_enabled": ["L-1", "L-2"],
        "capability_degradation": "Description of impact"
      }}
    }}
  ]
}}

Ensure complete coverage - every hazard should have at least one constraint addressing it."""
        
        return prompt
    
    def _parse_constraint_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured constraints"""
        try:
            # Extract JSON from response
            data = self._extract_json(response)
            constraints = data.get('constraints', [])
            
            # Validate and clean each constraint
            validated_constraints = []
            for constraint in constraints:
                if self._validate_constraint(constraint):
                    validated_constraints.append(constraint)
            
            return validated_constraints
            
        except Exception as e:
            self.logger.error(f"Failed to parse constraint response: {e}")
            return []
    
    def _validate_constraint(self, constraint: Dict[str, Any]) -> bool:
        """Validate a single constraint has required fields"""
        required_fields = ['identifier', 'constraint_statement', 'constraint_type']
        
        for field in required_fields:
            if field not in constraint:
                self.logger.warning(f"Constraint missing required field: {field}")
                return False
        
        # Validate constraint type
        valid_types = ['preventive', 'detective', 'corrective', 'compensating']
        if constraint['constraint_type'] not in valid_types:
            self.logger.warning(f"Invalid constraint type: {constraint['constraint_type']}")
            return False
        
        # Validate enforcement level
        valid_levels = ['mandatory', 'recommended', 'optional']
        enforcement = constraint.get('enforcement_level', 'recommended')
        if enforcement not in valid_levels:
            constraint['enforcement_level'] = 'recommended'
        
        return True
    
    def _generate_mappings(self, constraints: List[Dict], hazards: List[Dict]) -> List[Dict]:
        """Generate constraint-hazard mappings"""
        mappings = []
        hazard_ids = {h['identifier'] for h in hazards}
        
        for constraint in constraints:
            hazard_list = constraint.get('addresses_hazards', [])
            
            for hazard_id in hazard_list:
                if hazard_id in hazard_ids:
                    # Determine relationship type based on constraint type
                    if constraint['constraint_type'] == 'preventive':
                        relationship = 'eliminates'
                    elif constraint['constraint_type'] == 'detective':
                        relationship = 'detects'
                    elif constraint['constraint_type'] == 'corrective':
                        relationship = 'reduces'
                    else:  # compensating
                        relationship = 'transfers'
                    
                    mapping = {
                        "constraint_id": constraint['identifier'],
                        "hazard_id": hazard_id,
                        "relationship_type": relationship
                    }
                    mappings.append(mapping)
        
        return mappings
    
    def _create_summary(self, constraints: List[Dict], mappings: List[Dict]) -> Dict:
        """Create summary statistics"""
        type_counts = {
            'preventive': 0,
            'detective': 0,
            'corrective': 0,
            'compensating': 0
        }
        
        for constraint in constraints:
            c_type = constraint.get('constraint_type', 'preventive')
            if c_type in type_counts:
                type_counts[c_type] += 1
        
        return {
            "types": type_counts,
            "total_mappings": len(mappings)
        }
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response"""
        # Try to find JSON in the response
        import re
        
        # Look for JSON between ```json and ``` or just {...}
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No JSON found in response")
        
        return json.loads(json_str)