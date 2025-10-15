# backend/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        nome=user.nome,
        sobrenome=user.sobrenome,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# Message CRUD operations
def create_message(db: Session, message: schemas.MessageCreate, sender_id: int):
    db_message = models.Message(
        sender_id=sender_id,
        recipient_id=message.recipient_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_between_users(db: Session, user1_id: int, user2_id: int, skip: int = 0, limit: int = 50):
    return db.query(models.Message).filter(
        ((models.Message.sender_id == user1_id) & (models.Message.recipient_id == user2_id)) |
        ((models.Message.sender_id == user2_id) & (models.Message.recipient_id == user1_id))
    ).order_by(models.Message.created_at.desc()).offset(skip).limit(limit).all()

def mark_messages_as_read(db: Session, user_id: int, sender_id: int):
    db.query(models.Message).filter(
        models.Message.recipient_id == user_id,
        models.Message.sender_id == sender_id,
        models.Message.is_read == False
    ).update({"is_read": True})
    db.commit()

