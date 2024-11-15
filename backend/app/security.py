from fastapi import Depends
import bcrypt
import jwt
import os
import dotenv
import time
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import html
import re

dotenv.load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
HASH_SECRET_KEY = os.environ.get('HASH_SECRET_KEY')


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Sanitize query parameters
        for param in request.query_params:
            sanitized = html.escape(request.query_params[param])
            request.scope["query_string"] = request.scope["query_string"].replace(
                request.query_params[param].encode(), sanitized.encode()
            )

        response = await call_next(request)
        return response


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed

def verify_password(password, hashed):
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password, hashed)
    # return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'expire_at': int(time.time()) + 60 * int(os.environ.get('TOKEN_EXPIRE_MINUTES'))
    }
    token = jwt.encode(payload, HASH_SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, HASH_SECRET_KEY, algorithms=['HS256'])
        if payload['expire_at'] < int(time.time()):
            return None
        return payload
    except Exception as e:
        raise Exception(e)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    return user


# Add input validation functions
def validate_user_input(text: str) -> bool:
    # Basic input validation
    if not text or len(text) > 1000:  # Adjust max length as needed
        return False
    # Check for common injection patterns
    dangerous_patterns = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"onerror=",
        r"onload=",
        r"eval\(",
    ]
    return not any(
        re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns
    )