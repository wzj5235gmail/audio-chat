import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import dotenv

dotenv.load_dotenv(override=True)

MONGODB_URL = os.environ.get("MONGODB_URL")
DATABASE_NAME = os.environ.get("MONGODB_DATABASE_NAME")
if DATABASE_NAME is None:
    raise ValueError("MONGODB_DATABASE_NAME environment variable is not set")

client = AsyncIOMotorClient(MONGODB_URL, maxPoolSize=10, minPoolSize=10)
db = client[DATABASE_NAME]

