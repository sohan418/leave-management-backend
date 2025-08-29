from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....crud import employee, user
from ....api.deps import get_current_employee, get_current_superuser, get_current_user
from ....api.deps_roles import require_admin, require_user_or_admin
from ....schemas.employee import Employee, EmployeeCreate, EmployeeUpdate, LeaveBalance, EmployeeWithUserCreate, EmployeeWithUserUpdate
from ....schemas.user import UserCreate
from ....models.user import User
from ....models.employee import Employee as EmployeeModel
from ....core.security import get_password_hash

router = APIRouter()


@router.get("/me", response_model=Employee)
async def read_employee_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current employee profile
    """
    # Check if user has an employee profile
    current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    return current_employee


@router.put("/me", response_model=Employee)
async def update_employee_me(
    employee_in: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update own employee profile
    """
    # Check if user has an employee profile
    current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    updated_employee = await employee.update(
        db, db_obj=current_employee, obj_in=employee_in
    )
    return updated_employee


@router.get("/me/leave-balance", response_model=LeaveBalance)
async def read_employee_leave_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current employee's leave balance
    """
    # Check if user has an employee profile
    current_employee = await employee.get_by_user_id(db, user_id=current_user.id)
    if not current_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    leave_balance = await employee.get_leave_balance(db, employee_id=current_employee.id)
    if not leave_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave balance not found"
        )
    return leave_balance


@router.get("/", response_model=List[dict])
async def read_employees(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Retrieve employees (admin only)
    """
    if department:
        employees = await employee.get_by_department(db, department=department)
    else:
        employees = await employee.get_active_employees(db, skip=skip, limit=limit)
    
    # Convert to dict to avoid serialization issues
    employee_list = []
    for emp in employees:
        employee_data = {
            "id": emp.id,
            "employee_id": emp.employee_id,
            "designation": emp.designation,
            "department": emp.department,
            "hire_date": emp.hire_date,
            "salary": emp.salary,
            "is_active": emp.is_active,
            "created_at": emp.created_at,
            "phone": emp.phone,
            "first_name": emp.user.first_name if emp.user else "",
            "last_name": emp.user.last_name if emp.user else "",
            "email": emp.user.email if emp.user else ""
        }
        employee_list.append(employee_data)
    
    return employee_list


@router.post("/setup", response_model=Employee)
async def setup_employee_profile(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create employee profile for current user (self-service)
    """
    # Check if user already has an employee profile
    existing_employee = await employee.get_by_user_id(db, user_id=current_user.id)
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists for this user"
        )
    
    # Check if employee_id already exists
    existing_employee_id = await employee.get_by_employee_id(
        db, employee_id=employee_in.employee_id
    )
    if existing_employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID is already taken"
        )
    
    # Set the user_id to current user
    employee_data = employee_in.dict()
    employee_data["user_id"] = current_user.id
    
    created_employee = await employee.create(db, obj_in=EmployeeCreate(**employee_data))
    return created_employee


@router.post("/", response_model=Employee)
async def create_employee(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Create new employee (admin only)
    """
    # Check if employee_id already exists
    existing_employee = await employee.get_by_employee_id(
        db, employee_id=employee_in.employee_id
    )
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this employee ID already exists"
        )
    
    created_employee = await employee.create(db, obj_in=employee_in)
    return created_employee


