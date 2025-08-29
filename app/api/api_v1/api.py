from fastapi import APIRouter

from .endpoints import auth, employees, leaves

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include employee routes
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])

# Include leave management routes
api_router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
