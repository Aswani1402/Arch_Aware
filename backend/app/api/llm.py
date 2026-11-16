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

class VisionIdentifyRequest(BaseModel):
    image_url: str
    title: str = ""

class VideoAnalyzeRequest(BaseModel):
    video_url: str
    title: str = ""
    duration_seconds: int = 180

@router.post("/vision/identify")
def identify_image_materials(req: VisionIdentifyRequest):
    """
    Stage 10 Vision AI: Identifies architectural materials from an image,
    strictly categorized into observed, inferred (Tier 4), and uncertain (Tier 5).
    """
    from app.services.vision_service import identify_materials_from_image
    return identify_materials_from_image(image_url=req.image_url, title=req.title)

@router.post("/video/analyze")
def analyze_video_materials(req: VideoAnalyzeRequest):
    """
    Stage 11 Video Analysis: Extracts 6-8 keyframes and correlates scene materials.
    """
    from app.services.vision_service import analyze_video_keyframes
    return analyze_video_keyframes(video_url=req.video_url, title=req.title, duration_seconds=req.duration_seconds)
