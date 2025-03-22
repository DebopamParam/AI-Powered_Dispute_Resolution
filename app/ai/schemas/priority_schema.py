# app/ai/schemas/priority_schema.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

class PrioritySchema(BaseModel):
    """Schema for priority assignment"""
    priority_level: int = Field(
        description="Priority level from 1 (lowest) to 10 (highest)"
    )
    priority_reason: str = Field(
        description="Explanation for the assigned priority level"
    )