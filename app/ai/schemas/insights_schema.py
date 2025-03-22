# app/ai/schemas/insights_schema.py
from typing import List
from pydantic import BaseModel, Field


class InsightsSchema(BaseModel):
    """Schema for dispute insights"""

    insights: str = Field(description="Detailed insights regarding the dispute")
    followup_questions: List[str] = Field(
        description="List of relevant follow-up questions to gather more information"
    )
    probable_solutions: List[str] = Field(
        description="Potential solutions to address the dispute"
    )
    possible_reasons: List[str] = Field(
        description="Possible reasons that might have caused the dispute"
    )

    risk_score: float = Field(
        description="Risk score for the dispute from 0 (lowest) to 10 (highest)"
    )

    risk_factors: List[str] = Field(
        description="3 Factors contributing to the calculated risk score, if low risk, keep empty"
    )




