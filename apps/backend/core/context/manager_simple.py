"""
Simple Context Manager (without LlamaIndex)
Manages conversation history and provides context
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from uuid import UUID
import logging

from core.models.schemas import AgentContext

logger = logging.getLogger(__name__)


class SimpleContextManager:
    """Simple context manager without vector store"""
    
    def __init__(self):
        self.contexts: Dict[str, AgentContext] = {}
        self.chat_histories: Dict[str, List[Dict[str, Any]]] = {}
    
    async def initialize_analysis_context(
        self, 
        analysis_id: UUID,
        system_description: str,
        existing_artifacts: Optional[Dict[str, Any]] = None
    ) -> AgentContext:
        """Initialize context for a new analysis"""
        context = AgentContext(
            analysis_id=analysis_id,
            system_description=system_description,
            artifacts=existing_artifacts or {},
            completed_frameworks=[],
            metadata={}
        )
        
        self.contexts[str(analysis_id)] = context
        self.chat_histories[str(analysis_id)] = []
        
        logger.info(f"Initialized context for analysis {analysis_id}")
        return context
    
    async def add_artifact(
        self,
        analysis_id: UUID,
        artifact_key: str,
        artifact_data: Any
    ):
        """Add artifact to context"""
        context = self.contexts.get(str(analysis_id))
        if context:
            context.artifacts[artifact_key] = artifact_data
            logger.info(f"Added artifact {artifact_key} to analysis {analysis_id}")
    
    async def add_chat_message(
        self,
        analysis_id: UUID,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add chat message to history"""
        chat_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "response": response,
            "metadata": metadata or {}
        }
        
        history = self.chat_histories.get(str(analysis_id), [])
        history.append(chat_entry)
        self.chat_histories[str(analysis_id)] = history
        
        logger.info(f"Added chat message to analysis {analysis_id}")
    
    async def query_context(
        self,
        analysis_id: UUID,
        query: str,
        include_chat_history: bool = True,
        k: int = 5
    ) -> str:
        """Query context - returns relevant context as string"""
        context_parts = []
        
        # Add system description
        context = self.contexts.get(str(analysis_id))
        if context:
            context_parts.append(f"System Description: {context.system_description}")
            
            # Add artifacts summary
            if context.artifacts:
                context_parts.append("\nArtifacts:")
                for key, value in list(context.artifacts.items())[:k]:
                    context_parts.append(f"- {key}: {str(value)[:200]}...")
        
        # Add recent chat history
        if include_chat_history:
            history = self.chat_histories.get(str(analysis_id), [])
            if history:
                context_parts.append("\nRecent Conversations:")
                for entry in history[-k:]:
                    context_parts.append(f"Q: {entry['message']}")
                    context_parts.append(f"A: {entry['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    async def get_analysis_context(self, analysis_id: UUID) -> Optional[AgentContext]:
        """Get analysis context"""
        return self.contexts.get(str(analysis_id))
    
    async def cleanup_analysis_context(self, analysis_id: UUID):
        """Cleanup context for an analysis"""
        analysis_id_str = str(analysis_id)
        if analysis_id_str in self.contexts:
            del self.contexts[analysis_id_str]
        if analysis_id_str in self.chat_histories:
            del self.chat_histories[analysis_id_str]
        logger.info(f"Cleaned up context for analysis {analysis_id}")


# Global instance
context_manager = SimpleContextManager()