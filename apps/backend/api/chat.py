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
from core.utils.llm_client import llm_manager
from config.settings import settings

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
    db: AsyncSession
) -> str:
    """Build context for chat based on analysis"""
    context_parts = []
    
    if analysis_id:
        # Get analysis details
        analysis = await db.get(Analysis, analysis_id)
        if analysis:
            context_parts.append(f"System Description: {analysis.system_description}")
            
            # Get analysis results
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
    context = await build_chat_context(request.analysis_id, db)
    
    # Prepare prompt
    system_prompt = """You are an expert security analyst assistant. 
    You help users understand security analysis results, explain concepts, 
    and provide actionable recommendations based on various security frameworks 
    like STPA-Sec, STRIDE, PASTA, etc."""
    
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
    count_query = select(ChatMessage)
    if analysis_id:
        count_query = count_query.where(ChatMessage.analysis_id == analysis_id)
    total = await db.scalar(select(db.func.count()).select_from(count_query.subquery()))
    
    return ChatHistoryResponse(
        messages=[
            ChatResponse(
                id=msg.id,
                message=msg.message,
                response=msg.response,
                analysis_id=msg.analysis_id,
                timestamp=msg.created_at,
                metadata=msg.metadata
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


@router.post("/suggestions")
async def get_chat_suggestions(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get suggested questions based on analysis"""
    # Get analysis context
    context = await build_chat_context(analysis_id, db)
    
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
        suggestions = json.loads(response.content)
        
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