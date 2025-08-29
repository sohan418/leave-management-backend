from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from .employee import Employee


class LeaveStatusEnum(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class HalfDayPeriodEnum(str, Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"


class LeaveTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_days_per_year: Optional[int] = None
    carry_forward_allowed: bool = False
    requires_document: bool = False
    is_active: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_days_per_year: Optional[int] = None
    carry_forward_allowed: Optional[bool] = None
    requires_document: Optional[bool] = None
    is_active: Optional[bool] = None


class LeaveType(LeaveTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HolidayBase(BaseModel):
    name: str
    date: date
    description: Optional[str] = None
    is_mandatory: bool = True
    applicable_departments: Optional[str] = None  # JSON string


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None
    is_mandatory: Optional[bool] = None
    applicable_departments: Optional[str] = None


class Holiday(HolidayBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveBase(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    is_half_day: bool = False
    half_day_period: Optional[HalfDayPeriodEnum] = None
    emergency_contact: Optional[str] = None
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class LeaveCreate(LeaveBase):
    documents: Optional[List[str]] = None  # List of document paths


class LeaveUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    is_half_day: Optional[bool] = None
    half_day_period: Optional[HalfDayPeriodEnum] = None
    emergency_contact: Optional[str] = None
    status: Optional[LeaveStatusEnum] = None
    rejection_reason: Optional[str] = None


class LeaveApproval(BaseModel):
    status: LeaveStatusEnum
    rejection_reason: Optional[str] = None


class Leave(LeaveBase):
    id: int
    employee_id: int
    days_requested: int
    status: LeaveStatusEnum = LeaveStatusEnum.PENDING
    applied_date: date
    approved_by: Optional[int] = None
    approved_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    documents: Optional[str] = None  # JSON string of document paths
    created_at: datetime
    updated_at: datetime
    
    # Relations
    employee: Optional[Employee] = None
    approver: Optional[Employee] = None

    class Config:
        from_attributes = True


class LeaveListResponse(BaseModel):
    leaves: List[Leave]
    total: int
    page: int
    per_page: int
    total_pages: int


class LeaveStatistics(BaseModel):
    total_leaves: int
    pending_leaves: int
    approved_leaves: int
    rejected_leaves: int
    leaves_this_month: int
    leaves_this_year: int
    on_leave_today: int = 0


class CalendarEvent(BaseModel):
    id: int
    title: str
    start_date: date
    end_date: date
    type: str  # 'leave', 'holiday'
    status: Optional[str] = None
    employee_name: Optional[str] = None
