"""
Core persistence models for Lumen CV profile, job, and generated CV data.
"""

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from server.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, nullable=True)
    display_name = Column(String, nullable=True)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    job_description_draft = relationship(
        "JobDescriptionDraft", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")


class Profile(BaseModel):
    __tablename__ = "profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_profiles_user_id"),
        Index("ix_profiles_user_id", "user_id"),
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=True)
    headline = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")
    education = relationship("ProfileEducation", back_populates="profile", cascade="all, delete-orphan")
    experience = relationship("ProfileExperience", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("ProfileProject", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("ProfileSkill", back_populates="profile", cascade="all, delete-orphan")
    stories = relationship("ProfileStory", back_populates="profile", cascade="all, delete-orphan")
    generated_cvs = relationship("GeneratedCV", back_populates="profile", passive_deletes=True)
    match_scores = relationship("MatchScore", back_populates="profile", passive_deletes=True)


class ProfileEducation(BaseModel):
    __tablename__ = "profile_education"
    __table_args__ = (Index("ix_profile_education_profile_id", "profile_id"),)

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    school = Column(Text, nullable=True)
    degree = Column(Text, nullable=True)
    year = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False)

    profile = relationship("Profile", back_populates="education")


class ProfileExperience(BaseModel):
    __tablename__ = "profile_experience"
    __table_args__ = (Index("ix_profile_experience_profile_id", "profile_id"),)

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    company = Column(Text, nullable=True)
    role = Column(Text, nullable=True)
    period = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False)

    profile = relationship("Profile", back_populates="experience")


class ProfileProject(BaseModel):
    __tablename__ = "profile_projects"
    __table_args__ = (Index("ix_profile_projects_profile_id", "profile_id"),)

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=True)
    tech = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False)

    profile = relationship("Profile", back_populates="projects")


class ProfileSkill(BaseModel):
    __tablename__ = "profile_skills"
    __table_args__ = (
        UniqueConstraint("profile_id", "normalized_name", name="uq_profile_skills_profile_normalized_name"),
        Index("ix_profile_skills_profile_id", "profile_id"),
    )

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    normalized_name = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False)

    profile = relationship("Profile", back_populates="skills")


class ProfileStory(BaseModel):
    __tablename__ = "profile_stories"
    __table_args__ = (Index("ix_profile_stories_profile_id", "profile_id"),)

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False)

    profile = relationship("Profile", back_populates="stories")


class JobDescriptionDraft(BaseModel):
    __tablename__ = "job_description_drafts"
    __table_args__ = (UniqueConstraint("user_id", name="uq_job_description_drafts_user_id"),)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=True)

    user = relationship("User", back_populates="job_description_draft")


class SavedJob(BaseModel):
    __tablename__ = "saved_jobs"
    __table_args__ = (
        Index("ix_saved_jobs_user_id", "user_id"),
        Index("ix_saved_jobs_saved_at", "saved_at"),
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    job_description = Column(Text, nullable=False)
    saved_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="saved_jobs")
    generated_cv = relationship("GeneratedCV", back_populates="saved_job", uselist=False, cascade="all, delete-orphan")
    match_scores = relationship("MatchScore", back_populates="saved_job", cascade="all, delete-orphan")


class GeneratedCV(BaseModel):
    __tablename__ = "generated_cvs"
    __table_args__ = (
        UniqueConstraint("saved_job_id", name="uq_generated_cvs_saved_job_id"),
        Index("ix_generated_cvs_saved_job_id", "saved_job_id"),
    )

    saved_job_id = Column(UUID(as_uuid=True), ForeignKey("saved_jobs.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="RESTRICT"), nullable=False)
    summary = Column(Text, nullable=False)
    generator = Column(Text, nullable=True)
    model = Column(Text, nullable=True)

    saved_job = relationship("SavedJob", back_populates="generated_cv")
    profile = relationship("Profile", back_populates="generated_cvs")
    skills = relationship("GeneratedCVSkill", back_populates="generated_cv", cascade="all, delete-orphan")
    bullets = relationship("GeneratedCVBullet", back_populates="generated_cv", cascade="all, delete-orphan")
    used_items = relationship("GeneratedCVUsedItem", back_populates="generated_cv", cascade="all, delete-orphan")
    keywords = relationship("GeneratedCVKeyword", back_populates="generated_cv", cascade="all, delete-orphan")


class GeneratedCVSkill(BaseModel):
    __tablename__ = "generated_cv_skills"
    __table_args__ = (Index("ix_generated_cv_skills_generated_cv_id", "generated_cv_id"),)

    generated_cv_id = Column(UUID(as_uuid=True), ForeignKey("generated_cvs.id", ondelete="CASCADE"), nullable=False)
    skill = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False)

    generated_cv = relationship("GeneratedCV", back_populates="skills")


class GeneratedCVBullet(BaseModel):
    __tablename__ = "generated_cv_bullets"
    __table_args__ = (Index("ix_generated_cv_bullets_generated_cv_id", "generated_cv_id"),)

    generated_cv_id = Column(UUID(as_uuid=True), ForeignKey("generated_cvs.id", ondelete="CASCADE"), nullable=False)
    source = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False)

    generated_cv = relationship("GeneratedCV", back_populates="bullets")


class GeneratedCVUsedItem(BaseModel):
    __tablename__ = "generated_cv_used_items"
    __table_args__ = (Index("ix_generated_cv_used_items_generated_cv_id", "generated_cv_id"),)

    generated_cv_id = Column(UUID(as_uuid=True), ForeignKey("generated_cvs.id", ondelete="CASCADE"), nullable=False)
    kind = Column(Text, nullable=False)
    label = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    source_table = Column(Text, nullable=True)
    source_id = Column(UUID(as_uuid=True), nullable=True)
    sort_order = Column(Integer, nullable=False)

    generated_cv = relationship("GeneratedCV", back_populates="used_items")


class GeneratedCVKeyword(BaseModel):
    __tablename__ = "generated_cv_keywords"
    __table_args__ = (Index("ix_generated_cv_keywords_generated_cv_id", "generated_cv_id"),)

    generated_cv_id = Column(UUID(as_uuid=True), ForeignKey("generated_cvs.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False)

    generated_cv = relationship("GeneratedCV", back_populates="keywords")


class MatchScore(BaseModel):
    __tablename__ = "match_scores"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_match_scores_score_range"),
        Index("ix_match_scores_saved_job_id", "saved_job_id"),
        Index("ix_match_scores_profile_id", "profile_id"),
    )

    saved_job_id = Column(UUID(as_uuid=True), ForeignKey("saved_jobs.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    matched_keywords = Column(JSONB, nullable=False)
    missing_keywords = Column(JSONB, nullable=False)

    saved_job = relationship("SavedJob", back_populates="match_scores")
    profile = relationship("Profile", back_populates="match_scores")
