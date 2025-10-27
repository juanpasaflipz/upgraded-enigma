from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    youtube_url: str
    title: Optional[str] = None


class ArtifactRead(BaseModel):
    id: int
    type: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectRead(BaseModel):
    id: int
    youtube_url: str
    title: Optional[str]
    status: str
    mvp_viability: Optional[str] = None
    viability_score: Optional[float] = None
    viability_reason: Optional[str] = None
    artifacts: List[ArtifactRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
