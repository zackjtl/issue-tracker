"""Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class IssueStatus(str, Enum):
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


class IssueType(str, Enum):
    """Issue type enum."""
    BUG = "bug"
    TASK = "task"
    REQUEST = "request"
    QUESTION = "question"
    INCIDENT = "incident"


class IssuePriority(str, Enum):
    """Issue priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ============ User Schemas ============

class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User create schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None


# ============ Project Schemas ============

class ProjectBase(BaseModel):
    """Base project schema."""
    name: str
    path: str
    parent_path: Optional[str] = None
    description: Optional[str] = None
    default_priority: Optional[str] = "medium"


class ProjectCreate(ProjectBase):
    """Project create schema."""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    default_assignee_id: Optional[int] = None
    default_priority: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: int
    owner_id: Optional[int] = None
    default_assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Issue Schemas ============

class IssueBase(BaseModel):
    """Base issue schema."""
    title: str
    project_path: str
    description: Optional[str] = None
    issue_type: IssueType = IssueType.TASK
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = []
    visibility: Optional[str] = "public"


class IssueCreate(IssueBase):
    """Issue create schema."""
    pass


class IssueUpdate(BaseModel):
    """Issue update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    issue_type: Optional[IssueType] = None
    priority: Optional[IssuePriority] = None
    status: Optional[IssueStatus] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None


class IssueStatusChange(BaseModel):
    """Issue status change schema."""
    status: IssueStatus


class IssueAssign(BaseModel):
    """Issue assign schema."""
    assignee_id: int


class IssueResponse(IssueBase):
    """Issue response schema."""
    id: int
    issue_key: str
    status: IssueStatus
    creator_id: int
    reporter_id: Optional[int] = None
    assigned_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    source: str
    reopen_count: int
    created_at: datetime
    updated_at: datetime
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True


class IssueDetailResponse(IssueResponse):
    """Issue detail response with full content."""
    issue_content: Optional[str] = None
    comments: List[dict] = []
    events: List[dict] = []
    attachments: List[dict] = []
    linked_issues: List[dict] = []


# ============ Comment Schemas ============

class CommentBase(BaseModel):
    """Base comment schema."""
    body: str


class CommentCreate(CommentBase):
    """Comment create schema."""
    pass


class CommentResponse(CommentBase):
    """Comment response schema."""
    id: int
    issue_key: str
    user_id: int
    user_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Event Schemas ============

class EventResponse(BaseModel):
    """Event response schema."""
    id: int
    event_type: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    details: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Attachment Schemas ============

class AttachmentResponse(BaseModel):
    """Attachment response schema."""
    attachment_id: str
    filename: str
    original_filename: str
    mime_type: str
    size: int
    uploaded_by: int
    uploaded_at: datetime
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ============ Search Schemas ============

class IssueSearchParams(BaseModel):
    """Issue search parameters."""
    project_path: Optional[str] = None
    status: Optional[List[IssueStatus]] = None
    priority: Optional[List[IssuePriority]] = None
    assignee_id: Optional[int] = None
    creator_id: Optional[int] = None
    issue_type: Optional[List[IssueType]] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0
