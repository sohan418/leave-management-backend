from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import math

from ....core.database import get_db
from ....crud import leave, leave_type, holiday, employee
from ....api.deps import get_current_employee, get_current_superuser, get_current_active_user
from ....schemas.leave import (
    Leave, LeaveCreate, LeaveUpdate, LeaveApproval, LeaveListResponse,
    LeaveType, LeaveTypeCreate, LeaveTypeUpdate,
    Holiday, HolidayCreate, HolidayUpdate,
    LeaveStatistics, CalendarEvent
)
from ....models.user import User
from ....models.employee import Employee as EmployeeModel

router = APIRouter()


# Leave endpoints
@router.get("/", response_model=LeaveListResponse)
async def read_leaves(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    leave_status: Optional[str] = Query(None, alias="status"),
    leave_type: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve leaves with filtering and pagination
    """
    print(f"DEBUG: read_leaves called with status={leave_status}, leave_type={leave_type}, department={department}")
    print(f"DEBUG: Current user: {current_user.email}, role: {current_user.role}, is_superuser: {current_user.is_superuser}")
    
    if current_user.is_superuser or current_user.role.value == "admin":
        # Admin can see all leaves - no employee profile required
        print(f"DEBUG: Admin access - getting all leaves with status filter: {leave_status}")
        leaves = await leave.get_all_leaves(
            db,
            skip=skip,
            limit=limit,
            status=leave_status,
            leave_type=leave_type,
            department=department,
            start_date=start_date,
            end_date=end_date
        )
        print(f"DEBUG: Admin leaves returned: {len(leaves)} leaves")
        # Count total for pagination
        all_leaves = await leave.get_all_leaves(db, skip=0, limit=1000)  # Get all for count
        total = len(all_leaves)
        print(f"DEBUG: Total leaves count: {total}")
    else:
        # Regular user can only see their own leaves
        current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        leaves = await leave.get_employee_leaves(
            db,
            employee_id=current_employee.id,
            skip=skip,
            limit=limit,
            status=leave_status,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date
        )
        # Count total for pagination
        all_employee_leaves = await leave.get_employee_leaves(
            db, employee_id=current_employee.id, skip=0, limit=1000
        )
        total = len(all_employee_leaves)
    
    total_pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1
    
    response = LeaveListResponse(
        leaves=leaves,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )
    print(f"DEBUG: Returning response with {len(leaves)} leaves, total: {total}")
    return response


@router.post("/", response_model=Leave)
async def create_leave(
    leave_in: LeaveCreate,
    db: AsyncSession = Depends(get_db),
    current_employee: EmployeeModel = Depends(get_current_employee),
) -> Any:
    """
    Create new leave application
    """
    created_leave = await leave.create_leave(
        db, obj_in=leave_in, employee_id=current_employee.id
    )
    return created_leave


@router.get("/me", response_model=List[Leave])
async def read_my_leaves(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    leave_status: Optional[str] = Query(None, alias="status"),
    leave_type: Optional[str] = Query(None),
    current_employee: EmployeeModel = Depends(get_current_employee),
) -> Any:
    """
    Get current employee's leaves
    """
    leaves = await leave.get_employee_leaves(
        db,
        employee_id=current_employee.id,
        skip=skip,
        limit=limit,
        status=leave_status,
        leave_type=leave_type
    )
    return leaves


@router.get("/statistics", response_model=LeaveStatistics)
async def read_leave_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get leave statistics
    """
    if current_user.is_superuser or current_user.role.value == "admin":
        # Admin gets overall statistics - no employee profile required
        statistics = await leave.get_leave_statistics(db)
    else:
        # Employee gets their own statistics
        current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        statistics = await leave.get_leave_statistics(db, employee_id=current_employee.id)
    
    return statistics


@router.get("/calendar", response_model=List[CalendarEvent])
async def read_calendar_events(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get calendar events for leave and holidays
    """
    if current_user.is_superuser or current_user.role.value == "admin":
        # Admin sees all events - no employee profile required
        events = await leave.get_calendar_events(db, year=year, month=month)
    else:
        # Employee sees only their events and holidays
        current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
        if not current_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        employee_id = current_employee.id
        events = await leave.get_calendar_events(
            db, year=year, month=month, employee_id=employee_id
        )
    
    return events


@router.get("/{leave_id}", response_model=Leave)
async def read_leave(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific leave by ID
    """
    db_leave = await leave.get(db, id=leave_id)
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )
    
    # Check permission: admin or owner can access
    if not (current_user.is_superuser or current_user.role.value == "admin"):
        current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
        if not current_employee or db_leave.employee_id != current_employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return db_leave


@router.put("/{leave_id}", response_model=Leave)
async def update_leave(
    leave_id: int,
    leave_in: LeaveUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update leave application
    """
    db_leave = await leave.get(db, id=leave_id)
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )
    
    # Check permission: admin or owner can update
    if not (current_user.is_superuser or current_user.role.value == "admin"):
        current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
        if not current_employee or db_leave.employee_id != current_employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Regular employees can only update pending leaves
        if db_leave.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update pending leaves"
            )
    
    updated_leave = await leave.update(db, db_obj=db_leave, obj_in=leave_in)
    return updated_leave


@router.post("/{leave_id}/approve", response_model=Leave)
async def approve_leave(
    leave_id: int,
    approval: LeaveApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Approve or reject leave (admin only)
    """
    # Check if user is admin
    if not (current_user.is_superuser or current_user.role.value == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # For admin users, we'll use NULL for approved_by since they don't need employee profiles
    # The database allows NULL values for approved_by
    approved_leave = await leave.approve_leave(
        db,
        leave_id=leave_id,
        approver_id=None,  # Set to None for admin users
        status=approval.status,
        rejection_reason=approval.rejection_reason
    )
    
    if not approved_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )
    
    return approved_leave


@router.delete("/{leave_id}")
async def delete_leave(
    leave_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete leave application
    """
    db_leave = await leave.get(db, id=leave_id)
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )
    
    # Check permission: admin or owner can delete
    if not (current_user.is_superuser or current_user.role.value == "admin"):
        current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
        if not current_employee or db_leave.employee_id != current_employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # Regular employees can only delete pending leaves
        if db_leave.status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete pending leaves"
            )
    
    await leave.remove(db, id=leave_id)
    return {"message": "Leave deleted successfully"}


# Leave Types endpoints
@router.get("/types/", response_model=List[LeaveType])
async def read_leave_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all active leave types
    """
    leave_types = await leave_type.get_active_leave_types(db)
    return leave_types


@router.post("/types/", response_model=LeaveType)
async def create_leave_type(
    leave_type_in: LeaveTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new leave type (admin only)
    """
    # Check if user is admin
    if not (current_user.is_superuser or current_user.role.value == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if leave type already exists
    existing_type = await leave_type.get_by_name(db, name=leave_type_in.name)
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type with this name already exists"
        )
    
    created_type = await leave_type.create(db, obj_in=leave_type_in)
    return created_type


# Holidays endpoints
@router.get("/holidays/", response_model=List[Holiday])
async def read_holidays(
    year: Optional[int] = Query(None, ge=2020, le=2030),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get holidays, optionally filtered by year
    """
    if year:
        holidays = await holiday.get_by_year(db, year=year)
    else:
        holidays = await holiday.get_upcoming_holidays(db)
    return holidays


@router.post("/holidays/", response_model=Holiday)
async def create_holiday(
    holiday_in: HolidayCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new holiday (admin only)
    """
    # Check if user is admin
    if not (current_user.is_superuser or current_user.role.value == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    created_holiday = await holiday.create(db, obj_in=holiday_in)
    return created_holiday
