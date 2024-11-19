from fastapi.testclient import TestClient
from fastapi import status
from ..main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from sqlalchemy.pool import StaticPool
from ..routers.auth import get_db, get_current_user


SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1111@localhost:5432/Testdb'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_testdb():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_test_user():
    return {"username": "dem", "id": 1, "role": "admin"}

app.dependency_overrides[get_db] = get_testdb   
app.dependency_overrides[get_current_user] = get_test_user

client = TestClient(app)

def test_aut():
    responce = client.get('/')
    assert responce.status_code == status.HTTP_200_OK