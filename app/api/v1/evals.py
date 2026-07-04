from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Experiment, EvalRun, Prompt, Dataset
from app.schemas import EvalRequest, EvalResult, ExperimentCreate, ExperimentRead, EvalRunRead
from app.services.eval_engine import execute_experiment
from app.core.judge import run_judge
from uuid import UUID
from typing import List
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
    
@router.post("/run", response_model=ExperimentRead, status_code=202)
async def trigger_experiment(req: ExperimentCreate,  background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Triggers a batch evaluation. Creates the DB record, hand the heavy lifting to BackgroundTasks, and immediately returns.
    """
    # Verify the prompt and dataset exist
    if not session.get(Prompt, req.prompt_id):
        raise HTTPException(status_code=404, detail="Prompt ID not found")
    if not session.get(Dataset, req.dataset_id):
        raise HTTPException(status_code=404, details="Dataset ID not found")
    
    db_experiment = Experiment.model_validate(req)
    session.add(db_experiment)
    session.commit()
    session.refresh(db_experiment)

    # hand the async function to FastAPI's background queue
    background_tasks.add_task(execute_experiment, db_experiment.id)

    logger.info(f"Queued Experiment {db_experiment.id} for background execution.")
    return db_experiment

@router.get("/experiments/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: UUID, session: Session = Depends(get_session)):
    "Poll this endpoint to check if status is RUNNING or COMPLETED."
    experiment = session.get(Experiment, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@router.get("/experiment/{experiment_id}/runs", response_model=List[EvalRunRead])
def get_experiment_runs(experiment_id: UUID, session: Session = Depends(get_session)):
    "Retrieves the granular results of every row in the batch."
    statement = select(EvalRun).where(EvalRun.experiment_id == experiment_id)
    runs = session.exec(statement).all()
    return runs