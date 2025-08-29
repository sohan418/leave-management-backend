from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.employee import Employee
from ..schemas.employee import EmployeeCreate, EmployeeUpdate, LeaveBalance
from .base import CRUDBase


class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    async def get_by_employee_id(self, db: AsyncSession, *, employee_id: str) -> Optional[Employee]:
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.user))
            .where(Employee.employee_id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, db: AsyncSession, *, user_id: int) -> Optional[Employee]:
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.user))
            .where(Employee.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_with_user(self, db: AsyncSession, *, id: int) -> Optional[Employee]:
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.user))
            .where(Employee.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_department(self, db: AsyncSession, *, department: str) -> List[Employee]:
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.user))
            .where(Employee.department == department)
            .where(Employee.is_active == True)
        )
        return result.scalars().all()

    async def get_by_manager(self, db: AsyncSession, *, manager_id: int) -> List[Employee]:
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.user))
            .where(Employee.manager_id == manager_id)
            .where(Employee.is_active == True)
        )
        return result.scalars().all()

    async def get_active_employees(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Employee]:
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.user))
            .where(Employee.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_leave_balance(self, db: AsyncSession, *, employee_id: int) -> LeaveBalance:
        from ..models.leave import Leave
        
        employee = await self.get(db, employee_id)
        if not employee:
            return None

        # Get total leaves taken (approved leaves)
        result = await db.execute(
            select(Leave).where(
                Leave.employee_id == employee_id,
                Leave.status == "Approved"
            )
        )
        approved_leaves = result.scalars().all()
        total_leaves_taken = sum(leave.days_requested for leave in approved_leaves)

        # Get pending leaves
        result = await db.execute(
            select(Leave).where(
                Leave.employee_id == employee_id,
                Leave.status == "Pending"
            )
        )
        pending_leaves = result.scalars().all()
        leaves_pending = sum(leave.days_requested for leave in pending_leaves)

        return LeaveBalance(
            annual_leave_balance=employee.annual_leave_balance,
            sick_leave_balance=employee.sick_leave_balance,
            personal_leave_balance=employee.personal_leave_balance,
            total_leaves_taken=total_leaves_taken,
            leaves_pending=leaves_pending
        )

    async def update_leave_balance(
        self, 
        db: AsyncSession, 
        *, 
        employee_id: int, 
        leave_type: str, 
        days: int, 
        operation: str = "subtract"
    ) -> Optional[Employee]:
        employee = await self.get(db, employee_id)
        if not employee:
            return None

        multiplier = -1 if operation == "subtract" else 1
        days_to_update = days * multiplier

        if leave_type.lower() == "annual":
            employee.annual_leave_balance += days_to_update
        elif leave_type.lower() == "sick":
            employee.sick_leave_balance += days_to_update
        elif leave_type.lower() == "personal":
            employee.personal_leave_balance += days_to_update

        await db.commit()
        await db.refresh(employee)
        return employee


employee = CRUDEmployee(Employee)
