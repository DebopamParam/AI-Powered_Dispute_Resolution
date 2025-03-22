# app/api/database.py
from datetime import datetime
from app.core.config import settings
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
    case,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection
import uuid

# Create SQLite engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    account_type = Column(String)  # e.g., "Individual", "Business"
    dispute_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    disputes = relationship("Dispute", back_populates="customer")


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    transaction_id = Column(String, index=True)
    merchant_name = Column(String)
    amount = Column(Float)
    description = Column(Text)
    category = Column(String, index=True)  # e.g., "Unauthorized", "Duplicate"
    status = Column(String, default="Open")  # "Open", "Under Review", "Resolved"
    priority = Column(Integer, nullable=True)  # 1-5, with 5 being highest priority
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationship
    customer = relationship("Customer", back_populates="disputes")
    notes = relationship("DisputeNote", back_populates="dispute")
    ai_insights = relationship(
        "DisputeInsight", back_populates="dispute", uselist=False
    )


class DisputeNote(Base):
    __tablename__ = "dispute_notes"

    id = Column(String, primary_key=True, index=True)
    dispute_id = Column(String, ForeignKey("disputes.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    dispute = relationship("Dispute", back_populates="notes")



class DisputeInsight(Base):
    """SQLAlchemy model for dispute insights"""

    __tablename__ = "dispute_insights"
    __table_args__ = {"extend_existing": True}  # Allows redefining table options

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dispute_id = Column(
        String, ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False
    )

    # Core insight fields
    insights = Column(String, nullable=False)
    followup_questions = Column(String, nullable=False)
    probable_solutions = Column(String, nullable=False)
    possible_reasons = Column(String, nullable=False)

    # Risk assessment
    risk_score = Column(Float, nullable=False)
    risk_factors = Column(String, nullable=False)

    # Priority fields (from your existing model)
    priority_level = Column(Integer, nullable=False)
    priority_reason = Column(String, nullable=False)

    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship
    dispute = relationship("Dispute", back_populates="ai_insights")

    def __repr__(self):
        return f"<DisputeInsight(id={self.id}, dispute_id={self.dispute_id})>"


# Create all tables
Base.metadata.create_all(bind=engine)


# Add this event listener
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
