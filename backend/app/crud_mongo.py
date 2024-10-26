from mongoengine import connect
from .security import hash_password
from . import models, schemas
import time

# Assuming you've set up the MongoDB connection elsewhere
# connect('your_database_name')

def create_character_if_not_exists(
        name: str,
        avatar_uri: str,
        gpt_model_path: str,
        sovits_model_path: str,
        refer_path: str,
        refer_text: str
    ):
    existing_character = get_character(name)
    if existing_character:
        return existing_character
    db_character = models.Character(
        name=name,
        avatar_uri=avatar_uri,
        gpt_model_path=gpt_model_path,
        sovits_model_path=sovits_model_path,
        refer_path=refer_path,
        refer_text=refer_text
    )
    db_character.save()
    return db_character

def get_character(name: str):
    return models.Character.objects(name=name).first()

def get_characters(skip: int = 0, limit: int = 100):
    return models.Character.objects.skip(skip).limit(limit)

def get_user(user_id: str):
    return models.User.objects(id=user_id).first()

def get_user_by_username(username: str):
    return models.User.objects(username=username).first()

def get_users(skip: int = 0, limit: int = 20):
    return models.User.objects.skip(skip).limit(limit)

def create_user(user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db_user.save()
    return db_user

def get_conversations(user_id: str, character_id: str, skip: int = 0, limit: int = 20):
    return models.Conversation.objects(
        user=user_id,
        character=character_id
    ).order_by('-created_at').skip(skip).limit(limit)

def create_conversation(conversation: schemas.ConversationCreate):
    db_conversation = models.Conversation(
        message=conversation.message,
        role=conversation.role,
        translation=conversation.translation,
        user=conversation.user_id,
        character=conversation.character_id,
        created_at=str(int(time.time() * 1000))
    )
    db_conversation.save()
    return db_conversation

def get_all_characters(skip: int = 0, limit: int = 100):
    return models.Character.objects.skip(skip).limit(limit)