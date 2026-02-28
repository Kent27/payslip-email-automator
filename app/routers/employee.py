from fastapi import APIRouter, HTTPException
from typing import List, Dict

from app.models.employee_models import Employee, EmployeeCreate, EmployeeUpdate
from app.services.employee_service import employee_service

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.post("", response_model=Employee)
def create_employee(payload: EmployeeCreate) -> Employee:
    return employee_service.create_employee(payload)


@router.get("", response_model=List[Employee])
def list_employees() -> List[Employee]:
    return employee_service.list_employees()


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: str) -> Employee:
    employee = employee_service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, payload: EmployeeUpdate) -> Employee:
    employee = employee_service.update_employee(employee_id, payload)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", response_model=Dict[str, bool])
def delete_employee(employee_id: str) -> Dict[str, bool]:
    deleted = employee_service.delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"success": True}
