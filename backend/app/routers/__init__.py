# API routers for different resources
from . import (
    health_router, auth_router, case_router, appointment_router, nlp_router,
    lawyers, documents, notifications, legal_search, legal_qa
)

__all__ = [
    "health_router",
    "auth_router",
    "case_router",
    "appointment_router",
    "nlp_router",
    "lawyers",
    "documents",
    "notifications",
    "legal_search",
    "legal_qa",
]
