# app/api/routes/disputes.py
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import case
import json
from app.api.database import get_db, Dispute, Customer, DisputeNote, DisputeInsight
from app.api.models import (
    DisputeCreate,
    Dispute as DisputeModel,
    DisputeUpdate,
    DisputeWithCustomer,
    DisputeAnalysisResponse,
)
from app.ai.langchain_service import DisputeAIService

router = APIRouter()


# Dependency for AI service
def get_ai_service():
    return DisputeAIService()


@router.post("/", response_model=DisputeModel, status_code=201)
async def create_dispute(
    dispute: DisputeCreate,
    db: Session = Depends(get_db),
):
    """Create a new dispute"""
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == dispute.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create new dispute with all required fields from DisputeCreate model
    new_dispute = Dispute(
        id=str(uuid.uuid4()),
        customer_id=dispute.customer_id,
        transaction_id=dispute.transaction_id,
        merchant_name=dispute.merchant_name,
        amount=dispute.amount,
        description=dispute.description,
        category=dispute.category,
        status="Open",
        priority=None,
        created_at=datetime.utcnow(),
        resolved_at=None,
    )

    # Increment customer dispute count
    customer.dispute_count += 1

    # Add to database
    db.add(new_dispute)
    db.commit()
    db.refresh(new_dispute)

    # Convert to Pydantic model
    return DisputeModel.model_validate(new_dispute.__dict__, strict=False)


