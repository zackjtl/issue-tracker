"""Initialize database with sample data."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.db.database import async_session_maker, init_db
from app.models import User, Project, Issue, IssueStatus, IssuePriority, IssueType
from app.core.security import get_password_hash


async def seed_data():
    """Seed initial data."""
    await init_db()

    async with async_session_maker() as session:
        # Check if data already exists
        from sqlalchemy import select
        result = await session.execute(select(User))
        if result.scalars().first():
            print("Data already exists, skipping seed.")
            return

        # Create default user
        user = User(
            username="admin",
            email="admin@example.com",
            full_name="System Admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
        )
        session.add(user)

        # Create sample projects
        projects = [
            Project(
                name="Infrastructure",
                path="infra",
                description="Infrastructure and DevOps tasks",
                owner_id=1,
                default_priority="high",
            ),
            Project(
                name="Mail Gateway",
                path="infra/mail",
                parent_path="infra",
                description="Email gateway services",
                owner_id=1,
                default_priority="medium",
            ),
            Project(
                name="Frontend",
                path="frontend",
                description="Frontend application development",
                owner_id=1,
                default_priority="medium",
            ),
            Project(
                name="Backend API",
                path="backend",
                description="Backend API development",
                owner_id=1,
                default_priority="high",
            ),
        ]

        for project in projects:
            session.add(project)

        # Create sample issues
        issues = [
            Issue(
                issue_key="INFRA-0001",
                project_path="infra",
                title="Set up CI/CD pipeline",
                description="Configure automated CI/CD pipeline for the project",
                issue_type=IssueType.TASK,
                priority=IssuePriority.HIGH,
                status=IssueStatus.IN_PROGRESS,
                creator_id=1,
                assignee_id=1,
                source="web",
            ),
            Issue(
                issue_key="INFRA-0002",
                project_path="infra",
                title="Fix Docker networking issues",
                description="Docker containers cannot communicate properly",
                issue_type=IssueType.BUG,
                priority=IssuePriority.URGENT,
                status=IssueStatus.NEW,
                creator_id=1,
                source="web",
            ),
            Issue(
                issue_key="MAIL-0001",
                project_path="infra/mail",
                title="Email notification not sending",
                description="Users are not receiving email notifications",
                issue_type=IssueType.BUG,
                priority=IssuePriority.HIGH,
                status=IssueStatus.ASSIGNED,
                creator_id=1,
                assignee_id=1,
                source="email",
            ),
            Issue(
                issue_key="FRONT-0001",
                project_path="frontend",
                title="Implement dark mode toggle",
                description="Add a toggle button for dark/light mode in settings",
                issue_type=IssueType.TASK,
                priority=IssuePriority.MEDIUM,
                status=IssueStatus.TRIAGED,
                creator_id=1,
                source="web",
            ),
            Issue(
                issue_key="BACK-0001",
                project_path="backend",
                title="Optimize database queries",
                description="Several endpoints have slow query performance",
                issue_type=IssueType.TASK,
                priority=IssuePriority.MEDIUM,
                status=IssueStatus.RESOLVED,
                creator_id=1,
                assignee_id=1,
                source="web",
            ),
        ]

        for issue in issues:
            session.add(issue)

        await session.commit()
        print("Sample data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
