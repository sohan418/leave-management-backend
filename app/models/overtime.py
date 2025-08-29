from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Overtime(Base):
    __tablename__ = "overtimes"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Overtime Details
    date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    hours = Column(DECIMAL(4, 2), nullable=False)
    overtime_type = Column(String(50), nullable=False)  # Regular, Weekend, Holiday
    reason = Column(Text, nullable=False)
    
    # Project/Task details
    project_name = Column(String(200), nullable=True)
    task_description = Column(Text, nullable=True)
    
    # Status and Approval
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected
    applied_date = Column(Date, default=func.current_date())
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Compensation
    rate_multiplier = Column(DECIMAL(3, 2), default=1.5)  # 1.5x for regular overtime
    compensation_amount = Column(DECIMAL(10, 2), nullable=True)
    is_compensated = Column(Boolean, default=False)
    compensation_type = Column(String(20), default="Payment")  # Payment, Time Off
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="overtimes", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Overtime(id={self.id}, employee_id={self.employee_id}, date={self.date}, hours={self.hours})>"
