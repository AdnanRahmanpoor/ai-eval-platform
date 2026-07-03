from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

# Prompt schemas
class PromptBase(BaseModel):
    name: str
    template: str
    variables: List[str]

class PromptCreate(PromptBase):
    pass

class PromptRead(PromptBase):
    id: UUID
    version: int
    is_active: bool
    created_at: datetime
    # pydantic config to read from sqlalchemy object
    model_config = ConfigDict(from_attributes=True)

# Dataset schemas
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    pass

class DatasetRead(DatasetBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DatasetItemCreate(BaseModel):
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    extra_info: Optional[Dict[str, Any]] = None

class DatasetItemRead(BaseModel):
    id: UUID
    dataset_id: UUID
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    extra_info: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes = True)

# Evaluation Schemas
class EvalRequest(BaseModel):
    criteria: str = Field(..., description = "The specific rubric or instruction for the judge.")
    text_to_grade: str = Field(..., description = "The raw output from the AI agent/prompt being evaluated.")

class EvalResult(BaseModel):
    score: int = Field(ge=1, le=5, description="An integer score from 1 (terrible) to 5 (perfect).")
    reasoning: str = Field(..., description="A concise, 1-2 sentence explanation of the score.")