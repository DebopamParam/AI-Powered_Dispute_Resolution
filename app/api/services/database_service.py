import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union

from ..database import (
    Customer,
    Dispute,
    DisputeAnalysis,
    SupportingDocument,
    DisputeStatus,
)
from ..models import (
    CustomerCreate,
    DisputeCreate,
    CustomerUpdate,
    DisputeUpdate,
    DisputeAnalysisCreate,
)


# Customer operations
def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """Create a new customer in the database"""
    db_customer = Customer(
        id=str(uuid.uuid4()),
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        account_type=customer.account_type,
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer(db: Session, customer_id: str) -> Optional[Customer]:
    """Get a customer by ID"""
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
    """Get a customer by email"""
    return db.query(Customer).filter(Customer.email == email).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    """Get a list of customers"""
    return db.query(Customer).offset(skip).limit(limit).all()


def update_customer(
    db: Session, customer_id: str, customer: CustomerUpdate
) -> Optional[Customer]:
    """Update a customer's information"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None

    # Update only the fields that are provided
    customer_data = customer.dict(exclude_unset=True)
    for key, value in customer_data.items():
        setattr(db_customer, key, value)

    db_customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: str) -> bool:
    """Delete a customer"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False

    db.delete(db_customer)
    db.commit()
    return True


def increment_dispute_count(db: Session, customer_id: str) -> Optional[Customer]:
    """Increment the dispute count for a customer"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None

    db_customer.dispute_count += 1
    db_customer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_customer)
    return db_customer


# Dispute operations
def create_dispute(db: Session, dispute: DisputeCreate) -> Dispute:
    """Create a new dispute in the database"""
    dispute_id = str(uuid.uuid4())
    db_dispute = Dispute(
        id=dispute_id,
        customer_id=dispute.customer_id,
        transaction_id=dispute.transaction_id,
        merchant_name=dispute.merchant_name,
        amount=dispute.amount,
        description=dispute.description,
        category=dispute.category,
        status=DisputeStatus.NEW,
    )
    db.add(db_dispute)
    db.commit()
    db.refresh(db_dispute)

    # Increment the customer's dispute count
    increment_dispute_count(db, dispute.customer_id)

    return db_dispute


def get_dispute(db: Session, dispute_id: str) -> Optional[Dispute]:
    """Get a dispute by ID"""
    return db.query(Dispute).filter(Dispute.id == dispute_id).first()


def get_disputes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[List[DisputeStatus]] = None,
    priority: Optional[List[int]] = None,
    customer_id: Optional[str] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
) -> List[Dispute]:
    """Get a list of disputes with filtering and sorting options"""
    query = db.query(Dispute)

    # Apply filters
    if status:
        query = query.filter(Dispute.status.in_(status))

    if priority:
        query = query.filter(Dispute.priority.in_(priority))

    if customer_id:
        query = query.filter(Dispute.customer_id == customer_id)

    # Apply sorting
    if sort_by == "priority" and sort_desc:
        query = query.order_by(
            Dispute.priority.desc().nullslast(), Dispute.created_at.desc()
        )
    elif sort_by == "priority" and not sort_desc:
        query = query.order_by(
            Dispute.priority.asc().nullsfirst(), Dispute.created_at.desc()
        )
    elif sort_by == "amount" and sort_desc:
        query = query.order_by(Dispute.amount.desc(), Dispute.created_at.desc())
    elif sort_by == "amount" and not sort_desc:
        query = query.order_by(Dispute.amount.asc(), Dispute.created_at.desc())
    elif sort_desc:
        query = query.order_by(getattr(Dispute, sort_by).desc())
    else:
        query = query.order_by(getattr(Dispute, sort_by).asc())

    return query.offset(skip).limit(limit).all()


def update_dispute(
    db: Session, dispute_id: str, dispute: DisputeUpdate
) -> Optional[Dispute]:
    """Update a dispute's information"""
    db_dispute = get_dispute(db, dispute_id)
    if not db_dispute:
        return None

    # Update only the fields that are provided
    dispute_data = dispute.dict(exclude_unset=True)
    for key, value in dispute_data.items():
        if key == "status" and value in [
            DisputeStatus.APPROVED,
            DisputeStatus.REJECTED,
            DisputeStatus.CLOSED,
        ]:
            # Set resolved_at timestamp when dispute is resolved
            db_dispute.resolved_at = datetime.utcnow()
        setattr(db_dispute, key, value)

    db_dispute.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_dispute)
    return db_dispute


