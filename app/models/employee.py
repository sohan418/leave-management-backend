from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Personal Information
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Employment Information
    designation = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    hire_date = Column(Date, nullable=False)
    employment_type = Column(String(50), nullable=False, default="Full-time")  # Full-time, Part-time, Contract
    salary = Column(DECIMAL(10, 2), nullable=True)
    
    # Leave Balances
    annual_leave_balance = Column(Integer, default=21)  # Default 21 days
    sick_leave_balance = Column(Integer, default=10)    # Default 10 days
    personal_leave_balance = Column(Integer, default=5) # Default 5 days
    
    # Status
    is_active = Column(Boolean, default=True)
    termination_date = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="employee_profile")
    manager = relationship("Employee", remote_side=[id], backref="subordinates")
    leaves = relationship("Leave", back_populates="employee", foreign_keys="Leave.employee_id")
    approved_leaves = relationship("Leave", foreign_keys="Leave.approved_by")
    attendances = relationship("Attendance", back_populates="employee", foreign_keys="Attendance.employee_id")
    overtimes = relationship("Overtime", back_populates="employee", foreign_keys="Overtime.employee_id")
    time_entries = relationship("TimeEntry", foreign_keys="TimeEntry.employee_id")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_id={self.employee_id}, designation={self.designation})>"
