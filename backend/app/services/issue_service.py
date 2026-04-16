"""Issue service."""
import logging
import traceback
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import Issue, IssueStatus, IssuePriority, IssueType
from app.services.file_storage import file_storage

logger = logging.getLogger(__name__)


class IssueService:
    """Service for managing issues."""

    @staticmethod
    def generate_issue_key(project_path: str) -> str:
        """Generate a unique issue key."""
        # Get the last part of the project path
        short_path = project_path.split("/")[-1].upper()
        # Generate a random number for uniqueness
        random_num = str(uuid.uuid4())[:4].upper()
        return f"{short_path}-{random_num}"

    async def create_issue(
        self,
        db: AsyncSession,
        title: str,
        project_path: str,
        creator_id: int,
        description: Optional[str] = None,
        issue_type: IssueType = IssueType.TASK,
        priority: IssuePriority = IssuePriority.MEDIUM,
        assignee_id: Optional[int] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        visibility: str = "public",
    ) -> Issue:
        """Create a new issue."""
        issue_key = self.generate_issue_key(project_path)

        issue = Issue(
            issue_key=issue_key,
            project_path=project_path,
            title=title,
            description=description or "",
            issue_type=issue_type,
            priority=priority,
            status=IssueStatus.NEW,
            creator_id=creator_id,
            assignee_id=assignee_id,
            due_date=due_date,
            tags=",".join(tags) if tags else "",
            visibility=visibility,
        )

        db.add(issue)
        await db.commit()
        await db.refresh(issue)

        # Create issue files
        issue_content = f"""# {title}

{description or ""}

---
*Created at: {datetime.utcnow().isoformat()}*
"""

        await file_storage.save_issue_content(issue_key, issue_content)

        meta = {
            "issue_key": issue_key,
            "project_path": project_path,
            "title": title,
            "type": issue_type.value,
            "priority": priority.value,
            "status": IssueStatus.NEW.value,
            "creator_id": creator_id,
            "assignee_id": assignee_id,
            "created_at": datetime.utcnow().isoformat(),
            "tags": tags or [],
        }

        await file_storage.save_issue_meta(issue_key, meta)

        # Add creation event
        await file_storage.add_event(issue_key, {
            "event_type": "issue_created",
            "user_id": creator_id,
            "details": {"title": title, "type": issue_type.value}
        })

        return issue

    async def get_issue_by_key(self, db: AsyncSession, issue_key: str) -> Optional[Issue]:
        """Get issue by key."""
        result = await db.execute(
            select(Issue).where(Issue.issue_key == issue_key)
        )
        return result.scalar_one_or_none()

    async def get_issue_detail(
        self, db: AsyncSession, issue_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get issue with full details."""
        issue = await self.get_issue_by_key(db, issue_key)
        if not issue:
            return None

        # Get file-based content
        issue_content = await file_storage.read_issue_content(issue_key)
        comments = await file_storage.get_comments(issue_key)
        events = await file_storage.get_events(issue_key)
        attachments = await file_storage.get_attachments(issue_key)
        links = await file_storage.get_issue_links(issue_key)

        # Parse tags
        tags = issue.tags.split(",") if issue.tags else []

        return {
            "id": issue.id,
            "issue_key": issue.issue_key,
            "project_path": issue.project_path,
            "title": issue.title,
            "description": issue.description,
            "issue_type": issue.issue_type,
            "priority": issue.priority,
            "status": issue.status,
            "creator_id": issue.creator_id,
            "reporter_id": issue.reporter_id,
            "assignee_id": issue.assignee_id,
            "assigned_by_id": issue.assigned_by_id,
            "due_date": issue.due_date,
            "resolved_at": issue.resolved_at,
            "closed_at": issue.closed_at,
            "source": issue.source,
            "visibility": issue.visibility,
            "tags": tags,
            "reopen_count": issue.reopen_count,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "issue_content": issue_content,
            "comments": comments,
            "events": events,
            "attachments": attachments,
            "linked_issues": links,
        }

    async def update_issue(
        self,
        db: AsyncSession,
        issue_key: str,
        user_id: int,
        **updates,
    ) -> Optional[Issue]:
        """Update an issue."""
        issue = await self.get_issue_by_key(db, issue_key)
        if not issue:
            return None

        # Track changes for events
        changes = {}

        for field, value in updates.items():
            if value is not None and hasattr(issue, field):
                old_value = getattr(issue, field)
                if old_value != value:
                    changes[field] = {"old": str(old_value), "new": str(value)}
                    setattr(issue, field, value)

        issue.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(issue)

        # Update file storage
        meta = await file_storage.read_issue_meta(issue_key) or {}
        meta.update({
            "title": issue.title,
            "type": issue.issue_type.value,
            "priority": issue.priority.value,
            "status": issue.status.value,
            "assignee_id": issue.assignee_id,
            "updated_at": datetime.utcnow().isoformat(),
        })
        await file_storage.save_issue_meta(issue_key, meta)

        # Add change events
        for field, change in changes.items():
            await file_storage.add_event(issue_key, {
                "event_type": f"{field}_changed",
                "user_id": user_id,
                "details": change
            })

        return issue

    async def change_status(
        self,
        db: AsyncSession,
        issue_key: str,
        new_status: IssueStatus,
        user_id: int,
    ) -> Optional[Issue]:
        """Change issue status."""
        issue = await self.get_issue_by_key(db, issue_key)
        if not issue:
            return None

        old_status = issue.status
        issue.status = new_status
        issue.updated_at = datetime.utcnow()

        if new_status == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.utcnow()
        elif new_status == IssueStatus.CLOSED:
            issue.closed_at = datetime.utcnow()
        elif new_status == IssueStatus.REOPENED:
            issue.reopen_count += 1

        await db.commit()
        await db.refresh(issue)

        # Add status change event
        await file_storage.add_event(issue_key, {
            "event_type": "status_changed",
            "user_id": user_id,
            "details": {"old": old_status.value, "new": new_status.value}
        })

        return issue

    async def assign_issue(
        self,
        db: AsyncSession,
        issue_key: str,
        assignee_id: int,
        assigned_by_id: int,
    ) -> Optional[Issue]:
        """Assign issue to a user."""
        issue = await self.get_issue_by_key(db, issue_key)
        if not issue:
            return None

        old_assignee = issue.assignee_id
        issue.assignee_id = assignee_id
        issue.assigned_by_id = assigned_by_id
        issue.updated_at = datetime.utcnow()

        if issue.status == IssueStatus.NEW:
            issue.status = IssueStatus.ASSIGNED

        await db.commit()
        await db.refresh(issue)

        # Add assignment event
        await file_storage.add_event(issue_key, {
            "event_type": "assignee_changed",
            "user_id": assigned_by_id,
            "details": {
                "old_assignee_id": old_assignee,
                "new_assignee_id": assignee_id
            }
        })

        return issue

    async def list_issues(
        self,
        db: AsyncSession,
        project_path: Optional[str] = None,
        status: Optional[List[IssueStatus]] = None,
        priority: Optional[List[IssuePriority]] = None,
        assignee_id: Optional[int] = None,
        creator_id: Optional[int] = None,
        issue_type: Optional[List[IssueType]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Issue]:
        """List issues with filters."""
        try:
            logger.info(
                "[issue_service] list_issues: project_path=%s status=%s priority=%s "
                "assignee_id=%s creator_id=%s issue_type=%s limit=%d offset=%d",
                project_path, status, priority, assignee_id, creator_id, issue_type, limit, offset,
            )
            query = select(Issue)

            if project_path:
                query = query.where(Issue.project_path == project_path)
            if status:
                query = query.where(Issue.status.in_(status))
            if priority:
                query = query.where(Issue.priority.in_(priority))
            if assignee_id:
                query = query.where(Issue.assignee_id == assignee_id)
            if creator_id:
                query = query.where(Issue.creator_id == creator_id)
            if issue_type:
                query = query.where(Issue.issue_type.in_(issue_type))

            query = query.order_by(Issue.updated_at.desc()).limit(limit).offset(offset)

            result = await db.execute(query)
            issues = list(result.scalars().all())
            logger.info("[issue_service] list_issues: returned %d issue(s)", len(issues))
            return issues
        except Exception as exc:
            logger.error(
                "[issue_service] list_issues FAILED\n"
                "Exception type : %s\n"
                "Exception value: %s\n"
                "Traceback:\n%s",
                type(exc).__name__,
                exc,
                traceback.format_exc(),
            )
            raise

    async def add_comment(
        self,
        db: AsyncSession,
        issue_key: str,
        user_id: int,
        body: str,
        user_name: str = "Anonymous",
    ) -> Optional[str]:
        """Add a comment to an issue."""
        issue = await self.get_issue_by_key(db, issue_key)
        if not issue:
            return None

        comment_id = await file_storage.add_comment(issue_key, {
            "user_id": user_id,
            "user_name": user_name,
            "body": body,
        })

        # Update issue timestamp
        issue.updated_at = datetime.utcnow()
        await db.commit()

        return comment_id


issue_service = IssueService()
