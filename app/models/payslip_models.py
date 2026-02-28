from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PayslipBenefit(BaseModel):
    type: str
    claimed: float = Field(..., ge=0)
    approved: float = Field(..., ge=0)
    limit: float = Field(..., ge=0)


class PayslipData(BaseModel):
    employee_id: str
    employee_name: str
    employee_email: str
    period: str
    base_salary: float = Field(..., ge=0)
    total_working_days: int = Field(..., ge=0)
    worked_days: int = Field(..., ge=0)
    prorated_salary: float = Field(..., ge=0)
    benefits: List[PayslipBenefit]
    total_benefits: float = Field(..., ge=0)
    net_pay: float = Field(..., ge=0)
    generated_at: datetime


class PayslipGenerateRequest(BaseModel):
    employee_id: str
    month: str
    worked_days: Optional[int] = Field(None, ge=0)


class PayslipGenerateResponse(BaseModel):
    payslip: PayslipData
    pdf_path: str


class PayslipSendResponse(BaseModel):
    payslip: PayslipData
    pdf_path: str
    sent: bool
