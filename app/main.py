import sys

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.api.v1.router import api_router
from app.config import settings
from app.core.llm_client import check_llm_health
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(messages)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

for noisy_logger in ["httpx", "sqlalchemy.engine", "sqlalchemy.pool", "openai"]:
    logging.getLogger(noisy_logger).setLevel(logging.WARNING)
    logging.getLogger(noisy_logger).propagate = False 
    
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Starting up AI Eval Platform...")
    # init db
    create_db_and_tables()
    # check LLM connectivity
    is_healthy = await check_llm_health()
    if not is_healthy:
        logger.critical("DeepSeek API connection failed. Check your API keys and credits. Shutting down.")
        raise RuntimeError("LLM Health Check Failed")
    
    logger.info("System ready.")
    yield
    
    # Shutdown
    logger.info("Shutting down AI Eval Platform...")

app = FastAPI(
    title = settings.APP_NAME,
    description = "Production-grade platform for LLM evaluation, prompt versioning, and LLM-as-a-Judge.",
    version = "1.0.0",
    lifespan = lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def read_root():
    return {"status": "healthy","message": f"Welcome to the {settings.APP_NAME} API. Visit /docs for Swagger UI."}