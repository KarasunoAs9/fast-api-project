from fastapi.testclient import TestClient
from ..main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from fastapi import status
from ..main import app
from sqlalchemy import text
from ..models import Todos, Users
import pytest

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1111@localhost:5432/Testdb'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

client = TestClient(app)

def get_testdb():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_test_user():
    return {"username": "dem", "id": 1, "role": "admin"}

@pytest.fixture
def test_todo():
    db = TestingSessionLocal()
    
    user = Users(
        email="dem@gmail.com",
        username="dem",
        first_name="rem",
        last_name="lem",
        hashed_password="42rqwerk21j12n21nd1kn213kn21nk1e",
        is_active=True,
        role="admin",
        phone_number="5151251",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    todo = Todos(
        title="First todo",
        description="myr myr",
        priority=5,
        complete=False,
        owner_id=user.id,
    )
    db.add(todo)
    db.commit()

    yield todo
    

    with engine.connect() as connect:
        connect.execute(text("DELETE FROM todos;"))
        connect.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1;"))
        connect.execute(text("DELETE FROM users;"))
        connect.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))   
        connect.commit()
        