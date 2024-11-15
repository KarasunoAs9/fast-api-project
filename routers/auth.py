from fastapi import APIRouter, Depends, HTTPException, Path
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from database import SessionLocal
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError


router = APIRouter()

SECRET_KEY = "48f4fbe5e370c4443eb0e6373632b33a87e819723b7227a9023a3c0516a286a1"
ALGORITHM = "HS256"

bcrypt_context = CryptContext("bcrypt") 
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    acces_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]


def authenticated_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_acces_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expiration = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expiration})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        username: str = payload.get("username")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(401, "User is not authenticated")
    except JWTError:
        raise HTTPException(401, "User is not authenticated")
        
        
class CreateUserRequest(BaseModel):
    email: Annotated[str, Field(min_length=5)]
    username: Annotated[str, Field(min_length=3)]
    first_name: Annotated[str, Field(min_length=3)]
    last_name: Annotated[str, Field(min_length=3)]
    password: Annotated[str, Field(min_length=8)]
    role: Annotated[str, Field(min_length=3)]

@router.get("/auth/users")
async def print_all_users(db: db_dependency):
    return db.query(Users).all()

@router.post("/auth/create-user")
async def create_user(db: db_dependency, user_request: CreateUserRequest):
    create_user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role,
    )
    db.add(create_user_model)
    db.commit() 
    
@router.delete("/auth/delet-user/{id}")
async def delete_user(db: db_dependency, id: Annotated[int, Path(gt=0)]):
    user = db.query(Users).filter(Users.id == id).first()
    if user is None:
        raise HTTPException(404, "User is not found")
    db.delete(user)
    db.commit()
    
@router.post("/auth/user/", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticated_user(form_data.username, form_data.password, db)
    if not user:
        return HTTPException(404, "Please enter a correct username or password")
    
    token = create_acces_token(user.username, user.id, timedelta(minutes=20))
    return {"acces_token": token, "token_type": "bearer"}
    