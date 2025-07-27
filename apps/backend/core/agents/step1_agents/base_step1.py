"""
Base class for STPA-Sec Step 1 agents
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio
import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import asyncpg

from core.agents.base import BaseAnalysisAgent
from core.models.schemas import AgentContext, AgentResult


class BaseStep1Agent(ABC):
    """
    Base class for all Step 1 agents
    
    Step 1 maintains mission-level abstraction:
    - WHAT the system must do (not HOW)
    - System states (not actions or mechanisms)
    - Mission impacts (not technical details)
    """
    
    def __init__(self, analysis_id: str, db_connection: Optional[asyncpg.Connection] = None):
        self.analysis_id = analysis_id
        self.db_connection = db_connection
        self.agent_id = str(uuid4())
        self.created_at = datetime.now()
        
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
                (id, agent_type, analysis_id, activity, details, timestamp)
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
                (id, analysis_id, agent_type, results, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """,
                str(uuid4()),
                self.analysis_id,
                self.get_agent_type(),
                json.dumps(results),
                datetime.now()
            )