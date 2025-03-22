from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# Customer Models
class CustomerBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    name: str
    email: EmailStr
    account_type: str = "Individual"

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: str
    dispute_count: int = 0
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")

# Dispute Models
class DisputeBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    customer_id: str
    transaction_id: str
    merchant_name: str
    amount: float
    description: str
    category: str

class DisputeCreate(DisputeBase):
    pass

class DisputeUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    status: Optional[str] = None
    priority: Optional[int] = None
    description: Optional[str] = None

class Dispute(DisputeBase):
    id: str
    status: str
    priority: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")

class DisputeWithCustomer(Dispute):
    customer: Customer
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")

# Note Models
class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    content: str
    dispute_id: str

class Note(NoteCreate):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")

# AI Insight Models
class FollowupQuestion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    question: str

class ProbableSolution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    solution: str
    confidence: Optional[float] = None

class PossibleReason(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    reason: str
    confidence: Optional[float] = None

class InsightCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    dispute_id: str
    priority_level: int
    priority_reason: str
    insights: str
    followup_questions: List[str]
    probable_solutions: List[str]
    possible_reasons: List[str]

class Insight(InsightCreate):
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")

# AI Analysis Request/Response
class DisputeAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    dispute_id: str
    analysis: Dict[str, Any]

class DashboardMetrics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    total_disputes: int
    high_priority_count: int
    pending_count: int
    resolved_today: Optional[int] = None 
    disputes_by_category: Dict[str, int] = {}
    disputes_by_status: Dict[str, int] = {}
    disputes_by_priority: Dict[str, int] = {}
    average_resolution_time: Optional[str] = None

class Insights(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    
    id: str
    dispute_id: str
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
        description="Factors contributing to the calculated risk score, if low risk, keep empty"
    )
    priority_level: int
    priority_reason: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class InsightsCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
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
        description="Factors contributing to the calculated risk score, if low risk, keep empty"
    )
    priority_level: int
    priority_reason: str
