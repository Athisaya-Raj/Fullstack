"""
FastAPI application entrypoint for JurisLink.
Sets up server, connects to database, and registers routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .core.config import settings
from .db.mongodb import connect_to_db, close_db_connection, get_database
from .routers import (
    health_router, auth_router, case_router, appointment_router, nlp_router,
    lawyers, documents, notifications, legal_search, legal_qa
)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    Handles database connection lifecycle and index creation.
    """
    # Startup
    print("[*] Starting JurisLink backend...")
    await connect_to_db()
    
    # Create database indexes
    try:
        db = get_database()
        
        # Users indexes
        await db["users"].create_index("email", unique=True)
        
        # Lawyers indexes
        await db["lawyers"].create_index("user_id", unique=True)
        await db["lawyers"].create_index("specializations")
        
        # Cases indexes
        await db["cases"].create_index("user_id")
        await db["cases"].create_index("lawyer_id")
        await db["cases"].create_index("status")
        
        # Appointments indexes
        await db["appointments"].create_index("case_id")
        await db["appointments"].create_index("lawyer_id")
        await db["appointments"].create_index("user_id")
        
        # Documents indexes
        await db["documents"].create_index("case_id")
        await db["documents"].create_index("user_id")
        
        # Notifications indexes
        await db["notifications"].create_index("user_id")
        await db["notifications"].create_index("read")
        
        # Case Updates indexes
        await db["case_updates"].create_index("case_id")
        await db["case_updates"].create_index("created_at")
        
        # Legal Cases indexes
        await db["legal_cases"].create_index("source_case_id", unique=True)
        await db["legal_cases"].create_index("legal_category")
        await db["legal_cases"].create_index("case_title")
        
        # Legal QA indexes
        await db["legal_qa"].create_index("legal_category")
        
        print("[+] Database indexes created")
    except Exception as e:
        print(f"[!] Error creating indexes: {e}")
    
    yield
    
    # Shutdown
    print("[*] Shutting down JurisLink backend...")
    await close_db_connection()


# Initialize FastAPI app
app = FastAPI(
    title="JurisLink API",
    description="Legal aid platform API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(case_router.router)
app.include_router(appointment_router.router)
app.include_router(nlp_router.router)
app.include_router(lawyers.router)
app.include_router(documents.router)
app.include_router(notifications.router)
app.include_router(legal_search.router)
app.include_router(legal_qa.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "JurisLink API", "version": "0.1.0"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.ENVIRONMENT == "development"
    )
