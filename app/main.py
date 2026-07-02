from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.api.v1.router import api_router
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Creating database tables.") # on startup
    create_db_and_tables()
    yield
    print("Shutting down...") # on shutdown

app = FastAPI(
    title = settings.APP_NAME,
    description = "Production-grade platform for LLM evaluation, prompt versioning, and LLM-as-a-Judge.",
    version = "1.0.0",
    lifespan = lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to the {settings.APP_NAME} API. Visit /docs for Swagger UI."}