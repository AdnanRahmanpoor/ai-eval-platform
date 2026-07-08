from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from app.database import get_session
from app.models import Experiment
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Dashboard"])

# Point Jinja2 to the templates folder in the root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/dashboard", response_class=HTMLResponse)
def render_dashboard(request: Request, session: Session = Depends(get_session)):
    """
    Renders the visual HTML dashboard.
    Queries the DB for summary stats and chart data.
    """
    # 1. Fetch all completed experiments ordered by date
    statement = select(Experiment).where(Experiment.status == "COMPLETED").order_by(Experiment.created_at)
    experiments = session.exec(statement).all()
    
    # 2. Calculate Summary Metrics
    total_experiments = len(experiments)
    total_regressions = sum(1 for exp in experiments if exp.is_regression)
    
    if total_experiments > 0:
        global_avg_score = round(sum(exp.avg_score for exp in experiments) / total_experiments, 2)
    else:
        global_avg_score = 0.0

    # 3. Prepare Data for Chart.js
    labels = [exp.created_at.strftime("%m-%d %H:%M") for exp in experiments]
    scores = [exp.avg_score for exp in experiments]
    regressions = [bool(exp.is_regression) for exp in experiments]

    # 4. Render the Jinja2 Template
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request,
            "experiments": experiments,
            "total_experiments": total_experiments,
            "global_avg_score": global_avg_score,
            "total_regressions": total_regressions,
            "labels": labels,
            "scores": scores,
            "regressions": regressions
        }
    )

@router.get("/run", response_class = HTMLResponse)
def render_run_page(request: Request):
    """Serves the Evaluation Runner UI"""
    return templates.TemplateResponse("run.html", {"request": request})

@router.get("/experiment/{experiment_id}", response_class = HTMLResponse)
def render_experiment_detail(request: Request, experiment_id: str):
    """Serves the Experiment Detail UI"""
    return templates.TemplateResponse("experiment.html", {"request": request, "exp_id": experiment_id})
