from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from app.models.payslip_models import PayslipBenefit, PayslipData
from app.services.claim_service import ClaimService, claim_service
from app.services.employee_service import EmployeeService, employee_service
from app.services.payslip_generator import generate_payslip_pdf
from app.services.proration_service import (
    calculate_prorated_amount,
    calculate_worked_days_for_month,
    calculate_working_days,
)
from app.services.email_service import EmailService, email_service


def _parse_month(month: str) -> Tuple[int, int]:
    try:
        parsed = datetime.strptime(month, "%Y-%m")
        return parsed.year, parsed.month
    except ValueError:
        raise ValueError("Month must be in YYYY-MM format")


class PayslipService:
    def __init__(
        self,
        employee_service_instance: EmployeeService = employee_service,
        claim_service_instance: ClaimService = claim_service,
        email_service_instance: EmailService = email_service,
    ):
        self.employee_service = employee_service_instance
        self.claim_service = claim_service_instance
        self.email_service = email_service_instance

    def generate_payslip(
        self,
        employee_id: str,
        month: str,
        worked_days: Optional[int] = None,
    ) -> Tuple[PayslipData, str]:
        employee = self.employee_service.get_employee(employee_id)
        if not employee:
            raise ValueError("Employee not found")

        year, month_index = _parse_month(month)
        total_working_days = calculate_working_days(year, month_index)
        if worked_days is None:
            worked_days = calculate_worked_days_for_month(
                year, month_index, join_date=employee.join_date
            )

        prorated_salary = calculate_prorated_amount(
            employee.salary, worked_days, total_working_days
        )

        claims = self.claim_service.list_claims(employee_id=employee_id, month=month)
        benefits_summary = []
        total_benefits = 0.0
        for benefit in employee.benefits:
            claimed = sum(
                claim.amount_raw for claim in claims if claim.benefit_type == benefit.type
            )
            approved = sum(
                claim.amount_approved
                for claim in claims
                if claim.benefit_type == benefit.type
            )
            benefits_summary.append(
                PayslipBenefit(
                    type=benefit.type,
                    claimed=claimed,
                    approved=approved,
                    limit=benefit.limit,
                )
            )
            total_benefits += approved

        net_pay = prorated_salary + total_benefits
        payslip_data = PayslipData(
            employee_id=employee.id,
            employee_name=employee.full_name,
            employee_email=employee.email,
            period=month,
            base_salary=employee.salary,
            total_working_days=total_working_days,
            worked_days=worked_days,
            prorated_salary=prorated_salary,
            benefits=benefits_summary,
            total_benefits=total_benefits,
            net_pay=net_pay,
            generated_at=datetime.utcnow(),
        )

        pdf_path = generate_payslip_pdf(payslip_data)
        return payslip_data, str(pdf_path)

    def send_payslip(self, employee_id: str, month: str, worked_days: Optional[int] = None) -> str:
        payslip_data, pdf_path = self.generate_payslip(employee_id, month, worked_days)
        self.email_service.send_payslip(payslip_data, pdf_path)
        return pdf_path


payslip_service = PayslipService()
