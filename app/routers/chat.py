
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict

from app import crud, schemas, models
from app.database import get_db
from app.security import get_current_user, get_current_user_websocket
import json

router = APIRouter(prefix="/chat", tags=["chat"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: models.User = Depends(get_current_user_websocket), db: Session = Depends(get_db)):
    # TODO: Implement proper authentication for WebSocket connection
    # For now, we'll assume the user_id is valid and authenticated
    user_id = current_user.id
    # The user is already authenticated by get_current_user_websocket


    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Assuming data is a JSON string with 'recipient_id' and 'content'
            message_data = json.loads(data)
            recipient_id = message_data.get("recipient_id")
            content = message_data.get("content")

            if recipient_id and content:
                message_create = schemas.MessageCreate(recipient_id=recipient_id, content=content)
                db_message = crud.create_message(db, message=message_create, sender_id=user_id)
                
                # Send message to recipient if connected
                await manager.send_personal_message(json.dumps({
                    "sender_id": user_id,
                    "content": content,
                    "created_at": db_message.created_at.isoformat()
                }), recipient_id)
                # Optionally, send confirmation to sender
                await manager.send_personal_message(json.dumps({
                    "status": "sent",
                    "recipient_id": recipient_id,
                    "content": content
                }), user_id)
            else:
                await manager.send_personal_message(json.dumps({"error": "Invalid message format"}), user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"Client #{user_id} left")

@router.get("/messages/{recipient_id}", response_model=List[schemas.MessageOut])
def get_user_messages(
    recipient_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    messages = crud.get_messages_between_users(db, current_user.id, recipient_id, skip=skip, limit=limit)
    # Mark messages from recipient as read
    crud.mark_messages_as_read(db, current_user.id, recipient_id)
    return messages

