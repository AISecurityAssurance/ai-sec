"""
Hazard State Identification Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List, Optional, Tuple
import re
import json
from uuid import uuid4

from .base_step1 import BaseStep1Agent, CognitiveStyle


class HazardIdentificationAgent(BaseStep1Agent):
    """
    Identifies hazardous system states that could lead to losses
    
    Responsibilities:
    - Identify system states (not actions)
    - Map states to potential losses
    - Analyze temporal aspects
    - Consider environmental factors
    """
    
    def get_agent_type(self) -> str:
        return "hazard_identification"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and analyze hazardous system states"""
        await self.log_activity("Starting hazard identification")
        
        system_description = context.get('system_description', '')
        prior_results = await self.get_prior_results(['mission_analyst', 'loss_identification'])
        
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        mission_context = prior_results.get('mission_analyst', {}).get('mission_context', {})
        
        # Always use LLM for analysis
        hazards = await self._identify_hazards_with_llm(system_description, losses, mission_context)
        
        # Assign identifiers
        for i, hazard in enumerate(hazards):
            hazard['identifier'] = f"H-{i+1}"
        
        # Create hazard-loss mappings using LLM
        mappings = await self._create_hazard_loss_mappings_with_llm(hazards, losses)
        
        # Analyze temporal exposure
        temporal_analysis = await self._analyze_temporal_exposure(hazards)
        
        # Analyze environmental factors
        environmental_analysis = await self._analyze_environmental_factors(hazards, mission_context)
        
        results = {
            "hazards": hazards,
            "hazard_count": len(hazards),
            "hazard_categories": self._summarize_categories(hazards),
            "hazard_loss_mappings": mappings,
            "temporal_analysis": temporal_analysis,
            "environmental_analysis": environmental_analysis,
            "coverage_analysis": await self._analyze_loss_coverage(hazards, losses, mappings),
            "cognitive_style": self.cognitive_style.value
        }
        
        await self.save_results(results)
        await self.log_activity("Completed hazard identification", {
            "hazard_count": len(hazards),
            "mapping_count": len(mappings)
        })
        
        return results
    
    async def _create_hazard_loss_mappings_with_llm(self, hazards: List[Dict[str, Any]], 
                                                   losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use LLM to create mappings between hazards and losses"""
        # Get cognitive style prompt modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Format hazards and losses for prompt
        hazards_summary = "\n".join([f"- {h['identifier']}: {h['description']} (Category: {h['hazard_category']})" for h in hazards])
        losses_summary = "\n".join([f"- {l['identifier']}: {l['description']} (Category: {l['loss_category']})" for l in losses])
        
        # Build the prompt
        prompt = f"""{style_modifier}

You are analyzing relationships between hazards and losses in STPA-Sec Step 1.

Hazards (System States):
{hazards_summary}

Losses (Unacceptable Outcomes):
{losses_summary}

Map each hazard to the losses it could lead to. Consider:
1. Direct relationships where the hazard directly causes the loss
2. Conditional relationships where additional factors are needed
3. Indirect relationships where the hazard contributes to conditions enabling the loss

For each meaningful mapping, provide:
- The hazard and loss being mapped
- Relationship strength (direct, conditional, indirect)
- Rationale explaining the connection
- Enabling conditions that must be present

Provide your response as a JSON array of mapping objects:
[
  {{
    "hazard_id": "H-X",
    "loss_id": "L-Y",
    "relationship_strength": "direct|conditional|indirect",
    "rationale": "Explanation of how this hazard leads to this loss",
    "conditions": ["condition1", "condition2"]
  }}
]

Only include mappings that are meaningful for risk analysis. Avoid tenuous connections."""
        
        try:
            # Call LLM
            response = await self.call_llm(prompt)
            
            # Parse JSON response
            content = response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            mappings = json.loads(content)
            
            # Add UUIDs to each mapping
            for mapping in mappings:
                mapping['id'] = str(uuid4())
            
            return mappings
            
        except Exception as e:
            await self.log_activity(f"LLM hazard-loss mapping failed: {e}", {"error": str(e)})
            # Return empty list on failure
            return []
    
    async def _analyze_temporal_exposure(self, hazards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal aspects of hazards"""
        analysis = {
            "always_present": [],
            "periodic": [],
            "conditional": [],
            "coverage_gaps": []
        }
        
        for hazard in hazards:
            temporal = hazard.get('temporal_nature', {})
            existence = temporal.get('existence', 'always')
            
            if existence == 'always':
                analysis['always_present'].append({
                    "hazard_id": hazard['identifier'],
                    "description": hazard['description']
                })
            elif existence == 'periodic':
                analysis['periodic'].append({
                    "hazard_id": hazard['identifier'],
                    "description": hazard['description'],
                    "when": temporal.get('when_present', 'unspecified')
                })
            else:
                analysis['conditional'].append({
                    "hazard_id": hazard['identifier'],
                    "description": hazard['description'],
                    "conditions": temporal.get('conditions', [])
                })
        
        # Identify coverage gaps
        if analysis['periodic']:
            analysis['coverage_gaps'].append({
                "gap_type": "temporal",
                "description": "Periodic hazards create vulnerability windows",
                "affected_hazards": [h['hazard_id'] for h in analysis['periodic']]
            })
        
        return analysis
    
    async def _analyze_environmental_factors(self, hazards: List[Dict[str, Any]], 
                                           mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental factors affecting hazards"""
        analysis = {
            "operational_sensitivity": {},
            "threat_sensitivity": {},
            "combined_risk_scenarios": []
        }
        
        for hazard in hazards:
            env_factors = hazard.get('environmental_factors', {})
            
            # Operational sensitivity
            ops_conditions = env_factors.get('operational_conditions', {})
            if ops_conditions:
                worst_case = max(ops_conditions.values(), 
                               key=lambda x: self._severity_score(x.get('impact', 'low')))
                analysis['operational_sensitivity'][hazard['identifier']] = {
                    "worst_case_condition": list(ops_conditions.keys())[
                        list(ops_conditions.values()).index(worst_case)
                    ],
                    "impact": worst_case.get('impact', 'unknown')
                }
            
            # Threat sensitivity
            threat_conditions = env_factors.get('threat_conditions', {})
            if threat_conditions:
                analysis['threat_sensitivity'][hazard['identifier']] = {
                    "escalation_pattern": self._analyze_threat_escalation(threat_conditions)
                }
        
        # Combined risk scenarios
        high_risk_hazards = [
            h_id for h_id, sens in analysis['operational_sensitivity'].items()
            if sens['impact'] in ['high', 'catastrophic']
        ]
        
        if high_risk_hazards:
            analysis['combined_risk_scenarios'].append({
                "scenario": "Multiple high-impact hazards under stress",
                "hazards": high_risk_hazards,
                "risk_level": "extreme"
            })
        
        return analysis
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score"""
        scores = {
            "low": 1,
            "moderate": 2,
            "high": 3,
            "catastrophic": 4
        }
        return scores.get(severity.lower(), 0)
    
    def _analyze_threat_escalation(self, threat_conditions: Dict[str, Any]) -> str:
        """Analyze how threats escalate"""
        if 'severe' in threat_conditions:
            severe = threat_conditions['severe']
            if 'overwhelmed' in str(severe).lower():
                return "System degrades catastrophically under severe threats"
            elif 'compromised' in str(severe).lower():
                return "System integrity fails under severe threats"
        
        return "System shows progressive degradation with threat escalation"
    
    async def _analyze_loss_coverage(self, hazards: List[Dict[str, Any]], 
                                   losses: List[Dict[str, Any]], 
                                   mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well hazards cover identified losses"""
        coverage = {
            "covered_losses": [],
            "uncovered_losses": [],
            "coverage_percentage": 0,
            "loss_hazard_ratio": {}
        }
        
        # Find covered losses
        covered_loss_set = set()
        for mapping in mappings:
            covered_loss_set.add(mapping['loss_id'])
        coverage['covered_losses'] = list(covered_loss_set)
        
        # Find uncovered losses
        all_loss_ids = {loss['identifier'] for loss in losses}
        uncovered_ids = all_loss_ids - covered_loss_set
        coverage['uncovered_losses'] = list(uncovered_ids)
        
        # Calculate coverage
        if losses:
            coverage['coverage_percentage'] = (
                len(covered_loss_set) / len(losses) * 100
            )
        
        # Calculate loss-hazard ratio
        for loss in losses:
            hazard_count = sum(1 for m in mappings if m['loss_id'] == loss['identifier'])
            coverage['loss_hazard_ratio'][loss['identifier']] = hazard_count
        
        return coverage
    
    def _summarize_categories(self, hazards: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize hazard categories"""
        categories = {}
        for hazard in hazards:
            category = hazard['hazard_category']
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    
    async def _identify_hazards_with_llm(self, description: str, losses: List[Dict[str, Any]], 
                                        mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to identify hazards based on cognitive style"""
        # Get cognitive style prompt modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Format losses for prompt
        losses_summary = "\n".join([f"- {loss['identifier']}: {loss['description']}" for loss in losses[:10]])
        
        # Build the prompt
        prompt = f"""{style_modifier}

You are a security analyst performing STPA-Sec Step 1 hazard identification.

System Description:
{description}

Identified Losses:
{losses_summary}

Mission Context:
{json.dumps(mission_context, indent=2)}

Identify hazardous SYSTEM STATES that could lead to the identified losses.

CRITICAL GUIDANCE FOR HAZARD WORDING:
✓ CORRECT Hazard Format: "System operates in a state where [dangerous condition exists]"
✗ WRONG Format: "System operates without [missing control]" or descriptions of attacks/exploits

Examples:
✓ CORRECT: "System operates with unverified user identities for sensitive operations"
✗ WRONG: "System operates without multi-factor authentication"

✓ CORRECT: "System operates with corrupted operational data"
✗ WRONG: "System operates without data validation"

✓ CORRECT: "System operates in a state where malicious activity remains undetected"
✗ WRONG: "System operates without sufficient monitoring"

For each hazard:
1. Describe what dangerous condition EXISTS (not what's missing)
2. Use positive state language: "with", "in a state where", "while maintaining"
3. NEVER use negative language: "without", "missing", "lack of", "absence of"
4. Focus on the dangerous system condition, NOT the control that would prevent it
5. Categorize as: integrity_compromised, confidentiality_breached, availability_degraded, capability_loss, non_compliance, or mission_degraded
6. Identify which system property is affected (MUST be one of: data_integrity, data_protection, service_availability, regulatory_compliance, operational_capability, mission_effectiveness)
7. Assess environmental factors (operational conditions, threat conditions)
8. Describe temporal nature (always present, periodic, conditional)

Provide your response as a JSON array of hazard objects with the following structure:
[
  {{
    "description": "System operates with/in/without... (state description)",
    "hazard_category": "integrity_compromised|confidentiality_breached|availability_degraded|capability_loss|non_compliance|mission_degraded",
    "affected_system_property": "property name",
    "environmental_factors": {{
      "operational_conditions": {{
        "normal": {{"impact": "low|moderate|high", "likelihood": "rare|possible|likely"}},
        "degraded": {{"impact": "low|moderate|high", "likelihood": "rare|possible|likely"}},
        "emergency": {{"impact": "low|moderate|high", "likelihood": "rare|possible|likely"}}
      }},
      "threat_conditions": {{
        "benign": {{"impact": "minimal", "detection": "easy"}},
        "moderate": {{"impact": "moderate", "detection": "moderate"}},
        "severe": {{"impact": "high", "detection": "hard"}}
      }}
    }},
    "temporal_nature": {{
      "existence": "always|periodic|conditional",
      "when_present": "description of when hazard exists",
      "duration": "continuous|intermittent|transient"
    }}
  }}
]

IMPORTANT: 
- Focus on system STATES, not actions or attack methods
- Use state-based language (operates, exists in, maintains, etc.)
- Each hazard should clearly relate to one or more identified losses

HAZARD CATEGORY GUIDE - Match hazards to their PRIMARY concern:
- integrity_compromised: System processes incorrect, tampered, or invalid data
- confidentiality_breached: System exposes or leaks protected information
- availability_degraded: System cannot provide expected services when needed
- capability_loss: System cannot perform a required function (different from availability - function is broken, not just unavailable)
- non_compliance: System violates regulatory or policy requirements
- mission_degraded: System cannot achieve its intended purpose effectively

Examples:
- "System operates with corrupted critical data" → integrity_compromised
- "System operates in a state where sensitive data is exposed" → confidentiality_breached
- "System operates with insufficient resources to handle requests" → availability_degraded
- "System operates without ability to detect anomalies" → capability_loss

HAZARD IDENTIFICATION CHECKLIST - Aim for 12-15 hazards covering these areas:
□ Authentication & Authorization (user identity verification, session management)
□ Data Protection (encryption state, access control, data retention)
□ System Integrity (data accuracy, data consistency, audit trails)
□ Availability (resource constraints, dependencies, performance degradation)
□ Compliance (regulatory requirements, audit capabilities, reporting)
□ Operational Security (segregation of duties, insider threats, privileged access)
□ External Interfaces (API security, third-party integrations, data exchanges)
□ Resilience (backup/recovery states, failover capabilities, incident response)

MINIMUM REQUIREMENT: Identify at least 12 hazards for comprehensive coverage. Fewer than 12 hazards will be considered incomplete."""
        
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
            
            hazards = json.loads(content)
            
            # Validate structure
            if not isinstance(hazards, list):
                raise ValueError("Response must be a JSON array")
            
            return hazards
            
        except Exception as e:
            await self.log_activity(f"LLM hazard identification failed: {e}", {"error": str(e)})
            # Re-raise the exception - analysis should fail if LLM fails
            raise
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate hazard maintains system state abstraction"""
        content_lower = content.lower()
        
        # Hazards must NOT use negative language
        negative_words = ["without", "missing", "lack of", "absence of", "no ", "not "]
        if any(word in content_lower for word in negative_words):
            return False
        
        # Hazards must describe states, not actions
        action_words = ["attack", "exploit", "injection", "overflow", "bypass"]
        if any(word in content_lower for word in action_words):
            return False
        
        # Must use positive state language
        state_indicators = ["operates", "state", "condition", "mode", "with", "in a state where", "maintains"]
        has_state_language = any(word in content_lower for word in state_indicators)
        
        return has_state_language and not self.is_implementation_detail(content)