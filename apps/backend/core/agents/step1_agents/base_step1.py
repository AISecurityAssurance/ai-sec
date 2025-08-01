"""
Base class for STPA-Sec Step 1 agents
"""
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
import asyncio
import json
import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from core.agents.base import BaseAnalysisAgent
from core.models.schemas import AgentContext, AgentResult
from core.model_providers import get_model_client, ModelResponse
from core.utils.json_parser import parse_llm_json
from core.utils.prompt_saver import get_prompt_saver
from enum import Enum


class CognitiveStyle(str, Enum):
    """Cognitive styles for ASI-ARCH Dream Team approach"""
    BALANCED = "balanced"  # Default single-agent mode
    INTUITIVE = "intuitive"  # Fast, aesthetic, pattern recognition
    TECHNICAL = "technical"  # Fast, technical, pragmatic execution
    CREATIVE = "creative"  # Slow, aesthetic, novel connections
    SYSTEMATIC = "systematic"  # Slow, technical, rigorous verification


class BaseStep1Agent(ABC):
    """
    Base class for all Step 1 agents
    
    Step 1 maintains mission-level abstraction:
    - WHAT the system must do (not HOW)
    - System states (not actions or mechanisms)
    - Mission impacts (not technical details)
    """
    
    def __init__(self, analysis_id: str, db_connection: Optional[asyncpg.Connection] = None,
                 cognitive_style: CognitiveStyle = CognitiveStyle.BALANCED):
        self.analysis_id = analysis_id
        self.db_connection = db_connection
        self.agent_id = str(uuid4())
        self.created_at = datetime.now()
        self.cognitive_style = cognitive_style
        self.logger = logging.getLogger(f"{self.__class__.__name__}-{self.agent_id[:8]}")
        
    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the agent's analysis
        
        Args:
            context: Analysis context including system description, prior results
            
        Returns:
            Analysis results specific to this agent
        """
        pass
    
    @abstractmethod
    def validate_abstraction_level(self, content: str) -> bool:
        """
        Validate that content maintains Step 1 abstraction level
        
        Args:
            content: Content to validate
            
        Returns:
            True if content maintains proper abstraction
        """
        pass
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the type of this agent"""
        pass
    
    async def log_activity(self, activity: str, details: Optional[Dict[str, Any]] = None):
        """Log agent activity"""
        if self.db_connection:
            await self.db_connection.execute("""
                INSERT INTO agent_activity_log 
                (id, agent_type, analysis_id, activity, details, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                str(uuid4()),
                self.get_agent_type(),
                self.analysis_id,
                activity,
                json.dumps(details) if details else None,
                datetime.now()
            )
    
    def extract_mission_language(self, text: str) -> str:
        """
        Extract and ensure mission-level language
        
        Converts implementation details to abstract states
        """
        # Common patterns to replace
        replacements = {
            # Technical to abstract
            "authentication system": "identity verification capability",
            "authorization system": "access control capability",
            "encryption": "data protection capability",
            "API": "service interface",
            "database": "information store",
            "network": "communication infrastructure",
            
            # Action to state
            "fails to": "operates without",
            "unable to": "lacks capability for",
            "cannot": "does not have ability to",
            "compromised by": "operates in compromised state due to",
            
            # Implementation to mission
            "SQL injection": "data integrity compromise",
            "XSS attack": "user interface compromise",
            "DDoS": "availability disruption",
            "malware": "system compromise",
            "phishing": "user deception"
        }
        
        result = text
        for pattern, replacement in replacements.items():
            result = result.replace(pattern, replacement)
            
        return result
    
    def is_implementation_detail(self, text: str) -> bool:
        """Check if text contains implementation details"""
        implementation_keywords = [
            "algorithm", "protocol", "API", "database", "firewall",
            "encryption key", "TLS", "SSL", "HTTP", "TCP/IP",
            "code", "function", "method", "class", "module",
            "SQL", "NoSQL", "REST", "SOAP", "GraphQL",
            "AWS", "Azure", "Docker", "Kubernetes",
            "patch", "update", "version", "library"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in implementation_keywords)
    
    def is_prevention_language(self, text: str) -> bool:
        """Check if text contains prevention/mitigation language"""
        prevention_keywords = [
            "prevent", "mitigate", "defend", "protect against",
            "security control", "countermeasure", "safeguard",
            "must not", "shall not", "avoid", "ensure",
            "validate", "verify", "authenticate", "authorize"
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in prevention_keywords)
    
    async def get_prior_results(self, agent_types: List[str]) -> Dict[str, Any]:
        """Get results from other agents that have already run"""
        if not self.db_connection:
            return {}
            
        results = {}
        for agent_type in agent_types:
            row = await self.db_connection.fetchrow("""
                SELECT results 
                FROM agent_results
                WHERE analysis_id = $1 AND agent_type = $2
                ORDER BY created_at DESC
                LIMIT 1
            """, self.analysis_id, agent_type)
            
            if row and row['results']:
                results[agent_type] = json.loads(row['results'])
                
        return results
    
    async def save_results(self, results: Dict[str, Any]):
        """Save agent results to database"""
        if self.db_connection:
            await self.db_connection.execute("""
                INSERT INTO agent_results
                (id, analysis_id, agent_type, cognitive_style, results, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                str(uuid4()),
                self.analysis_id,
                self.get_agent_type(),
                self.cognitive_style.value,
                json.dumps(results),
                datetime.now()
            )
    
    async def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call the configured LLM with cognitive style modifications
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response content
        """
        # Get cognitive style modifier
        style_modifier = self.get_cognitive_style_prompt_modifier()
        
        # Build messages
        messages = []
        
        if system_prompt:
            # Prepend cognitive style to system prompt
            full_system = f"{style_modifier}\n\n{system_prompt}" if style_modifier else system_prompt
            messages.append({"role": "system", "content": full_system})
        elif style_modifier:
            # Add style modifier as system message if no system prompt
            messages.append({"role": "system", "content": style_modifier})
            
        messages.append({"role": "user", "content": prompt})
        
        # Get model client and generate response
        try:
            client = get_model_client()
            response = await client.generate(messages, temperature=0.7)
            
            # Save to PromptSaver if enabled
            prompt_saver = get_prompt_saver()
            if prompt_saver:
                prompt_saver.save_prompt_response(
                    agent_name=self.__class__.__name__.lower().replace('agent', ''),
                    cognitive_style=self.cognitive_style.value,
                    prompt=prompt,
                    response=response.content,
                    step=1,
                    metadata={
                        'temperature': 0.7,
                        'has_system_prompt': system_prompt is not None
                    }
                )
            
            return response.content
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {str(e)}") from e
    
    async def parse_llm_json_response(self, response: str) -> Union[Dict, List]:
        """
        Parse JSON from LLM response with error recovery.
        
        Args:
            response: Raw LLM response that should contain JSON
            
        Returns:
            Parsed JSON object (dict or list)
            
        Raises:
            ValueError: If JSON cannot be parsed after all attempts
        """
        try:
            return parse_llm_json(response)
        except ValueError as e:
            # Log for debugging
            await self.log_activity(
                f"JSON parsing failed in {self.__class__.__name__}",
                {
                    "error": str(e),
                    "response_preview": response[:500] if response else "Empty response"
                }
            )
            raise
    
    def get_cognitive_style_prompt_modifier(self) -> str:
        """
        Get prompt modifications based on cognitive style
        
        Returns:
            String to prepend to prompts to influence cognitive style
        """
        modifiers = {
            CognitiveStyle.BALANCED: "",  # No modification for default
            
            CognitiveStyle.INTUITIVE: """Think like an intuitive pattern recognizer:
- Trust your instincts about what "feels" wrong or dangerous
- Look for non-obvious patterns and emergent risks
- Consider the aesthetic and human aspects of the system
- Identify risks that might not be immediately measurable
- Focus on the "big picture" and systemic issues

""",
            
            CognitiveStyle.TECHNICAL: """Think like a pragmatic technical implementer:
- Focus on concrete, measurable, and exploitable vulnerabilities
- Consider practical attack vectors and failure modes
- Emphasize technically feasible risks
- Be specific about mechanisms and dependencies
- Prioritize high-impact, high-likelihood scenarios

""",
            
            CognitiveStyle.CREATIVE: """Think like a creative innovator:
- Imagine novel and unexpected failure scenarios
- Consider edge cases and unusual combinations
- Think "outside the box" about potential risks
- Explore unconventional attack vectors
- Don't limit yourself to known patterns

""",
            
            CognitiveStyle.SYSTEMATIC: """Think like a systematic validator:
- Ensure comprehensive and complete coverage
- Check for logical consistency and completeness
- Validate that nothing important is missed
- Be rigorous and methodical in your analysis
- Ensure MECE (Mutually Exclusive, Collectively Exhaustive) categorization

"""
        }
        
        return modifiers.get(self.cognitive_style, "")
    
    def should_emphasize_novelty(self) -> bool:
        """Whether this cognitive style should emphasize novel findings"""
        return self.cognitive_style in [CognitiveStyle.INTUITIVE, CognitiveStyle.CREATIVE]
    
    def should_emphasize_rigor(self) -> bool:
        """Whether this cognitive style should emphasize rigorous validation"""
        return self.cognitive_style in [CognitiveStyle.TECHNICAL, CognitiveStyle.SYSTEMATIC]