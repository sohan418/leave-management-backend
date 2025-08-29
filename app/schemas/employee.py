from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from .user import User


class EmployeeBase(BaseModel):
    employee_id: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    designation: str
    department: str
    hire_date: date
    employment_type: str = "Full-time"
    salary: Optional[Decimal] = None
    annual_leave_balance: int = 21
    sick_leave_balance: int = 10
    personal_leave_balance: int = 5
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    user_id: int
    manager_id: Optional[int] = None


class EmployeeWithUserCreate(BaseModel):
    """Schema for creating employee with user data"""
    # User data
    email: str
    first_name: str
    last_name: str
    password: str
    role: str = "user"
    
    # Employee data
    employee_id: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    designation: str
    department: str
    hire_date: date
    employment_type: str = "Full-time"
    salary: Optional[Decimal] = None
    annual_leave_balance: int = 21
    sick_leave_balance: int = 10
    personal_leave_balance: int = 5
    is_active: bool = True
    manager_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[Decimal] = None
    annual_leave_balance: Optional[int] = None
    sick_leave_balance: Optional[int] = None
    personal_leave_balance: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class EmployeeWithUserUpdate(BaseModel):
    """Schema for updating both employee and user data together"""
    # User fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    
    # Employee fields
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None  # Accept string, will convert to date
    gender: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[str] = None  # Accept string, will convert to Decimal
    annual_leave_balance: Optional[int] = None
    sick_leave_balance: Optional[int] = None
    personal_leave_balance: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('date_of_birth', pre=True)
    def parse_date_of_birth(cls, v):
        if isinstance(v, str) and v:
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v
    
    @validator('salary', pre=True)
    def parse_salary(cls, v):
        if isinstance(v, str) and v:
            try:
                return Decimal(v)
            except (ValueError, TypeError):
                raise ValueError('Invalid salary format')
        return v
    
    @validator('is_active', pre=True)
    def parse_is_active(cls, v):
        if isinstance(v, str):
            if v.lower() == 'true':
                return True
            elif v.lower() == 'false':
                return False
        return v
    
    @validator('manager_id', pre=True)
    def parse_manager_id(cls, v):
        if isinstance(v, str) and v:
            try:
                return int(v)
            except (ValueError, TypeError):
                raise ValueError('Invalid manager ID format')
        return v
    
    @validator('annual_leave_balance', 'sick_leave_balance', 'personal_leave_balance', pre=True)
    def parse_leave_balance(cls, v):
        if isinstance(v, str) and v:
            try:
                return int(v)
            except (ValueError, TypeError):
                raise ValueError('Invalid leave balance format')
        return v


class Employee(EmployeeBase):
    id: int
    user_id: int
    manager_id: Optional[int] = None
    termination_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    # Relations
    user: Optional[User] = None

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    """Simplified employee schema for list operations"""
    id: int
    employee_id: str
    designation: str
    department: str
    hire_date: date
    salary: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    
    # Basic user info without full relationship
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class EmployeeWithManager(Employee):
    manager: Optional['Employee'] = None


class LeaveBalance(BaseModel):
    annual_leave_balance: int
    sick_leave_balance: int
    personal_leave_balance: int
    total_leaves_taken: int
    leaves_pending: int

    class Config:
        from_attributes = True


# Forward reference resolution
EmployeeWithManager.model_rebuild()
