from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

# import database
from . import database


class User(database.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)

    conversation = relationship("Conversation", back_populates="user")


class Conversation(database.Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    translation = Column(Text)
    created_at = Column(String(255), index=True)
    role = Column(String(255), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    character_id = Column(Integer, ForeignKey("characters.id"))

    user = relationship("User", back_populates="conversation")
    character = relationship("Character", back_populates="conversation")

class Character(database.Base):
    __tablename__ = "characters"
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True)
    avatar_uri = Column(String(255))
    gpt_model_path = Column(String(255))
    sovits_model_path = Column(String(255))
    refer_path = Column(String(255))
    refer_text = Column(String(255))

    conversation = relationship("Conversation", back_populates="character")