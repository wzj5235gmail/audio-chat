import time
import dotenv
import os
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, Response
from typing import Annotated
from sqlalchemy.orm import Session
from . import configs, crud, database, security, schemas
from .utils import get_current_user_from_token, get_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
from .redis import redis
from .controllers import *
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
from .security import SecurityHeadersMiddleware, XSSProtectionMiddleware, validate_user_input
from prometheus_client import Counter, Histogram, generate_latest
import logging
from datetime import datetime

dotenv.load_dotenv()

database.Base.metadata.create_all(bind=database.engine)

for character in configs.db_init:
    crud.create_character_if_not_exists(
        db=next(get_db()),
        name=character["name"], 
        avatar_uri=character["avatar_uri"], 
        gpt_model_path=character["gpt_model_path"], 
        sovits_model_path=character["sovits_model_path"], 
        refer_path=character["refer_path"], 
        refer_text=character["refer_text"]
    )

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 定义允许的域名列表
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "https://animechat.live",
    "https://www.animechat.live"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if os.getenv("ENV") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
if os.getenv("ENV") == "production":
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(XSSProtectionMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_ORIGINS)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
USER_ACTIONS = Counter('user_actions_total', 'User actions counter', ['action_type'])

@app.middleware("http")
async def cache_conversations(request: Request, call_next):
    if request.method == "GET" and request.url.path == "/api/conversations":
        user_id = request.query_params.get("user_id")
        character_id = request.query_params.get("character_id")
        skip = request.query_params.get("skip")
        limit = request.query_params.get("limit")
        # check if the conversations are cached
        cache_key = f"conversations_{user_id}_{character_id}_{skip}_{limit}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            return Response(
                content=cached_data,
                media_type="application/json"
            )
        # get the response
        response = await call_next(request)
        # read the response content and cache it
        response_body = [chunk async for chunk in response.body_iterator]
        response_content = b"".join(response_body)
        # cache the response content
        await redis.set(cache_key, response_content, ex=int(os.getenv("CACHE_EXPIRE_TIME_SECONDS")))
        # return the new response
        return Response(
            content=response_content,
            media_type=response.media_type
        )

    return await call_next(request)


@app.middleware("http")
async def cache_characters(request: Request, call_next):
    if request.method == "GET" and request.url.path == "/api/characters":
        cached_characters = await redis.get("characters")
        if cached_characters:
            return Response(
                content=cached_characters,
                media_type="application/json"
            )
        response = await call_next(request)
        response_body = [chunk async for chunk in response.body_iterator]
        response_content = b"".join(response_body)
        await redis.set("characters", response_content, ex=int(os.getenv("CACHE_EXPIRE_TIME_SECONDS")))
        return Response(
            content=response_content,
            media_type=response.media_type
        )
    return await call_next(request)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.observe(duration)
    
    # Log request details
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.2f}s - "
        f"Client: {request.client.host}"
    )
    
    return response


@app.post("/api/chat/{character_id}")
@limiter.limit("10/minute")
async def chat(
    request: Request, 
    character_id: int,
    message: schemas.Message,
    db: Session = Depends(get_db)
):
    logger.info(f"Chat request - Character: {character_id} - Message: {message.content[:50]}...")
    if not validate_user_input(message.content):
        logger.warning(f"Invalid input detected: {message.content[:50]}...")
        raise HTTPException(status_code=400, detail="Invalid input")
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, chat_handler, request, character_id, message, db)


@app.post("/api/stt")
@limiter.limit("10/minute")
async def stt(
    request: Request,
    audio: Annotated[UploadFile, File()],
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, stt_handler, request, audio)


@app.get("/api/characters")
async def get_characters(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> list[schemas.Character]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_characters_handler, db, skip, limit)


@app.post("/api/users", response_model=schemas.User)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_user_handler, db, user)


@app.get("/api/users", response_model=list[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> list[schemas.User]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_users_handler, db, skip, limit)


@app.get("/api/users/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> schemas.User:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_user_handler, db, user_id)


@app.post("/api/conversations", response_model=schemas.Conversation)
async def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_conversation_handler, db, conversation)


@app.get("/api/conversations", response_model=list[schemas.Conversation])
async def get_conversations(
    user_id: int,
    character_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_conversations_handler, db, user_id, character_id, skip, limit)


@app.post("/api/token")
@limiter.limit("100/minute")
async def create_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_token_handler, db, form_data)


@app.get("/api/voice_output/{conversation_id}")
async def get_audio(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    logger.info(f"Getting audio for conversation: {conversation_id}")
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        logger.error("Conversation not found")
        raise HTTPException(status_code=404, detail="Conversation not found")
    file_path = conversation.audio_url
    split_path = file_path.split('/')
    local_path = os.path.join(os.getcwd(), split_path[-2], split_path[-1])
    if not os.path.exists(local_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(local_path, filename=split_path[-1])


@app.post("/api/save_audio/{conversation_id}")
@limiter.limit("10/minute")
async def save_audio(
    request: Request,
    conversation_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, save_audio_handler, conversation_id, audio, db)


@app.get("/api/download_audio/{conversation_id}")
async def download_audio(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    audio_url = crud.get_audio_url(db, conversation_id)
    return FileResponse(audio_url)


@app.get("/api/search_character/{name}")
async def search_character(
    name: str,
    db: Session = Depends(get_db),
):
    if not validate_user_input(name):
        raise HTTPException(status_code=400, detail="Invalid input")
    return crud.search_character_by_name(db, name)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/api/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


@app.post("/api/analytics/event")
async def track_event(
    event: schemas.AnalyticsEvent,
    current_user: schemas.User = Depends(get_current_user_from_token)
):
    USER_ACTIONS.labels(action_type=event.event_type).inc()
    logger.info(
        f"Analytics Event - User: {current_user.id} - "
        f"Type: {event.event_type} - "
        f"Data: {event.event_data}"
    )
    return {"status": "recorded"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
