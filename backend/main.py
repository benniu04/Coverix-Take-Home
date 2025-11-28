import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Conversation, Message
from schemas import ChatRequest, ChatResponse, ConversationResponse
from conversation_engine import ConversationEngine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Insurance Onboarding Chatbot",
    description="Conversational chatbot for insurance onboarding",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize conversation engine
conversation_engine = ConversationEngine()


@app.get("/")
async def root():
    return {"message": "Insurance Onboarding Chatbot API", "status": "running"}


@app.post("/api/conversation/start")
async def start_conversation(db: Session = Depends(get_db)):
    """Start a new conversation session."""
    
    session_id = str(uuid.uuid4())
    
    conversation = Conversation(session_id=session_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Get welcome message
    welcome_message = await conversation_engine.get_welcome_message(conversation, db)
    
    return {
        "session_id": session_id,
        "message": welcome_message,
        "current_state": conversation.current_state
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Process a chat message."""
    
    # Find conversation
    conversation = db.query(Conversation).filter(
        Conversation.session_id == request.session_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Process the message
    response = await conversation_engine.process_message(
        conversation=conversation,
        user_message=request.message,
        db=db
    )
    
    db.refresh(conversation)
    
    return ChatResponse(
        session_id=request.session_id,
        response=response,
        current_state=conversation.current_state,
        is_complete=conversation.current_state == "complete"
    )


@app.get("/api/conversation/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str, db: Session = Depends(get_db)):
    """Get conversation details and history."""
    
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@app.get("/api/conversations")
async def list_conversations(db: Session = Depends(get_db)):
    """List all conversations (for admin/debugging)."""
    
    conversations = db.query(Conversation).order_by(
        Conversation.created_at.desc()
    ).limit(50).all()
    
    return [
        {
            "session_id": c.session_id,
            "current_state": c.current_state,
            "full_name": c.full_name,
            "email": c.email,
            "vehicles_count": len(c.vehicles),
            "messages_count": len(c.messages),
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in conversations
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

