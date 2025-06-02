from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from . import models, schemas, crud, auth
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Регистрация пользователя
@app.post("/register/", response_model=schemas.User)
def register(user: schemas.UserCreate):
    db = SessionLocal()
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

# Вход и получение токена
@app.post("/token/")
def login(user: schemas.UserLogin):
    db = SessionLocal()
    return auth.authenticate_user(db, user.email, user.password)

# Создать задачу (только для авторизованных)
@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    token: str = Depends(oauth2_scheme)
):
    db = SessionLocal()
    return crud.create_task(db, task, user_id=auth.get_current_user_id(token))

# Получить все задачи
@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    return crud.get_tasks(db, skip=skip, limit=limit)
