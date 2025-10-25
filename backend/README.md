# Backend — FastAPI (YouTube → MVP)

This FastAPI backend powers the YouTube → MVP pipeline:

- Accepts a YouTube URL to create a Project
- Attempts captions (stub) → Whisper fallback (stub)
- Analyzes transcript into a structured spec.json (mocked deterministic generator for local dev)
- Generates a Next.js + Tailwind prototype ZIP from the spec
- Serves artifacts via `/downloads/...`

## Quickstart

- Python 3.11+
- Create and fill `.env` (see `.env.example`)

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` and artifacts at `http://localhost:8000/downloads/...`.

## Key Endpoints

- POST `/api/projects` — create project from YouTube URL (queues background processing)
- GET  `/api/projects` — list projects
- GET  `/api/projects/{id}` — get project with artifacts
- POST `/api/projects/{id}/artifacts` — upload artifact file
- POST `/api/generate-prototype` — generate prototype ZIP from provided spec
- POST `/api/projects/{id}/complete` — mark complete (Make.com stub)

## Notes

- SQLite database located at `backend/data.db` by default.
- Artifacts stored under `backend/artifacts/{project_id}/...` and served via `/downloads/...`.
- For local/offline dev, the pipeline uses deterministic stubs when no API keys are present.

