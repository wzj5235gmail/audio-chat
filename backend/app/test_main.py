from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .main import app, get_db
from .database import Base
from .models import User, Character, Conversation
from .security import hash_password

# Create a separate test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_module(module):
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Add test data
    db = TestingSessionLocal()
    test_user = User(username="testuser", hashed_password=hash_password("testpassword"))
    db.add(test_user)
    test_character = Character(name="Test Character", avatar_uri="https://example.com/avatar.png", bg_uri="https://example.com/bg.png")
    db.add(test_character)
    test_conversation = Conversation(user_id=test_user.id, character_id=test_character.id, message="Hello", translation="你好")
    db.add(test_conversation)
    db.commit()
    db.close()

def teardown_module(module):
    # Drop tables
    Base.metadata.drop_all(bind=engine)

def test_create_user():
    response = client.post("/api/users", headers={"Content-Type": "application/json"}, json={"username": "newuser", "password": "newpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data

def test_create_token():
    response = client.post("/api/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert "expires_at" in data
    assert "user_id" in data
    assert "username" in data
    
    # test failed case
    response = client.post("/api/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 400

def test_chat():
    # First, get a token
    token_response = client.post("/api/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"username": "testuser", "password": "testpassword"})
    token = token_response.json()["access_token"]
    
    response = client.post("/api/chat/1", headers={"Authorization": f"Bearer {token}"}, json={"content": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "translation" in data
    
    # test failed case
    response = client.post("/api/chat/1", json={"content": "Hello"})
    assert response.status_code == 401

def test_get_conversation():
    # First, get a token
    token_response = client.post("/api/token", headers={"Content-Type": "application/x-www-form-urlencoded"}, data={"username": "testuser", "password": "testpassword"})
    token = token_response.json()["access_token"]
    
    response = client.get(
        "/api/conversations", 
        headers={"Authorization": f"Bearer {token}"},
        params={"user_id": 1, "character_id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Note: The list might be empty if no conversations exist yet
    if len(data) > 0:
        assert "id" in data[0]
        assert "character_id" in data[0]
        assert "created_at" in data[0]

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "username" in data[0]

def test_get_user():
    response = client.get("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data

def test_create_conversation():
    response = client.post("/api/conversations", headers={"Content-Type": "application/json"}, json={"user_id": 1, "character_id": 1, "message": "Hello", "translation": "你好", "role": "user"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "user_id" in data
    assert "character_id" in data
    assert "message" in data
    assert "translation" in data

