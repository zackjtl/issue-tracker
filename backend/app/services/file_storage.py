"""File storage service for issue content."""
import os
import json
import uuid
import aiofiles
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.core.config import settings


class FileStorageService:
    """Service for managing issue files."""

    def __init__(self):
        self.issues_dir = Path(settings.ISSUES_DATA_DIR)
        self.attachments_dir = Path(settings.ATTACHMENTS_DIR)
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.issues_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)

    def _get_issue_dir(self, issue_key: str) -> Path:
        """Get issue directory path."""
        return self.issues_dir / issue_key

    def _ensure_issue_dir(self, issue_key: str) -> Path:
        """Ensure issue directory exists."""
        issue_dir = self._get_issue_dir(issue_key)
        issue_dir.mkdir(parents=True, exist_ok=True)
        return issue_dir

    # ============ Issue Content ============

    async def save_issue_content(self, issue_key: str, content: str) -> None:
        """Save issue.md content."""
        issue_dir = self._ensure_issue_dir(issue_key)
        async with aiofiles.open(issue_dir / "issue.md", "w", encoding="utf-8") as f:
            await f.write(content)

    async def read_issue_content(self, issue_key: str) -> Optional[str]:
        """Read issue.md content."""
        issue_dir = self._get_issue_dir(issue_key)
        file_path = issue_dir / "issue.md"
        if file_path.exists():
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        return None

    # ============ Issue Metadata ============

    async def save_issue_meta(self, issue_key: str, meta: Dict[str, Any]) -> None:
        """Save meta.json."""
        issue_dir = self._ensure_issue_dir(issue_key)
        async with aiofiles.open(issue_dir / "meta.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(meta, indent=2, ensure_ascii=False))

    async def read_issue_meta(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Read meta.json."""
        issue_dir = self._get_issue_dir(issue_key)
        file_path = issue_dir / "meta.json"
        if file_path.exists():
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content)
        return None

    # ============ Comments ============

    async def add_comment(self, issue_key: str, comment: Dict[str, Any]) -> str:
        """Add a comment to the issue."""
        issue_dir = self._ensure_issue_dir(issue_key)
        comments_dir = issue_dir / "comments"
        comments_dir.mkdir(exist_ok=True)

        comment_id = str(uuid.uuid4())[:8]
        comment_file = comments_dir / f"{comment_id}.json"

        comment["comment_id"] = comment_id
        comment["created_at"] = datetime.utcnow().isoformat()

        async with aiofiles.open(comment_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(comment, indent=2, ensure_ascii=False))

        return comment_id

    async def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all comments for an issue."""
        issue_dir = self._get_issue_dir(issue_key)
        comments_dir = issue_dir / "comments"

        if not comments_dir.exists():
            return []

        comments = []
        for file in sorted(comments_dir.glob("*.json")):
            async with aiofiles.open(file, "r", encoding="utf-8") as f:
                content = await f.read()
                comments.append(json.loads(content))

        return comments

    # ============ Events ============

    async def add_event(self, issue_key: str, event: Dict[str, Any]) -> str:
        """Add an event to the issue."""
        issue_dir = self._ensure_issue_dir(issue_key)
        events_dir = issue_dir / "events"
        events_dir.mkdir(exist_ok=True)

        event_id = str(uuid.uuid4())[:8]
        event_file = events_dir / f"{event_id}.json"

        event["event_id"] = event_id
        event["created_at"] = datetime.utcnow().isoformat()

        async with aiofiles.open(event_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(event, indent=2, ensure_ascii=False))

        return event_id

    async def get_events(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all events for an issue."""
        issue_dir = self._get_issue_dir(issue_key)
        events_dir = issue_dir / "events"

        if not events_dir.exists():
            return []

        events = []
        for file in sorted(events_dir.glob("*.json")):
            async with aiofiles.open(file, "r", encoding="utf-8") as f:
                content = await f.read()
                events.append(json.loads(content))

        return events

    # ============ Attachments ============

    async def save_attachment(self, issue_key: str, filename: str, content: bytes, 
                               mime_type: str, uploaded_by: int, description: str = "") -> Dict[str, Any]:
        """Save an attachment."""
        issue_dir = self._ensure_issue_dir(issue_key)
        attachments_dir = issue_dir / "attachments"
        attachments_dir.mkdir(exist_ok=True)

        attachment_id = str(uuid.uuid4())
        ext = Path(filename).suffix
        stored_filename = f"{attachment_id}{ext}"
        storage_path = attachments_dir / stored_filename

        async with aiofiles.open(storage_path, "wb") as f:
            await f.write(content)

        import hashlib
        file_hash = hashlib.md5(content).hexdigest()

        attachment_meta = {
            "attachment_id": attachment_id,
            "filename": stored_filename,
            "original_filename": filename,
            "mime_type": mime_type,
            "size": len(content),
            "uploaded_by": uploaded_by,
            "description": description,
            "hash": file_hash,
            "storage_path": str(storage_path),
        }

        meta_file = attachments_dir / f"{attachment_id}.json"
        async with aiofiles.open(meta_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(attachment_meta, indent=2, ensure_ascii=False))

        return attachment_meta

    async def get_attachments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get all attachments for an issue."""
        issue_dir = self._get_issue_dir(issue_key)
        attachments_dir = issue_dir / "attachments"

        if not attachments_dir.exists():
            return []

        attachments = []
        for file in attachments_dir.glob("*.json"):
            async with aiofiles.open(file, "r", encoding="utf-8") as f:
                content = await f.read()
                attachments.append(json.loads(content))

        return attachments

    async def get_attachment_file(self, issue_key: str, attachment_id: str) -> Optional[tuple]:
        """Get attachment file content and metadata."""
        issue_dir = self._get_issue_dir(issue_key)
        attachments_dir = issue_dir / "attachments"
        meta_file = attachments_dir / f"{attachment_id}.json"

        if not meta_file.exists():
            return None

        async with aiofiles.open(meta_file, "r", encoding="utf-8") as f:
            meta = json.loads(await f.read())

        storage_path = Path(meta["storage_path"])
        if not storage_path.exists():
            return None

        async with aiofiles.open(storage_path, "rb") as f:
            content = await f.read()

        return content, meta

    # ============ Issue Links ============

    async def save_issue_links(self, issue_key: str, links: List[Dict[str, Any]]) -> None:
        """Save issue links."""
        issue_dir = self._ensure_issue_dir(issue_key)
        links_file = issue_dir / "links" / "links.json"
        links_file.parent.mkdir(exist_ok=True)

        async with aiofiles.open(links_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(links, indent=2, ensure_ascii=False))

    async def get_issue_links(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get issue links."""
        issue_dir = self._get_issue_dir(issue_key)
        links_file = issue_dir / "links" / "links.json"

        if not links_file.exists():
            return []

        async with aiofiles.open(links_file, "r", encoding="utf-8") as f:
            return json.loads(await f.read())


# Singleton instance
file_storage = FileStorageService()
