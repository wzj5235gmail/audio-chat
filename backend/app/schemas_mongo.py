from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ConversationBase(BaseModel):
    message: str
    role: str
    translation: Optional[str] = None


class ConversationCreate(ConversationBase):
    user_id: PyObjectId
    character_id: PyObjectId


class Conversation(ConversationBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    character_id: PyObjectId
    created_at: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    conversations: List[Conversation] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Message(BaseModel):
    content: str
