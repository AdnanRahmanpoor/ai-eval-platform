from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True) # echo=True for debugging, printing sql to the console

def create_db_and_tables():
    # will be replaced in production
    SQLModel.metadata.create_all(engine)

def get_session():
    # generator that FastAPI uses to manages db sessions
    with Session(engine) as session:
        yield session