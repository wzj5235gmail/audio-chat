import shutil
import time
import os
from fastapi.security import OAuth2PasswordRequestForm
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, Response, Form
from typing import Annotated
from sqlalchemy.orm import Session
from . import configs, crud, database, security, schemas
from .utils import get_current_user_from_token, get_db, chat_with_history, translate_chain_en, translate_chain_zh, client
import boto3
import uuid
import logging

logger = logging.getLogger(__name__)

def chat_handler(
    request: Request, 
    character_id: int,
    message: schemas.Message,
    db: Session = Depends(get_db)
):
    try:
        # Get the user's info from the token
        current_user = get_current_user_from_token(request)
        # Get the user's conversation history
        user_id = current_user['user_id']
        # Use RedisChatMessageHistory with a combined session_id
        session_id = f"{user_id}_{character_id}"
        chat_history = RedisChatMessageHistory(
            session_id=session_id,
            url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        )

        # Check if the chat history is empty
        if len(chat_history.messages) == 0:
            # Get the user's conversation history from the database
            conversations = crud.get_conversations(
                db=db, 
                user_id=user_id, 
                character_id=character_id,
                limit=configs.max_chat_history
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
            truncated_messages = chat_history.messages[-configs.max_chat_history:]
            chat_history.clear()
            for msg in truncated_messages:
                chat_history.add_message(msg)

        # Add the user's message to database
        crud.create_conversation(
            db=db,
            conversation={
                "message": message.content,
                "role": "user",
                "user_id": user_id,
                "character_id": character_id,
            },
        )
        # Set the session_id and character_prompt in the config
        config = {
            "configurable": {
                "session_id": session_id,
                "character_prompt": configs.chat_prompt[character_id],
            }
        }

        # Get the bot's response
        chat_reply = chat_with_history.invoke(
            {
                "messages": [HumanMessage(content=message.content)],
                "character_prompt": configs.chat_prompt[character_id],
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
        crud.create_conversation(
            db=db,
            conversation={
                "message": chat_reply,
            "translation": translation,
            "role": "assistant",
            "user_id": user_id,
            "character_id": character_id,
        },
    )
        return {'message': chat_reply, 'translation': translation}
    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def stt_handler(
    request: Request,
    audio: Annotated[UploadFile, File()],
):
    try:
        current_user = get_current_user_from_token(request)
        supported_formats = ['audio/flac', 'audio/m4a', 'audio/mp3', 'audio/mp4', 'audio/mpeg', 'audio/mpga', 'audio/oga', 'audio/ogg', 'audio/wav', 'audio/webm']
        if audio.content_type not in supported_formats:
            return {"error": "Unsupported file format. Please upload a valid audio file."}
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


def get_characters_handler(
    db: Session,
    skip: int,
    limit: int,
) -> list[schemas.Character]:
    logger.info("querying database...")
    return crud.get_characters(db, skip=skip, limit=limit)


def create_user_handler(
    db: Session,
    user: schemas.UserCreate,
) -> schemas.User:
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.error("Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


def read_users_handler(
    db: Session,
    skip: int,
    limit: int,
) -> list[schemas.User]:
    return crud.get_users(db, skip=skip, limit=limit)


def read_user_handler(
    db: Session,
    user_id: int,
) -> schemas.User:
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        logger.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def create_conversation_handler(
    db: Session,
    conversation: schemas.ConversationCreate,
) -> schemas.Conversation:
    return crud.create_conversation(db=db, conversation=conversation.model_dump())


def get_conversations_handler(
    db: Session,
    user_id: int,
    character_id: int,
    skip: int,
    limit: int,
) -> list[schemas.Conversation]:
    print("querying database...")
    conversations = crud.get_conversations(
        db=db,
        user_id=user_id,
        character_id=character_id,
        skip=skip,
        limit=limit
    )
    conversations.reverse()
    return conversations


def create_token_handler(
    db: Session,
    form_data: OAuth2PasswordRequestForm,
) -> dict:
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user:
        logger.error("Invalid username")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        logger.error("Invalid password")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = security.generate_token(user.id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": int(time.time()) + 60 * int(os.environ.get('TOKEN_EXPIRE_MINUTES')),
        "user_id": user.id,
        "username": user.username,
        }


def save_audio_handler(
    conversation_id: int,
    audio: UploadFile,
    db: Session,
):
    filename = f"{uuid.uuid4()}.{audio.content_type.split('/')[-1]}"

    # Save to cloud storage or local filesystem
    audio_url = save_to_storage(audio.file, filename, conversation_id, to="local")
    logger.info(f"Saved audio to local: {audio_url}")

    crud.update_audio_url(db, conversation_id, audio_url)
    logger.info(f"Updated conversation: {conversation_id}")

    return {
        'audio_url': audio_url
    }


def save_to_storage(audio_file, filename, conversation_id, to="local"):
    if to == "local":
        save_path = os.path.join(os.getcwd(), 'voice_output')
        os.makedirs(save_path, exist_ok=True)
        file_location = os.path.join(save_path, filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(audio_file, buffer)
        logger.info(f"Saved audio to local: {file_location}")
        return f"/api/voice_output/{filename}"
    elif to == "cloud":
        # Upload to S3 bucket
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION')
        )
        bucket_name = os.environ.get('AWS_BUCKET_NAME')
        s3_path = f"{conversation_id}/{filename}"
        # Map common audio extensions to MIME types
        content_type_map = {
            'aac': 'audio/aac',
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'ogg': 'audio/ogg',
            'm4a': 'audio/mp4',
            'flac': 'audio/flac',
            'webm': 'audio/webm'
        }
        # Get file extension and corresponding content type
        file_ext = filename.split('.')[-1].lower()
        content_type = content_type_map.get(file_ext, 'application/octet-stream')
        logger.info(f"Content type: {content_type}")
        try:
            logger.info(f"Uploading audio to S3: {bucket_name}")
            s3_client.upload_fileobj(
                audio_file,
                bucket_name,
                s3_path,
                ExtraArgs={'ContentType': content_type}
            )
            # Generate permanent URL
            url = f"https://{bucket_name}.s3.{os.environ.get('AWS_REGION')}.amazonaws.com/{s3_path}"
            logger.info(f"Uploaded audio to S3: {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload to S3")

