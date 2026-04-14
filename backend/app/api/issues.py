"""Issue API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas import (
    IssueCreate, IssueUpdate, IssueResponse, IssueDetailResponse,
    IssueStatusChange, IssueAssign, CommentCreate, CommentResponse,
    IssueStatus, IssuePriority, IssueType
)
from app.services.issue_service import issue_service

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue: IssueCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new issue."""
    new_issue = await issue_service.create_issue(
        db=db,
        title=issue.title,
        project_path=issue.project_path,
        creator_id=1,  # TODO: Get from auth
        description=issue.description,
        issue_type=issue.issue_type,
        priority=issue.priority,
        assignee_id=issue.assignee_id,
        due_date=issue.due_date,
        tags=issue.tags,
        visibility=issue.visibility,
    )

    return new_issue


@router.get("", response_model=List[IssueResponse])
async def list_issues(
    project_path: Optional[str] = Query(None),
    status: Optional[List[IssueStatus]] = Query(None),
    priority: Optional[List[IssuePriority]] = Query(None),
    assignee_id: Optional[int] = Query(None),
    creator_id: Optional[int] = Query(None),
    issue_type: Optional[List[IssueType]] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List issues with filters."""
    issues = await issue_service.list_issues(
        db=db,
        project_path=project_path,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        creator_id=creator_id,
        issue_type=issue_type,
        limit=limit,
        offset=offset,
    )
    return issues


@router.get("/{issue_key}", response_model=IssueDetailResponse)
async def get_issue(issue_key: str, db: AsyncSession = Depends(get_db)):
    """Get issue details."""
    issue_detail = await issue_service.get_issue_detail(db, issue_key)
    if not issue_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return issue_detail


@router.put("/{issue_key}", response_model=IssueResponse)
async def update_issue(
    issue_key: str,
    issue_update: IssueUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an issue."""
    updated = await issue_service.update_issue(
        db=db,
        issue_key=issue_key,
        user_id=1,  # TODO: Get from auth
        **issue_update.dict(exclude_unset=True),
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return updated


@router.post("/{issue_key}/status", response_model=IssueResponse)
async def change_status(
    issue_key: str,
    status_change: IssueStatusChange,
    db: AsyncSession = Depends(get_db),
):
    """Change issue status."""
    updated = await issue_service.change_status(
        db=db,
        issue_key=issue_key,
        new_status=status_change.status,
        user_id=1,  # TODO: Get from auth
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return updated


@router.post("/{issue_key}/assign", response_model=IssueResponse)
async def assign_issue(
    issue_key: str,
    assignment: IssueAssign,
    db: AsyncSession = Depends(get_db),
):
    """Assign issue to a user."""
    updated = await issue_service.assign_issue(
        db=db,
        issue_key=issue_key,
        assignee_id=assignment.assignee_id,
        assigned_by_id=1,  # TODO: Get from auth
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return updated


@router.post("/{issue_key}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    issue_key: str,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a comment to an issue."""
    comment_id = await issue_service.add_comment(
        db=db,
        issue_key=issue_key,
        user_id=1,  # TODO: Get from auth
        body=comment.body,
        user_name="User",  # TODO: Get from auth
    )
    if not comment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return {"comment_id": comment_id}


@router.get("/{issue_key}/comments")
async def get_comments(issue_key: str, db: AsyncSession = Depends(get_db)):
    """Get all comments for an issue."""
    issue = await issue_service.get_issue_by_key(db, issue_key)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    from app.services.file_storage import file_storage
    comments = await file_storage.get_comments(issue_key)
    return comments


@router.get("/{issue_key}/events")
async def get_events(issue_key: str, db: AsyncSession = Depends(get_db)):
    """Get all events for an issue."""
    issue = await issue_service.get_issue_by_key(db, issue_key)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    from app.services.file_storage import file_storage
    events = await file_storage.get_events(issue_key)
    return events
