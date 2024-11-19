import shutil
import time
import os
from fastapi.security import OAuth2PasswordRequestForm
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
)
from typing import Annotated
from . import configs, crud_mongodb as crud, security, schemas_mongodb as schemas
from .utils import (
    get_current_user_from_token,
    chat_with_history,
    translate_chain_en,
    translate_chain_zh,
    client,
)
import boto3
import uuid
import logging
import traceback


logger = logging.getLogger(__name__)


async def chat_handler(
    request: Request,
    character_id: str,
    message: schemas.Message,
):
    try:
        # Get the user's info from the token
        current_user = get_current_user_from_token(request)
        # Get the user's conversation history
        user_id = current_user["user_id"]
        # Use RedisChatMessageHistory with a combined session_id
        session_id = f"{user_id}_{character_id}"
        chat_history = RedisChatMessageHistory(
            session_id=session_id,
            url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
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
                if con.role == "user":
                    chat_history.add_user_message(con.message)
                elif con.role == "assistant":
                    chat_history.add_ai_message(con.message)

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
    }


async def save_audio_handler(
    conversation_id: str,
    audio: UploadFile,
):
    print(f"Generating filename for audio with content type: {audio.content_type}")
    filename = f"{conversation_id}.{audio.content_type.split('/')[-1]}"
    print(f"Generated filename: {filename}")

    # Save to cloud storage or local filesystem
    print(f"Saving audio file {filename} for conversation {conversation_id}")
    audio_url = save_to_storage(audio.file, filename, conversation_id, to="local")
    logger.info(f"Saved audio to local: {audio_url}")

    print(f"Updating audio URL in database for conversation {conversation_id}")
    await crud.update_audio_url(conversation_id, audio_url)
    logger.info(f"Updated conversation: {conversation_id}")

    print(f"Returning audio URL: {audio_url}")
    return {"audio_url": audio_url}


def save_to_storage(audio_file, filename, conversation_id, to="local"):
    if to == "local":
        print("Saving to local storage")
        save_path = os.path.join(os.getcwd(), "voice_output")
        print(f"Save path: {save_path}")
        os.makedirs(save_path, exist_ok=True)
        file_location = os.path.join(save_path, filename)
        print(f"File location: {file_location}")
        with open(file_location, "wb") as buffer:
            print("Copying file to buffer")
            shutil.copyfileobj(audio_file, buffer)
        logger.info(f"Saved audio to local: {file_location}")
        return f"/api/voice_output/{filename.split('.')[0]}"
    elif to == "cloud":
        print("Saving to cloud storage")
        # Upload to S3 bucket
        print("Initializing S3 client")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_REGION"),
        )
        bucket_name = os.environ.get("AWS_BUCKET_NAME")
        print(f"Using bucket: {bucket_name}")
        s3_path = f"{conversation_id}/{filename}"
        print(f"S3 path: {s3_path}")
        # Map common audio extensions to MIME types
        content_type_map = {
            "aac": "audio/aac",
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "ogg": "audio/ogg",
            "m4a": "audio/mp4",
            "flac": "audio/flac",
            "webm": "audio/webm",
        }
        # Get file extension and corresponding content type
        file_ext = filename.split(".")[-1].lower()
        print(f"File extension: {file_ext}")
        content_type = content_type_map.get(file_ext, "application/octet-stream")
        logger.info(f"Content type: {content_type}")
        try:
            print("Starting S3 upload")
            logger.info(f"Uploading audio to S3: {bucket_name}")
            s3_client.upload_fileobj(
                audio_file,
                bucket_name,
                s3_path,
                ExtraArgs={"ContentType": content_type},
            )
            # Generate permanent URL
            url = f"https://{bucket_name}.s3.{os.environ.get('AWS_REGION')}.amazonaws.com/{s3_path}"
            print(f"Generated S3 URL: {url}")
            logger.info(f"Uploaded audio to S3: {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload to S3")
