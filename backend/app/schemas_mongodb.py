from pydantic import BaseModel, Field, BeforeValidator
from typing import Literal, Optional, Annotated
from bson import ObjectId


PyObjectId = Annotated[str, BeforeValidator(str)]


class ConversationBase(BaseModel):
    message: str
    role: str
    translation: str | None = None


class ConversationCreate(ConversationBase):
    user_id: PyObjectId
    character_id: PyObjectId


class Conversation(ConversationBase):
    id: PyObjectId = Field(alias="_id", default=None)
    user_id: PyObjectId
    character_id: PyObjectId
    created_at: str
    audio: str | None = None

    class Config:
        from_attributes = True
        # json_encoders = {PyObjectId: str}
        arbitrary_types_allowed = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserFromDB(UserBase):
    id: PyObjectId = Field(alias="_id", default=None)
    hashed_password: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class User(UserBase):
    id: PyObjectId = Field(alias="_id", default=None)
    is_active: bool
    conversations: list[Conversation] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class Message(BaseModel):
    content: str
    language: Literal["en", "zh"]


class Character(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    name: str
    avatar_uri: str
    gpt_model_path: str
    sovits_model_path: str
    refer_path: str
    refer_text: str
    prompt: str
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "populate_by_alias": False,
    }


class AnalyticsEvent(BaseModel):
    event_type: str
    event_data: dict


class AudioUpdate(BaseModel):
    audio: str
