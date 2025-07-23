"""
Context Manager using LlamaIndex
Manages conversation history and provides context to LLMs
"""
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from uuid import UUID
import logging

from llama_index import Document, VectorStoreIndex, StorageContext
from llama_index.node_parser import SimpleNodeParser
from llama_index.retrievers import VectorIndexRetriever
from llama_index.response_synthesizers import get_response_synthesizer
from llama_index.indices.query.query_transform import HyDEQueryTransform
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.vector_stores import SimpleVectorStore
try:
    from llama_index.embeddings import BaseEmbedding, OpenAIEmbedding
except ImportError:
    # Fallback for older versions
    from llama_index.embeddings.base import BaseEmbedding
    from llama_index.embeddings.openai import OpenAIEmbedding
try:
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
except ImportError:
    # For older versions or if not available
    HuggingFaceEmbedding = None

from core.models.schemas import AgentContext
from config.settings import settings

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages context for analysis sessions using LlamaIndex
    
    Features:
    - Stores and retrieves conversation history
    - Maintains artifacts from previous analyses
    - Provides relevant context to agents
    - Supports multiple embedding models
    """
    
    def __init__(self, embedding_model: Optional[str] = None):
        # Default to OpenAI embeddings to avoid dependency issues
        self.embedding_model = embedding_model or getattr(settings, 'EMBEDDING_MODEL', 'openai/text-embedding-ada-002')
        self.embedding = self._initialize_embedding()
        self.indices: Dict[str, VectorStoreIndex] = {}
        self.storage_contexts: Dict[str, StorageContext] = {}
        
    def _initialize_embedding(self) -> BaseEmbedding:
        """Initialize embedding model based on configuration"""
        if self.embedding_model.startswith("openai"):
            # Extract model name after 'openai/'
            model_name = self.embedding_model.split('/')[-1] if '/' in self.embedding_model else self.embedding_model
            return OpenAIEmbedding(
                model=model_name,
                api_key=getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
            )
        elif self.embedding_model.startswith("sentence-transformers"):
            if HuggingFaceEmbedding:
                return HuggingFaceEmbedding(
                    model_name=self.embedding_model
                )
            else:
                # Fallback to OpenAI if HuggingFace not available
                logger.warning("HuggingFace embeddings not available, using OpenAI")
                return OpenAIEmbedding()
        else:
            # Default to local embedding
            if HuggingFaceEmbedding:
                return HuggingFaceEmbedding(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            else:
                return OpenAIEmbedding()
    
    async def initialize_analysis_context(
        self, 
        analysis_id: UUID,
        system_description: str,
        existing_artifacts: Optional[Dict[str, Any]] = None
    ) -> AgentContext:
        """Initialize context for a new analysis"""
        # Create storage context
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            index_store=SimpleIndexStore(),
            vector_store=SimpleVectorStore()
        )
        self.storage_contexts[str(analysis_id)] = storage_context
        
        # Create initial documents
        documents = [
            Document(
                text=system_description,
                metadata={
                    "type": "system_description",
                    "analysis_id": str(analysis_id),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        ]
        
        # Add existing artifacts if any
        if existing_artifacts:
            for artifact_type, artifact_data in existing_artifacts.items():
                documents.append(
                    Document(
                        text=json.dumps(artifact_data),
                        metadata={
                            "type": f"artifact_{artifact_type}",
                            "analysis_id": str(analysis_id),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )
        
        # Create index
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=self.embedding
        )
        self.indices[str(analysis_id)] = index
        
        # Create agent context
        context = AgentContext(
            analysis_id=analysis_id,
            project_id=None,  # Will be set by caller
            system_description=system_description,
            artifacts=existing_artifacts or {},
            metadata={}
        )
        
        return context
    
    async def add_analysis_result(
        self,
        analysis_id: UUID,
        framework: str,
        result: Dict[str, Any]
    ):
        """Add analysis result to context"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            logger.warning(f"No index found for analysis {analysis_id}")
            return
        
        # Create document from result
        document = Document(
            text=json.dumps(result),
            metadata={
                "type": "analysis_result",
                "framework": framework,
                "analysis_id": analysis_id_str,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Insert into index
        self.indices[analysis_id_str].insert(document)
    
    async def add_chat_message(
        self,
        analysis_id: UUID,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add chat message to context"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            logger.warning(f"No index found for analysis {analysis_id}")
            return
        
        # Create document from message
        chat_text = f"User: {message}\nAssistant: {response}"
        document = Document(
            text=chat_text,
            metadata={
                "type": "chat_message",
                "analysis_id": analysis_id_str,
                "timestamp": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        )
        
        # Insert into index
        self.indices[analysis_id_str].insert(document)
    
    async def get_relevant_context(
        self,
        analysis_id: UUID,
        query: str,
        top_k: int = 5,
        context_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context for a query"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            logger.warning(f"No index found for analysis {analysis_id}")
            return []
        
        index = self.indices[analysis_id_str]
        
        # Create retriever
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=top_k
        )
        
        # Apply filters if context type specified
        if context_type:
            retriever.filters = {"type": context_type}
        
        # Retrieve nodes
        nodes = retriever.retrieve(query)
        
        # Extract relevant information
        context_items = []
        for node in nodes:
            context_items.append({
                "content": node.node.text,
                "metadata": node.node.metadata,
                "score": node.score
            })
        
        return context_items
    
    async def get_conversation_history(
        self,
        analysis_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            return []
        
        # Retrieve chat messages
        context_items = await self.get_relevant_context(
            analysis_id,
            "conversation history",
            top_k=limit,
            context_type="chat_message"
        )
        
        # Convert to dict format
        messages = []
        for item in context_items:
            messages.append({
                "content": item["content"],
                "timestamp": item["metadata"].get("timestamp"),
                "metadata": item["metadata"]
            })
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get("timestamp", ""))
        
        return messages
    
    async def get_analysis_artifacts(
        self,
        analysis_id: UUID,
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get artifacts from previous analyses"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            return {}
        
        # Build query
        query = f"artifacts from {framework} analysis" if framework else "analysis artifacts"
        
        # Retrieve artifacts
        context_items = await self.get_relevant_context(
            analysis_id,
            query,
            top_k=20,
            context_type="artifact"
        )
        
        # Organize artifacts by type
        artifacts = {}
        for item in context_items:
            artifact_type = item["metadata"].get("type", "").replace("artifact_", "")
            if artifact_type:
                try:
                    artifacts[artifact_type] = json.loads(item["content"])
                except json.JSONDecodeError:
                    artifacts[artifact_type] = item["content"]
        
        return artifacts
    
    async def synthesize_context_summary(
        self,
        analysis_id: UUID,
        query: str
    ) -> str:
        """Synthesize a summary of relevant context"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            return "No context available for this analysis."
        
        index = self.indices[analysis_id_str]
        
        # Create query engine
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            response_synthesizer=get_response_synthesizer(
                response_mode="tree_summarize"
            )
        )
        
        # Get response
        response = query_engine.query(query)
        
        return str(response)
    
    async def cleanup_analysis_context(self, analysis_id: UUID):
        """Clean up context for completed analysis"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str in self.indices:
            del self.indices[analysis_id_str]
        
        if analysis_id_str in self.storage_contexts:
            del self.storage_contexts[analysis_id_str]
    
    def get_context_stats(self, analysis_id: UUID) -> Dict[str, Any]:
        """Get statistics about stored context"""
        analysis_id_str = str(analysis_id)
        
        if analysis_id_str not in self.indices:
            return {"status": "no_context"}
        
        index = self.indices[analysis_id_str]
        storage_context = self.storage_contexts[analysis_id_str]
        
        # Get document count by type
        doc_types = {}
        for doc_id in storage_context.docstore.docs:
            doc = storage_context.docstore.get_document(doc_id)
            doc_type = doc.metadata.get("type", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            "status": "active",
            "total_documents": len(storage_context.docstore.docs),
            "document_types": doc_types,
            "index_size": len(index.vector_store._data) if hasattr(index.vector_store, "_data") else "unknown"
        }


# Global context manager instance
context_manager = ContextManager()
