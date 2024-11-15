from pydantic import BaseModel
from typing import Literal

class ConversationBase(BaseModel):
    message: str
    role: str
    translation: str | None = None


class ConversationCreate(ConversationBase):
    user_id: int
    character_id: int


class Conversation(ConversationBase):
    id: int
    user_id: int
    character_id: int
    created_at: str

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    conversations: list[Conversation] = []

    class Config:
        from_attributes = True

class Message(BaseModel):
    content: str
    language: Literal["en", "zh"]

class Character(BaseModel):
    id: int
    name: str
    avatar_uri: str
    gpt_model_path: str
    sovits_model_path: str
    refer_path: str
    refer_text: str


class AnalyticsEvent(BaseModel):
    event_type: str
    event_data: dict
