from fastapi import APIRouter, HTTPException
from app.schemas import EvalRequest, EvalResult
from app.core.judge import run_judge
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evals", tags=["Evaluations"])

@router.post("/test-judge", response_model=EvalResult, status_code=200)
async def test_judge_endpoint(req: EvalRequest):
    "sandbox endpoint to test the LLM-as-a-judge logic manually"
    try:
        logger.info(f"Running judge test on criteria: {req.criteria[:50]}...")
        result = await run_judge(req.criteria, req.text_to_grade)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in test-judge endpoint")
        raise HTTPException(status_code=500, detail="An unexpected server error occured.")