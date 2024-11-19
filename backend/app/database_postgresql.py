from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# 强制重新加载环境变量
load_dotenv(override=True)

# 使用os.environ.get获取环境变量
POSTGRE_USER = os.environ.get("POSTGRE_USER")
POSTGRE_PASSWORD = os.environ.get("POSTGRE_PASSWORD")
POSTGRE_SERVER = os.environ.get("POSTGRE_SERVER")
POSTGRE_DB = os.environ.get("POSTGRE_DB")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRE_USER}:{POSTGRE_PASSWORD}@{POSTGRE_SERVER}/{POSTGRE_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
