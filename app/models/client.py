from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    client_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Company Information
    company_name = Column(String(200), nullable=False)
    company_type = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Contact Information
    primary_contact_name = Column(String(100), nullable=False)
    primary_contact_email = Column(String(255), nullable=False)
    primary_contact_phone = Column(String(20), nullable=True)
    secondary_contact_name = Column(String(100), nullable=True)
    secondary_contact_email = Column(String(255), nullable=True)
    secondary_contact_phone = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Business Details
    tax_id = Column(String(50), nullable=True)
    registration_number = Column(String(100), nullable=True)
    payment_terms = Column(Integer, default=30)  # Payment terms in days
    currency = Column(String(10), default="USD")
    
    # Status and Relationship
    status = Column(String(20), default="Active")  # Active, Inactive, On Hold
    client_since = Column(Date, nullable=False, default=func.current_date())
    account_manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Financial
    credit_limit = Column(DECIMAL(12, 2), nullable=True)
    current_balance = Column(DECIMAL(12, 2), default=0.0)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    account_manager = relationship("Employee")
    projects = relationship("Project", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    
    def __repr__(self):
        return f"<Client(id={self.id}, code={self.client_code}, company={self.company_name})>"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    project_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Project Details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(100), nullable=True)
    priority = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    
    # Timeline
    start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String(20), default="Planning")  # Planning, Active, On Hold, Completed, Cancelled
    progress_percentage = Column(Integer, default=0)
    
    # Financial
    budget = Column(DECIMAL(12, 2), nullable=True)
    hourly_rate = Column(DECIMAL(8, 2), nullable=True)
    fixed_price = Column(DECIMAL(12, 2), nullable=True)
    billing_type = Column(String(20), default="Hourly")  # Hourly, Fixed, Milestone
    
    # Team
    project_manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    team_members = Column(Text, nullable=True)  # JSON string of employee IDs
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="projects")
    project_manager = relationship("Employee")
    time_entries = relationship("TimeEntry", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, code={self.project_code}, name={self.name})>"

class TimeEntry(Base):
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Time Details
    date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    hours = Column(DECIMAL(4, 2), nullable=False)
    
    # Task Details
    task_description = Column(Text, nullable=False)
    task_type = Column(String(100), nullable=True)  # Development, Testing, Meeting, etc.
    
    # Billing
    billable = Column(Boolean, default=True)
    hourly_rate = Column(DECIMAL(8, 2), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=True)
    
    # Status
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected, Invoiced
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_date = Column(Date, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], overlaps="time_entries")
    project = relationship("Project", back_populates="time_entries")
    approver = relationship("Employee", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<TimeEntry(id={self.id}, employee_id={self.employee_id}, project_id={self.project_id}, hours={self.hours})>"
