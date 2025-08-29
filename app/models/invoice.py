from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, DECIMAL, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Invoice Details
    invoice_date = Column(Date, nullable=False, default=func.current_date())
    due_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    
    # Financial Details
    subtotal = Column(DECIMAL(12, 2), nullable=False, default=0.0)
    tax_rate = Column(DECIMAL(5, 2), default=0.0)  # Percentage
    tax_amount = Column(DECIMAL(12, 2), default=0.0)
    discount_rate = Column(DECIMAL(5, 2), default=0.0)  # Percentage
    discount_amount = Column(DECIMAL(12, 2), default=0.0)
    total_amount = Column(DECIMAL(12, 2), nullable=False, default=0.0)
    
    # Payment Details
    status = Column(String(20), default="Draft")  # Draft, Sent, Paid, Overdue, Cancelled
    payment_status = Column(String(20), default="Unpaid")  # Unpaid, Partial, Paid
    paid_amount = Column(DECIMAL(12, 2), default=0.0)
    payment_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    # Additional Information
    currency = Column(String(10), default="USD")
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # References
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sent_date = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project")
    creator = relationship("Employee")
    line_items = relationship("InvoiceLineItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number={self.invoice_number}, total={self.total_amount})>"

class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Item Details
    description = Column(Text, nullable=False)
    item_type = Column(String(50), nullable=True)  # Hours, Fixed, Expense, etc.
    quantity = Column(DECIMAL(8, 2), default=1.0)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(12, 2), nullable=False)
    
    # References
    time_entry_id = Column(Integer, ForeignKey("time_entries.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")
    time_entry = relationship("TimeEntry")
    project = relationship("Project")
    
    def __repr__(self):
        return f"<InvoiceLineItem(id={self.id}, invoice_id={self.invoice_id}, total={self.total_price})>"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # Cash, Check, Bank Transfer, Credit Card, etc.
    reference_number = Column(String(100), nullable=True)
    
    # Bank Details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="Received")  # Received, Cleared, Bounced
    notes = Column(Text, nullable=True)
    
    # References
    recorded_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    recorder = relationship("Employee")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, invoice_id={self.invoice_id}, amount={self.amount})>"
