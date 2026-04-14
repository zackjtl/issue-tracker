"""Project API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    # Check if path already exists
    existing = await project_service.get_project_by_path(db, project.path)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project path already exists",
        )

    # Validate parent path if provided
    if project.parent_path:
        parent = await project_service.get_project_by_path(db, project.parent_path)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent project not found",
            )

    new_project = await project_service.create_project(
        db=db,
        name=project.name,
        path=project.path,
        owner_id=1,  # TODO: Get from auth
        parent_path=project.parent_path,
        description=project.description,
        default_priority=project.default_priority,
    )

    return new_project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    projects = await project_service.list_projects(db)
    return projects


@router.get("/tree")
async def get_project_tree(db: AsyncSession = Depends(get_db)):
    """Get projects as a tree structure."""
    tree = await project_service.get_project_tree(db)
    return tree


@router.get("/{path:path}", response_model=ProjectResponse)
async def get_project(path: str, db: AsyncSession = Depends(get_db)):
    """Get a project by path."""
    project = await project_service.get_project_by_path(db, path)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.put("/{project_id:int}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a project."""
    updated = await project_service.update_project(db, project_id, **project.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return updated
