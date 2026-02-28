from pathlib import Path

from app.models.employee_models import Benefit, EmployeeCreate
from app.services.claim_service import ClaimService
from app.services.employee_service import EmployeeService


def test_claim_is_capped_by_benefit_limit(tmp_path: Path):
    employees_path = tmp_path / "employees.json"
    claims_path = tmp_path / "claims.json"
    claims_dir = tmp_path / "claims"

    employee_service = EmployeeService(employees_path)
    employee = employee_service.create_employee(
        EmployeeCreate(
            full_name="Eric Wiyanto",
            email="eric@example.com",
            salary=10000000,
            benefits=[Benefit(type="education", limit=100)],
        )
    )

    claim_service = ClaimService(
        claims_path=claims_path,
        claims_dir=claims_dir,
        employee_service_instance=employee_service,
    )

    invoice1 = tmp_path / "invoice1.txt"
    invoice1.write_text("dummy")
    claim1 = claim_service.add_claim(
        employee_id=employee.id,
        benefit_type="education",
        invoice_path=invoice1,
        month="2026-01",
        amount_override=60,
    )

    invoice2 = tmp_path / "invoice2.txt"
    invoice2.write_text("dummy")
    claim2 = claim_service.add_claim(
        employee_id=employee.id,
        benefit_type="education",
        invoice_path=invoice2,
        month="2026-01",
        amount_override=80,
    )

    assert claim1.amount_approved == 60
    assert claim2.amount_approved == 40
