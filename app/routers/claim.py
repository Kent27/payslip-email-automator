from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from uuid import uuid4

from app.config import CLAIMS_DIR
from app.models.claim_models import Claim
from app.services.claim_service import claim_service

router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post("", response_model=Claim)
async def add_claim(
    employee_id: str = Form(...),
    benefit_type: str = Form(...),
    month: Optional[str] = Form(None),
    amount: Optional[float] = Form(None),
    invoice: UploadFile = File(...),
) -> Claim:
    try:
        CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
        temp_path = CLAIMS_DIR / f"upload-{uuid4()}-{invoice.filename}"
        temp_path.write_bytes(await invoice.read())
        return claim_service.add_claim(
            employee_id=employee_id,
            benefit_type=benefit_type,
            invoice_path=temp_path,
            month=month,
            amount_override=amount,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("", response_model=List[Claim])
def list_claims(
    employee_id: Optional[str] = None,
    month: Optional[str] = None,
) -> List[Claim]:
    return claim_service.list_claims(employee_id=employee_id, month=month)
