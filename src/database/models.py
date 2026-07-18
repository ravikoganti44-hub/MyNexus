"""
Database models for Activity, Completion tracking, Integrations, and Document Vault
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .config import Base


class RecurrenceType(enum.Enum):
    """Recurrence pattern enumeration"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class CategoryType(enum.Enum):
    """Activity category enumeration"""
    PAYMENT = "payment"
    SUBSCRIPTION = "subscription"
    MAINTENANCE = "maintenance"
    MEETING = "meeting"
    TASK = "task"
    HEALTH = "health"
    OTHER = "other"


class Activity(Base):
    """Main activity/reminder model"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(CategoryType), default=CategoryType.TASK)
    
    # Recurrence settings
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.ONCE)
    recurrence_interval = Column(Integer, default=1)  # For custom intervals
    
    # Dates
    start_date = Column(DateTime, default=datetime.now, nullable=False)
    next_due_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)  # Optional end date
    
    # Notification settings
    reminder_days_before = Column(Integer, default=1)
    reminder_hours_before = Column(Integer, default=0)
    send_notification = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Tags / labels (comma-separated)
    tags = Column(Text, default="")
    
    # Associated integrations
    integration_id = Column(Integer, ForeignKey('integrations.id'), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    completions = relationship("ActivityCompletion", back_populates="activity", cascade="all, delete-orphan")
    integration = relationship("Integration", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, title={self.title}, next_due={self.next_due_date})>"
    
    def calculate_next_due_date(self):
        """Calculate the next due date based on recurrence pattern"""
        from dateutil.relativedelta import relativedelta
        
        base_date = self.next_due_date or datetime.now()
        
        if self.recurrence_type == RecurrenceType.ONCE:
            return None
        elif self.recurrence_type == RecurrenceType.DAILY:
            return base_date + timedelta(days=self.recurrence_interval)
        elif self.recurrence_type == RecurrenceType.WEEKLY:
            return base_date + timedelta(weeks=self.recurrence_interval)
        elif self.recurrence_type == RecurrenceType.BIWEEKLY:
            return base_date + timedelta(weeks=2)
        elif self.recurrence_type == RecurrenceType.MONTHLY:
            return base_date + relativedelta(months=self.recurrence_interval)
        elif self.recurrence_type == RecurrenceType.QUARTERLY:
            return base_date + relativedelta(months=3)
        elif self.recurrence_type == RecurrenceType.YEARLY:
            return base_date + relativedelta(years=1)
        else:
            return base_date + timedelta(days=self.recurrence_interval)


class ActivityCompletion(Base):
    """Track activity completion history"""
    __tablename__ = "activity_completions"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    completed_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)
    
    # Relationships
    activity = relationship("Activity", back_populates="completions")
    
    def __repr__(self):
        return f"<ActivityCompletion(activity_id={self.activity_id}, completed_at={self.completed_at})>"


class Integration(Base):
    """Store application integrations and credentials"""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    app_type = Column(String(100), nullable=False)  # "email", "calendar", "payment", etc.
    
    # Credentials (encrypted in production)
    username = Column(String(255))
    api_key = Column(Text)
    access_token = Column(Text)
    refresh_token = Column(Text)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    config_data = Column(Text)  # JSON string for additional config
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    last_synced = Column(DateTime)
    
    # Relationships
    activities = relationship("Activity", back_populates="integration")
    
    def __repr__(self):
        return f"<Integration(id={self.id}, name={self.name}, app_type={self.app_type})>"


class Notification(Base):
    """Store notification history"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    notification_type = Column(String(50))  # "reminder", "due", "overdue"
    
    sent_at = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)
    
    title = Column(String(255))
    message = Column(Text)
    
    def __repr__(self):
        return f"<Notification(activity_id={self.activity_id}, type={self.notification_type})>"


