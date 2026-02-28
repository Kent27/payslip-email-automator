from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class InvoiceExtractionResult(BaseModel):
    invoice_id: Optional[str] = None
    total_amount: float = Field(..., ge=0)
    currency: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    raw: Optional[Dict[str, Any]] = None


class Claim(BaseModel):
    id: str
    employee_id: str
    benefit_type: str
    month: str
    amount_raw: float = Field(..., ge=0)
    amount_approved: float = Field(..., ge=0)
    benefit_limit: float = Field(..., ge=0)
    invoice_id: Optional[str] = None
    invoice_path: Optional[str] = None
    currency: Optional[str] = None
    extraction: Optional[InvoiceExtractionResult] = None
    created_at: datetime


class ClaimCreate(BaseModel):
    employee_id: str
    benefit_type: str
    month: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
