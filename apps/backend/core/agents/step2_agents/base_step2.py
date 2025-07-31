"""
Base class for Step 2 STPA-Sec agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging
import asyncpg

from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.models.schemas import AgentResult


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
        query = """
        SELECT id, identifier, loss_type, description, stakeholder_impact
        FROM losses
        WHERE analysis_id = $1
        ORDER BY identifier
        """
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_hazards(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get hazards from Step 1."""
        query = """
        SELECT h.id, h.identifier, h.description, h.system_state,
               array_agg(DISTINCT hl.loss_id) as associated_losses
        FROM hazards h
        LEFT JOIN hazard_losses hl ON h.id = hl.hazard_id
        WHERE h.analysis_id = $1
        GROUP BY h.id, h.identifier, h.description, h.system_state
        ORDER BY h.identifier
        """
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_security_constraints(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get security constraints from Step 1."""
        query = """
        SELECT sc.id, sc.identifier, sc.constraint_text, sc.constraint_type,
               array_agg(DISTINCT sch.hazard_id) as mitigated_hazards
        FROM security_constraints sc
        LEFT JOIN security_constraint_hazards sch ON sc.id = sch.constraint_id
        WHERE sc.analysis_id = $1
        GROUP BY sc.id, sc.identifier, sc.constraint_text, sc.constraint_type
        ORDER BY sc.identifier
        """
        rows = await self.db_connection.fetch(query, analysis_id)
        return [dict(row) for row in rows]
        
    async def _get_stakeholders(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get stakeholders from Step 1."""
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
        query = """
        SELECT id, boundary_type, description, includes, excludes
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
        
    @abstractmethod
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """
        Perform Step 2 analysis.
        Must be implemented by each specific Step 2 agent.
        """
        pass