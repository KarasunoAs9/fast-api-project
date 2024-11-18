from fastapi import APIRouter, Depends, HTTPException, Path
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from database import SessionLocal

router = APIRouter(prefix='/auth', tags=['auth'])

SECRET_KEY = "48f4fbe5e370c4443eb0e6373632b33a87e819723b7227a9023a3c0516a286a1"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bcrypt_context = CryptContext("bcrypt") 
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str

        
db_dependency = Annotated[Session, Depends(get_db)]


def authenticated_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_acces_token(username: str, user_id: int, user_role: str,expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": user_role}
    expiration = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expiration})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(401, "User is not authenticated")
        return {"username": username, "id": user_id, "role": user_role}
    
    except JWTError:
        raise HTTPException(401, "User is not authenticated")
        
        
class CreateUserRequest(BaseModel):
    email: Annotated[str, Field(min_length=5)]
    username: Annotated[str, Field(min_length=3)]
    first_name: Annotated[str, Field(min_length=3)]
    last_name: Annotated[str, Field(min_length=3)]
    password: Annotated[str, Field(min_length=8)]
    role: Annotated[str, Field(min_length=3)]
    phone_number: Annotated[str, Field(min_length=3)]

@router.get("/")
async def print_all_users(db: db_dependency):
    return db.query(Users).all()

@router.post("/create-user")
async def create_user(db: db_dependency, user_request: CreateUserRequest):
    create_user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role,
        phone_number = user_request.phone_number
    )
    db.add(create_user_model)
    db.commit() 
    
@router.delete("/delet-user/{id}")
async def delete_user(db: db_dependency, id: Annotated[int, Path(gt=0)]):
    user = db.query(Users).filter(Users.id == id).first()
    if user is None:
        raise HTTPException(404, "User is not found")
    db.delete(user)
    db.commit()
    
@router.post("/token", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticated_user(form_data.username, form_data.password, db)
    if not user:
        return HTTPException(404, "Please enter a correct username or password")
    
    token = create_acces_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
    