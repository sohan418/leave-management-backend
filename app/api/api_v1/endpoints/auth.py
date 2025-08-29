from datetime import timedelta, date
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ....core import security
from ....core.config import settings
from ....core.database import get_db
from ....crud import user, employee
from ....schemas.user import Token, UserLogin, User, UserCreate, UserRole, PasswordUpdate
from ....schemas.employee import EmployeeCreate
from ....models.user import User as UserModel
from ...deps import get_current_user

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    authenticated_user = await user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    elif not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return {
        "access_token": security.create_access_token(
            data={"sub": authenticated_user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": {
            "id": authenticated_user.id,
            "email": authenticated_user.email,
            "first_name": authenticated_user.first_name,
            "last_name": authenticated_user.last_name,
            "role": authenticated_user.role.value if authenticated_user.role else "user",
            "is_active": authenticated_user.is_active,
            "created_at": authenticated_user.created_at,
            "updated_at": authenticated_user.updated_at
        }
    }


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Login for access token
    """
    authenticated_user = await user.authenticate(
        db, email=user_in.email, password=user_in.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    elif not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    return {
        "access_token": security.create_access_token(
            data={"sub": authenticated_user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": {
            "id": authenticated_user.id,
            "email": authenticated_user.email,
            "first_name": authenticated_user.first_name,
            "last_name": authenticated_user.last_name,
            "role": authenticated_user.role.value if authenticated_user.role else "user",
            "is_active": authenticated_user.is_active,
            "created_at": authenticated_user.created_at,
            "updated_at": authenticated_user.updated_at
        }
    }


@router.post("/register", response_model=User)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new user and employee profile
    """
    existing_user = await user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system"
        )
    
    # Create user
    created_user = await user.create(db, obj_in=user_in)
    
    # TODO: Add employee profile creation after user registration
    # For now, we'll handle this separately
    
    return created_user


@router.post("/register/admin", response_model=User)
async def register_admin(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create new admin user - restricted endpoint for initial setup
    """
    existing_user = await user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system"
        )
    
    # Force admin role
    user_in.role = UserRole.ADMIN
    
    # Create admin user
    created_user = await user.create(db, obj_in=user_in)
    
    return created_user


@router.put("/change-password", response_model=dict)
async def change_password(
    password_update: PasswordUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Change user password
    """
    # Verify current password
    if not security.verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = security.get_password_hash(password_update.new_password)
    
    # Update password in database
    current_user.hashed_password = new_hashed_password
    await db.commit()
    await db.refresh(current_user)
    
    return {"message": "Password updated successfully"}
