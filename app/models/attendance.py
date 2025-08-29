from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date, Time, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    
    # Time tracking
    punch_in_time = Column(DateTime, nullable=True)
    punch_out_time = Column(DateTime, nullable=True)
    total_hours = Column(DECIMAL(4, 2), nullable=True)
    break_duration = Column(Integer, default=0)  # in minutes
    
    # Status
    status = Column(String(20), default="Present")  # Present, Absent, Half Day, Late, Early Leave
    is_late = Column(Boolean, default=False)
    late_by_minutes = Column(Integer, default=0)
    early_leave_minutes = Column(Integer, default=0)
    
    # Location and device info
    punch_in_location = Column(String(200), nullable=True)
    punch_out_location = Column(String(200), nullable=True)
    device_info = Column(Text, nullable=True)  # JSON string
    
    # Notes and approvals
    notes = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="attendances", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])
    breaks = relationship("AttendanceBreak", back_populates="attendance")
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, employee_id={self.employee_id}, date={self.date}, status={self.status})>"

class AttendanceBreak(Base):
    __tablename__ = "attendance_breaks"
    
    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendances.id"), nullable=False)
    
    # Break details
    break_start = Column(DateTime, nullable=False)
    break_end = Column(DateTime, nullable=True)
    break_type = Column(String(50), default="Regular")  # Regular, Lunch, Tea, Personal
    duration_minutes = Column(Integer, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    attendance = relationship("Attendance", back_populates="breaks")
    
    def __repr__(self):
        return f"<AttendanceBreak(id={self.id}, attendance_id={self.attendance_id}, type={self.break_type})>"

class AttendancePolicy(Base):
    __tablename__ = "attendance_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Working hours
    standard_work_hours = Column(DECIMAL(4, 2), default=8.0)
    grace_period_minutes = Column(Integer, default=15)
    half_day_hours = Column(DECIMAL(4, 2), default=4.0)
    
    # Break settings
    max_break_duration = Column(Integer, default=60)  # in minutes
    lunch_break_duration = Column(Integer, default=30)  # in minutes
    
    # Late/Early leave penalties
    late_penalty_after_minutes = Column(Integer, default=30)
    early_leave_penalty_after_minutes = Column(Integer, default=30)
    
    # Overtime settings
    overtime_after_hours = Column(DECIMAL(4, 2), default=8.0)
    weekend_overtime_multiplier = Column(DECIMAL(3, 2), default=2.0)
    
    is_active = Column(Boolean, default=True)
    applicable_departments = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AttendancePolicy(id={self.id}, name={self.name})>"
