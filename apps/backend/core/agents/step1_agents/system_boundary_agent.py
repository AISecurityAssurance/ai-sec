"""
System Boundary Agent for STPA-Sec Step 1
Defines clear system boundaries from multiple perspectives
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_step1 import BaseStep1Agent, CognitiveStyle


class SystemBoundaryAgent(BaseStep1Agent):
    """Agent responsible for defining system boundaries"""
    
    def __init__(self, cognitive_style: CognitiveStyle = CognitiveStyle.BALANCED):
        super().__init__(cognitive_style)
        self.agent_type = "system_boundaries"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define system boundaries from multiple perspectives
        
        Args:
            context: Dictionary containing:
                - system_description: System being analyzed
                - stakeholders: List of identified stakeholders (optional)
                - mission: Mission analysis results (optional)
                
        Returns:
            Dictionary containing system boundaries and elements
        """
        system_description = context.get('system_description', '')
        stakeholders = context.get('stakeholders', [])
        mission = context.get('mission', {})
        
        # Generate prompt for boundary definition
        prompt = self._create_boundary_prompt(system_description, stakeholders, mission)
        
        # Call LLM with cognitive style modifier
        response = await self.call_llm(prompt)
        
        # Parse and structure the response
        boundaries = self._parse_boundary_response(response)
        
        # Generate boundary relationships
        relationships = self._identify_relationships(boundaries)
        
        # Create summary
        summary = self._create_summary(boundaries)
        
        return {
            "system_boundaries": boundaries,
            "boundary_relationships": relationships,
            "boundary_summary": summary,
            "cognitive_style": self.cognitive_style.value,
            "analysis_metadata": {
                "agent_type": self.agent_type,
                "analysis_id": context.get('analysis_id', 'unknown'),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0"
            }
        }
    
    def _create_boundary_prompt(self, system_description: str, 
                              stakeholders: List[Dict], mission: Dict) -> str:
        """Create prompt for boundary definition"""
        
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Format stakeholders if available
        stakeholder_text = ""
        if stakeholders:
            stakeholder_text = "\n\nSTAKEHOLDERS:\n" + "\n".join([
                f"- {s.get('name', 'Unknown')}: {s.get('description', '')}"
                for s in stakeholders
            ])
        
        prompt = f"""You are a security analyst performing STPA-Sec Step 1 analysis.
{style_modifier}

Define clear system boundaries for security analysis from multiple perspectives.

SYSTEM DESCRIPTION:
{system_description}
{stakeholder_text}

INSTRUCTIONS:
Define boundaries from these perspectives:

1. SYSTEM SCOPE BOUNDARY
   - What components/functions are inside our system (we control)
   - What is outside (we don't control but depend on)
   - What interfaces exist between inside and outside

2. TRUST BOUNDARIES
   - Where trust levels change
   - Where authentication/authorization is needed
   - Where data validation is critical

3. RESPONSIBILITY BOUNDARIES
   - What we are legally/contractually responsible for
   - What others are responsible for
   - Shared responsibilities (clearly defined)

4. DATA GOVERNANCE BOUNDARIES
   - Where data ownership changes
   - Where data protection requirements change
   - Where data classification changes

For each boundary, identify:
- Clear definition criteria
- Key elements (components, data, actors, interfaces)
- Position of each element (inside, outside, crossing, interface)
- Critical assumptions about external elements

Generate boundaries in this JSON format:
{{
  "boundaries": [
    {{
      "boundary_name": "Banking Platform System Scope",
      "boundary_type": "system_scope|trust|responsibility|data_governance",
      "description": "Clear description of what this boundary represents",
      "definition_criteria": {{
        "criterion1": "Description",
        "criterion2": "Description"
      }},
      "elements": [
        {{
          "element_name": "Component/Data/Actor name",
          "element_type": "component|actor|data|process|interface",
          "position": "inside|outside|crossing|interface",
          "assumptions": {{
            "key": "assumption description"
          }},
          "constraints": {{
            "key": "constraint description"
          }}
        }}
      ]
    }}
  ]
}}

Ensure all boundary types are covered and elements are clearly positioned."""
        
        return prompt
    
    def _parse_boundary_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured boundaries"""
        try:
            # Extract JSON from response
            data = self._extract_json(response)
            boundaries = data.get('boundaries', [])
            
            # Validate and clean each boundary
            validated_boundaries = []
            for boundary in boundaries:
                if self._validate_boundary(boundary):
                    validated_boundaries.append(boundary)
            
            return validated_boundaries
            
        except Exception as e:
            self.logger.error(f"Failed to parse boundary response: {e}")
            return []
    
    def _validate_boundary(self, boundary: Dict[str, Any]) -> bool:
        """Validate a boundary has required fields"""
        required_fields = ['boundary_name', 'boundary_type', 'description']
        
        for field in required_fields:
            if field not in boundary:
                self.logger.warning(f"Boundary missing required field: {field}")
                return False
        
        # Validate boundary type
        valid_types = ['system_scope', 'trust', 'responsibility', 'data_governance', 
                      'control', 'influence']
        if boundary['boundary_type'] not in valid_types:
            self.logger.warning(f"Invalid boundary type: {boundary['boundary_type']}")
            return False
        
        # Validate elements if present
        if 'elements' in boundary:
            valid_positions = ['inside', 'outside', 'crossing', 'interface']
            valid_element_types = ['component', 'actor', 'data', 'process', 'interface']
            
            for element in boundary['elements']:
                if element.get('position') not in valid_positions:
                    element['position'] = 'interface'  # Default
                if element.get('element_type') not in valid_element_types:
                    element['element_type'] = 'component'  # Default
        
        return True
    
    def _identify_relationships(self, boundaries: List[Dict]) -> List[Dict]:
        """Identify relationships between boundaries"""
        relationships = []
        
        # Simple heuristics for common relationships
        boundary_map = {b['boundary_name']: b for b in boundaries}
        
        for boundary in boundaries:
            # System scope usually contains trust boundaries
            if boundary['boundary_type'] == 'system_scope':
                for other in boundaries:
                    if other['boundary_type'] == 'trust':
                        relationships.append({
                            "parent_boundary": boundary['boundary_name'],
                            "child_boundary": other['boundary_name'],
                            "relationship_type": "contains"
                        })
            
            # Regulatory boundaries often overlap with data governance
            elif boundary['boundary_type'] == 'responsibility':
                for other in boundaries:
                    if other['boundary_type'] == 'data_governance':
                        relationships.append({
                            "parent_boundary": boundary['boundary_name'],
                            "child_boundary": other['boundary_name'],
                            "relationship_type": "overlaps"
                        })
        
        return relationships
    
    def _create_summary(self, boundaries: List[Dict]) -> Dict:
        """Create boundary summary statistics"""
        type_counts = {}
        total_elements = 0
        interface_count = 0
        external_dependencies = set()
        
        for boundary in boundaries:
            # Count boundary types
            b_type = boundary.get('boundary_type')
            type_counts[b_type] = type_counts.get(b_type, 0) + 1
            
            # Count elements
            elements = boundary.get('elements', [])
            total_elements += len(elements)
            
            for element in elements:
                if element.get('position') == 'interface':
                    interface_count += 1
                elif element.get('position') == 'outside':
                    external_dependencies.add(element.get('element_name'))
        
        return {
            "total_boundaries": len(boundaries),
            "boundary_types": type_counts,
            "total_elements": total_elements,
            "critical_interfaces": interface_count,
            "external_dependencies": len(external_dependencies)
        }
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response"""
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