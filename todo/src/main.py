
from fastapi import Depends, FastAPI, HTTPException
from typing import Optional, Annotated
from sqlmodel import Session, create_engine , SQLModel, Field, select
from src import settings
from contextlib import asynccontextmanager

class Todo(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  title: str
  description: str
  complete: bool

conn_str = str(settings.DB_URL).replace("postgresql", "postgresql+psycopg")
engine = create_engine(conn_str)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifeSpan(app: FastAPI):
  try:
    create_db_and_tables()
    yield
  finally:
    engine.dispose()

app = FastAPI(lifespan=lifeSpan, title="Todo API", version="0.0.1")

def get_session():
  with engine.begin() as session:
    yield session

@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/todos")
async def get_todos(session: Annotated[Session, Depends(get_session)]):
  todos = session.exec(select(Todo)).all()
  return todos


@app.post("/todos")
async def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
  if todo.title.strip():
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
  else:
    raise HTTPException(status_code=400, detail="Title cannot be empty")
