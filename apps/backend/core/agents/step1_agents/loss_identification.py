"""
Loss Identification Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List, Optional
import re
import json
from uuid import uuid4

from .base_step1 import BaseStep1Agent, CognitiveStyle


class LossIdentificationAgent(BaseStep1Agent):
    """
    Identifies and analyzes losses (unacceptable outcomes)
    
    Responsibilities:
    - Identify mission-level losses
    - Categorize losses appropriately
    - Assess severity at mission level
    - Map capability losses
    - Identify loss dependencies
    """
    
    def get_agent_type(self) -> str:
        return "loss_identification"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and analyze losses"""
        await self.log_activity("Starting loss identification")
        
        system_description = context.get('system_description', '')
        mission_results = await self.get_prior_results(['mission_analyst'])
        
        # Always use LLM for analysis
        losses = await self._identify_losses_with_llm(system_description, mission_results)
        
        # Assign identifiers
        for i, loss in enumerate(losses):
            loss['identifier'] = f"L-{i+1}"
        
        # Identify loss dependencies using LLM
        dependencies = await self._identify_loss_dependencies_with_llm(losses)
        
        # Create loss cascade analysis
        cascade_analysis = await self._analyze_loss_cascades(losses, dependencies)
        
        results = {
            "losses": losses,
            "loss_count": len(losses),
            "loss_categories": self._summarize_categories(losses),
            "dependencies": dependencies,
            "cascade_analysis": cascade_analysis,
            "severity_distribution": self._analyze_severity_distribution(losses),
            "cognitive_style": self.cognitive_style.value
        }
        
        await self.save_results(results)
        await self.log_activity("Completed loss identification", {
            "loss_count": len(losses),
            "dependency_count": len(dependencies)
        })
        
        return results
    
    async def _identify_loss_dependencies_with_llm(self, losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use LLM to identify dependencies between losses"""
        # Get cognitive style prompt modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Format losses for prompt
        losses_summary = "\n".join([f"- {loss['identifier']}: {loss['description']} (Category: {loss['loss_category']})" for loss in losses])
        
        # Build the prompt
        prompt = f"""{style_modifier}

You are analyzing dependencies between identified losses in STPA-Sec Step 1.

Identified Losses:
{losses_summary}

Analyze relationships between these losses to identify:
1. Which losses trigger or enable other losses
2. The strength and timing of these dependencies
3. Cascading effects through the system

For each dependency, provide:
- Primary loss that triggers/enables the dependent loss
- Type of dependency (triggers, enables, amplifies)
- Strength (certain, likely, possible)
- Time relationship (immediate, delayed, concurrent)
- Rationale for the dependency

Provide your response as a JSON array of dependency objects:
[
  {{
    "primary_loss_id": "L-X",
    "dependent_loss_id": "L-Y",
    "dependency_type": "triggers|enables|amplifies",
    "dependency_strength": "certain|likely|possible",
    "time_relationship": {{
      "sequence": "immediate|delayed|concurrent",
      "typical_delay": "description of timing",
      "persistence": "sustained|temporary|variable"
    }},
    "rationale": "Explanation of why this dependency exists"
  }}
]

Focus on meaningful dependencies that affect risk analysis and mitigation strategies."""
        
        try:
            # Call LLM
            response = await self.call_llm(prompt)
            
            # Parse JSON response
            content = response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            dependencies = json.loads(content)
            
            # Add UUIDs to each dependency
            for dep in dependencies:
                dep['id'] = str(uuid4())
            
            return dependencies
            
        except Exception as e:
            await self.log_activity(f"LLM dependency analysis failed: {e}", {"error": str(e)})
            # Return empty list on failure - don't fall back to hardcoded
            return []
    
    async def _analyze_loss_cascades(self, losses: List[Dict[str, Any]], 
                                    dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze potential loss cascade chains"""
        cascades = {
            "primary_losses": [],
            "cascade_chains": [],
            "max_cascade_depth": 0
        }
        
        # Identify primary losses (no incoming dependencies)
        dependent_loss_ids = {dep['dependent_loss_id'] for dep in dependencies}
        primary_losses = [loss for loss in losses 
                         if loss['identifier'] not in dependent_loss_ids]
        cascades['primary_losses'] = [loss['identifier'] for loss in primary_losses]
        
        # Build cascade chains
        for primary_loss in primary_losses:
            chain = self._build_cascade_chain(primary_loss['identifier'], dependencies, losses)
            if len(chain) > 1:
                cascades['cascade_chains'].append({
                    "chain": chain,
                    "trigger": primary_loss['identifier'],
                    "terminal_losses": chain[-1:],
                    "chain_length": len(chain)
                })
        
        # Calculate max cascade depth
        if cascades['cascade_chains']:
            cascades['max_cascade_depth'] = max(
                chain['chain_length'] for chain in cascades['cascade_chains']
            )
        
        return cascades
    
    def _build_cascade_chain(self, loss_id: str, dependencies: List[Dict[str, Any]], 
                            losses: List[Dict[str, Any]], visited: Optional[set] = None) -> List[str]:
        """Build a cascade chain starting from a loss"""
        if visited is None:
            visited = set()
            
        if loss_id in visited:
            return []
            
        visited.add(loss_id)
        chain = [loss_id]
        
        # Find dependent losses
        for dep in dependencies:
            if dep['primary_loss_id'] == loss_id:
                sub_chain = self._build_cascade_chain(
                    dep['dependent_loss_id'], dependencies, losses, visited
                )
                if sub_chain:
                    chain.extend(sub_chain)
        
        return chain
    
    def _summarize_categories(self, losses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize loss categories"""
        categories = {}
        for loss in losses:
            category = loss['loss_category']
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _analyze_severity_distribution(self, losses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze severity distribution"""
        distribution = {
            "catastrophic": 0,
            "major": 0,
            "moderate": 0,
            "minor": 0
        }
        
        for loss in losses:
            magnitude = loss['severity_classification']['magnitude']
            if magnitude in distribution:
                distribution[magnitude] += 1
                
        return distribution
    
    
    async def _identify_losses_with_llm(self, description: str, mission_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to identify losses based on cognitive style"""
        # Get cognitive style prompt modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Build the prompt
        prompt = f"""{style_modifier}

You are a security analyst performing STPA-Sec Step 1 loss identification.

System Description:
{description}

Mission Context:
{json.dumps(mission_results.get('mission_analyst', {}).get('mission_context', {}), indent=2)}

Identify all potential losses (unacceptable outcomes) for this system. 

CRITICAL GUIDANCE FOR LOSS WORDING:
✓ CORRECT Loss Format: "Loss of [something valuable]" with brief context about the nature
✗ WRONG Format: Descriptions of specific attacks or implementation details

Examples:
✓ GOOD: "Loss of critical system capability affecting primary mission"
✗ BAD: "Loss due to SQL injection attack"

✓ GOOD: "Loss of service availability during essential operations"  
✗ BAD: "System downtime due to DDoS attack"

✓ GOOD: "Loss of regulatory compliance resulting in penalties and sanctions"
✗ BAD: "Non-compliance because of missing encryption"

CONTEXT GUIDELINES:
- Include brief context about the NATURE of the loss (not the attack method)
- Context helps stakeholders understand impact without prescribing solutions
- Keep focus on the loss itself, with context as clarification

For each loss:
1. Describe the IMPACT or CONSEQUENCE (what is lost/harmed), NOT the attack scenario or event
2. Use phrases like "Loss of", "Damage to", "Harm to", "Compromise of"
3. Categorize using ONLY these categories: life, injury, financial, environmental, mission, reputation, privacy, regulatory
4. Assess severity with magnitude (catastrophic/major/moderate/minor), scope, duration, reversibility, and detection difficulty
5. Identify mission impacts including capability loss, cascading effects, and stakeholder harm

Provide your response as a JSON array of loss objects with the following structure:
[
  {{
    "description": "Loss description",
    "loss_category": "category",
    "severity_classification": {{
      "magnitude": "catastrophic|major|moderate|minor",
      "scope": "enterprise_wide|organization_wide|business_unit|customer_wide|market_wide|mission_wide",
      "duration": "permanent|long_term|medium_term|short_term|variable",
      "reversibility": "impossible|very_difficult|difficult|possible|easy",
      "detection_difficulty": "hard|moderate|easy"
    }},
    "mission_impact": {{
      "primary_capability_loss": ["capability1", "capability2"],
      "cascading_effects": ["effect1", "effect2"],
      "stakeholder_harm": {{
        "stakeholder_name": {{
          "type": "harm_type",
          "severity": "catastrophic|major|moderate|minor"
        }}
      }}
    }}
  }}
]

IMPORTANT: 
1. Focus on outcomes and consequences, not attack methods or vulnerabilities.
2. Use ONLY these loss categories: life, injury, financial, environmental, mission, reputation, privacy, regulatory
3. Do NOT use "security" as a loss category - map security concerns to one of the allowed categories (e.g., financial for theft, privacy for data breaches).

VALIDATION: Check each loss before including it:
- Does it describe something valuable being lost/harmed?
- Could you put "We have experienced..." in front of it and have it make sense?
- Is it distinct from other losses (not just a subset or more specific version)?
- Does it describe a loss, NOT a missing control or failure mode?

Examples of validation:
✓ "Loss of critical data integrity" - Yes, we lost something valuable
✗ "Loss of encryption" - No, this is a control failing, not a loss
✗ "Loss of integration with external service" - No, this is a failure event, not a loss

REDUNDANCY CHECK:
- Don't include losses that are just specific versions of broader losses
- Example: If you have "Loss of data confidentiality", don't also include "Loss of encryption for data"
- Combine similar losses into single, comprehensive statements

COMPLETENESS REQUIREMENTS:
□ Identify 5-8 distinct losses minimum
□ Cover multiple loss categories (financial, privacy, mission, reputation, regulatory)
□ Consider both direct and indirect losses
□ Include losses affecting different stakeholder groups
□ Address both immediate and long-term consequences

COMPLETENESS VERIFICATION:
After identifying losses, verify:
1. Does every major stakeholder have at least one relevant loss?
2. Are all critical system functions represented in potential losses?
3. Have you considered losses from system unavailability AND misuse?
4. Are there losses that could cascade to create other losses?
5. Do the losses reflect the system's actual mission and purpose?"""
        
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
            
            losses = json.loads(content)
            
            # Validate structure
            if not isinstance(losses, list):
                raise ValueError("Response must be a JSON array")
            
            return losses
            
        except Exception as e:
            await self.log_activity(f"LLM loss identification failed: {e}", {"error": str(e)})
            # Re-raise the exception - analysis should fail if LLM fails
            raise
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate loss maintains mission-level abstraction"""
        # Losses should describe outcomes, not mechanisms
        mechanism_words = ["attack", "exploit", "vulnerability", "breach", "hack"]
        content_lower = content.lower()
        
        if any(word in content_lower for word in mechanism_words):
            return False
            
        return not self.is_implementation_detail(content)