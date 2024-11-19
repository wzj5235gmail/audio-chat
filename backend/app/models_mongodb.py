from bson import ObjectId
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    __tablename__ = "users"

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    hashed_password: str
    is_active: bool = True

    conversation: List["Conversation"] = []


class Conversation(BaseModel):
    __tablename__ = "conversations"

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    message: str
    translation: str | None = None
    created_at: str
    role: str
    user_id: str
    character_id: str
    audio_url: str | None = None

    user: "User" = Field(default=None, alias="user")
    character: "Character" = Field(default=None, alias="character")

class Character(BaseModel):
    __tablename__ = "characters"

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    avatar_uri: str
    gpt_model_path: str
    sovits_model_path: str
    refer_path: str
    refer_text: str
    prompt: str

    conversation: List["Conversation"] = []
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
