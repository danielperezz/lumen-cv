"""create lumen cv tables

Revision ID: 20260506_0001
Revises:
Create Date: 2026-05-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260506_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False)


def upgrade() -> None:
    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "profiles",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("headline", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_profiles_user_id"),
    )
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"])

    op.create_table(
        "job_description_drafts",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_job_description_drafts_user_id"),
    )

    op.create_table(
        "profile_education",
        uuid_pk(),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school", sa.Text(), nullable=True),
        sa.Column("degree", sa.Text(), nullable=True),
        sa.Column("year", sa.Text(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_education_profile_id", "profile_education", ["profile_id"])

    op.create_table(
        "profile_experience",
        uuid_pk(),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company", sa.Text(), nullable=True),
        sa.Column("role", sa.Text(), nullable=True),
        sa.Column("period", sa.Text(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_experience_profile_id", "profile_experience", ["profile_id"])

    op.create_table(
        "profile_projects",
        uuid_pk(),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("tech", sa.Text(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_projects_profile_id", "profile_projects", ["profile_id"])

    op.create_table(
        "profile_skills",
        uuid_pk(),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("normalized_name", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "normalized_name", name="uq_profile_skills_profile_normalized_name"),
    )
    op.create_index("ix_profile_skills_profile_id", "profile_skills", ["profile_id"])

    op.create_table(
        "profile_stories",
        uuid_pk(),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_stories_profile_id", "profile_stories", ["profile_id"])

    op.create_table(
        "saved_jobs",
        uuid_pk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_jobs_user_id", "saved_jobs", ["user_id"])
    op.create_index("ix_saved_jobs_saved_at", "saved_jobs", ["saved_at"])

    op.create_table(
        "generated_cvs",
        uuid_pk(),
        sa.Column("saved_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("generator", sa.Text(), nullable=True),
        sa.Column("model", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["saved_job_id"], ["saved_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("saved_job_id", name="uq_generated_cvs_saved_job_id"),
    )
    op.create_index("ix_generated_cvs_saved_job_id", "generated_cvs", ["saved_job_id"])

    op.create_table(
        "match_scores",
        uuid_pk(),
        sa.Column("saved_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("matched_keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("missing_keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        *timestamps(),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_match_scores_score_range"),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["saved_job_id"], ["saved_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_match_scores_profile_id", "match_scores", ["profile_id"])
    op.create_index("ix_match_scores_saved_job_id", "match_scores", ["saved_job_id"])

    op.create_table(
        "generated_cv_bullets",
        uuid_pk(),
        sa.Column("generated_cv_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["generated_cv_id"], ["generated_cvs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_cv_bullets_generated_cv_id", "generated_cv_bullets", ["generated_cv_id"])

    op.create_table(
        "generated_cv_keywords",
        uuid_pk(),
        sa.Column("generated_cv_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("keyword", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["generated_cv_id"], ["generated_cvs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_cv_keywords_generated_cv_id", "generated_cv_keywords", ["generated_cv_id"])

    op.create_table(
        "generated_cv_skills",
        uuid_pk(),
        sa.Column("generated_cv_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["generated_cv_id"], ["generated_cvs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_cv_skills_generated_cv_id", "generated_cv_skills", ["generated_cv_id"])

    op.create_table(
        "generated_cv_used_items",
        uuid_pk(),
        sa.Column("generated_cv_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("source_table", sa.Text(), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["generated_cv_id"], ["generated_cvs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_cv_used_items_generated_cv_id", "generated_cv_used_items", ["generated_cv_id"])


def downgrade() -> None:
    op.drop_index("ix_generated_cv_used_items_generated_cv_id", table_name="generated_cv_used_items")
    op.drop_table("generated_cv_used_items")
    op.drop_index("ix_generated_cv_skills_generated_cv_id", table_name="generated_cv_skills")
    op.drop_table("generated_cv_skills")
    op.drop_index("ix_generated_cv_keywords_generated_cv_id", table_name="generated_cv_keywords")
    op.drop_table("generated_cv_keywords")
    op.drop_index("ix_generated_cv_bullets_generated_cv_id", table_name="generated_cv_bullets")
    op.drop_table("generated_cv_bullets")
    op.drop_index("ix_match_scores_saved_job_id", table_name="match_scores")
    op.drop_index("ix_match_scores_profile_id", table_name="match_scores")
    op.drop_table("match_scores")
    op.drop_index("ix_generated_cvs_saved_job_id", table_name="generated_cvs")
    op.drop_table("generated_cvs")
    op.drop_index("ix_saved_jobs_saved_at", table_name="saved_jobs")
    op.drop_index("ix_saved_jobs_user_id", table_name="saved_jobs")
    op.drop_table("saved_jobs")
    op.drop_index("ix_profile_stories_profile_id", table_name="profile_stories")
    op.drop_table("profile_stories")
    op.drop_index("ix_profile_skills_profile_id", table_name="profile_skills")
    op.drop_table("profile_skills")
    op.drop_index("ix_profile_projects_profile_id", table_name="profile_projects")
    op.drop_table("profile_projects")
    op.drop_index("ix_profile_experience_profile_id", table_name="profile_experience")
    op.drop_table("profile_experience")
    op.drop_index("ix_profile_education_profile_id", table_name="profile_education")
    op.drop_table("profile_education")
    op.drop_table("job_description_drafts")
    op.drop_index("ix_profiles_user_id", table_name="profiles")
    op.drop_table("profiles")
    op.drop_table("users")
