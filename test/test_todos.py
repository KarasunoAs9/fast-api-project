from fastapi.testclient import TestClient
from fastapi import status
from ..main import app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..models import Todos, Users
from ..routers.auth import get_current_user
from ..database import get_db
import pytest

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
        

def test_aut(test_todo):
    responce = client.get('/api/todo')
    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == [{"complete": False,
                                "title": "First todo",
                                "description": "myr myr",
                                "id": 1,
                                "priority": 5,
                                "owner_id": 1,}]
    
def test_todo_by_id(test_todo):
    todo_id = test_todo.id
    responce = client.get(f"/api/todo/{todo_id}")
    print(responce.json())
    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == {'title': 'First todo', 
                                'priority': 5, 'owner_id': 1, 
                                'complete': False, 'id': 1, 
                                'description': 'myr myr'}
    
    
def test_todo_by_id_not_found():
    responce = client.get("/api/todo/939")
    assert responce.status_code == status.HTTP_404_NOT_FOUND
    
def test_add_todo(test_todo):
    request_data = {
        'title': 'Second todo', 
        'priority': 5, 'owner_id': 1, 
        'complete': False, 'id': 2, 
        'description': 'miy miy'
    }
    responce = client.post("/api/todo/add-todo", json=request_data)
    assert responce.status_code == status.HTTP_201_CREATED
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == request_data['id']).first()
    assert model.title == request_data['title']
    assert model.priority == request_data['priority']
    assert model.owner_id == request_data['owner_id']
    assert model.complete == request_data['complete']
    assert model.id == request_data['id']
    assert model.description == request_data['description']
    
    
    
def test_put_todo(test_todo):
    request_data = {
        'title': 'Puting todo', 
        'priority': 3, 'owner_id': 1, 
        'complete': False, 'id': 1, 
        'description': 'ochki miy miy'
    }
    responce = client.put(f"/api/todo/update-todo/{request_data['id']}", json=request_data)
    assert responce.status_code == status.HTTP_204_NO_CONTENT
    
    
def test_delete_todo(test_todo):
    todo_id = test_todo.id
    responce = client.delete(f"/api/todo/delete-todo/{todo_id}")
    assert responce.status_code == status.HTTP_204_NO_CONTENT
