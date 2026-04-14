"""Supabase token verification."""
import os
import httpx
from typing import Optional
from app.core.config import settings


class SupabaseAuth:
    """Supabase authentication helper."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify a Supabase JWT token and return the user info."""
        if not self.supabase_url:
            return None

        try:
            # Call Supabase Auth API to verify token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/auth/v1/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": self.supabase_anon_key,
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Supabase token verification error: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user info from Supabase by user ID."""
        if not self.supabase_url or not self.supabase_service_key:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {self.supabase_service_key}",
                        "apikey": self.supabase_service_key,
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"Supabase get user error: {e}")
            return None


supabase_auth = SupabaseAuth()
