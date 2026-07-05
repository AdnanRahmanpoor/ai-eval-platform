from fastapi import APIRouter
from app.api.v1 import dashboard, prompts, datasets, evals

api_router = APIRouter()
api_router.include_router(prompts.router)
api_router.include_router(datasets.router)
api_router.include_router(evals.router)
api_router.include_router(dashboard.router)