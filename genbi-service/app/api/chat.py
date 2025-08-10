"""
Chat API routes for LibreChat integration.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio

from app.database import get_db
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.agents.crew_manager import CrewManager

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.post("/", response_model=dict)
async def chat_message(
    message: dict,
    db: Session = Depends(get_db)
):
    """
    Handle chat messages and route to appropriate analysis.
    
    Expected message format:
    {
        "message": "Analyze sales data for Q4",
        "context": "analysis_request",
        "analysis_type": "trend_analysis",
        "data_source": "sales_data.csv"
    }
    """
    try:
        user_message = message.get("message", "")
        context = message.get("context", "general")
        analysis_type = message.get("analysis_type", "custom")
        data_source = message.get("data_source")
        
        if context == "analysis_request":
            # Route to analysis service
            analysis_service = AnalysisService()
            
            result = await analysis_service.run_analysis(
                db=db,
                query=user_message,
                analysis_type=analysis_type,
                data_source=data_source
            )
            
            return {
                "response": f"Analysis task created with ID: {result['task_id']}",
                "task_id": result["task_id"],
                "status": result["status"],
                "type": "analysis_response"
            }
        else:
            # General chat response
            crew_manager = CrewManager()
            result = await crew_manager.run_analysis(
                query=user_message,
                analysis_type="general_chat"
            )
            
            return {
                "response": result.get("result", "I'm here to help with your analysis needs!"),
                "type": "chat_response"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process the message
            response = await process_websocket_message(message, client_id)
            
            # Send response back
            await manager.send_personal_message(
                json.dumps(response), 
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def process_websocket_message(message: dict, client_id: str) -> dict:
    """Process WebSocket messages."""
    try:
        user_message = message.get("message", "")
        context = message.get("context", "general")
        
        if context == "analysis_request":
            # Create analysis task
            crew_manager = CrewManager()
            result = await crew_manager.run_analysis(
                query=user_message,
                analysis_type="custom"
            )
            
            return {
                "type": "analysis_response",
                "task_id": result.get("task_id"),
                "status": result.get("status"),
                "message": f"Analysis task created: {result.get('task_id')}",
                "client_id": client_id
            }
        else:
            # General chat response
            return {
                "type": "chat_response",
                "message": f"Received: {user_message}",
                "client_id": client_id
            }
            
    except Exception as e:
        return {
            "type": "error",
            "message": f"Error processing message: {str(e)}",
            "client_id": client_id
        }


@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a user."""
    # This would typically fetch from a chat history table
    # For now, return analysis tasks as chat history
    analysis_service = AnalysisService()
    tasks = await analysis_service.get_all_tasks(db, skip=0, limit=limit)
    
    return {
        "user_id": user_id,
        "history": [
            {
                "id": task.id,
                "message": task.query,
                "response": task.result,
                "timestamp": task.created_at,
                "type": "analysis"
            }
            for task in tasks
        ]
    }


@router.delete("/history/{user_id}")
async def clear_chat_history(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Clear chat history for a user."""
    # This would typically delete from a chat history table
    return {
        "message": f"Chat history cleared for user {user_id}",
        "user_id": user_id
    } 