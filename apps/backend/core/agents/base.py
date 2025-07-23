"""
Base agent class for all analysis agents.
This provides the foundation for structured output that maps to frontend templates.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from core.agents.websocket_integration import AgentWebSocketNotifier
from uuid import UUID
import time
import asyncio
from pydantic import BaseModel, Field

from core.models.schemas import (
    FrameworkType, AnalysisStatus, AgentContext, AgentResult,
    TableData, ChartData, DiagramData,
    create_table_content, create_chart_content, create_diagram_content,
    create_text_content, create_list_content
)
from core.utils.llm_client import llm_manager, LLMResponse
from config.settings import settings, metrics
from core.context import context_manager
from core.agents.types import SectionResult
    

class BaseAnalysisAgent(ABC):
    """
    Base class for all analysis agents.
    
    Each agent:
    1. Accepts structured context
    2. Runs analysis using LLM with structured output
    3. Returns results that map to frontend templates
    4. Stores artifacts for cross-referencing
    """
    
    def __init__(self, framework: FrameworkType):
        self.framework = framework
        self.prompt_dir = settings.prompts_dir / framework.value
        
    @abstractmethod
    async def analyze(self, context: AgentContext, section_ids: Optional[List[str]] = None) -> AgentResult:
        """
        Run analysis and return structured output.
        Must return AgentResult with sections that map to frontend templates.
        """
        pass
        
    @abstractmethod
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        # Returns: [{"id": "section-id", "title": "Section Title", "template": "table"}]
        pass
        
    async def analyze_sections(
        self,
        context: AgentContext,
        section_ids: Optional[List[str]] = None,
        notifier: Optional['AgentWebSocketNotifier'] = None
    ) -> List[SectionResult]:
        """Analyze specific sections or all sections"""
        sections_to_analyze = section_ids or [s["id"] for s in self.get_sections()]
        results = []
        total_sections = len(sections_to_analyze)
        
        for i, section_id in enumerate(sections_to_analyze):
            try:
                # Notify section start if notifier available
                if notifier:
                    section_title = self._get_section_title(section_id)
                    await notifier.notify_section_start(
                        self.framework.value,
                        section_id,
                        section_title
                    )
                    
                result = await self.analyze_section(section_id, context)
                results.append(result)
                
                # Notify section complete
                if notifier:
                    await notifier.notify_section_complete(
                        self.framework.value,
                        result
                    )
                    # Update overall progress
                    progress = ((i + 1) / total_sections) * 100
                    await notifier.notify_analysis_progress(
                        progress,
                        f"Completed {result.title}"
                    )
                    
            except Exception as e:
                error_result = SectionResult(
                    section_id=section_id,
                    title=self._get_section_title(section_id),
                    content={},
                    template_type="error",
                    status=AnalysisStatus.FAILED,
                    error=str(e)
                )
                results.append(error_result)
                
                # Notify section error
                if notifier:
                    await notifier.notify_section_complete(
                        self.framework.value,
                        error_result
                    )
        
        return results
        
    async def analyze_section(
        self,
        section_id: str,
        context: AgentContext
    ) -> SectionResult:
        """Analyze a specific section"""
        # Get section-specific prompt
        prompt = await self._load_prompt(section_id)
        
        # Build complete prompt with context
        full_prompt = await self._build_prompt(prompt, context, section_id)
        
        # Get response from LLM
        response = await llm_manager.generate(full_prompt)
        
        # Parse and structure the response
        structured_content = await self._parse_response(response.content, section_id)
        
        # Store as artifact in context
        context.artifacts[f"{self.framework.value}_{section_id}"] = structured_content
        
        # Add to context manager for future reference
        try:
            await context_manager.add_analysis_result(
                context.analysis_id,
                self.framework.value,
                {
                    "section_id": section_id,
                    "content": structured_content,
                    "timestamp": time.time()
                }
            )
        except Exception as e:
            # Don't fail if context manager has issues
            pass
        
        return SectionResult(
            section_id=section_id,
            title=self._get_section_title(section_id),
            content=structured_content,
            template_type=self._get_template_type(section_id)
        )
        
    async def _load_prompt(self, section_id: str) -> str:
        """Load prompt from file"""
        prompt_file = self.prompt_dir / f"{section_id}.txt"
        if not prompt_file.exists():
            # Try master prompt
            prompt_file = self.prompt_dir / "master.txt"
        
        if prompt_file.exists():
            return prompt_file.read_text()
        else:
            return self._get_default_prompt(section_id)
    
    async def _build_prompt(
        self,
        base_prompt: str,
        context: AgentContext,
        section_id: str
    ) -> str:
        """Build complete prompt with context using LlamaIndex"""
        # Replace placeholders in prompt
        prompt = base_prompt.replace("{{SYSTEM_DESCRIPTION}}", context.system_description)
        
        # Get relevant context from LlamaIndex
        try:
            # Get relevant artifacts from previous analyses
            relevant_artifacts = await context_manager.get_relevant_context(
                context.analysis_id,
                f"{self.framework.value} {section_id} analysis",
                top_k=3,
                context_type="artifact"
            )
            
            if relevant_artifacts:
                artifacts_text = "\n\nRelevant information from previous analyses:\n"
                for artifact in relevant_artifacts:
                    artifact_type = artifact["metadata"].get("framework", "unknown")
                    artifacts_text += f"\n### From {artifact_type}:\n{artifact['content'][:500]}...\n"
                prompt += artifacts_text
            
            # Get relevant conversation history
            chat_history = await context_manager.get_conversation_history(
                context.analysis_id,
                limit=3
            )
            
            if chat_history:
                chat_text = "\n\nRecent conversation context:\n"
                for msg in chat_history:
                    chat_text += f"\n{msg.role}: {msg.content[:200]}...\n"
                prompt += chat_text
        
        except Exception as e:
            # If context manager fails, continue without enhanced context
            pass
        
        # Add immediate artifacts from current analysis
        if context.artifacts:
            relevant_artifacts = self._get_relevant_artifacts(context.artifacts, section_id)
            if relevant_artifacts:
                artifacts_text = "\n\nRelevant information from current analysis:\n"
                for key, value in relevant_artifacts.items():
                    artifacts_text += f"\n{key}:\n{str(value)[:500]}...\n"
                prompt += artifacts_text
        
        # Add specific instructions for structured output
        prompt += f"\n\nProvide the output in a structured format suitable for the '{self._get_template_type(section_id)}' template."
        
        return prompt
    
    def _get_relevant_artifacts(
        self,
        artifacts: Dict[str, Any],
        section_id: str
    ) -> Dict[str, Any]:
        """Get artifacts relevant to current section"""
        # Override in subclasses for specific relevance logic
        relevant = {}
        
        # Always include STPA-Sec results if available
        if "stpa-sec_control_structure" in artifacts:
            relevant["Control Structure"] = artifacts["stpa-sec_control_structure"]
        
        return relevant
    
    @abstractmethod
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format for frontend template"""
        pass
    
    def _get_section_title(self, section_id: str) -> str:
        """Get title for a section"""
        for section in self.get_sections():
            if section["id"] == section_id:
                return section["title"]
        return section_id.replace("_", " ").title()
    
    def _get_template_type(self, section_id: str) -> str:
        """Get template type for a section"""
        for section in self.get_sections():
            if section["id"] == section_id:
                return section.get("template", "text")
        return "text"
    
    def _load_master_prompt(self) -> str:
        """Load master prompt for framework"""
        master_file = self.prompt_dir / "master.txt"
        if master_file.exists():
            return master_file.read_text()
        return ""
    
    def _get_default_prompt(self, section_id: str) -> str:
        """Get default prompt for a section"""
        return f"""Analyze the following system for {self.framework.value} framework, focusing on {section_id}.

System Description:
{{{{SYSTEM_DESCRIPTION}}}}

Provide a comprehensive analysis following the {self.framework.value} methodology."""
    
    # Helper methods for creating structured content
    def create_table(self, columns: List[Dict], rows: List[Dict]) -> Dict[str, Any]:
        """Create table content"""
        return create_table_content(TableData(columns=columns, rows=rows))
    
    def create_chart(self, chart_type: str, labels: List[str], datasets: List[Dict]) -> Dict[str, Any]:
        """Create chart content"""
        return create_chart_content(ChartData(type=chart_type, labels=labels, datasets=datasets))
    
    def create_diagram(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Create diagram content"""
        return create_diagram_content(DiagramData(nodes=nodes, edges=edges))
    
    def create_text(self, content: str, format: str = "markdown") -> Dict[str, Any]:
        """Create text content"""
        return create_text_content(content, format)
    
    def create_list(self, items: List[Dict], ordered: bool = False) -> Dict[str, Any]:
        """Create list content"""
        return create_list_content(items, ordered)