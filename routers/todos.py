from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from ..models import Todos
from starlette import status
from .auth import get_current_user
from ..database import get_db

router = APIRouter(prefix='/api', tags=['todo'])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=200)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/todo")
async def read_all(user: user_dependency, db: db_dependency):
    user_id = user.get('id')
    return db.query(Todos).filter(Todos.owner_id == user_id).all()

@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def todo_by_id(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)]):
    user_id = user.get('id')
    todo_model = db.query(Todos).filter(Todos.id == id and Todos.owner_id == user_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")
    

@router.post("/todo/add-todo", status_code=status.HTTP_201_CREATED)
async def add_todo(db: db_dependency, user: user_dependency, todo: TodoRequest):
    if user is None:
        raise HTTPException(401, "Authorithation fail")
    todo_model = Todos(**todo.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()

@router.put("/todo/update-todo/{id}")
async def update_todo(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)], todo_request: TodoRequest):
    user_id = user.get('id')
    todo_model = db.query(Todos).filter(Todos.id == id and Todos.owner_id == user_id).first()
    if todo_model is None:
        raise HTTPException(404, "Todo not found")
    
    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)
    
    db.commit()
    
@router.delete("/todo/delete-todo/{id}")
async def delete_todo(user: user_dependency, db: db_dependency, id: Annotated[int, Path(gt=0)]):
    user_id = user.get('id')
    todo_model = db.query(Todos).filter(Todos.id == id and Todos.owner_id == user_id).first()
    if todo_model is None:
        raise HTTPException(404, "Todo not found")
    
    db.delete(todo_model)
    db.commit()
    
    