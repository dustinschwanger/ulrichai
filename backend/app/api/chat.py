from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import logging

from ..services.chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    session_id: str
    timestamp: str

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """Process a chat query and return AI response with sources"""
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Validate query
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query is too long (max 2000 characters)")
    
    try:
        # Process query
        logger.info(f"Processing query: {request.query[:100]}...")
        response = await chat_service.process_query(request.query, session_id)
        
        # Add session ID to response
        response["session_id"] = session_id
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")

@router.get("/test")
async def test_chat():
    """Test endpoint to verify chat service is working"""
    
    try:
        # Check if we have documents in vector store
        from ..core.vector_store import vector_store
        stats = vector_store.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        return {
            "status": "ready",
            "vector_count": total_vectors,
            "message": f"Chat service is ready with {total_vectors} vectors indexed"
        }
        
    except Exception as e:
        logger.error(f"Chat test failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    message_id: str,
    feedback: str,
    rating: Optional[int] = None
):
    """Submit feedback for a chat response"""
    
    try:
        # Log feedback to analytics
        if chat_service.db.engine:
            from sqlalchemy import text
            from datetime import datetime
            import json
            
            with chat_service.db.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO analytics_events (event_type, event_data, session_id, created_at)
                        VALUES (:event_type, :event_data, :session_id, :created_at)
                    """),
                    {
                        'event_type': 'chat_feedback',
                        'event_data': json.dumps({
                            'message_id': message_id,
                            'feedback': feedback,
                            'rating': rating
                        }),
                        'session_id': session_id,
                        'created_at': datetime.now()
                    }
                )
                conn.commit()
        
        return {"status": "success", "message": "Feedback recorded"}
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Error recording feedback")