@router.post("/with-user", response_model=Employee)
async def create_employee_with_user(
    employee_data: EmployeeWithUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Create new employee with user account (admin only)
    """
    # Check if employee_id already exists
    existing_employee = await employee.get_by_employee_id(
        db, employee_id=employee_data.employee_id
    )
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this employee ID already exists"
        )
    
    # Check if user email already exists
    existing_user = await user.get_by_email(db, email=employee_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user first
    user_data = UserCreate(
        email=employee_data.email,
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        password=employee_data.password,
        role=employee_data.role
    )
    
    created_user = await user.create(db, obj_in=user_data)
    
    # Create employee profile
    employee_create_data = EmployeeCreate(
        user_id=created_user.id,
        employee_id=employee_data.employee_id,
        phone=employee_data.phone,
        address=employee_data.address,
        date_of_birth=employee_data.date_of_birth,
        gender=employee_data.gender,
        emergency_contact_name=employee_data.emergency_contact_name,
        emergency_contact_phone=employee_data.emergency_contact_phone,
        designation=employee_data.designation,
        department=employee_data.department,
        hire_date=employee_data.hire_date,
        employment_type=employee_data.employment_type,
        salary=employee_data.salary,
        annual_leave_balance=employee_data.annual_leave_balance,
        sick_leave_balance=employee_data.sick_leave_balance,
        personal_leave_balance=employee_data.personal_leave_balance,
        is_active=employee_data.is_active,
        manager_id=employee_data.manager_id
    )
    
    created_employee = await employee.create(db, obj_in=employee_create_data)
    
    # Return employee with user data
    return await employee.get_with_user(db, id=created_employee.id)


@router.get("/{employee_id}", response_model=Employee)
async def read_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Get employee by ID (admin only)
    """
    db_employee = await employee.get_with_user(db, id=employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return db_employee


@router.put("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: int,
    employee_in: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Update employee (admin only)
    """
    db_employee = await employee.get(db, id=employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Update employee data
    updated_employee = await employee.update(
        db, db_obj=db_employee, obj_in=employee_in
    )
    
    # Return the updated employee with user data
    return await employee.get_with_user(db, id=updated_employee.id)


@router.put("/{employee_id}/with-user", response_model=Employee)
async def update_employee_with_user(
    employee_id: int,
    update_data: EmployeeWithUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Update employee and user information (admin only)
    """
    try:
        print(f"DEBUG: Updating employee {employee_id} with data: {update_data}")
        
        db_employee = await employee.get_with_user(db, id=employee_id)
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Convert to dict and filter out None values
        update_dict = update_data.dict(exclude_unset=True)
        print(f"DEBUG: Filtered update dict: {update_dict}")
        
        # Separate user and employee data
        user_data = {}
        employee_data = {}
        
        # Fields that belong to user
        user_fields = ['first_name', 'last_name', 'email']
        # Fields that belong to employee
        employee_fields = [
            'phone', 'address', 'date_of_birth', 'gender', 'emergency_contact_name',
            'emergency_contact_phone', 'designation', 'department', 'employment_type',
            'salary', 'annual_leave_balance', 'sick_leave_balance', 'personal_leave_balance',
            'manager_id', 'is_active'
        ]
        
        for field, value in update_dict.items():
            if field in user_fields and value is not None:
                user_data[field] = value
            elif field in employee_fields and value is not None:
                employee_data[field] = value
        
        print(f"DEBUG: User data to update: {user_data}")
        print(f"DEBUG: Employee data to update: {employee_data}")
        
        # Update user data if there are user fields to update
        if user_data and db_employee.user:
            try:
                await user.update(db, db_obj=db_employee.user, obj_in=user_data)
                print(f"DEBUG: User updated successfully")
            except Exception as e:
                print(f"DEBUG: Error updating user: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update user data: {str(e)}"
                )
        
        # Update employee data if there are employee fields to update
        if employee_data:
            try:
                await employee.update(db, db_obj=db_employee, obj_in=employee_data)
                print(f"DEBUG: Employee updated successfully")
            except Exception as e:
                print(f"DEBUG: Error updating employee: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update employee data: {str(e)}"
                )
        
        # Commit all changes
        await db.commit()
        print(f"DEBUG: Database committed successfully")
        
        # Return the updated employee with user data
        updated_employee = await employee.get_with_user(db, id=employee_id)
        print(f"DEBUG: Returning updated employee: {updated_employee}")
        return updated_employee
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"DEBUG: Error occurred, rolling back: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{employee_id}/leave-balance", response_model=LeaveBalance)
async def read_employee_leave_balance_by_id(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Get employee's leave balance by ID (admin only)
    """
    leave_balance = await employee.get_leave_balance(db, employee_id=employee_id)
    if not leave_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee or leave balance not found"
        )
    return leave_balance


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Any:
    """
    Delete employee (admin only)
    """
    db_employee = await employee.get(db, id=employee_id)
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Soft delete - mark as inactive instead of hard delete
    updated_employee = await employee.update(
        db, 
        db_obj=db_employee, 
        obj_in={"is_active": False}
    )
    
    return {"message": "Employee deactivated successfully"}
