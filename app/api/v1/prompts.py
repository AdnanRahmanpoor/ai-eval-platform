from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Prompt
from app.schemas import PromptCreate, PromptRead

router = APIRouter(prefix="/prompts", tags=["Prompts"])

@router.post("/", response_model=PromptRead, status_code=201)
def create_prompt(prompt_in: PromptCreate, session: Session = Depends(get_session)):
    # check if prompt name exists to auto-increment version
    statement = select(Prompt).where(Prompt.name == prompt_in.name)
    existing_prompts = session.exec(statement).all()
    next_version = len(existing_prompts) + 1

    # create db object
    db_prompt = Prompt(
        name = prompt_in.name,
        template = prompt_in.template,
        variables = prompt_in.variables,
        version = next_version
    )

    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt) # update the object with db-generated id and timestamps
    return db_prompt

@router.get("/", response_model=list[PromptRead])
def get_prompts(session: Session = Depends(get_session)):
    statement = select(Prompt).where(Prompt.is_active == True)
    prompts = session.exec(statement).all()
    return prompts