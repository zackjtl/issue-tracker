"""Auth API routes with Supabase support."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.core.config import settings
from app.core.supabase import supabase_auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from Supabase token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization.replace("Bearer ", "")

    # Try Supabase verification first
    supabase_user = await supabase_auth.verify_token(token)
    
    if supabase_user:
        # Find or create user in local database
        email = supabase_user.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Supabase token",
            )

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Auto-create user from Supabase
            user = User(
                username=email.split("@")[0],
                email=email,
                hashed_password="",  # No password needed, using Supabase auth
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user

    # Fallback: try local JWT verification (for development)
    from app.core.security import decode_access_token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


@router.post("/sync")
async def sync_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    """Sync Supabase user to local database."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization.replace("Bearer ", "")
    supabase_user = await supabase_auth.verify_token(token)

    if not supabase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token",
        )

    email = supabase_user.get("email")
    user_id = supabase_user.get("id")

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=email.split("@")[0],
            email=email,
            hashed_password="",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "supabase_id": user_id,
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user
