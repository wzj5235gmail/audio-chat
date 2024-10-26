from pymongo import MongoClient
import os
import dotenv

dotenv.load_dotenv()

user = os.environ.get("MONGO_USER")
password = os.environ.get("MONGO_PASSWORD")
server = os.environ.get("MONGO_SERVER")
db = os.environ.get("MONGO_DB")

MONGODB_URL = f"mongodb://{user}:{password}@{server}/{db}"

client = MongoClient(MONGODB_URL)
db = client[db]

def get_db():
    try:
        yield db
    finally:
        client.close()
