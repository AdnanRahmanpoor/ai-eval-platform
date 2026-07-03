from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import Dataset, DatasetItem
from app.schemas import DatasetCreate, DatasetRead, DatasetItemCreate, DatasetItemRead
import uuid

router = APIRouter(prefix="/datasets", tags=["Datasets"])

# Dataset CRUD

@router.post("/", response_model=DatasetRead, status_code=201)
def create_dataset(dataset_in: DatasetCreate, session: Session = Depends(get_session)):
    "Create a new empty dataset"
    db_dataset = Dataset.model_validate(dataset_in)
    session.add(db_dataset)
    session.commit()
    session.refresh(db_dataset)
    return db_dataset

@router.get("/", response_model=List[DatasetRead])
def get_datasets(session: Session = Depends(get_session)):
    "Retrieve all datasets"
    datasets = session.exec(select(Dataset)).all()
    return datasets

# Dataset Items CRUD
@router.post("/{dataset_id}/items", response_model=DatasetItemRead, status_code=201)
def add_dataset_item(dataset_id: uuid.UUID, item_in: DatasetItemCreate, session: Session = Depends(get_session)):
    "Add a Golden Dataset Item (input + expected output) to a specfic dataset"
    # 1. Verify the parent dataset exists
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 2. Create the item. We override the dataset_id with the one form the URL path for security
    db_item = DatasetItem.model_validate(item_in, update={"dataset_id": dataset_id})

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/{dataset_id}/items", response_model=List[DatasetItemRead])
def get_dataset_items(dataset_id: uuid.UUID, session: Session = Depends(get_session)):
    """Retrieve all Golden Items for a specific Dataset"""
    # 1. Verify the parent dataset exists
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 2. Query items filtered by dataset_id
    statement = select(DatasetItem).where(DatasetItem.dataset_id == dataset_id)
    items = session.exec(statement).all()
    return items
