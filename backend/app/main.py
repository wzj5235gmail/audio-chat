import shutil
import time
import dotenv
import os
from fastapi.security import OAuth2PasswordRequestForm
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from typing import Annotated
from sqlalchemy.orm import Session
from . import configs, crud, database, security, schemas
from .utils import get_current_user_from_token, get_db, chat_with_history, translate_chain_en, translate_chain_zh, client
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis




dotenv.load_dotenv()

database.Base.metadata.create_all(bind=database.engine)

crud.create_character_if_not_exists(db=next(get_db()), name="加藤惠", avatar_uri="megumi-avatar.jpg", gpt_model_path="GPT_weights/megumi20240607-e15.ckpt", sovits_model_path="SoVITS_weights/megumi20240607_e8_s200.pth", refer_path="refer/megumi/megumi-1.wav", refer_text="主人公相手だって考えればいいのか")
crud.create_character_if_not_exists(db=next(get_db()), name="泽村英梨梨", avatar_uri="eriri-avatar.jpg", gpt_model_path="GPT_weights/eriri-e15.ckpt", sovits_model_path="SoVITS_weights/eriri_e8_s248.pth", refer_path="refer/eriri/eriri-2.wav", refer_text="そんなわけでさ 今ラフデザインやってるんだけど")
crud.create_character_if_not_exists(db=next(get_db()), name="霞之丘诗羽", avatar_uri="utaha-avatar.jpg", gpt_model_path="GPT_weights/utaha-e15.ckpt", sovits_model_path="SoVITS_weights/utaha_e8_s256.pth", refer_path="refer/utaha/utaha-2.wav", refer_text="はいそれじゃあ次のシーン 最初はヒロインの方から抱きついてくる")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在创建 app 后，添加缓存初始化
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

def chat_handler(
    request: Request, 
    character_id: int,
    message: schemas.Message,
    db: Session = Depends(get_db)
):
    # Get the user's info from the token
    current_user = get_current_user_from_token(request)
    # Get the user's conversation history
    user_id = current_user['user_id']
    character_name = configs.characters[character_id]
    
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
            "character_prompt": configs.chat_prompt[character_name],
        }
    }

    # Get the bot's response
    chat_reply = chat_with_history.invoke(
        {
            "messages": [HumanMessage(content=message.content)],
            "character_prompt": configs.chat_prompt[character_name],
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


@app.post("/api/chat/{character_id}")
@limiter.limit("10/minute")
async def chat(
    request: Request, 
    character_id: int,
    message: schemas.Message,
    db: Session = Depends(get_db)
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, chat_handler, request, character_id, message, db)

def stt_handler(
    request: Request,
    audio: Annotated[UploadFile, File()],
):
    # Get the user's info from the token
    current_user = get_current_user_from_token(request)
    # Check if the audio file is in a supported format
    supported_formats = ['audio/flac', 'audio/m4a', 'audio/mp3', 'audio/mp4', 'audio/mpeg', 'audio/mpga', 'audio/oga', 'audio/ogg', 'audio/wav', 'audio/webm']
    if audio.content_type not in supported_formats:
        return {"error": "Unsupported file format. Please upload a valid audio file."}
    # Save the audio file locally
    file_location = f"{audio.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
    try:
        # Transcribe the audio file
        file = open(file_location, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
        )
        file.close()
    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"error": str(e)}

    return {
        "transcription": transcription.text,
    }

@app.post("/api/stt")
@limiter.limit("10/minute")
async def stt(
    request: Request,
    audio: Annotated[UploadFile, File()],
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, stt_handler, request, audio)


def get_characters_handler(
    db: Session,
    skip: int,
    limit: int,
):
    return crud.get_characters(db, skip=skip, limit=limit)


@app.get("/api/characters")
async def get_characters(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_characters_handler, db, skip, limit)


def create_user_handler(
    db: Session,
    user: schemas.UserCreate,
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/api/users", response_model=schemas.User)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_user_handler, db, user)


def read_users_handler(
    db: Session,
    skip: int,
    limit: int,
):
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/api/users", response_model=list[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_users_handler, db, skip, limit)


def read_user_handler(
    db: Session,
    user_id: int,
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/api/users/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_user_handler, db, user_id)


def create_conversation_handler(
    db: Session,
    conversation: schemas.ConversationCreate,
):
    return crud.create_conversation(db=db, conversation=conversation.model_dump())

@app.post("/api/conversations", response_model=schemas.Conversation)
async def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_conversation_handler, db, conversation)

def get_conversations_handler(
    db: Session,
    user_id: int,
    character_id: int,
    skip: int,
    limit: int,
):
    conversations = crud.get_conversations(
        db=db,
        user_id=user_id,
        character_id=character_id,
        skip=skip,
        limit=limit
    )
    conversations.reverse()
    return conversations

@app.get("/api/conversations", response_model=list[schemas.Conversation])
@cache(expire=5)
async def get_conversations(
    user_id: int,
    character_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_conversations_handler, db, user_id, character_id, skip, limit)

def create_token_handler(
    db: Session,
    form_data: OAuth2PasswordRequestForm,
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = security.generate_token(user.id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": int(time.time()) + 60 * int(os.environ.get('TOKEN_EXPIRE_MINUTES')),
        "user_id": user.id,
        "username": user.username,
        }

@app.post("/api/token")
@limiter.limit("100/minute")
async def create_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_token_handler, db, form_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
