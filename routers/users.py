from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from ..models import Users
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext
from ..database import get_db

router = APIRouter(prefix='/users', tags=['users'])

bcrypt_context = CryptContext("bcrypt") 


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class ChangePassword(BaseModel):
    password: Annotated[str, Field(min_length=8)]
    
class ChagePhoneNumber(BaseModel):
    phone_number: Annotated[str, Field(min_length=3)]


@router.get("/")
async def print_user_info(user: user_dependency, db:db_dependency):
    user_id = user.get('id')
    user_info = db.query(Users).filter(Users.id == user_id).first()
    return user_info

@router.patch('/change-password')
async def change_user_password(user: user_dependency, db: db_dependency, change_request: ChangePassword):
    user_id = user.get('id')
    user_info = db.query(Users).filter(Users.id == user_id).first()
    
    user_info.hashed_password = bcrypt_context.hash(change_request.password)
    db.commit()

@router.patch('/change-phone_number')
async def change_phone_number(user: user_dependency, db: db_dependency, change_request: ChagePhoneNumber):
    user_id = user.get('id')
    objct = db.query(Users).filter(Users.id == user_id).first()
    objct.phone_number = change_request.phone_number
    db.commit()