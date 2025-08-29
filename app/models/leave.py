from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Leave(Base):
    __tablename__ = "leaves"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Leave Details
    leave_type = Column(String(50), nullable=False)  # Annual, Sick, Personal, Maternity, etc.
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    
    # Status and Approval
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected, Cancelled
    applied_date = Column(Date, default=func.current_date())
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Additional Information
    is_half_day = Column(Boolean, default=False)
    half_day_period = Column(String(20), nullable=True)  # Morning, Afternoon
    emergency_contact = Column(String(200), nullable=True)
    documents = Column(Text, nullable=True)  # JSON string of document paths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="leaves", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by], overlaps="approved_leaves")
    
    def __repr__(self):
        return f"<Leave(id={self.id}, employee_id={self.employee_id}, type={self.leave_type}, status={self.status})>"

class LeaveType(Base):
    __tablename__ = "leave_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    max_days_per_year = Column(Integer, nullable=True)
    carry_forward_allowed = Column(Boolean, default=False)
    requires_document = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LeaveType(id={self.id}, name={self.name})>"

class Holiday(Base):
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    is_mandatory = Column(Boolean, default=True)  # Mandatory for all employees
    applicable_departments = Column(Text, nullable=True)  # JSON string of departments
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Holiday(id={self.id}, name={self.name}, date={self.date})>"
