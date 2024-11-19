from ..routers.auth import get_current_user
from ..database import get_db
from .utils import *
from passlib.context import CryptContext

app.dependency_overrides[get_db] = get_testdb   
app.dependency_overrides[get_current_user] = get_test_user

db = TestingSessionLocal()
bcrypt_context = CryptContext("bcrypt") 


def test_print_user_info(test_user):
    responce = client.get('/users/')
    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == {'first_name': 'tolibi', 
                               'last_name': 'roleri', 'is_active': True, 
                               'phone_number': '8484564', 'id': 1, 
                               'email': 'tobi@gmail.com', 
                               'username': 'tobi', 
                               'hashed_password': hashed_user_password, 
                               'role': 'user'}
    
def test_change_password_user(test_user):
    request_data = {
        "password": "12341234"
    }
    responce = client.patch('/users/change-password', json=request_data)
    assert responce.status_code == status.HTTP_204_NO_CONTENT

    model = db.query(Users).filter(Users.id == test_user.id).first()
    
    assert bcrypt_context.verify(request_data['password'], 
                                 model.hashed_password)
    
def test_change_phone_number(test_user):
    request_data = {
        "phone_number": "93913912"
    }
    
    responce = client.patch('/users/change-phone_number', json=request_data)
    assert responce.status_code == status.HTTP_204_NO_CONTENT
    
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert model.phone_number == request_data['phone_number']
    
    