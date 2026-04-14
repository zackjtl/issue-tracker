"""Initialize sample issues as files."""
import asyncio
import aiofiles
import json
from datetime import datetime, timedelta
import random

ISSUES_DIR = "data/issues"


async def create_issue_files():
    """Create sample issue files."""
    import os
    os.makedirs(ISSUES_DIR, exist_ok=True)

    sample_issues = [
        {
            "key": "INFRA-0001",
            "meta": {
                "issue_key": "INFRA-0001",
                "project_path": "infra",
                "title": "Set up CI/CD pipeline",
                "type": "task",
                "priority": "high",
                "status": "in_progress",
                "creator_id": 1,
                "assignee_id": 1,
                "created_at": datetime.utcnow().isoformat(),
                "tags": ["ci/cd", "devops"],
            },
            "content": """# Set up CI/CD pipeline

## Description
Configure automated CI/CD pipeline for the project using GitHub Actions.

## Requirements
- Automated testing on every push
- Automated deployment to staging
- Manual deployment to production
- Slack notifications on failure

## Acceptance Criteria
- [ ] Tests run automatically
- [ ] Staging deployment works
- [ ] Production deployment approved
"""
        },
        {
            "key": "INFRA-0002",
            "meta": {
                "issue_key": "INFRA-0002",
                "project_path": "infra",
                "title": "Fix Docker networking issues",
                "type": "bug",
                "priority": "urgent",
                "status": "new",
                "creator_id": 1,
                "created_at": datetime.utcnow().isoformat(),
                "tags": ["docker", "networking"],
            },
            "content": """# Fix Docker networking issues

## Description
Docker containers cannot communicate properly. Services fail to connect to each other.

## Steps to Reproduce
1. Start all services using docker-compose
2. Try to access API from frontend
3. Connection fails

## Expected Behavior
Services should be able to communicate via internal network.

## Environment
- Docker version: 24.0
- docker-compose version: 2.20
"""
        },
        {
            "key": "MAIL-0001",
            "meta": {
                "issue_key": "MAIL-0001",
                "project_path": "infra/mail",
                "title": "Email notification not sending",
                "type": "bug",
                "priority": "high",
                "status": "assigned",
                "creator_id": 1,
                "assignee_id": 1,
                "created_at": datetime.utcnow().isoformat(),
                "tags": ["email", "notifications"],
            },
            "content": """# Email notification not sending

## Description
Users are not receiving email notifications for new assignments.

## Investigation
- SMTP server appears to be running
- No errors in application logs
- Email queue is empty (messages sent immediately?)

## Possible Causes
- [ ] SMTP credentials expired
- [ ] Firewall blocking outbound SMTP
- [ ] Recipient email marked as spam
"""
        },
    ]

    for issue in sample_issues:
        issue_dir = f"{ISSUES_DIR}/{issue['key']}"
        os.makedirs(issue_dir, exist_ok=True)
        os.makedirs(f"{issue_dir}/comments", exist_ok=True)
        os.makedirs(f"{issue_dir}/events", exist_ok=True)
        os.makedirs(f"{issue_dir}/attachments", exist_ok=True)
        os.makedirs(f"{issue_dir}/links", exist_ok=True)

        # Write issue.md
        async with aiofiles.open(f"{issue_dir}/issue.md", "w", encoding="utf-8") as f:
            await f.write(issue["content"])

        # Write meta.json
        async with aiofiles.open(f"{issue_dir}/meta.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(issue["meta"], indent=2, ensure_ascii=False))

        # Add sample events
        events = [
            {
                "event_id": "evt001",
                "event_type": "issue_created",
                "user_id": 1,
                "details": {"title": issue["meta"]["title"]},
                "created_at": datetime.utcnow().isoformat(),
            },
        ]
        async with aiofiles.open(f"{issue_dir}/events/evt001.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(events[0], indent=2, ensure_ascii=False))

    print(f"Created {len(sample_issues)} sample issues")


if __name__ == "__main__":
    asyncio.run(create_issue_files())
