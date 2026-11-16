from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, QuotationRequest, QuotationResponse, Product, Supplier
from app.schemas.schemas import QuotationRequestCreate, QuotationRequestOut, QuotationResponseCreate, QuotationResponseOut

router = APIRouter(prefix="/quotations", tags=["Quotation Requests"])

@router.post("", response_model=QuotationRequestOut)
def create_quotation_request(
    req: QuotationRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prod = db.query(Product).filter_by(id=req.product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    sup = db.query(Supplier).filter_by(id=req.supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")

    qr = QuotationRequest(
        user_id=current_user.id,
        product_id=req.product_id,
        supplier_id=req.supplier_id,
        quantity=req.quantity,
        dimensions=req.dimensions,
        project_location=req.project_location,
        city=req.city,
        state=req.state,
        pin_code=req.pin_code,
        delivery_urgency=req.delivery_urgency,
        additional_notes=req.additional_notes,
        status="submitted"
    )
    db.add(qr)
    db.commit()
    db.refresh(qr)

    return QuotationRequestOut(
        id=qr.id,
        user_id=qr.user_id,
        product_id=qr.product_id,
        product_name=prod.name,
        supplier_id=qr.supplier_id,
        supplier_name=sup.name,
        quantity=qr.quantity,
        dimensions=qr.dimensions,
        project_location=qr.project_location,
        city=qr.city,
        state=qr.state,
        pin_code=qr.pin_code,
        delivery_urgency=qr.delivery_urgency,
        additional_notes=qr.additional_notes,
        status=qr.status,
        created_at=qr.created_at,
        responses=[]
    )

@router.get("", response_model=List[QuotationRequestOut])
def get_user_quotation_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(QuotationRequest).filter_by(user_id=current_user.id).order_by(QuotationRequest.id.desc()).all()
    results: List[QuotationRequestOut] = []
    for r in requests:
        responses_out = [
            QuotationResponseOut(
                id=res.id,
                supplier_id=res.supplier_id,
                supplier_name=res.supplier.name if res.supplier else "Supplier",
                quoted_price=res.quoted_price,
                currency=res.currency,
                estimated_delivery_days=res.estimated_delivery_days,
                delivery_terms=res.delivery_terms,
                response_message=res.response_message,
                created_at=res.created_at
            ) for res in r.responses
        ]
        results.append(
            QuotationRequestOut(
                id=r.id,
                user_id=r.user_id,
                product_id=r.product_id,
                product_name=r.product.name if r.product else "Product",
                supplier_id=r.supplier_id,
                supplier_name=r.supplier.name if r.supplier else "Supplier",
                quantity=r.quantity,
                dimensions=r.dimensions,
                project_location=r.project_location,
                city=r.city,
                state=r.state,
                pin_code=r.pin_code,
                delivery_urgency=r.delivery_urgency,
                additional_notes=r.additional_notes,
                status=r.status,
                created_at=r.created_at,
                responses=responses_out
            )
        )
    return results

@router.post("/{request_id}/respond", response_model=QuotationResponseOut)
def respond_to_quotation(
    request_id: int,
    resp_in: QuotationResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    qr = db.query(QuotationRequest).filter_by(id=request_id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="Quotation request not found")

    response = QuotationResponse(
        quotation_request_id=qr.id,
        supplier_id=qr.supplier_id,
        quoted_price=resp_in.quoted_price,
        currency=resp_in.currency,
        estimated_delivery_days=resp_in.estimated_delivery_days,
        delivery_terms=resp_in.delivery_terms,
        response_message=resp_in.response_message
    )
    qr.status = "quoted"
    db.add(response)
    db.commit()
    db.refresh(response)

    return QuotationResponseOut(
        id=response.id,
        supplier_id=response.supplier_id,
        supplier_name=qr.supplier.name if qr.supplier else "Supplier",
        quoted_price=response.quoted_price,
        currency=response.currency,
        estimated_delivery_days=response.estimated_delivery_days,
        delivery_terms=response.delivery_terms,
        response_message=response.response_message,
        created_at=response.created_at
    )
