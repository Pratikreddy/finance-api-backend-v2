from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import json
from datetime import datetime
from llm_agent.agent_multi import run_pinescript_agent
from services.chat_service import ChatService
from core.auth import get_current_user, User

# Create FastAPI app
app = FastAPI(
    title="Finance Trading Assistant API",
    description="LangServe API for trading strategy consultation and PineScript generation",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create chat service instance
chat_service = ChatService()

# Main chat endpoint that uses headers ONLY
@app.post("/chat/invoke")
async def chat_with_header(
    request: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    """
    Chat endpoint that uses header authentication
    """
    query = request.get("query", "")
    conversation_id = request.get("conversation_id")
    
    # Use chat service with user from header
    response = await chat_service.process_chat(
        user_uuid=user.uuid,
        query=query,
        conversation_id=conversation_id,
    )
    
    return {"output": response, "metadata": {"run_id": "", "feedback_tokens": []}}

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "type": "LangServe API",
        "features": [
            "LangGraph-powered agent execution",
            "Token usage tracking and cost calculation",
            "PineScript code generation", 
            "Trading strategy consultation",
            "React component visualizations",
            "ApexCharts integration",
            "Conversation summaries",
            "Markdown formatted responses"
        ]
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Finance Trading Assistant API",
        "version": "3.0.0",
        "endpoints": {
            "chat": "/chat/invoke",
            "threads": {
                "new": "/threads/new",
                "list": "/threads/list",
                "get": "/threads/{id}",
                "rename": "/threads/{id}/rename",
                "delete": "/threads/{id}"
            }
        },
        "docs": "/docs",
        "authentication": "All endpoints require x-user-uuid header",
        "example": {
            "url": "POST /chat/invoke",
            "headers": {
                "x-user-uuid": "your-user-uuid",
                "Content-Type": "application/json"
            },
            "request": {
                "query": "Create a simple RSI strategy with visual representation",
                "conversation_id": "optional-existing-conversation-id"
            },
            "response": {
                "output": {
                    "answer": "# RSI Trading Strategy\n\n## Overview\nThe **Relative Strength Index (RSI)** is a momentum oscillator...\n\n## PineScript Implementation\n\n```pinescript\n//@version=5\nstrategy('RSI Strategy', overlay=true)...\n```\n\n## Visualization\n\n```jsx\nimport { Card } from '@/components/ui/card'...\n```",
                    "chatsummary": "User requested RSI strategy with visualizations",
                    "whatsapp_summary": "*RSI Trading Strategy*\n\nKey Parameters:\n• RSI Length: 14\n• Overbought: 70\n• Oversold: 30\n\nStrategy uses RSI to identify overbought/oversold conditions...\n\n_Full implementation included_",
                    "conversation_id": "uuid-of-conversation",
                    "tokens_used": 3456,
                    "cost": 0.0345
                },
                "metadata": {
                    "run_id": "",
                    "feedback_tokens": []
                }
            }
        }
    }

# Thread management routes
@app.post("/threads/new")
async def create_thread(
    request: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    """Create a new conversation thread"""
    thread_name = request.get("thread_name")
    conversation_id = chat_service.storage.create_conversation(
        user_uuid=user.uuid,
        thread_name=thread_name
    )
    # Get the actual thread name from storage
    conversation = chat_service.get_conversation(user.uuid, conversation_id)
    return {
        "conversation_id": conversation_id,
        "thread_name": conversation["thread_name"]
    }

@app.get("/threads/list")
async def list_threads(user: User = Depends(get_current_user)):
    """List all conversation threads for a user"""
    conversations = chat_service.list_conversations(user.uuid)
    return {"conversations": conversations}

@app.get("/threads/{conversation_id}")
async def get_thread(
    conversation_id: str,
    user: User = Depends(get_current_user)
):
    """Get a specific conversation thread"""
    conversation = chat_service.get_conversation(user.uuid, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.put("/threads/{conversation_id}/rename")
async def rename_thread(
    conversation_id: str,
    request: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    """Rename a conversation thread"""
    new_name = request.get("new_name")
    if not new_name:
        raise HTTPException(status_code=400, detail="new_name is required")
    
    success = chat_service.rename_conversation(user.uuid, conversation_id, new_name)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "new_name": new_name}

@app.delete("/threads/{conversation_id}")
async def delete_thread(
    conversation_id: str,
    user: User = Depends(get_current_user)
):
    """Delete a conversation thread"""
    success = chat_service.delete_conversation(user.uuid, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True}