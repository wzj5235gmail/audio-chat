from sqlalchemy.orm import Session
from .security import hash_password
from . import models, schemas
import time


def create_character_if_not_exists(
        db: Session, 
        name: str,
        avatar_uri: str,
        gpt_model_path: str,
        sovits_model_path: str,
        refer_path: str,
        refer_text: str
    ):
    existing_character = get_character(db, name)
    if existing_character:
        return existing_character
    db_character = models.Character(name=name, avatar_uri=avatar_uri, gpt_model_path=gpt_model_path, sovits_model_path=sovits_model_path, refer_path=refer_path, refer_text=refer_text)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def get_character(
        db: Session, 
        name: str
    ):
    return db.query(models.Character).filter(models.Character.name == name).first() 

def get_characters(
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ):
    return db.query(models.Character).offset(skip).limit(limit).all()

def get_user(
        db: Session, 
        user_id: int
    ):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(
        db: Session, 
        username: str
    ):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 20
    ):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(
        db: Session, 
        user: schemas.UserCreate
    ):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_conversations(
        db: Session, 
        user_id: int, 
        character_id: int, 
        skip: int = 0, 
        limit: int = 20
    ):
    return db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id).filter(
        models.Conversation.character_id == character_id).order_by(
        models.Conversation.created_at.desc()).offset(skip).limit(limit).all()


def create_conversation(
        db: Session, 
        conversation: schemas.ConversationCreate, 
    ):
    db_conversation = models.Conversation(
        **conversation, 
        created_at=str(int(time.time() * 1000))
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_all_characters(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Character).offset(skip).limit(limit).all()


def update_audio_url(db: Session, conversation_id: int, audio_url: str):
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    db_conversation.audio_url = audio_url
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_audio_url(db: Session, conversation_id: int):
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    return db_conversation.audio_url


def get_conversation(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()


def search_character_by_name(db: Session, name: str):
    return db.query(models.Character).filter(models.Character.name.like(f"%{name}%")).all()
