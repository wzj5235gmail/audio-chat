from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from openai import OpenAI
from fastapi import HTTPException, Request
import time
import os
from . import configs, database, security, schemas


def get_current_user_from_token(request: Request):
    token = request.headers.get('Authorization')
    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = token.replace('Bearer ', '')
    try:
        user = security.decode_token(token)
        if user['expire_at'] < time.time():
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_chat_with_history():
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        return RedisChatMessageHistory(
            session_id=session_id,
            url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        )
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{character_prompt}"),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chat_chain = chat_prompt | model
    with_message_history = RunnableWithMessageHistory(
        chat_chain,
        get_session_history,
        input_messages_key="messages",
    )
    return with_message_history

def get_translate_chain():
    translate_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", configs.translate_prompt,),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    translate_chain = translate_prompt | model
    return translate_chain

model = ChatOpenAI(
    model=os.environ.get("GPT_MODEL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=float(os.environ.get("TEMPERATURE")),
    )

client = OpenAI()

chat_with_history = get_chat_with_history()

translate_chain = get_translate_chain()
