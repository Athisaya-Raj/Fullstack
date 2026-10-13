"""
NLP router for JurisLink.
Handles issue classification and document summarization.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional


router = APIRouter(prefix="/nlp", tags=["nlp"])
classification_service = None
summarization_service = None


def get_nlp_services():
    """Lazy initialization of NLP services."""
    global classification_service, summarization_service
    if classification_service is None:
        from ..services.classification_service import ClassificationService
        classification_service = ClassificationService()
    if summarization_service is None:
        from ..services.summarization_service import SummarizationService
        summarization_service = SummarizationService()
    return classification_service, summarization_service


class ClassifyRequest(BaseModel):
    """Request model for issue classification."""
    text: str


class ClassifyResponse(BaseModel):
    """Response model for issue classification."""
    category: str
    confidence: float


class SummarizeRequest(BaseModel):
    """Request model for document summarization."""
    text: str
    sentences_count: Optional[int] = 3


class SummarizeResponse(BaseModel):
    """Response model for document summarization."""
    summary: str


@router.post("/classify", response_model=ClassifyResponse)
async def classify_issue(request: ClassifyRequest):
    """
    Classify a legal issue from text.
    
    Uses trained ML model (with fallback to rule-based classification).
    Predicts one of: tenancy, family, labor, consumer, criminal, other.
    
    Args:
        request: Issue text to classify
        
    Returns:
        Classification result with category and confidence score
        
    Raises:
        HTTPException: 400 if text empty, 500 on error
    """
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issue text must be at least 10 characters"
            )
        
        classif_svc, _ = get_nlp_services()
        category, confidence = classif_svc.classify_issue(request.text)
        
        return ClassifyResponse(
            category=category,
            confidence=confidence
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    """
    Summarize a legal document.
    
    Uses LSA (Latent Semantic Analysis) to extract key sentences.
    Minimum text length: 100 characters.
    
    Args:
        request: Document text to summarize and optional sentence count (default 3)
        
    Returns:
        Summary text combining key sentences
        
    Raises:
        HTTPException: 400 if text too short, 500 on error
    """
    try:
        if not request.text or len(request.text.strip()) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document text must be at least 100 characters"
            )
        
        if not request.sentences_count or request.sentences_count < 1:
            request.sentences_count = 3
        
        _, summ_svc = get_nlp_services()
        summary = summ_svc.summarize(
            text=request.text,
            sentences_count=request.sentences_count
        )
        
        return SummarizeResponse(summary=summary)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )
