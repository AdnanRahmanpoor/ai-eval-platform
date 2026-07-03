from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column
from typing import Optional, List
from datetime import datetime
import uuid

class Prompt(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    version: int = Field(default=1)
    template: str
    # sqlalchemy json allows stroring python list in sqlite
    variables: List[str] = Field(sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Dataset(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DatasetItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    dataset_id: uuid.UUID = Field(foreign_key="dataset.id")
    input_data: dict = Field(sa_column=Column(JSON))
    expected_output: dict = Field(sa_column=Column(JSON))
    # avoid clashing with SQLAlchemy DeclarativeMeta.metadata by renaming
    extra_info: Optional[dict] = Field(default=None, sa_column=Column("metadata", JSON))