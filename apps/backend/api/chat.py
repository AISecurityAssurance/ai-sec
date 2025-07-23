"""
Chat API routes
Handles conversational AI interactions about analyses
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from core.database import get_db
from core.models.database import ChatMessage, Analysis
from core.models.schemas import AnalysisStatus
from core.utils.llm_client import llm_manager
from config.settings import settings
from core.context import context_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat message request"""
    message: str
    analysis_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat message response"""
    id: UUID
    message: str
    response: str
    analysis_id: Optional[UUID]
    timestamp: datetime
    metadata: Dict[str, Any]


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    messages: List[ChatResponse]
    total: int


async def build_chat_context(
    analysis_id: Optional[UUID],
    db: AsyncSession,
    user_message: str
) -> str:
    """Build context for chat based on analysis using LlamaIndex"""
    context_parts = []
    
    if analysis_id:
        # Get analysis details
        analysis = await db.get(Analysis, analysis_id)
        if analysis:
            context_parts.append(f"System Description: {analysis.system_description}")
            context_parts.append(f"Analysis Status: {analysis.status}")
            context_parts.append(f"Frameworks: {', '.join(analysis.frameworks)}")
            
            # Get analysis results if completed
            if analysis.status == AnalysisStatus.COMPLETED:
                from core.models.database import AnalysisResult
                from sqlalchemy import select
                
                results = await db.execute(
                    select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
                )
                analysis_results = results.scalars().all()
                
                if analysis_results:
                    context_parts.append("\n## Analysis Results Summary:")
                    for result in analysis_results:
                        context_parts.append(f"\n### {result.framework.value.upper()} Analysis:")
                        if result.sections:
                            for section in result.sections[:3]:  # First 3 sections
                                context_parts.append(f"- {section.get('title', 'Unknown')}: {section.get('status', 'pending')}")
                        if result.artifacts:
                            context_parts.append(f"  Total findings: {len(result.artifacts)}")
            
            # Get relevant context from LlamaIndex
            try:
                # Get relevant artifacts
                relevant_context = await context_manager.get_relevant_context(
                    analysis_id,
                    user_message,
                    top_k=5
                )
                
                if relevant_context:
                    context_parts.append("\n## Relevant Analysis Context:")
                    for item in relevant_context:
                        metadata = item["metadata"]
                        content_preview = item["content"][:300] + "..." if len(item["content"]) > 300 else item["content"]
                        context_parts.append(f"\n### {metadata.get('type', 'Unknown')} - {metadata.get('framework', 'Unknown')}:")
                        context_parts.append(content_preview)
                
                # Get recent conversation history
                chat_history = await context_manager.get_conversation_history(
                    analysis_id,
                    limit=5
                )
                
                if chat_history:
                    context_parts.append("\n## Recent Conversation:")
                    for msg in chat_history[-3:]:  # Last 3 messages
                        context_parts.append(f"\n{msg.role}: {msg.content[:200]}...")
                        
            except Exception as e:
                logger.warning(f"Failed to get LlamaIndex context: {e}")
                # Fall back to basic context
                from core.models.database import AnalysisResult
                results = await db.execute(
                    select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
                )
                results = results.scalars().all()
                
                for result in results:
                    context_parts.append(f"\n{result.framework.value} Analysis:")
                    for section in result.sections:
                        context_parts.append(f"- {section['title']}: {section.get('status', 'pending')}")
                    
    return "\n".join(context_parts)


@router.post("/", response_model=ChatResponse)
async def create_chat_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message and get AI response"""
    # Build context
    context = await build_chat_context(request.analysis_id, db, request.message)
    
    # Prepare prompt
    system_prompt = """You are the SA Agent (Security Analyst Agent), an expert in systems security and cybersecurity analysis. 
    Your primary focus is on security threat modeling, vulnerability assessment, and risk analysis.
    
    When discussing frameworks like PASTA, STRIDE, STPA-SEC, DREAD, etc., always interpret them in the security context:
    - PASTA: Process for Attack Simulation and Threat Analysis (NOT the food)
    - STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege
    - STPA-SEC: System-Theoretic Process Analysis for Security
    - DREAD: Damage, Reproducibility, Exploitability, Affected Users, Discoverability
    
    If an analysis has been performed, reference the specific findings and provide insights based on the actual results.
    Always maintain a professional, security-focused perspective in your responses."""
    
    user_prompt = request.message
    if context:
        user_prompt = f"Context:\n{context}\n\nUser Question: {request.message}"
    
    # Get AI response
    try:
        response = await llm_manager.generate(
            user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Store chat message
        chat_message = ChatMessage(
            id=uuid4(),
            analysis_id=request.analysis_id,
            message=request.message,
            response=response.content,
            metadata={
                "model": response.model,
                "tokens": response.usage
            }
        )
        
        db.add(chat_message)
        await db.commit()
        
        # Add to context manager
        if request.analysis_id:
            try:
                # Add user message
                await context_manager.add_chat_message(
                    request.analysis_id,
                    {
                        "role": "user",
                        "content": request.message,
                        "timestamp": datetime.utcnow()
                    }
                )
                
                # Add assistant response
                await context_manager.add_chat_message(
                    request.analysis_id,
                    {
                        "role": "assistant",
                        "content": response.content,
                        "timestamp": datetime.utcnow()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to add to context manager: {e}")
        
        return ChatResponse(
            id=chat_message.id,
            message=chat_message.message,
            response=chat_message.response,
            analysis_id=chat_message.analysis_id,
            timestamp=chat_message.created_at,
            metadata=chat_message.metadata
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    analysis_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history"""
    query = select(ChatMessage)
    if analysis_id:
        query = query.where(ChatMessage.analysis_id == analysis_id)
        
    query = query.order_by(ChatMessage.created_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Get total count
    from sqlalchemy import func
    count_query = select(func.count(ChatMessage.id))
    if analysis_id:
        count_query = count_query.where(ChatMessage.analysis_id == analysis_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    return ChatHistoryResponse(
        messages=[
            ChatResponse(
                id=msg.id,
                message=msg.message,
                response=msg.response,
                analysis_id=msg.analysis_id,
                timestamp=msg.created_at,
                metadata=msg.project_metadata if hasattr(msg, 'project_metadata') else {}
            )
            for msg in messages
        ],
        total=total
    )


@router.get("/{message_id}", response_model=ChatResponse)
async def get_chat_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific chat message"""
    message = await db.get(ChatMessage, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    return ChatResponse(
        id=message.id,
        message=message.message,
        response=message.response,
        analysis_id=message.analysis_id,
        timestamp=message.created_at,
        metadata=message.metadata
    )


@router.delete("/{message_id}")
async def delete_chat_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat message"""
    message = await db.get(ChatMessage, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    await db.delete(message)
    await db.commit()
    
    return {"message": "Chat message deleted"}


class SuggestionsRequest(BaseModel):
    """Request for chat suggestions"""
    analysis_id: UUID


@router.post("/suggestions")
async def get_chat_suggestions(
    request: SuggestionsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Get suggested questions based on analysis"""
    # Get analysis context
    context = await build_chat_context(request.analysis_id, db, "Generate question suggestions")
    
    # Generate suggestions
    prompt = f"""Based on this security analysis context:
    {context}
    
    Generate 5 relevant questions a user might ask about the analysis results.
    Format as a JSON array of strings."""
    
    try:
        response = await llm_manager.generate(
            prompt,
            temperature=0.8,
            max_tokens=300
        )
        
        # Parse suggestions (simple approach - could be improved)
        import json
        try:
            suggestions = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract suggestions from text
            lines = response.content.split('\n')
            suggestions = [line.strip('- 1234567890."') for line in lines if line.strip() and not line.startswith('#')][:5]
        
        return {"suggestions": suggestions[:5]}
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return {
            "suggestions": [
                "What are the main security risks identified?",
                "Which hazards have the highest priority?",
                "What security controls are recommended?",
                "How do the different framework results compare?",
                "What should be our immediate next steps?"
            ]
        }