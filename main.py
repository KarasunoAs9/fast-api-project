from fastapi import FastAPI, Request
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates("TodoApp/templates")

app.mount('/static', StaticFiles(directory='TodoApp/static'), name='static')

@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/healthy")
def check_healthy():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
