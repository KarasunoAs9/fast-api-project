from ..routers.auth import get_current_user
from ..database import get_db
from .utils import *

app.dependency_overrides[get_db] = get_testdb   
app.dependency_overrides[get_current_user] = get_test_user

db = TestingSessionLocal()

def test_all_todos(test_todo):
    responce = client.get('/admin/todo')
    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == [{'title': 'First todo', 
                                'priority': 5, 
                                'owner_id': 1, 
                                'complete': False, 
                                'id': 1, 
                                'description': 'myr myr'},]
    
    
def test_delete_todo(test_todo):
    todo_id = test_todo.id
    responce = client.delete(f'/admin/todo/delete/{todo_id}')
    assert responce.status_code == 204
    
    model = db.query(Todos).filter(Todos.id == todo_id).first()
    assert model is None
    
def test_delete_todo_not_found():
    responce = client.delete('/admin/todo/delete/510')
    assert responce.status_code == status.HTTP_404_NOT_FOUND
    
    
    