"""
Base class for Step 2 STPA-Sec agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
import asyncpg
import json

from core.agents.step1_agents.base_step1 import CognitiveStyle
from typing import Dict, Any, Optional
from dataclasses import dataclass
from core.utils.prompt_saver import get_prompt_saver
from core.utils.json_parser import parse_llm_json


@dataclass
class AgentResult:
    """Result from a Step 2 agent"""
    agent_type: str
    success: bool
    data: Dict[str, Any]
    execution_time_ms: int
    metadata: Optional[Dict[str, Any]] = None
    
    def dict(self):
        """Convert to dictionary for storage"""
        return {
            'agent_type': self.agent_type,
            'success': self.success,
            'data': self.data,
            'execution_time_ms': self.execution_time_ms,
            'metadata': self.metadata or {}
        }


class BaseStep2Agent(ABC):
    """
    Base class for all Step 2 agents.
    Provides common functionality for control structure analysis.
    """
    
    def __init__(self, model_provider, db_connection: asyncpg.Connection, cognitive_style: CognitiveStyle = CognitiveStyle.BALANCED):
        self.model_provider = model_provider
        self.db_connection = db_connection
        self.cognitive_style = cognitive_style
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{self.agent_id[:8]}")
        
    async def load_step1_results(self, step1_analysis_id: str) -> Dict[str, Any]:
        """
        Load relevant Step 1 results for Step 2 analysis.
        Returns consolidated view of Step 1 outputs.
        """
        # Load Step 1 analysis metadata
        step1_analysis = await self.db_connection.fetchrow(
            "SELECT * FROM step1_analyses WHERE id = $1", 
            step1_analysis_id
        )
        if not step1_analysis:
            raise ValueError(f"Step 1 analysis {step1_analysis_id} not found")
            
        # Load key Step 1 results
        results = {
            'analysis_id': step1_analysis_id,
            'system_name': step1_analysis.get('name', 'Unknown System'),
            'mission_statement': await self._get_mission_statement(step1_analysis_id),
            'losses': await self._get_losses(step1_analysis_id),
            'hazards': await self._get_hazards(step1_analysis_id),
            'security_constraints': await self._get_security_constraints(step1_analysis_id),
            'stakeholders': await self._get_stakeholders(step1_analysis_id),
            'system_boundaries': await self._get_system_boundaries(step1_analysis_id)
        }
        
        return results
        
    async def _get_mission_statement(self, analysis_id: str) -> str:
        """Extract mission statement from Step 1 results."""
        query = """
        SELECT metadata->>'mission_statement' as mission_statement
        FROM step1_analyses
        WHERE id = $1
        """
        result = await self.db_connection.fetchrow(query, analysis_id)
        return result['mission_statement'] if result else ''
        
    async def _get_losses(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get losses from Step 1."""
        # Check which table exists (step1_losses for new schema, losses for old)
        has_step1_losses = await self.db_connection.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'step1_losses'
            )
        """)
        
        if has_step1_losses:
            # New schema with step1_losses table
            query = """
            SELECT id, identifier, loss_category as loss_type, description, 
                   COALESCE(severity_classification->>'stakeholder_impact', '') as stakeholder_impact
            FROM step1_losses
            WHERE analysis_id = $1
            ORDER BY identifier
            """
        else:
            # Old schema with losses table
            query = """
            SELECT id, description, 
                   COALESCE(properties->>'loss_type', 'safety') as loss_type,
                   COALESCE(properties->>'stakeholder_impact', '') as stakeholder_impact,
                   'L-' || SUBSTRING(id::text, 1, 8) as identifier
            FROM losses
            ORDER BY created_at
            """
        
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_hazards(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get hazards from Step 1."""
        # Check which table exists (step1_hazards for new schema, hazards for old)
        has_step1_hazards = await self.db_connection.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'step1_hazards'
            )
        """)
        
        if has_step1_hazards:
            # New schema with step1_hazards table
            query = """
            SELECT h.id, h.identifier, h.description, h.hazard_category,
                   h.affected_system_property,
                   COALESCE(h.environmental_factors->>'system_state', '') as system_state,
                   array_agg(DISTINCT hm.loss_id) as associated_losses
            FROM step1_hazards h
            LEFT JOIN hazard_loss_mappings hm ON h.id = hm.hazard_id
            WHERE h.analysis_id = $1
            GROUP BY h.id, h.identifier, h.description, h.hazard_category, 
                     h.affected_system_property, h.environmental_factors
            ORDER BY h.identifier
            """
        else:
            # Old schema without identifier
            query = """
            SELECT h.id, h.description, 
                   COALESCE(h.properties->>'system_state', '') as system_state,
                   'H-' || SUBSTRING(h.id::text, 1, 8) as identifier,
                   array_agg(DISTINCT hl.loss_id) as associated_losses
            FROM hazards h
            LEFT JOIN hazard_losses hl ON h.id = hl.hazard_id
            GROUP BY h.id, h.description, h.properties
            ORDER BY h.created_at
            """
        
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_security_constraints(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get security constraints from Step 1."""
        # Always use security_constraints table (both old and new schemas use this name)
        query = """
        SELECT sc.id, sc.identifier, sc.constraint_statement as constraint_text, sc.constraint_type,
               array_agg(DISTINCT chm.hazard_id) as mitigated_hazards
        FROM security_constraints sc
        LEFT JOIN constraint_hazard_mappings chm ON sc.id = chm.constraint_id
        WHERE sc.analysis_id = $1
        GROUP BY sc.id, sc.identifier, sc.constraint_statement, sc.constraint_type
        ORDER BY sc.identifier
        """
        
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_stakeholders(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get stakeholders from Step 1."""
        # Check which table exists (step1_stakeholders for new schema, stakeholders for old)
        has_step1_stakeholders = await self.db_connection.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'step1_stakeholders'
            )
        """)
        
        if has_step1_stakeholders:
            # New schema with step1_stakeholders table
            query = """
            SELECT id, name, stakeholder_type, 
                   COALESCE(mission_perspective->>'primary_needs', '') as concerns,
                   COALESCE(influence_interest->>'trust_level', 'medium') as trust_level
            FROM step1_stakeholders
            WHERE analysis_id = $1
            ORDER BY name
            """
        else:
            # Old schema
            query = """
            SELECT id, name, stakeholder_type, concerns, trust_level
            FROM stakeholders
            WHERE analysis_id = $1
            ORDER BY name
            """
        
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_system_boundaries(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get system boundaries from Step 1."""
        # Always use system_boundaries table (both old and new schemas use this name)
        query = """
        SELECT id, boundary_type, description, 
               COALESCE(definition_criteria->>'includes', '[]') as includes,
               COALESCE(definition_criteria->>'excludes', '[]') as excludes
        FROM system_boundaries
        WHERE analysis_id = $1
        ORDER BY boundary_type
        """
        
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    def format_control_structure_prompt(self, step1_results: Dict[str, Any], specific_focus: str = "") -> str:
        """
        Format a prompt with Step 1 context for control structure analysis.
        """
        prompt = f"""
# STPA-Sec Step 2: Control Structure Analysis

## Important: Consistency Requirements
Use consistent terminology across all analysis:
- Component identifiers: Use CTRL-X for controllers, PROC-Y for processes, DUAL-Z for dual-role
- Action types: command/configuration/permission/monitoring
- Timing descriptors: continuous/periodic/event-driven/on-demand
- Trust levels: high/medium/low
- Abstraction levels: system/subsystem/component

## Abstraction Level Guidance
Maintain appropriate abstraction for security analysis:
- Focus on security-relevant control actions
- Omit implementation details unless security-critical
- Group related low-level actions into logical controls
- Emphasize control relationships that affect security properties
- Abstract away non-security operational details

## System Context from Step 1

**System**: {step1_results['system_name']}
**Mission**: {step1_results['mission_statement']}

### Key Losses (What We're Protecting Against)
"""
        for loss in step1_results['losses'][:5]:  # Top 5 losses
            prompt += f"- {loss['identifier']}: {loss['description']}\n"
            
        prompt += "\n### Key Hazards (System States to Prevent)\n"
        for hazard in step1_results['hazards'][:5]:  # Top 5 hazards
            prompt += f"- {hazard['identifier']}: {hazard['description']}\n"
            
        prompt += "\n### Security Constraints (What Must Be Enforced)\n"
        for constraint in step1_results['security_constraints'][:5]:  # Top 5 constraints
            prompt += f"- {constraint['identifier']}: {constraint['constraint_text']}\n"
            
        prompt += "\n### Key Stakeholders\n"
        for stakeholder in step1_results['stakeholders'][:5]:  # Top 5 stakeholders
            prompt += f"- {stakeholder['name']} ({stakeholder['stakeholder_type']}): {stakeholder['concerns']}\n"
            
        if specific_focus:
            prompt += f"\n## Specific Analysis Focus\n{specific_focus}\n"
            
        return prompt
        
    def apply_expert_refinement(self, base_prompt: str, previous_results: Dict[str, Any]) -> str:
        """
        Apply expert refinement guidance to prompts if available.
        """
        # Check if we have expert refinement guidance
        if "expert_refinement" not in previous_results:
            return base_prompt
            
        refinement = previous_results["expert_refinement"]
        
        # Add priority fixes
        if refinement.get("priority_fixes"):
            base_prompt += "\n## CRITICAL REFINEMENTS REQUIRED:\n"
            for fix in refinement["priority_fixes"]:
                base_prompt += f"\n### {fix['issue']}:\n"
                base_prompt += f"- Required Action: {fix['specific_guidance']}\n"
                if fix.get('example'):
                    base_prompt += f"- Example: {fix['example']}\n"
                    
        # Add patterns to avoid
        if refinement.get("avoid_patterns"):
            base_prompt += "\n## PATTERNS TO AVOID:\n"
            for pattern in refinement["avoid_patterns"]:
                base_prompt += f"- {pattern}\n"
                
        # Add specific requirements
        if refinement.get("specific_requirements"):
            base_prompt += "\n## ADDITIONAL REQUIREMENTS:\n"
            for req in refinement["specific_requirements"]:
                base_prompt += f"- {req}\n"
                
        # Add examples if provided
        if "expert_examples" in previous_results:
            base_prompt += "\n## EXPERT-PROVIDED EXAMPLES:\n"
            for example in previous_results["expert_examples"]:
                base_prompt += f"- {example}\n"
                
        # Add clarified requirements
        if "clarified_requirements" in previous_results:
            base_prompt += "\n## CLARIFIED REQUIREMENTS:\n"
            for req in previous_results["clarified_requirements"]:
                base_prompt += f"- {req}\n"
                
        return base_prompt
        
    @abstractmethod
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """
        Perform Step 2 analysis.
        Must be implemented by each specific Step 2 agent.
        """
        pass
    
    
    async def query_llm_with_retry(self, messages: List[Dict[str, str]], 
                                   max_retries: int = 3, 
                                   temperature: float = 0.7,
                                   max_tokens: int = 4000) -> str:
        """
        Query LLM with retry logic for better JSON parsing.
        Saves all attempts for debugging.
        """
        from core.utils.json_parser import parse_llm_json
        
        prompt = messages[-1]["content"] if messages else ""
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                # Make LLM call
                response = await self.model_provider.generate(
                    messages, 
                    temperature=temperature, 
                    max_tokens=max_tokens
                )
                response_text = response.content
                
                # Save to PromptSaver if enabled
                prompt_saver = get_prompt_saver()
                if prompt_saver:
                    prompt_saver.save_prompt_response(
                        agent_name=self.__class__.__name__.lower().replace('agent', ''),
                        cognitive_style=self.cognitive_style.value,
                        prompt=prompt,
                        response=response_text,
                        step=2,
                        metadata={
                            'attempt': attempt,
                            'temperature': temperature,
                            'max_tokens': max_tokens
                        }
                    )
                
                # Try to parse JSON to validate format
                try:
                    # First attempt to clean markdown formatting
                    cleaned_response = response_text.strip()
                    if cleaned_response.startswith('```'):
                        # Remove markdown code blocks
                        lines = cleaned_response.split('\n')
                        start_idx = 0
                        end_idx = len(lines)
                        for i, line in enumerate(lines):
                            if line.strip().startswith('```json') or line.strip() == '```':
                                if start_idx == 0:
                                    start_idx = i + 1
                                elif i > start_idx:
                                    end_idx = i
                                    break
                        cleaned_response = '\n'.join(lines[start_idx:end_idx])
                    
                    parse_llm_json(cleaned_response)
                    return cleaned_response  # Success!
                except Exception as parse_error:
                    last_error = parse_error
                    if attempt < max_retries:
                        self.logger.warning(f"JSON parse failed on attempt {attempt}: {parse_error}")
                        # Add a message asking for better formatting
                        messages.append({
                            "role": "assistant", 
                            "content": response_text
                        })
                        messages.append({
                            "role": "user",
                            "content": "Your response contained markdown formatting (```json blocks). Please provide ONLY the raw JSON without any markdown formatting, code blocks, or backticks. Start directly with {{ and end with }}."
                        })
                    else:
                        # On last attempt, return what we have
                        self.logger.error(f"All JSON parse attempts failed. Returning last response.")
                        return response_text
                        
            except Exception as e:
                self.logger.error(f"LLM query failed on attempt {attempt}: {e}")
                last_error = e
                if attempt == max_retries:
                    raise
                
        raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")
    
    async def query_llm_structured(self, 
                                  messages: List[Dict[str, str]], 
                                  response_schema: Dict[str, Any],
                                  temperature: float = 0.3,
                                  max_tokens: int = 4000) -> Dict[str, Any]:
        """Query LLM with structured output for guaranteed valid JSON."""
        
        try:
            # Try structured output first
            response = await self.model_provider.generate_structured(
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"{self.__class__.__name__.lower()}_response",
                        "schema": response_schema,
                        "strict": True
                    }
                },
                temperature=temperature,  # Lower for structured output
                max_tokens=max_tokens
            )
            
            # Save to PromptSaver if enabled
            prompt_saver = get_prompt_saver()
            if prompt_saver:
                prompt = messages[-1]["content"] if messages else ""
                prompt_saver.save_prompt_response(
                    agent_name=self.__class__.__name__.lower().replace('agent', ''),
                    cognitive_style=self.cognitive_style.value,
                    prompt=prompt,
                    response=json.dumps(response.content, indent=2) if isinstance(response.content, dict) else response.content,
                    step=2,
                    metadata={
                        'temperature': temperature,
                        'max_tokens': max_tokens,
                        'mode': 'structured_output'
                    }
                )
            
            # Return already parsed JSON (or parse if string)
            if isinstance(response.content, str):
                return json.loads(response.content)
            return response.content
            
        except Exception as e:
            # If structured output fails, fall back to regular query with retry
            self.logger.warning(f"Structured output failed: {e}. Falling back to regular generation.")
            self.logger.debug(f"Structured output error details: {type(e).__name__}: {str(e)}")
            response = await self.query_llm_with_retry(messages, max_retries=3, temperature=temperature, max_tokens=max_tokens)
            return parse_llm_json(response)