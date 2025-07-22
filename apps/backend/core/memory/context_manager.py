"""
Context Manager for handling analysis context and memory.
Uses LlamaIndex for efficient retrieval within context windows.
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from llama_index import (
    VectorStoreIndex, 
    Document,
    ServiceContext,
    StorageContext
)
from llama_index.embeddings import OpenAIEmbedding
from llama_index.llms import OpenAI
import tiktoken

from core.models.schemas import AnalysisResult
from storage.repositories.analysis import AnalysisRepository


class ContextManager:
    """
    Manages analysis context with:
    1. Token-aware context windowing
    2. Efficient artifact retrieval
    3. Cross-analysis referencing
    4. Version tracking
    """
    
    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        max_context_tokens: int = 8000
    ):
        self.repo = analysis_repo
        self.max_tokens = max_context_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize LlamaIndex
        self.service_context = ServiceContext.from_defaults(
            embed_model=OpenAIEmbedding(),
            llm=OpenAI(model="gpt-4")
        )
        
        # In-memory indices for active analyses
        self.indices: Dict[str, VectorStoreIndex] = {}
        
    async def initialize_analysis(
        self,
        analysis_id: str,
        system_description: str
    ):
        """Initialize context for new analysis"""
        # Create initial document
        doc = Document(
            text=system_description,
            metadata={
                "analysis_id": analysis_id,
                "type": "system_description",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Create index
        index = VectorStoreIndex.from_documents(
            [doc],
            service_context=self.service_context
        )
        
        self.indices[analysis_id] = index
        
    async def store_result(
        self,
        analysis_id: str,
        plugin_id: str,
        result: Any
    ):
        """Store analysis result in context"""
        # Serialize result
        result_text = self._serialize_result(result)
        
        # Create document
        doc = Document(
            text=result_text,
            metadata={
                "analysis_id": analysis_id,
                "plugin_id": plugin_id,
                "type": "analysis_result",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Add to index
        if analysis_id in self.indices:
            self.indices[analysis_id].insert(doc)
        else:
            # Recreate index from stored data
            await self._rebuild_index(analysis_id)
            self.indices[analysis_id].insert(doc)
            
    async def get_relevant_context(
        self,
        analysis_id: str,
        query: str,
        plugin_filter: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get relevant context for a query.
        Returns artifacts that fit within token limit.
        """
        if analysis_id not in self.indices:
            await self._rebuild_index(analysis_id)
            
        index = self.indices[analysis_id]
        
        # Query with metadata filters
        retriever = index.as_retriever(
            similarity_top_k=20,
            node_postprocessors=[
                self._create_token_limiter(self.max_tokens)
            ]
        )
        
        # Apply plugin filter if specified
        if plugin_filter:
            retriever.add_metadata_filter(
                "plugin_id",
                plugin_filter
            )
            
        # Get relevant nodes
        nodes = retriever.retrieve(query)
        
        # Convert to context dict
        context = {}
        current_tokens = 0
        
        for node in nodes:
            # Check token limit
            node_tokens = self._count_tokens(node.text)
            if current_tokens + node_tokens > self.max_tokens:
                break
                
            # Add to context
            plugin_id = node.metadata.get("plugin_id", "unknown")
            if plugin_id not in context:
                context[plugin_id] = []
                
            context[plugin_id].append({
                "text": node.text,
                "metadata": node.metadata,
                "score": node.score
            })
            
            current_tokens += node_tokens
            
        return context
        
    async def search_artifacts(
        self,
        analysis_id: str,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search artifacts for chat responses"""
        if analysis_id not in self.indices:
            await self._rebuild_index(analysis_id)
            
        index = self.indices[analysis_id]
        
        # Query index
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            response_mode="no_text"  # Just get nodes
        )
        
        response = query_engine.query(query)
        
        # Extract artifacts
        artifacts = []
        for node in response.source_nodes:
            artifacts.append({
                "text": node.text,
                "metadata": node.metadata,
                "score": node.score
            })
            
        return artifacts
        
    def _serialize_result(self, result: Any) -> str:
        """Serialize analysis result to text"""
        # Convert to JSON for now
        # TODO: Implement smarter serialization
        if hasattr(result, 'dict'):
            return json.dumps(result.dict(), indent=2)
        elif hasattr(result, '__dict__'):
            return json.dumps(result.__dict__, indent=2)
        else:
            return str(result)
            
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
        
    def _create_token_limiter(self, max_tokens: int):
        """Create token-aware postprocessor"""
        # TODO: Implement token limiter
        # This would track cumulative tokens and stop
        # when limit is reached
        pass
        
    async def _rebuild_index(self, analysis_id: str):
        """Rebuild index from stored data"""
        # Get all artifacts for analysis
        artifacts = await self.repo.get_artifacts(analysis_id)
        
        # Create documents
        docs = []
        for artifact in artifacts:
            doc = Document(
                text=artifact.content,
                metadata=artifact.metadata
            )
            docs.append(doc)
            
        # Create index
        if docs:
            index = VectorStoreIndex.from_documents(
                docs,
                service_context=self.service_context
            )
            self.indices[analysis_id] = index