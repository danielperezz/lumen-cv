from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Basics(BaseModel):
    name: str | None = None
    headline: str | None = None


class Education(BaseModel):
    school: str | None = None
    degree: str | None = None
    year: str | None = None
    details: str | None = None


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    period: str | None = None
    details: str | None = None


class Project(BaseModel):
    name: str | None = None
    tech: str | None = None
    details: str | None = None


class Story(BaseModel):
    title: str | None = None
    content: str | None = None


class ProfileDocument(BaseModel):
    basics: Basics = Field(default_factory=Basics)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills: list[NonEmptyStr] = Field(default_factory=list)
    stories: list[Story] = Field(default_factory=list)
