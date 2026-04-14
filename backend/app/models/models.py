"""Database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base


class IssueStatus(str, enum.Enum):
    """Issue status enum."""
    NEW = "new"
    TRIAGED = "triaged"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REOPENED = "reopened"
    CLOSED = "closed"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"


class IssueType(str, enum.Enum):
    """Issue type enum."""
    BUG = "bug"
    TASK = "task"
    REQUEST = "request"
    QUESTION = "question"
    INCIDENT = "incident"


class IssuePriority(str, enum.Enum):
    """Issue priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_issues = relationship("Issue", back_populates="assignee_rel")
    created_issues = relationship("Issue", foreign_keys="Issue.creator_id", back_populates="creator_rel")


# Association table for project members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role", String(50), default="member"),
)


class Project(Base):
    """Project model."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    path = Column(String(255), unique=True, index=True, nullable=False)
    parent_path = Column(String(255), ForeignKey("projects.path"), nullable=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    default_assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    default_priority = Column(String(20), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issues = relationship("Issue", back_populates="project_rel")
    members = relationship("User", secondary=project_members, back_populates="projects")


class Notification(Base):
    """Notification model."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit log model."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    details = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# Add relationships to User
User.projects = relationship("Project", secondary=project_members, back_populates="members")


class Issue(Base):
    """Issue model - primarily for metadata and DB references."""
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_key = Column(String(50), unique=True, index=True, nullable=False)
    project_path = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)  # Summary from issue.md
    issue_type = Column(SQLEnum(IssueType), default=IssueType.TASK)
    priority = Column(SQLEnum(IssuePriority), default=IssuePriority.MEDIUM)
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.NEW)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    due_date = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    source = Column(String(20), default="web")
    visibility = Column(String(20), default="public")
    tags = Column(Text)  # JSON string
    reopen_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project_rel = relationship("Project", back_populates="issues")
    creator_rel = relationship("User", foreign_keys=[creator_id], back_populates="created_issues")
    assignee_rel = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_issues")
