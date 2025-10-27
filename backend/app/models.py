from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    youtube_url: str
    title: Optional[str] = None
    status: str = Field(default="queued")  # queued, processing, complete, failed
    caption_path: Optional[str] = None
    transcript_path: Optional[str] = None
    spec_path: Optional[str] = None
    prototype_zip_path: Optional[str] = None
    # Viability assessment fields
    mvp_viability: Optional[str] = Field(default=None)  # "mvp-ready" | "idea-only" | "not-a-project"
    viability_score: Optional[float] = Field(default=None)
    viability_reason: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Artifact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    type: str  # e.g., caption, transcript, spec, prototype_zip, other
    path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
