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
    
    def get_agent_type(self) -> str:
        return "system_boundaries"
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate that content maintains Step 1 abstraction level"""
        # Check for implementation details
        if self.is_implementation_detail(content):
            return False
        # Boundaries should be at mission level
        return True
    
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
        
        # Generate comprehensive boundary analysis
        boundary_analysis = self._generate_boundary_analysis(boundaries, relationships, summary)
        
        # Extract the primary system boundary (first one or create one) and enhance it
        primary_boundary = boundaries[0] if boundaries else self._create_default_boundary(system_description)
        
        # Add required validation fields to the primary boundary
        primary_boundary = self._enhance_primary_boundary(primary_boundary, boundary_analysis)
        
        return {
            "system_boundaries": boundaries,
            "system_boundary": primary_boundary,
            "boundary_analysis": boundary_analysis,
            "boundary_relationships": relationships,
            "boundary_summary": summary,
            "cognitive_style": self.cognitive_style.value,
            "analysis_metadata": {
                "agent_type": self.get_agent_type(),
                "analysis_id": self.analysis_id,
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

CRITICAL: You MUST provide SPECIFIC, CONCRETE lists of actual system components, not abstract categories.

Define boundaries from these perspectives:

1. SYSTEM SCOPE BOUNDARY
   INSIDE (we control): List SPECIFIC components like:
   - "Core application server"
   - "Primary database" 
   - "Processing engine"
   - "API gateway"
   
   OUTSIDE (we depend on): List SPECIFIC external systems like:
   - "User devices"
   - "External service networks"
   - "Third-party APIs"
   - "Cloud infrastructure"
   
   INTERFACES: List SPECIFIC connection points like:
   - "RESTful API for mobile app"
   - "SFTP connection to regulatory reporting"
   - "OAuth2 integration with identity provider"

2. TRUST BOUNDARIES
   List SPECIFIC points where trust changes:
   - "Between client app and API gateway"
   - "Between application server and external services"
   - "Between database and backup storage"

3. RESPONSIBILITY BOUNDARIES
   List SPECIFIC areas of responsibility:
   - WE OWN: "Customer account data integrity"
   - THEY OWN: "Mobile device security"
   - SHARED: "Transaction dispute resolution process"

4. DATA GOVERNANCE BOUNDARIES
   List SPECIFIC data transitions:
   - "Customer PII moves from our database to credit bureau"
   - "Transaction data shared with regulatory authority"
   - "Account data replicated to disaster recovery site"

For each boundary, you MUST:
- List ACTUAL component names, not categories
- Be SPECIFIC about technologies and systems
- Name REAL external dependencies
- Identify CONCRETE interfaces

MINIMUM REQUIREMENTS (empty boundaries will be rejected):
- System Scope: At least 3 INSIDE components, 3 OUTSIDE systems, 2 INTERFACES
- Trust Boundaries: At least 3 specific trust transition points with concrete elements
- Responsibility: At least 2 items each for WE OWN, THEY OWN, SHARED (6 total minimum)
- Data Governance: At least 3 specific data transition scenarios with concrete elements

IMPORTANT: ALL 4 boundary types MUST have sufficient elements. Boundaries without elements will cause the analysis to fail.

Generate boundaries in this JSON format:
{{
  "boundaries": [
    {{
      "boundary_name": "System Scope",
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
        """Validate a boundary has required fields and concrete elements"""
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
        
        # Validate minimum element requirements
        elements = boundary.get('elements', [])
        boundary_type = boundary['boundary_type']
        
        if boundary_type == 'system_scope':
            inside_count = sum(1 for e in elements if e.get('position') == 'inside')
            outside_count = sum(1 for e in elements if e.get('position') == 'outside')
            interface_count = sum(1 for e in elements if e.get('position') == 'interface')
            
            if inside_count < 3:
                self.logger.warning(f"System scope boundary needs at least 3 INSIDE elements, found {inside_count}")
                return False
            if outside_count < 3:
                self.logger.warning(f"System scope boundary needs at least 3 OUTSIDE elements, found {outside_count}")
                return False
            if interface_count < 2:
                self.logger.warning(f"System scope boundary needs at least 2 INTERFACE elements, found {interface_count}")
                return False
                
        elif boundary_type == 'trust' and len(elements) < 3:
            self.logger.warning(f"Trust boundary needs at least 3 elements, found {len(elements)}")
            return False
            
        elif boundary_type == 'responsibility':
            we_own_count = sum(1 for e in elements if 'WE OWN' in e.get('element_name', ''))
            they_own_count = sum(1 for e in elements if 'THEY OWN' in e.get('element_name', ''))
            shared_count = sum(1 for e in elements if 'SHARED' in e.get('element_name', ''))
            
            if we_own_count < 2:
                self.logger.warning(f"Responsibility boundary needs at least 2 WE OWN elements, found {we_own_count}")
                return False
            if they_own_count < 2:
                self.logger.warning(f"Responsibility boundary needs at least 2 THEY OWN elements, found {they_own_count}")
                return False
            if shared_count < 2:
                self.logger.warning(f"Responsibility boundary needs at least 2 SHARED elements, found {shared_count}")
                return False
            
        elif boundary_type == 'data_governance' and len(elements) < 3:
            self.logger.warning(f"Data governance boundary needs at least 3 elements, found {len(elements)}")
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
    
    def _generate_boundary_analysis(self, boundaries: List[Dict], relationships: List[Dict], summary: Dict) -> Dict[str, Any]:
        """Generate comprehensive boundary analysis"""
        
        # Extract key elements across all boundaries
        primary_system = set()
        system_elements = set() 
        external_entities = set()
        interfaces = []
        assumptions = []
        exclusions = []
        
        for boundary in boundaries:
            elements = boundary.get('elements', [])
            for element in elements:
                name = element.get('element_name', '')
                position = element.get('position', '')
                
                if position == 'inside':
                    if boundary.get('boundary_type') == 'system_scope':
                        primary_system.add(name)
                    system_elements.add(name)
                elif position == 'outside':
                    external_entities.add(name)
                elif position == 'interface':
                    interfaces.append({
                        'name': name,
                        'boundary_type': boundary.get('boundary_type'),
                        'assumptions': element.get('assumptions', {}),
                        'constraints': element.get('constraints', {})
                    })
                
                # Collect assumptions and exclusions
                if 'assumptions' in element:
                    for key, value in element['assumptions'].items():
                        assumptions.append(f"{name}: {value}")
                        
                if 'constraints' in element:
                    for key, value in element['constraints'].items():
                        exclusions.append(f"{name}: {value}")
        
        return {
            "primary_system": list(primary_system),
            "system_elements": list(system_elements),
            "external_entities": list(external_entities),
            "interfaces": interfaces,
            "assumptions": assumptions,
            "exclusions": exclusions,
            "boundary_coverage": {
                "total_boundaries_defined": len(boundaries),
                "critical_interfaces_identified": len(interfaces),
                "external_dependencies": len(external_entities)
            }
        }
    
    def _create_default_boundary(self, system_description: str) -> Dict[str, Any]:
        """Create a default system boundary if none exists"""
        return {
            "boundary_name": "System Scope Boundary",
            "boundary_type": "system_scope", 
            "description": "Primary system boundary defining what is within system control",
            "definition_criteria": {
                "criterion1": "Components directly controlled and operated by the system",
                "criterion2": "External dependencies and interfaces outside system control"
            },
            "elements": [
                {
                    "element_name": "Core System",
                    "element_type": "component",
                    "position": "inside",
                    "assumptions": {"reliable": "Assumed to be under direct system control"},
                    "constraints": {"dependency": "Depends on external services for some operations"}
                }
            ]
        }
    
    def _enhance_primary_boundary(self, primary_boundary: Dict[str, Any], boundary_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance primary boundary with required validation fields"""
        enhanced_boundary = primary_boundary.copy()
        
        # Add required fields from boundary analysis
        enhanced_boundary["primary_system"] = boundary_analysis.get("primary_system", [])
        enhanced_boundary["system_elements"] = boundary_analysis.get("system_elements", [])
        enhanced_boundary["external_entities"] = boundary_analysis.get("external_entities", [])
        enhanced_boundary["interfaces"] = boundary_analysis.get("interfaces", [])
        enhanced_boundary["assumptions"] = boundary_analysis.get("assumptions", [])
        enhanced_boundary["exclusions"] = boundary_analysis.get("exclusions", [])
        
        return enhanced_boundary