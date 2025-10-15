# backend/app/schemas.py

from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    nome: str
    sobrenome: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    avatar_url: Optional[str] = None

class User(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    messages_sent: list[MessageOut] = []
    messages_received: list[MessageOut] = []

    class Config:
        from_attributes = True



# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Message Schemas
class MessageBase(BaseModel):
    recipient_id: int
    content: str

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    sender: "UserInDB"  # Usar um schema de usuário de saída
    recipient: "UserInDB"  # Usar um schema de usuário de saída

class UserInDB(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


User.update_forward_refs()
MessageOut.update_forward_refs()
UserInDB.update_forward_refs()

# Simulator Schemas
class SimulatorConfig(BaseModel):
    estrategia: str
    aposta_inicial: float
    saldo_inicial: float
    max_rodadas: int
    cor_alvo: Optional[str] = None
    gatilho_cor: Optional[str] = None
    gatilho_contagem: Optional[int] = None

