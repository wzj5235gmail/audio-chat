import shutil
import time
import os
from fastapi.security import OAuth2PasswordRequestForm
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from fastapi import (
    File,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from typing import Annotated
from . import configs, crud, schemas, security
from .utils import (
    get_current_user_from_token,
    chat_with_history,
    translate_chain_en,
    translate_chain_zh,
    client,
)
import logging
import traceback
import base64

logger = logging.getLogger(__name__)


async def chat_handler(
    request: Request,
    character_id: str,
    message: schemas.Message,
):
    try:
        # Get the user's info from the token
        current_user = get_current_user_from_token(request)
        user_in_db = await crud.get_user(user_id=current_user["user_id"])
        chat_remaining = user_in_db.chat_remaining
        if chat_remaining <= 0:
            return {
                "status_code": 400,
                "error": "No chat chances remaining",
            }
        # Update the user's chat remaining
        await crud.update_user_chat_remaining(
            user_id=current_user["user_id"], chat_remaining=chat_remaining - 1
        )
        # Get the user's conversation history
        user_id = current_user["user_id"]
        # Use RedisChatMessageHistory with a combined session_id
        session_id = f"{user_id}_{character_id}"
        chat_history = RedisChatMessageHistory(
            session_id=session_id,
            url=(
                os.environ.get("REDIS_URL_DOCKER")
                if os.environ.get("ENV") == "production"
                else os.environ.get("REDIS_URL_LOCAL")
            ),
        )

        # Check if the chat history is empty
        if len(chat_history.messages) == 0:
            # Get the user's conversation history from the database
            conversations = await crud.get_conversations(
                user_id=user_id,
                character_id=character_id,
                limit=configs.max_chat_history,
            )
            # Add the user's conversation history to the RedisChatMessageHistory
            conversations.reverse()
            for con in conversations:
                if con["role"] == "user":
                    chat_history.add_user_message(con["message"])
                elif con["role"] == "assistant":
                    chat_history.add_ai_message(con["message"])

        # If the chat history is longer than the maximum length, truncate it
        if len(chat_history.messages) > configs.max_chat_history:
            truncated_messages = chat_history.messages[-configs.max_chat_history :]
            chat_history.clear()
            for msg in truncated_messages:
                chat_history.add_message(msg)

        # Add the user's message to database
        await crud.create_conversation(
            conversation={
                "message": message.content,
                "role": "user",
                "user_id": user_id,
                "character_id": character_id,
            },
        )
        # Set the session_id and character_prompt in the config
        character = await crud.get_character_by_id(character_id)
        config = {
            "configurable": {
                "session_id": session_id,
                "character_prompt": character.prompt,
            }
        }

        # Get the bot's response
        chat_reply = chat_with_history.invoke(
            {
                "messages": [HumanMessage(content=message.content)],
                "character_prompt": character.prompt,
            },
            config=config,
        ).content

        # Translate the bot's response
        if message.language == "en":
            translation = translate_chain_en.invoke(
                {"messages": [HumanMessage(content=chat_reply)]}
            ).content
        elif message.language == "zh":
            translation = translate_chain_zh.invoke(
                {"messages": [HumanMessage(content=chat_reply)]}
            ).content
        # Add the bot's response to database
        conversation = await crud.create_conversation(
            conversation={
                "message": chat_reply,
                "translation": translation,
                "role": "assistant",
                "user_id": user_id,
                "character_id": character_id,
            },
        )
        return {
            "status_code": 200,
            "id": conversation.id,
            "message": conversation.message,
            "translation": conversation.translation,
        }
    except Exception as e:
        logger.error(f"Error during chat: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


def stt_handler(
    request: Request,
    audio: Annotated[UploadFile, File()],
):
    try:
        current_user = get_current_user_from_token(request)
        supported_formats = [
            "audio/flac",
            "audio/m4a",
            "audio/mp3",
            "audio/mp4",
            "audio/mpeg",
            "audio/mpga",
            "audio/oga",
            "audio/ogg",
            "audio/wav",
            "audio/webm",
        ]
        if audio.content_type not in supported_formats:
            return {
                "error": "Unsupported file format. Please upload a valid audio file."
            }
        file_location = f"{audio.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        try:
            file = open(file_location, "rb")
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=file,
            )
            file.close()
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return {"error": str(e)}
        os.remove(file_location)
        return {
            "transcription": transcription.text,
        }
    except Exception as e:
        logger.error(f"Error during stt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_characters_handler(
    skip: int,
    limit: int,
) -> list[schemas.Character]:
    logger.info("querying database...")
    return await crud.get_characters(skip=skip, limit=limit)


async def create_user_handler(
    user: schemas.UserCreate,
) -> schemas.User:
    db_user = await crud.get_user_by_username(username=user.username)
    if db_user:
        logger.error("Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(user=user)


async def read_users_handler(
    skip: int,
    limit: int,
) -> list[schemas.User]:
    return await crud.get_users(skip=skip, limit=limit)


async def read_user_handler(
    user_id: str,
) -> schemas.User:
    db_user = await crud.get_user(user_id=user_id)
    if db_user is None:
        logger.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


async def create_conversation_handler(
    conversation: schemas.ConversationCreate,
) -> schemas.Conversation:
    return await crud.create_conversation(conversation=conversation.model_dump())


async def get_conversations_handler(
    user_id: str,
    character_id: str,
    skip: int,
    limit: int,
) -> list[schemas.Conversation]:
    conversations = await crud.get_conversations(
        user_id=user_id, character_id=character_id, skip=skip, limit=limit
    )
    for con in conversations:
        if "audio" in con and con["audio"] is not None:
            con["audio"] = base64.b64encode(con["audio"]).decode("utf-8")
    conversations.reverse()
    return conversations


async def create_token_handler(
    form_data: OAuth2PasswordRequestForm,
) -> dict:
    user = await crud.get_user_by_username(username=form_data.username)
    user.id = str(user.id)
    if not user:
        logger.error("Invalid username")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        logger.error("Invalid password")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = security.generate_token(str(user.id), user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": int(time.time())
        + 60 * int(os.environ.get("TOKEN_EXPIRE_MINUTES")),
        "user_id": user.id,
        "username": user.username,
        "nickname": user.nickname,
    }
