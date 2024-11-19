from ..routers.auth import get_current_user, create_acces_token, authenticated_user, SECRET_KEY, ALGORITHM
from ..database import get_db
from jose import jwt, JWTError
from .utils import *
from datetime import timedelta


app.dependency_overrides[get_db] = get_testdb   
app.dependency_overrides[get_current_user] = get_test_user

db = TestingSessionLocal()


def test_authenticated_user(test_user):
    username = test_user.username
    
    log_user = authenticated_user(username, '12341234', db)
    assert log_user is not None
    assert log_user.username == username
    
    wrong_user = authenticated_user('mmmmm', '5325', db)
    wrong_password_user = authenticated_user(username, '2', db)
    
    assert wrong_user is False
    assert wrong_password_user is False


def test_create_acces_token():
    username = 'Myi Myi'
    user_id = 2
    user_role = 'admin'
    expires_delta = timedelta(minutes=30)
    
    token = create_acces_token(username, user_id, user_role, expires_delta)
    
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token.get('sub') == username
    assert decoded_token.get('id') == user_id
    assert decoded_token.get('role') == user_role
 
@pytest.mark.asyncio   
async def test_get_current_user(test_user):
    token = create_acces_token(test_user.username, test_user.id, test_user.role, timedelta(minutes=20))
    user = await get_current_user(token)
    assert user == {"username": test_user.username, "id": test_user.id, "role": test_user.role}

def test_print_all_users(test_user):
    responce = client.get('/auth/')
    assert responce.status_code == status.HTTP_200_OK
    assert responce.json() == [{'first_name': 'tolibi', 
                               'last_name': 'roleri', 'is_active': True, 
                               'phone_number': '8484564', 'id': 1, 
                               'email': 'tobi@gmail.com', 
                               'username': 'tobi', 
                               'hashed_password': hashed_user_password, 
                               'role': 'user'},]


        
