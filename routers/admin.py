from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal
from starlette import status
from .auth import get_current_user

router = APIRouter(prefix='/admin', tags=['admin'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo")
async def get_all_todos(user: user_dependency, db: db_dependency):
    user_role = user.get('role')
    if user_role == "admin":
        todos = db.query(Todos).all()
        return todos
    else:
        raise HTTPException(401, 'You are not admin')
    
@router.delete("/todo/delete/{id}")
async def get_all_todos(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)]):
    user_role = user.get('role')
    if user_role == "admin":
        todo = db.query(Todos).filter(Todos.id == id).first()
        db.delete(todo)
        db.commit()
    else:
        raise HTTPException(401, 'You are not admin')