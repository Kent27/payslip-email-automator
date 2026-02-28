from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from app.config import EMPLOYEES_FILE
from app.models.employee_models import Employee, EmployeeCreate, EmployeeUpdate
from app.services.storage_utils import read_json_list, write_json_list


class EmployeeService:
    def __init__(self, employees_path=EMPLOYEES_FILE):
        self.employees_path = employees_path

    def list_employees(self) -> List[Employee]:
        data = read_json_list(self.employees_path)
        return [Employee.model_validate(item) for item in data]

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        for employee in self.list_employees():
            if employee.id == employee_id:
                return employee
        return None

    def create_employee(self, payload: EmployeeCreate) -> Employee:
        employees = self.list_employees()
        new_employee = Employee(id=str(uuid4()), **payload.model_dump())
        employees.append(new_employee)
        write_json_list(self.employees_path, [emp.model_dump() for emp in employees])
        return new_employee

    def update_employee(self, employee_id: str, payload: EmployeeUpdate) -> Optional[Employee]:
        employees = self.list_employees()
        updated_employee: Optional[Employee] = None
        for index, employee in enumerate(employees):
            if employee.id == employee_id:
                update_data = payload.model_dump(exclude_unset=True)
                updated_employee = employee.model_copy(update=update_data)
                employees[index] = updated_employee
                break

        if updated_employee:
            write_json_list(self.employees_path, [emp.model_dump() for emp in employees])
        return updated_employee

    def delete_employee(self, employee_id: str) -> bool:
        employees = self.list_employees()
        remaining = [emp for emp in employees if emp.id != employee_id]
        if len(remaining) == len(employees):
            return False
        write_json_list(self.employees_path, [emp.model_dump() for emp in remaining])
        return True


employee_service = EmployeeService()