def delete_dispute(db: Session, dispute_id: str) -> bool:
    """Delete a dispute"""
    db_dispute = get_dispute(db, dispute_id)
    if not db_dispute:
        return False

    db.delete(db_dispute)
    db.commit()
    return True


# AI Analysis operations
def create_dispute_analysis(
    db: Session, dispute_id: str, analysis: DisputeAnalysisCreate
) -> Optional[DisputeAnalysis]:
    """Create a new AI analysis for a dispute"""
    # Check if dispute exists
    db_dispute = get_dispute(db, dispute_id)
    if not db_dispute:
        return None

    # Check if analysis already exists
    existing_analysis = (
        db.query(DisputeAnalysis)
        .filter(DisputeAnalysis.dispute_id == dispute_id)
        .first()
    )

    if existing_analysis:
        # Update existing analysis
        existing_analysis.priority = analysis.priority
        existing_analysis.priority_reason = analysis.priority_reason
        existing_analysis.insights = analysis.insights
        existing_analysis.possible_reasons = str(analysis.possible_reasons)
        existing_analysis.probable_solutions = str(analysis.probable_solutions)
        existing_analysis.followup_questions = str(analysis.followup_questions)
        existing_analysis.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing_analysis)
        return existing_analysis
    else:
        # Create new analysis
        db_analysis = DisputeAnalysis(
            id=str(uuid.uuid4()),
            dispute_id=dispute_id,
            priority=analysis.priority,
            priority_reason=analysis.priority_reason,
            insights=analysis.insights,
            possible_reasons=str(analysis.possible_reasons),
            probable_solutions=str(analysis.probable_solutions),
            followup_questions=str(analysis.followup_questions),
        )

        # Update dispute priority
        db_dispute.priority = analysis.priority
        db_dispute.updated_at = datetime.utcnow()

        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis


def get_dispute_analysis(db: Session, dispute_id: str) -> Optional[DisputeAnalysis]:
    """Get AI analysis for a dispute"""
    return (
        db.query(DisputeAnalysis)
        .filter(DisputeAnalysis.dispute_id == dispute_id)
        .first()
    )


# Dashboard metrics
def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
    """Get metrics for the dashboard"""
    # Total disputes
    total_disputes = db.query(Dispute).count()

    # High priority disputes (4-5)
    high_priority_count = db.query(Dispute).filter(Dispute.priority.in_([4, 5])).count()

    # Pending disputes
    pending_count = (
        db.query(Dispute)
        .filter(
            Dispute.status.in_(
                [
                    DisputeStatus.NEW,
                    DisputeStatus.UNDER_REVIEW,
                    DisputeStatus.INFO_REQUESTED,
                ]
            )
        )
        .count()
    )

    # Resolved today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = (
        db.query(Dispute).filter(Dispute.resolved_at >= today_start).count()
    )

    # Disputes by category
    category_query = (
        db.query(Dispute.category, db.func.count(Dispute.id).label("count"))
        .group_by(Dispute.category)
        .all()
    )
    disputes_by_category = {category: count for category, count in category_query}

    # Disputes by status
    status_query = (
        db.query(Dispute.status, db.func.count(Dispute.id).label("count"))
        .group_by(Dispute.status)
        .all()
    )
    disputes_by_status = {status.name: count for status, count in status_query}

    # Disputes by priority
    priority_query = (
        db.query(Dispute.priority, db.func.count(Dispute.id).label("count"))
        .filter(Dispute.priority.isnot(None))
        .group_by(Dispute.priority)
        .all()
    )
    disputes_by_priority = {priority: count for priority, count in priority_query}

    return {
        "total_disputes": total_disputes,
        "high_priority_count": high_priority_count,
        "pending_count": pending_count,
        "resolved_today": resolved_today,
        "disputes_by_category": disputes_by_category,
        "disputes_by_status": disputes_by_status,
        "disputes_by_priority": disputes_by_priority,
    }
