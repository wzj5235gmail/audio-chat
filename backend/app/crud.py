from . import schemas
from .database import db
from .security import hash_password
from . import models as models
from bson import ObjectId
import time
import base64


async def create_character_if_not_exists(
    name: str,
    avatar_uri: str,
    gpt_model_path: str,
    sovits_model_path: str,
    refer_path: str,
    refer_text: str,
    prompt: str,
):
    existing_character = await get_character(name)
    if existing_character:
        return existing_character
    db_character = models.Character(
        name=name,
        avatar_uri=avatar_uri,
        gpt_model_path=gpt_model_path,
        sovits_model_path=sovits_model_path,
        refer_path=refer_path,
        refer_text=refer_text,
        prompt=prompt,
    )
    await db.characters.insert_one(db_character.model_dump())
    return await get_character(name)


async def get_character(name: str):
    character = await db.characters.find_one({"name": name})
    if not character:
        return None
    character = schemas.Character(**character)
    return character


async def get_character_by_id(character_id: str):
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        return None
    character = schemas.Character(**character)
    return character


async def get_characters(skip: int = 0, limit: int = 100):
    characters = (
        await db.characters.find().skip(skip).limit(limit).to_list(length=limit)
    )
    characters = [schemas.Character(**character) for character in characters]
    return characters


async def get_user(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    user = schemas.UserFromDB(**user)
    return user


async def get_user_by_username(username: str):
    user = await db.users.find_one({"username": username})
    if not user:
        return None
    user = schemas.UserFromDB(**user)
    return user


async def get_users(skip: int = 0, limit: int = 20):
    users = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
    users = [schemas.UserFromDB(**user) for user in users]
    return users


async def create_user(user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    await db.users.insert_one(db_user.model_dump())
    db_user = await db.users.find_one({"username": user.username})
    db_user = schemas.User(**db_user)
    return db_user


async def get_conversations(
    user_id: str, character_id: str, skip: int = 0, limit: int = 20
):
    conversations = (
        await db.conversations.find({"user_id": user_id, "character_id": character_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(length=limit)
    )
    return conversations


async def create_conversation(
    conversation: schemas.ConversationCreate,
):
    db_conversation = models.Conversation(
        **conversation, created_at=str(int(time.time() * 1000))
    )
    res = await db.conversations.insert_one(db_conversation.model_dump())
    conversation = await db.conversations.find_one({"_id": res.inserted_id})
    conversation = schemas.Conversation(**conversation)
    return conversation


async def get_all_characters(skip: int = 0, limit: int = 100):
    characters = (
        await db.characters.find().skip(skip).limit(limit).to_list(length=limit)
    )
    characters = [schemas.Character(**character) for character in characters]
    return characters


async def get_conversation(conversation_id: str):
    conversation = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
    conversation = schemas.Conversation(**conversation)
    return conversation


async def update_conversation_audio(conversation_id: str, audio: str):
    audio = base64.b64decode(audio)
    await db.conversations.update_one(
        {"_id": ObjectId(conversation_id)}, {"$set": {"audio": audio}}
    )
    update_result = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
    if update_result:
        return True
    return False


async def search_character_by_name(name: str, limit: int = 10):
    characters = await db.characters.find(
        {"name": {"$regex": name, "$options": "i"}}
    ).to_list(length=limit)
    characters = [schemas.Character(**character) for character in characters]
    return characters


async def update_user_chat_remaining(user_id: str, chat_remaining: int):
    await db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"chat_remaining": chat_remaining}}
    )