@router.get(
    "/",
    response_model=List[DisputeModel],
)
async def get_disputes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    category: Optional[str] = None,
    priority_sort: bool = Query(True, description="Sort by priority (high to low)"),
    date_sort: str = Query("desc", description="Sort by date ('asc' or 'desc')"),
):
    """Get all disputes with improved filtering and sorting"""
    query = db.query(Dispute)

    # Apply filters
    if status:
        valid_statuses = ["Open", "Under Review", "Resolved"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}",
            )
        query = query.filter(Dispute.status == status)

    if priority:
        if not 1 <= priority <= 5:
            raise HTTPException(
                status_code=400, detail="Priority filter must be between 1 and 5"
            )
        query = query.filter(Dispute.priority == priority)

    if category:
        query = query.filter(Dispute.category == category)

    # Apply sorting
    if priority_sort:
        # Sort by priority descending (nulls last)
        query = query.order_by(
            case({None: 0}, value=Dispute.priority, else_=Dispute.priority).desc()
        )

    # Apply date sorting
    if date_sort.lower() == "asc":
        query = query.order_by(Dispute.created_at.asc())
    else:
        query = query.order_by(Dispute.created_at.desc())

    # Apply pagination with validation
    if skip < 0:
        skip = 0
    if limit <= 0:
        limit = 100
    elif limit > 500:  # Set a reasonable maximum
        limit = 500

    # Execute query with pagination
    try:
        disputes = query.offset(skip).limit(limit).all()
        # Convert to Pydantic models
        return [DisputeModel.model_validate(dispute.__dict__) for dispute in disputes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")


@router.get("/{dispute_id}", response_model=DisputeWithCustomer)
async def get_dispute(dispute_id: str, db: Session = Depends(get_db)):
    """Get a specific dispute with customer details"""
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Get the customer
    customer = db.query(Customer).filter(Customer.id == dispute.customer_id).first()

    # Prepare the result dict
    result = dispute.__dict__.copy()
    result["customer"] = customer.__dict__ if customer else None

    # Convert to Pydantic model
    return DisputeWithCustomer.model_validate(result)


@router.put("/{dispute_id}", response_model=DisputeModel)
async def update_dispute(
    dispute_id: str, dispute_update: DisputeUpdate, db: Session = Depends(get_db)
):
    """Update a dispute"""
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check if any fields are provided
    update_data = dispute_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    # Update fields with validation
    if dispute_update.status is not None:
        # Validate status
        valid_statuses = ["Open", "Under Review", "Resolved"]
        if dispute_update.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        dispute.status = dispute_update.status
        if dispute_update.status == "Resolved" and not dispute.resolved_at:
            dispute.resolved_at = datetime.utcnow()

    if dispute_update.priority is not None:
        # Validate priority
        if not 1 <= dispute_update.priority <= 5:
            raise HTTPException(
                status_code=400, detail="Priority must be between 1 and 5"
            )
        dispute.priority = dispute_update.priority

    if dispute_update.description is not None:
        dispute.description = dispute_update.description

    try:
        db.commit()
        db.refresh(dispute)
        # Convert to Pydantic model
        return DisputeModel.model_validate(dispute.__dict__)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Rest of the code remains the same...
# Just be sure to add the proper model_validate conversion in each endpoint


@router.post(
    "/{dispute_id}/analyze", response_model=DisputeAnalysisResponse, status_code=201
)
async def analyze_dispute(
    dispute_id: str,
    db: Session = Depends(get_db),
    ai_service: DisputeAIService = Depends(get_ai_service),
):
    # The response is already properly converted to a Pydantic model
    # No changes needed
    try:
        # Get dispute from database
        dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")

        # Check if analysis already exists
        existing_insight = (
            db.query(DisputeInsight)
            .filter(DisputeInsight.dispute_id == dispute_id)
            .first()
        )
        if existing_insight:
            # Return existing analysis instead of creating a duplicate
            analysis_result = {
                "priority": existing_insight.priority_level,
                "priority_reason": existing_insight.priority_reason,
                "insights": existing_insight.insights,
                "followup_questions": json.loads(existing_insight.followup_questions),
                "probable_solutions": json.loads(existing_insight.probable_solutions),
                "possible_reasons": json.loads(existing_insight.possible_reasons),
                "risk_score": existing_insight.risk_score,
                "risk_factors": json.loads(existing_insight.risk_factors),
            }
            response_data = {"dispute_id": dispute_id, "analysis": analysis_result}
            return DisputeAnalysisResponse.model_validate(response_data)

        # Get customer information
        customer = db.query(Customer).filter(Customer.id == dispute.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Prepare data for AI analysis
        dispute_data = {
            "dispute_id": dispute.id,
            "customer_id": dispute.customer_id,
            "customer_name": customer.name,
            "customer_type": customer.account_type,
            "transaction_id": dispute.transaction_id,
            "merchant_name": dispute.merchant_name,
            "transaction_date": dispute.created_at.isoformat(),
            "dispute_date": dispute.created_at.isoformat(),
            "transaction_amount": dispute.amount,
            "dispute_description": dispute.description,
            "category": dispute.category,
            "previous_disputes_count": customer.dispute_count,
            "customer_account_age_days": (
                (datetime.utcnow() - customer.created_at).days
            ),
            "has_supporting_documents": False,  # Example value
        }

        # Analyze dispute using AI
        analysis_result = ai_service.analyze_dispute(dispute_data)

        # Validate required fields in analysis_result
        required_fields = [
            "priority",
            "priority_reason",
            "insights",
            "followup_questions",
            "probable_solutions",
            "possible_reasons",
            "risk_score",
            "risk_factors",
        ]
        for field in required_fields:
            if field not in analysis_result:
                raise ValueError(f"AI analysis missing required field: {field}")

        # Update dispute with priority (from analysis_result, not directly setting it)
        dispute.priority = analysis_result["priority"]
        db.commit()

        # Store AI insights with proper field validation
        insight = DisputeInsight(
            id=str(uuid.uuid4()),
            dispute_id=dispute_id,
            priority_level=analysis_result["priority"],
            priority_reason=analysis_result["priority_reason"],
            insights=analysis_result["insights"],
            followup_questions=json.dumps(analysis_result["followup_questions"]),
            probable_solutions=json.dumps(analysis_result["probable_solutions"]),
            possible_reasons=json.dumps(analysis_result["possible_reasons"]),
            risk_score=analysis_result["risk_score"],
            risk_factors=json.dumps(analysis_result["risk_factors"]),
        )
        db.add(insight)
        db.commit()

        # Return analysis results
        response_data = {"dispute_id": dispute_id, "analysis": analysis_result}
        return DisputeAnalysisResponse.model_validate(response_data)
    except ValueError as e:
        # Handle missing fields in AI response
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the detailed error for debugging
        import traceback

        print(f"AI analysis failed: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.delete("/{dispute_id}", response_model=dict)
async def delete_dispute(dispute_id: str, db: Session = Depends(get_db)):
    """Delete a dispute"""
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check and delete dispute notes if they exist
    if db.query(DisputeNote).filter(DisputeNote.dispute_id == dispute_id).first():
        db.query(DisputeNote).filter(DisputeNote.dispute_id == dispute_id).delete()

    # Check and delete dispute insights if they exist
    if db.query(DisputeInsight).filter(DisputeInsight.dispute_id == dispute_id).first():
        db.query(DisputeInsight).filter(
            DisputeInsight.dispute_id == dispute_id
        ).delete()

    # Delete the dispute
    db.delete(dispute)
    db.commit()

    return {"message": "Dispute deleted successfully"}


from app.api.models import Insights, InsightsCreate


@router.post("/{dispute_id}/insights", response_model=Insights, status_code=201)
async def create_dispute_insights(
    dispute_id: str,
    insight_data: InsightsCreate,
    db: Session = Depends(get_db),
):
    """Create new insights for a dispute with proper validation"""
    # Check if dispute exists
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Check if insight already exists for this dispute
    existing_insight = (
        db.query(DisputeInsight).filter(DisputeInsight.dispute_id == dispute_id).first()
    )
    if existing_insight:
        raise HTTPException(
            status_code=400, detail="Insights already exist for this dispute"
        )

    # Validate risk_score range
    if not 0 <= insight_data.risk_score <= 10:
        raise HTTPException(
            status_code=400, detail="Risk score must be between 0 and 10"
        )

    # Validate priority_level range
    if not 1 <= insight_data.priority_level <= 5:
        raise HTTPException(
            status_code=400, detail="Priority level must be between 1 and 5"
        )

    try:
        # Create new insight with proper JSON serialization
        new_insight = DisputeInsight(
            id=str(uuid.uuid4()),
            dispute_id=dispute_id,
            insights=insight_data.insights,
            followup_questions=json.dumps(insight_data.followup_questions),
            probable_solutions=json.dumps(insight_data.probable_solutions),
            possible_reasons=json.dumps(insight_data.possible_reasons),
            risk_score=insight_data.risk_score,
            risk_factors=json.dumps(insight_data.risk_factors),
            priority_level=insight_data.priority_level,
            priority_reason=insight_data.priority_reason,
        )

        # Update the dispute's priority to match the insight priority
        dispute.priority = insight_data.priority_level

        # Add insight to database
        db.add(new_insight)
        db.commit()
        db.refresh(new_insight)

        # Return formatted response
        return _format_insight_response(new_insight)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating insights: {str(e)}"
        )


@router.get("/{dispute_id}/insights", response_model=Insights)
async def get_dispute_insights(dispute_id: str, db: Session = Depends(get_db)):
    """Get insights for a specific dispute"""
    # Check if dispute exists
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Get the insights
    insight = (
        db.query(DisputeInsight).filter(DisputeInsight.dispute_id == dispute_id).first()
    )
    if not insight:
        raise HTTPException(
            status_code=404, detail="No insights found for this dispute"
        )

    # Handle potentially malformed JSON with more detailed error messages
    try:
        return _format_insight_response(insight)
    except json.JSONDecodeError as e:
        # Log the specific JSON error
        print(f"JSON decode error in dispute insights: {str(e)}")
        # Create a response with empty lists for fields that failed to parse
        insight_data = {
            "id": insight.id,
            "dispute_id": insight.dispute_id,
            "insights": insight.insights,
            "followup_questions": [],
            "probable_solutions": [],
            "possible_reasons": [],
            "risk_score": insight.risk_score,
            "risk_factors": [],
            "priority_level": insight.priority_level,
            "priority_reason": insight.priority_reason,
            "created_at": insight.created_at,
            "updated_at": insight.updated_at,
        }
        return Insights.model_validate(insight_data)


@router.put("/{dispute_id}/insights", response_model=Insights)
async def update_dispute_insights(
    dispute_id: str, insight_data: InsightsCreate, db: Session = Depends(get_db)
):
    """Update insights for a specific dispute"""
    # Check if dispute exists
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    # Get the existing insight
    insight = (
        db.query(DisputeInsight).filter(DisputeInsight.dispute_id == dispute_id).first()
    )
    if not insight:
        raise HTTPException(
            status_code=404, detail="No insights found for this dispute"
        )

    # Update fields
    insight.insights = insight_data.insights
    insight.followup_questions = json.dumps(insight_data.followup_questions)
    insight.probable_solutions = json.dumps(insight_data.probable_solutions)
    insight.possible_reasons = json.dumps(insight_data.possible_reasons)
    insight.risk_score = insight_data.risk_score
    insight.risk_factors = json.dumps(insight_data.risk_factors)
    insight.priority_level = insight_data.priority_level
    insight.priority_reason = insight_data.priority_reason

    # Commit changes
    db.commit()
    db.refresh(insight)

    # Convert the stored JSON strings back to lists for the response
    return _format_insight_response(insight)


# Helper function to format insight response
def _format_insight_response(insight):
    """Convert SQLAlchemy model to Pydantic model with JSON parsing"""
    insight_data = {
        "id": insight.id,
        "dispute_id": insight.dispute_id,
        "insights": insight.insights,
        "followup_questions": json.loads(insight.followup_questions),
        "probable_solutions": json.loads(insight.probable_solutions),
        "possible_reasons": json.loads(insight.possible_reasons),
        "risk_score": insight.risk_score,
        "risk_factors": json.loads(insight.risk_factors),
        "priority_level": insight.priority_level,
        "priority_reason": insight.priority_reason,
        "created_at": insight.created_at,
        "updated_at": insight.updated_at if hasattr(insight, "updated_at") else None,
    }
    return Insights.model_validate(insight_data)
