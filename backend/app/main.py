import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from dotenv import load_dotenv, find_dotenv
# Ensure .env is loaded regardless of working directory
load_dotenv(find_dotenv(), override=False)

from .database import init_db, get_session
from .models import Artifact, Project
from .schemas import ArtifactRead, ProjectCreate, ProjectRead
from .services.pipeline import (
    captions_or_transcribe,
    analyze_to_spec,
    ensure_dir,
    generate_prototype_zip,
)


ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

ensure_dir(ARTIFACTS_DIR)

app = FastAPI(title="YouTube → MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    app.mount("/downloads", StaticFiles(directory=str(ARTIFACTS_DIR)), name="downloads")


def project_artifacts_urls(project: Project, session: Session) -> List[ArtifactRead]:
    results = session.exec(select(Artifact).where(Artifact.project_id == project.id)).all()
    items: List[ArtifactRead] = []
    for a in results:
        rel = Path(a.path).relative_to(ARTIFACTS_DIR)
        url = f"{BACKEND_BASE_URL}/downloads/{rel.as_posix()}"
        items.append(
            ArtifactRead(id=a.id, type=a.type, url=url, created_at=a.created_at)  # type: ignore[arg-type]
        )
    # Include implicit main artifacts from project fields if present
    implicit = [("transcript", project.transcript_path), ("spec", project.spec_path), ("prototype_zip", project.prototype_zip_path)]
    for t, p in implicit:
        if p:
            rel = Path(p).relative_to(ARTIFACTS_DIR)
            url = f"{BACKEND_BASE_URL}/downloads/{rel.as_posix()}"
            items.append(ArtifactRead(id=0, type=t, url=url, created_at=project.updated_at))
    return items


def run_pipeline(project_id: int) -> None:
    from .database import engine as _engine
    with Session(_engine) as session:
        project = session.get(Project, project_id)
        if not project:
            return

        project.status = "processing"
        project.updated_at = datetime.utcnow()
        session.add(project)
        session.commit()

        proj_dir = ARTIFACTS_DIR / str(project.id)
        ensure_dir(proj_dir)

        # 1) Captions/Transcription (stub)
        transcript = captions_or_transcribe(project.youtube_url, work_dir=proj_dir)
        transcript_path = proj_dir / "transcript.txt"
        transcript_path.write_text(transcript, encoding="utf-8")
        project.transcript_path = str(transcript_path)

        # 2) Analyze → spec.json (stub deterministic)
        spec = analyze_to_spec(transcript, project.title or "Generated MVP")
        spec_path = proj_dir / "spec.json"
        spec_path.write_text(__import__("json").dumps(spec, indent=2), encoding="utf-8")
        project.spec_path = str(spec_path)

        # 3) Generate prototype zip
        zip_path = generate_prototype_zip(project.id, spec, ARTIFACTS_DIR)
        project.prototype_zip_path = str(zip_path)

        project.status = "complete"
        project.updated_at = datetime.utcnow()
        session.add(project)
        session.commit()


@app.post("/api/projects", response_model=ProjectRead)
def create_project(payload: ProjectCreate, background: BackgroundTasks, session: Session = Depends(get_session)):
    project = Project(youtube_url=payload.youtube_url, title=payload.title or None, status="queued")
    session.add(project)
    session.commit()
    session.refresh(project)

    # Queue background pipeline
    background.add_task(run_pipeline, project.id)

    return ProjectRead(
        id=project.id, youtube_url=project.youtube_url, title=project.title, status=project.status,
        artifacts=project_artifacts_urls(project, session), created_at=project.created_at, updated_at=project.updated_at
    )


@app.get("/api/projects", response_model=List[ProjectRead])
def list_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project).order_by(Project.created_at.desc())).all()
    out: List[ProjectRead] = []
    for p in projects:
        out.append(
            ProjectRead(
                id=p.id, youtube_url=p.youtube_url, title=p.title, status=p.status,
                artifacts=project_artifacts_urls(p, session), created_at=p.created_at, updated_at=p.updated_at
            )
        )
    return out


@app.get("/api/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: Session = Depends(get_session)):
    p = session.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead(
        id=p.id, youtube_url=p.youtube_url, title=p.title, status=p.status,
        artifacts=project_artifacts_urls(p, session), created_at=p.created_at, updated_at=p.updated_at
    )


@app.post("/api/projects/{project_id}/artifacts", response_model=ArtifactRead)
async def upload_artifact(project_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    proj_dir = ARTIFACTS_DIR / str(project_id)
    ensure_dir(proj_dir)
    filename = file.filename or "upload.bin"
    dest = proj_dir / filename
    contents = await file.read()
    dest.write_bytes(contents)

    artifact = Artifact(project_id=project_id, type="upload", path=str(dest))
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    rel = dest.relative_to(ARTIFACTS_DIR)
    url = f"{BACKEND_BASE_URL}/downloads/{rel.as_posix()}"
    return ArtifactRead(id=artifact.id, type=artifact.type, url=url, created_at=artifact.created_at)


@app.post("/api/generate-prototype")
def generate_prototype(spec: dict, project_id: Optional[int] = None, session: Session = Depends(get_session)):
    pid = project_id or 0
    if project_id:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    zip_path = generate_prototype_zip(project_id or 0, spec, ARTIFACTS_DIR)
    rel = Path(zip_path).relative_to(ARTIFACTS_DIR)
    url = f"{BACKEND_BASE_URL}/downloads/{rel.as_posix()}"
    return {"zip_url": url}


@app.post("/api/projects/{project_id}/complete")
def mark_complete(project_id: int, session: Session = Depends(get_session)):
    p = session.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    p.status = "complete"
    p.updated_at = datetime.utcnow()
    session.add(p)
    session.commit()
    return {"status": "ok"}
