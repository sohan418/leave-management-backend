# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .employee import Employee
from .leave import Leave, LeaveType, Holiday
from .attendance import Attendance, AttendanceBreak, AttendancePolicy
from .overtime import Overtime
from .client import Client, Project, TimeEntry
from .invoice import Invoice, InvoiceLineItem, Payment
from .master_data import (
    Department,
    Designation,
    CompanyPolicy,
    SystemSetting,
    Notification,
    AuditLog
)
