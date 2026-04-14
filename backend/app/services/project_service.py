"""Project service."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Project, User


class ProjectService:
    """Service for managing projects."""

    async def create_project(
        self,
        db: AsyncSession,
        name: str,
        path: str,
        owner_id: int,
        parent_path: Optional[str] = None,
        description: Optional[str] = None,
        default_priority: str = "medium",
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=name,
            path=path,
            parent_path=parent_path,
            owner_id=owner_id,
            description=description,
            default_priority=default_priority,
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        return project

    async def get_project_by_path(self, db: AsyncSession, path: str) -> Optional[Project]:
        """Get project by path."""
        result = await db.execute(
            select(Project).where(Project.path == path)
        )
        return result.scalar_one_or_none()

    async def get_project_by_id(self, db: AsyncSession, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_projects(self, db: AsyncSession) -> List[Project]:
        """List all projects."""
        result = await db.execute(select(Project).order_by(Project.path))
        return list(result.scalars().all())

    async def update_project(
        self,
        db: AsyncSession,
        project_id: int,
        **updates,
    ) -> Optional[Project]:
        """Update a project."""
        project = await self.get_project_by_id(db, project_id)
        if not project:
            return None

        for field, value in updates.items():
            if value is not None and hasattr(project, field):
                setattr(project, field, value)

        await db.commit()
        await db.refresh(project)

        return project

    async def get_project_tree(self, db: AsyncSession) -> List[dict]:
        """Get projects as a tree structure."""
        projects = await self.list_projects(db)

        # Build tree
        tree = []
        path_to_node = {}

        for project in projects:
            node = {
                "id": project.id,
                "name": project.name,
                "path": project.path,
                "parent_path": project.parent_path,
                "description": project.description,
                "children": [],
            }
            path_to_node[project.path] = node

        for project in projects:
            node = path_to_node[project.path]
            if project.parent_path and project.parent_path in path_to_node:
                path_to_node[project.parent_path]["children"].append(node)
            else:
                tree.append(node)

        return tree


project_service = ProjectService()
