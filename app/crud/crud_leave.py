from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, extract
from sqlalchemy.orm import selectinload
import json
import calendar

from ..models.leave import Leave, LeaveType, Holiday
from ..models.employee import Employee
from ..schemas.leave import (
    LeaveCreate, LeaveUpdate, LeaveTypeCreate, LeaveTypeUpdate,
    HolidayCreate, HolidayUpdate, LeaveStatistics, CalendarEvent,
    LeaveStatusEnum
)
from .base import CRUDBase


class CRUDLeave(CRUDBase[Leave, LeaveCreate, LeaveUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[Leave]:
        """Override base get method to always load relationships"""
        result = await db.execute(
            select(Leave)
            .options(
                selectinload(Leave.employee).selectinload(Employee.user),
                selectinload(Leave.approver).selectinload(Employee.user)
            )
            .where(Leave.id == id)
        )
        return result.scalar_one_or_none()
    
    async def create_leave(self, db: AsyncSession, *, obj_in: LeaveCreate, employee_id: int) -> Leave:
        # Calculate business days between start and end date
        days_requested = self._calculate_business_days(obj_in.start_date, obj_in.end_date)
        if obj_in.is_half_day:
            days_requested = 0.5

        # Convert documents list to JSON string if provided
        documents_json = json.dumps(obj_in.documents) if obj_in.documents else None

        create_data = {
            **obj_in.dict(exclude={"documents"}),
            "employee_id": employee_id,
            "days_requested": days_requested,
            "documents": documents_json,
            "applied_date": date.today()
        }
        
        db_obj = Leave(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_employee_leaves(
        self, 
        db: AsyncSession, 
        *, 
        employee_id: int,
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        leave_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Leave]:
        query = select(Leave).options(
            selectinload(Leave.employee).selectinload(Employee.user),
            selectinload(Leave.approver).selectinload(Employee.user)
        ).where(Leave.employee_id == employee_id)

        if status:
            query = query.where(Leave.status == status)
        if leave_type:
            query = query.where(Leave.leave_type == leave_type)
        if start_date:
            query = query.where(Leave.start_date >= start_date)
        if end_date:
            query = query.where(Leave.end_date <= end_date)

        query = query.order_by(Leave.applied_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all_leaves(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        leave_type: Optional[str] = None,
        department: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Leave]:
        print(f"DEBUG: get_all_leaves called with status={status}, leave_type={leave_type}, department={department}")
        
        query = select(Leave).options(
            selectinload(Leave.employee).selectinload(Employee.user),
            selectinload(Leave.approver).selectinload(Employee.user)
        )

        if status:
            print(f"DEBUG: Applying status filter: {status}")
            query = query.where(Leave.status == status)
        if leave_type:
            query = query.where(Leave.leave_type == leave_type)
        if department:
            query = query.join(Employee).where(Employee.department == department)
        if start_date:
            query = query.where(Leave.start_date >= start_date)
        if end_date:
            query = query.where(Leave.end_date <= end_date)

        query = query.order_by(Leave.applied_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        leaves = result.scalars().all()
        print(f"DEBUG: get_all_leaves returned {len(leaves)} leaves")
        for leave in leaves:
            print(f"DEBUG: Leave {leave.id}: status={leave.status}, employee={leave.employee.employee_id if leave.employee else 'None'}")
        return leaves

    async def approve_leave(
        self, 
        db: AsyncSession, 
        *, 
        leave_id: int, 
        approver_id: Optional[int], 
        status: LeaveStatusEnum, 
        rejection_reason: Optional[str] = None
    ) -> Optional[Leave]:
        leave = await self.get(db, leave_id)
        if not leave:
            return None

        leave.status = status.value
        leave.approved_by = approver_id  # Can be None for admin users
        leave.approved_date = date.today()
        if rejection_reason:
            leave.rejection_reason = rejection_reason

        await db.commit()
        await db.refresh(leave)
        
        # Get the updated leave with relationships loaded
        return await self.get(db, leave_id)

    async def get_leave_statistics(self, db: AsyncSession, employee_id: Optional[int] = None) -> LeaveStatistics:
        query_base = select(Leave)
        if employee_id:
            query_base = query_base.where(Leave.employee_id == employee_id)

        # Total leaves
        result = await db.execute(query_base)
        all_leaves = result.scalars().all()
        total_leaves = len(all_leaves)

        # Count by status
        pending_leaves = len([l for l in all_leaves if l.status == "Pending"])
        approved_leaves = len([l for l in all_leaves if l.status == "Approved"])
        rejected_leaves = len([l for l in all_leaves if l.status == "Rejected"])

        # Leaves this month
        current_month = datetime.now().month
        current_year = datetime.now().year
        leaves_this_month = len([
            l for l in all_leaves 
            if l.applied_date.month == current_month and l.applied_date.year == current_year
        ])

        # Leaves this year
        leaves_this_year = len([
            l for l in all_leaves 
            if l.applied_date.year == current_year
        ])

        # Employees on leave today
        today = date.today()
        on_leave_today = len([
            l for l in all_leaves 
            if l.status == "Approved" and l.start_date <= today <= l.end_date
        ])

        return LeaveStatistics(
            total_leaves=total_leaves,
            pending_leaves=pending_leaves,
            approved_leaves=approved_leaves,
            rejected_leaves=rejected_leaves,
            leaves_this_month=leaves_this_month,
            leaves_this_year=leaves_this_year,
            on_leave_today=on_leave_today
        )

    async def get_calendar_events(
        self, 
        db: AsyncSession, 
        *, 
        year: int, 
        month: int, 
        employee_id: Optional[int] = None
    ) -> List[CalendarEvent]:
        events = []
        
        # Get leaves for the month
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        query = select(Leave).options(
            selectinload(Leave.employee).selectinload(Employee.user)
        ).where(
            and_(
                Leave.start_date <= end_date,
                Leave.end_date >= start_date
            )
        )

        if employee_id:
            query = query.where(Leave.employee_id == employee_id)

        result = await db.execute(query)
        leaves = result.scalars().all()

        for leave in leaves:
            events.append(CalendarEvent(
                id=leave.id,
                title=f"{leave.employee.user.first_name} {leave.employee.user.last_name} - {leave.leave_type}",
                start_date=leave.start_date,
                end_date=leave.end_date,
                type="leave",
                status=leave.status,
                employee_name=f"{leave.employee.user.first_name} {leave.employee.user.last_name}"
            ))

        # Get holidays for the month
        holiday_result = await db.execute(
            select(Holiday).where(
                and_(
                    Holiday.date >= start_date,
                    Holiday.date <= end_date
                )
            )
        )
        holidays = holiday_result.scalars().all()

        for holiday in holidays:
            events.append(CalendarEvent(
                id=holiday.id,
                title=holiday.name,
                start_date=holiday.date,
                end_date=holiday.date,
                type="holiday"
            ))

        return events

    def _calculate_business_days(self, start_date: date, end_date: date) -> int:
        """Calculate business days between two dates, excluding weekends"""
        if start_date > end_date:
            return 0
        
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days


class CRUDLeaveType(CRUDBase[LeaveType, LeaveTypeCreate, LeaveTypeUpdate]):
    async def get_active_leave_types(self, db: AsyncSession) -> List[LeaveType]:
        result = await db.execute(select(LeaveType).where(LeaveType.is_active == True))
        return result.scalars().all()

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[LeaveType]:
        result = await db.execute(select(LeaveType).where(LeaveType.name == name))
        return result.scalar_one_or_none()


class CRUDHoliday(CRUDBase[Holiday, HolidayCreate, HolidayUpdate]):
    async def get_by_year(self, db: AsyncSession, *, year: int) -> List[Holiday]:
        result = await db.execute(
            select(Holiday).where(extract('year', Holiday.date) == year)
        )
        return result.scalars().all()

    async def get_upcoming_holidays(self, db: AsyncSession, *, days: int = 30) -> List[Holiday]:
        end_date = date.today() + timedelta(days=days)
        result = await db.execute(
            select(Holiday).where(
                and_(
                    Holiday.date >= date.today(),
                    Holiday.date <= end_date
                )
            ).order_by(Holiday.date)
        )
        return result.scalars().all()


# Create instances
leave = CRUDLeave(Leave)
leave_type = CRUDLeaveType(LeaveType)
holiday = CRUDHoliday(Holiday)
