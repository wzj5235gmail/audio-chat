import time
import dotenv
import os
import logging
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, Response
from typing import Annotated
from . import crud, schemas
from . import configs
from .utils import get_current_user_from_token
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
from .redis import redis
from .controllers import *
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .security import (
    SecurityHeadersMiddleware,
    XSSProtectionMiddleware,
    validate_user_input,
    get_current_user,
)
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import JSONResponse


dotenv.load_dotenv(override=True)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOWED_ORIGINS = [
    "https://animechat.live",
    "https://www.animechat.live",
    "http://localhost:3000",
    "http://localhost",
]

# if os.getenv("ENV") == "production":
#     app.add_middleware(SecurityHeadersMiddleware)
#     app.add_middleware(XSSProtectionMiddleware)
#     app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_ORIGINS)
#     app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency")
USER_ACTIONS = Counter("user_actions_total", "User actions counter", ["action_type"])


@app.on_event("startup")
async def startup_event():
    for character in configs.db_init:
        await crud.create_character_if_not_exists(
            name=character["name"],
            avatar_uri=character["avatar_uri"],
            gpt_model_path=character["gpt_model_path"],
            sovits_model_path=character["sovits_model_path"],
            refer_path=character["refer_path"],
            refer_text=character["refer_text"],
            prompt=character["prompt"],
        )


NO_AUTHORIZATION_REQUIRED_ENDPOINTS = [
    "/api/token",
    "/api/users",
]


@app.middleware("http")
async def check_if_authorized(request: Request, call_next):
    path = request.url.path
    no_need_auth = any(
        path.startswith(endpoint) for endpoint in NO_AUTHORIZATION_REQUIRED_ENDPOINTS
    )
    if no_need_auth:
        return await call_next(request)
    if not request.headers.get("Authorization"):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    current_user = await get_current_user(
        request.headers.get("Authorization").split(" ")[1]
    )
    if not current_user:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    if current_user["expire_at"] < int(time.time()):
        return JSONResponse(status_code=401, content={"detail": "Token expired"})
    return await call_next(request)


@app.middleware("http")
async def cache_response(request: Request, call_next):
    # Only handle GET requests for conversations and characters
    if request.method != "GET" or request.url.path not in [
        "/api/conversations",
        "/api/characters",
    ]:
        return await call_next(request)

    # Generate cache key based on path and params
    cache_key = "characters"
    if request.url.path == "/api/conversations":
        user_id = request.query_params.get("user_id")
        character_id = request.query_params.get("character_id")
        skip = request.query_params.get("skip")
        limit = request.query_params.get("limit")
        cache_key = f"conversations_{user_id}_{character_id}_{skip}_{limit}"

    # Check cache
    cached_data = await redis.get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for {cache_key}")
        return Response(
            content=cached_data,
            media_type="application/json",
            headers={
                "Access-Control-Allow-Origin": request.headers.get(
                    "origin", ALLOWED_ORIGINS[0]
                ),
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*",
            },
        )

    # Cache miss - get fresh response
    logger.info(f"Cache miss for {cache_key}")
    response = await call_next(request)
    response_body = [chunk async for chunk in response.body_iterator]
    response_content = b"".join(response_body)

    # Cache the response
    await redis.set(
        cache_key, response_content, ex=int(os.getenv("CACHE_EXPIRE_TIME_SECONDS"))
    )

    # Return response
    return Response(
        content=response_content,
        media_type=response.media_type,
        headers={
            "Access-Control-Allow-Origin": request.headers.get(
                "origin", ALLOWED_ORIGINS[0]
            ),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)

    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat/{character_id}")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    character_id: str,
    message: schemas.Message,
):
    logger.info(
        f"Chat request - Character: {character_id} - Message: {message.content[:50]}..."
    )
    if not validate_user_input(message.content):
        logger.warning(f"Invalid input detected: {message.content[:50]}...")
        return JSONResponse(status_code=400, content={"detail": "Invalid input"})
    return await chat_handler(request, character_id, message)


@app.post("/api/stt")
@limiter.limit("10/minute")
async def stt(
    request: Request,
    audio: Annotated[UploadFile, File()],
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, stt_handler, request, audio)


@app.get("/api/characters", response_model=list[schemas.Character])
async def get_characters(
    skip: int = 0,
    limit: int = 100,
) -> list[schemas.Character]:
    return await get_characters_handler(skip, limit)


@app.post("/api/users", response_model=schemas.User)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    user: schemas.UserCreate,
):
    return await create_user_handler(user)


@app.get("/api/users", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100) -> list[schemas.User]:
    return await read_users_handler(skip, limit)


@app.get("/api/users/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: str,
) -> schemas.User:
    return await read_user_handler(user_id)


@app.post("/api/conversations", response_model=schemas.Conversation)
async def create_conversation(
    conversation: schemas.ConversationCreate,
):
    return await create_conversation_handler(conversation)


@app.get("/api/conversations", response_model=list[schemas.Conversation])
async def get_conversations(
    user_id: str,
    character_id: str,
    skip: int = 0,
    limit: int = 100,
):
    return await get_conversations_handler(user_id, character_id, skip, limit)


@app.post("/api/token")
@limiter.limit("100/minute")
async def create_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await create_token_handler(form_data)


@app.get("/api/voice_output/{conversation_id}")
async def get_audio(
    conversation_id: str,
):
    conversation = await crud.get_conversation(conversation_id)
    if not conversation:
        logger.error("Conversation not found")
        return JSONResponse(
            status_code=404, content={"detail": "Conversation not found"}
        )
    try:
        return FileResponse(
            os.path.join(os.getcwd(), "voice_output", f"{conversation_id}.aac")
        )
    except FileNotFoundError:
        logger.error(f"File not found: {conversation_id}.aac")
        return JSONResponse(status_code=404, content={"detail": "File not found"})


@app.put("/api/conversations/{conversation_id}")
async def update_conversation_audio(
    conversation_id: str,
    audio: schemas.AudioUpdate,
):
    return await crud.update_conversation_audio(conversation_id, audio.audio)


@app.get("/api/search_character/{name}")
async def search_character(
    name: str,
):
    if not validate_user_input(name):
        return JSONResponse(status_code=400, content={"detail": "Invalid input"})
    return await crud.search_character_by_name(name)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/api/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


@app.post("/api/analytics/event")
async def track_event(
    event: schemas.AnalyticsEvent,
    current_user: schemas.User = Depends(get_current_user_from_token),
):
    USER_ACTIONS.labels(action_type=event.event_type).inc()
    logger.info(
        f"Analytics Event - User: {current_user.id} - "
        f"Type: {event.event_type} - "
        f"Data: {event.event_data}"
    )
    return {"status": "recorded"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
