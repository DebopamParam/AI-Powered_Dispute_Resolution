# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.routes import disputes, customers
from app.api.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for banking dispute resolution system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(disputes.router, prefix="/api/v1/disputes", tags=["disputes"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])


# Create tables (for development)
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to the banking dispute resolution system."}


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "OK"}
