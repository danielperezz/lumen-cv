"""
Profile service: the single demo user and its profile row.
"""

import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from server.models import Profile, User

DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def ensure_demo_profile(db: Session) -> Profile:
    """
    Create the demo user and its profile if they do not exist yet, then return the profile.
    Both inserts use ON CONFLICT DO NOTHING on fixed keys, so concurrent first requests are safe.
    The caller commits.
    """
    now = datetime.now(UTC)

    db.execute(
        insert(User)
        .values(id=DEMO_USER_ID, display_name="Demo user", created_at=now, updated_at=now)
        .on_conflict_do_nothing(index_elements=["id"])
    )
    db.execute(
        insert(Profile)
        .values(id=uuid.uuid4(), user_id=DEMO_USER_ID, document={}, created_at=now, updated_at=now)
        .on_conflict_do_nothing(constraint="uq_profiles_user_id")
    )
    return db.execute(select(Profile).where(Profile.user_id == DEMO_USER_ID)).scalar_one()