class ConnectedApplication(Base):
    """Store external application connections"""
    __tablename__ = "connected_applications"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # e.g., "My Mortgage Account"
    app_type = Column(String(100), nullable=False)  # e.g., "mortgage", "banking", "utilities", etc.
    
    # Application details
    app_name = Column(String(255))  # e.g., "Chase Bank", "Better.com"
    website_url = Column(String(500))  # e.g., "https://www.chase.com"
    login_url = Column(String(500))  # Direct login URL if available
    
    # Credentials (will be encrypted in production)
    username = Column(String(255), nullable=False)
    password_encrypted = Column(Text)  # Encrypted password
    email = Column(String(255))  # Alternative contact method
    
    # Additional information
    account_number = Column(String(255))  # Mortgage account, bank account, etc.
    account_holder = Column(String(255))  # Name on account
    security_question = Column(Text)  # For reference only
    security_answer_encrypted = Column(Text)  # Encrypted
    
    # Categorization
    category = Column(String(100))  # "mortgage", "banking", "utilities", "insurance", "medical", etc.
    icon_emoji = Column(String(10))  # 🏠 🏦 🏥 etc.
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Notes for user reference
    notes = Column(Text)  # e.g., "Primary mortgage account", "Credit card backup"
    
    def __repr__(self):
        return f"<ConnectedApplication(id={self.id}, name={self.name}, app_type={self.app_type})>"


class DocumentCategory(enum.Enum):
    """Document category enumeration"""
    PASSPORT = "passport"
    TAX_DOCUMENTS = "tax_documents"
    PROPERTY_DOCUMENTS = "property_documents"
    CERTIFICATES = "certificates"
    IMMIGRATION_DOCUMENTS = "immigration_documents"
    MEDICAL_RECORDS = "medical_records"
    INSURANCE_DOCUMENTS = "insurance_documents"
    FINANCIAL_DOCUMENTS = "financial_documents"
    LEGAL_DOCUMENTS = "legal_documents"
    OTHER = "other"


class DocumentType(enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    IMAGE = "image"
    WORD = "word"
    EXCEL = "excel"
    TEXT = "text"
    OTHER = "other"


class Document(Base):
    """Store documents in the vault"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    
    # Document identification
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # In bytes
    file_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER)
    mime_type = Column(String(100))
    
    # Document details
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(SQLEnum(DocumentCategory), nullable=False, index=True)
    sub_category = Column(String(255))  # e.g., "2024" for tax documents, "Passport Type"
    
    # Document information
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    reference_number = Column(String(255), unique=True, nullable=True)  # Passport no., Certificate no., etc.
    tags = Column(Text)  # Comma-separated tags for search
    
    # Status and security
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_accessed = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, category={self.category})>"


# ── Budget Tracker ─────────────────────────────────────────────────────────────

class BudgetPeriod(Base):
    """Represents a month/year budget period"""
    __tablename__ = "budget_periods"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)   # 1-12
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    limits  = relationship("BudgetLimit",  back_populates="period", cascade="all, delete-orphan")
    entries = relationship("BudgetEntry",  back_populates="period", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BudgetPeriod({self.year}-{self.month:02d})>"


class BudgetLimit(Base):
    """Per-category spending limit within a budget period"""
    __tablename__ = "budget_limits"

    id = Column(Integer, primary_key=True)
    period_id    = Column(Integer, ForeignKey("budget_periods.id"), nullable=False)
    category     = Column(String(100), nullable=False)
    limit_amount = Column(Float, nullable=False, default=0.0)

    period = relationship("BudgetPeriod", back_populates="limits")

    def __repr__(self):
        return f"<BudgetLimit({self.category}: ${self.limit_amount})>"


class BudgetEntry(Base):
    """An individual expense entry"""
    __tablename__ = "budget_entries"

    id         = Column(Integer, primary_key=True)
    period_id  = Column(Integer, ForeignKey("budget_periods.id"), nullable=False)
    title      = Column(String(255), nullable=False)
    amount     = Column(Float, nullable=False)
    category   = Column(String(100), nullable=False)
    entry_date = Column(DateTime, default=datetime.now, nullable=False)
    notes      = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    period = relationship("BudgetPeriod", back_populates="entries")

    def __repr__(self):
        return f"<BudgetEntry(title={self.title}, amount={self.amount})>"


# ── Net Worth Tracker ──────────────────────────────────────────────────────────

class NetWorthSnapshot(Base):
    """A point-in-time snapshot of net worth"""
    __tablename__ = "net_worth_snapshots"

    id            = Column(Integer, primary_key=True)
    snapshot_date = Column(DateTime, default=datetime.now, nullable=False)
    # JSON strings: {"Savings": 10000, "Investments": 5000}
    assets_json      = Column(Text, default="{}")
    liabilities_json = Column(Text, default="{}")
    net_worth        = Column(Float, default=0.0)
    notes            = Column(Text)
    created_at  = Column(DateTime, default=datetime.now)
    updated_at  = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<NetWorthSnapshot(date={self.snapshot_date}, net_worth={self.net_worth})>"
