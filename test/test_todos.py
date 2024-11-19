from ..routers.auth import get_current_user
from ..database import get_db
from .utils import *

app.dependency_overrides[get_db] = get_testdb   
app.dependency_overrides[get_current_user] = get_test_user

db = TestingSessionLocal()

def test_aut(test_todo):
    responce = client.get('/api/todo')
    print(responce.json())
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
    
    model = db.query(Todos).filter(Todos.id == todo_id).first()
    assert model is None
