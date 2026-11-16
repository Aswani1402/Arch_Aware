from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.services.llm_service import architectural_llm_service

router = APIRouter(prefix="/llm", tags=["Architectural AI & Sourcing Intelligence"])

class AnalyzeProjectRequest(BaseModel):
    title: str
    description: str = ""
    tags: List[str] = []
    category: Optional[str] = None

class SourcingAdviceRequest(BaseModel):
    query: str
    location: str = "Nagercoil"
    material_type: Optional[str] = None

class DraftQuotationRequest(BaseModel):
    item_name: str
    category: str = "Construction Material"
    location: str = "Nagercoil"
    quantity_notes: Optional[str] = None

@router.post("/analyze-project")
async def analyze_project(req: AnalyzeProjectRequest):
    """
    AI Material Analysis for Architectural Projects.
    Identifies visible materials, construction techniques, IS codes, and sourcing queries.
    """
    return await architectural_llm_service.analyze_project_materials(
        project_title=req.title,
        description=req.description,
        tags=req.tags,
        category=req.category
    )

@router.post("/sourcing-advice")
async def sourcing_advice(req: SourcingAdviceRequest):
    """
    AI Sourcing Advice tailored to geography and coastal climate (Nagercoil, Tamil Nadu, Kerala).
    """
    return await architectural_llm_service.get_sourcing_advice(
        query=req.query,
        location=req.location,
        material_type=req.material_type
    )

@router.post("/draft-quotation")
async def draft_quotation(req: DraftQuotationRequest):
    """
    Drafts an architectural Request for Quotation (RFQ) with precise specifications.
    """
    return await architectural_llm_service.draft_quotation_rfp(
        item_name=req.item_name,
        category=req.category,
        location=req.location,
        quantity_notes=req.quantity_notes
    )

@router.get("/status")
async def get_llm_status():
    """
    Returns configuration status of LLM service.
    """
    return {
        "configured": architectural_llm_service.is_configured(),
        "model": "gemini-1.5-flash / openai-compatible",
        "has_key": bool(architectural_llm_service.api_key)
    }
