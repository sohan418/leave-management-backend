from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, DECIMAL
from sqlalchemy.sql import func
from ..core.database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    head_of_department = Column(String(100), nullable=True)
    budget = Column(DECIMAL(12, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, code={self.code})>"

class Designation(Base):
    __tablename__ = "designations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=True)  # Hierarchy level
    category = Column(String(50), nullable=True)  # Management, Technical, Administrative
    minimum_salary = Column(DECIMAL(10, 2), nullable=True)
    maximum_salary = Column(DECIMAL(10, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Designation(id={self.id}, title={self.title}, level={self.level})>"

class CompanyPolicy(Base):
    __tablename__ = "company_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)  # Leave, Attendance, Code of Conduct, etc.
    content = Column(Text, nullable=False)
    version = Column(String(20), default="1.0")
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    
    # Approval
    approved_by = Column(String(100), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="Draft")  # Draft, Active, Archived
    is_mandatory = Column(Boolean, default=True)
    applicable_departments = Column(Text, nullable=True)  # JSON string
    
    # File attachments
    attachments = Column(Text, nullable=True)  # JSON string of file paths
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CompanyPolicy(id={self.id}, title={self.title}, category={self.category})>"

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    data_type = Column(String(20), default="string")  # string, integer, float, boolean, json
    category = Column(String(50), nullable=False)  # General, Email, Security, etc.
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)  # Can be accessed by frontend
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemSetting(id={self.id}, key={self.key}, category={self.category})>"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, nullable=False)  # User/Employee ID
    sender_id = Column(Integer, nullable=True)  # User/Employee ID
    
    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # info, warning, success, error
    category = Column(String(50), nullable=True)  # leave, attendance, invoice, etc.
    
    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # References
    reference_type = Column(String(50), nullable=True)  # leave, attendance, invoice
    reference_id = Column(Integer, nullable=True)
    
    # Actions
    action_url = Column(String(255), nullable=True)
    action_label = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, recipient_id={self.recipient_id}, title={self.title})>"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    table_name = Column(String(100), nullable=True)
    record_id = Column(Integer, nullable=True)
    
    # Changes
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action})>"
