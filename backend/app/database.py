from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import dotenv

dotenv.load_dotenv()

user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
server = os.environ.get("MYSQL_SERVER")
db = os.environ.get("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{server}/{db}?charset=utf8mb4"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"charset": "utf8mb4"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
