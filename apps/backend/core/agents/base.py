"""
Base agent class for all analysis agents.
This provides the foundation for structured output that maps to frontend templates.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import instructor
from openai import AsyncOpenAI

from core.models.templates import (
    AnalysisSection, AnalysisTable, AnalysisDiagram,
    AnalysisText, AnalysisList, AnalysisChart
)
from core.utils.prompt_manager import PromptManager
from core.memory.artifact_store import ArtifactStore


class AnalysisContext(BaseModel):
    """Context passed between agents"""
    system_description: str
    analysis_request: Dict[str, Any]
    previous_results: Dict[str, Any] = {}
    user_modifications: Optional[str] = None
    enabled_plugins: List[str] = []
    

class BaseAnalysisAgent(ABC):
    """
    Base class for all analysis agents.
    
    Each agent:
    1. Accepts structured context
    2. Runs analysis using LLM with structured output
    3. Returns results that map to frontend templates
    4. Stores artifacts for cross-referencing
    """
    
    def __init__(
        self,
        agent_id: str,
        llm_client: AsyncOpenAI,
        prompt_manager: PromptManager,
        artifact_store: ArtifactStore
    ):
        self.agent_id = agent_id
        self.llm = instructor.from_openai(llm_client)
        self.prompts = prompt_manager
        self.artifacts = artifact_store
        
    @abstractmethod
    async def analyze(self, context: AnalysisContext) -> AnalysisSection:
        """
        Run analysis and return structured output.
        Must return AnalysisSection that maps to frontend templates.
        """
        pass
        
    @abstractmethod
    def get_sections(self) -> List[str]:
        """Return list of sections this agent can analyze"""
        pass
        
    @abstractmethod
    def get_template_structure(self) -> Dict[str, Any]:
        """Return expected template structure for frontend"""
        pass
        
    async def analyze_section(
        self,
        section_id: str,
        context: AnalysisContext
    ) -> AnalysisSection:
        """Analyze a specific section"""
        # Get section-specific prompt
        prompt = self.prompts.get_prompt(
            self.agent_id,
            section_id,
            context.user_modifications
        )
        
        # Get relevant artifacts from other analyses
        relevant_context = await self.artifacts.get_relevant_context(
            query=f"{self.agent_id} {section_id}",
            existing_results=context.previous_results
        )
        
        # Build complete prompt with context
        full_prompt = self._build_prompt(prompt, context, relevant_context)
        
        # Get structured output from LLM
        result = await self._get_llm_response(full_prompt, section_id)
        
        # Store artifact
        await self.artifacts.store(
            agent_id=self.agent_id,
            section_id=section_id,
            artifact=result
        )
        
        return result
        
    def _build_prompt(
        self,
        base_prompt: str,
        context: AnalysisContext,
        relevant_artifacts: Dict[str, Any]
    ) -> str:
        """Build complete prompt with context"""
        # TODO: Implement prompt building logic
        # Include system description, previous results, etc.
        pass
        
    async def _get_llm_response(
        self,
        prompt: str,
        section_id: str
    ) -> AnalysisSection:
        """Get structured response from LLM"""
        # TODO: Use instructor to get structured output
        # Map to appropriate template type based on section
        pass