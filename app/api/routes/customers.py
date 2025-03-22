# app/api/routes/customers.py
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.database import get_db, Customer
from app.api.models import Dispute as DisputeModel
from app.api.database import Dispute as DbDispute
from app.api.models import CustomerCreate, Customer as CustomerModel

router = APIRouter()


@router.post("/", response_model=CustomerModel, status_code=201)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if customer with this email already exists
    db_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new customer
    new_customer = Customer(
        id=str(uuid.uuid4()),
        name=customer.name,
        email=customer.email,
        account_type=customer.account_type,
    )

    # Add to database
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # Convert to Pydantic model
    return CustomerModel.model_validate(new_customer.__dict__)


@router.get("/", response_model=List[CustomerModel])
async def get_customers(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    account_type: str = None,
):
    """Get all customers with optional filtering"""
    query = db.query(Customer)

    # Apply filters
    if account_type:
        query = query.filter(Customer.account_type == account_type)

    # Apply pagination
    customers = query.offset(skip).limit(limit).all()

    # Convert to Pydantic models
    return [CustomerModel.model_validate(customer.__dict__) for customer in customers]


@router.get("/{customer_id}", response_model=CustomerModel)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get a specific customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Convert to Pydantic model
    return CustomerModel.model_validate(customer.__dict__)


@router.get("/{customer_id}/disputes", response_model=List[DisputeModel])
async def get_customer_disputes(
    customer_id: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
):
    """Get all disputes for a specific customer with filtering"""
    try:
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Build query
        query = db.query(DbDispute).filter(DbDispute.customer_id == customer_id)

        # Apply status filter if provided
        if status:
            valid_statuses = ["Open", "Under Review", "Resolved"]
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                )
            query = query.filter(DbDispute.status == status)

        # Apply sorting and pagination
        query = query.order_by(DbDispute.created_at.desc())

        # Validate pagination parameters
        if skip < 0:
            skip = 0
        if limit <= 0:
            limit = 100
        elif limit > 500:
            limit = 500

        disputes = query.offset(skip).limit(limit).all()

        # Convert to Pydantic models
        return [DisputeModel.model_validate(dispute.__dict__) for dispute in disputes]
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback

        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.put("/{customer_id}", response_model=CustomerModel)
async def update_customer(
    customer_id: str, customer_update: CustomerCreate, db: Session = Depends(get_db)
):
    """Update a customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if email is being changed and if it's already in use
    if customer_update.email != customer.email:
        existing_customer = (
            db.query(Customer).filter(Customer.email == customer_update.email).first()
        )
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Update fields
    customer.name = customer_update.name
    customer.email = customer_update.email
    customer.account_type = customer_update.account_type

    db.commit()
    db.refresh(customer)

    # Convert to Pydantic model
    return CustomerModel.model_validate(customer.__dict__)


@router.delete("/{customer_id}", response_model=dict)
async def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    """Delete a customer with option to cascade delete disputes"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if customer has disputes
    disputes = db.query(DbDispute).filter(DbDispute.customer_id == customer_id).all()

    if disputes:
        # Inform user of existing disputes that block deletion
        dispute_count = len(disputes)
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete customer with existing disputes. The customer has {dispute_count} disputes.",
        )

    try:
        # Delete the customer
        db.delete(customer)
        db.commit()
        return {"message": "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to delete customer: {str(e)}"
        )
