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

### Environment variables

See `.env.example` for a complete list. Key vars:
- `DATABASE_URL` (default sqlite:///./data.db)
- `ARTIFACTS_DIR` (default artifacts)
- `BACKEND_BASE_URL` (public URL of this service)
- `ALLOWED_ORIGINS` (comma-separated origins for CORS; e.g. https://yourapp.vercel.app)
- `OPENAI_API_KEY`, `OPENAI_MODEL_GPT` (LLM viability)
- `STRIPE_SECRET_KEY`, `STRIPE_PRICE_FREE`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_STUDIO`, `FRONTEND_URL`

If unset, viability falls back to heuristics and the Stripe route returns a safe fallback URL.

## Key Endpoints

- POST `/api/projects` — create project from YouTube URL (queues background processing)
- GET  `/api/projects` — list projects
- GET  `/api/projects/{id}` — get project with artifacts
- POST `/api/projects/{id}/artifacts` — upload artifact file
- POST `/api/generate-prototype` — generate prototype ZIP from provided spec
- POST `/api/projects/{id}/complete` — mark complete (Make.com stub)
- POST `/api/viability-check` — returns viability label/score/reason for a transcript
- POST `/api/stripe/create-checkout-session` — returns a Checkout `url` for a plan (`free|pro|studio`)

## Notes

- SQLite database located at `backend/data.db` by default.
- Artifacts stored under `backend/artifacts/{project_id}/...` and served via `/downloads/...`.
- For local/offline dev, the pipeline uses deterministic stubs when no API keys are present.

## Deploy (Render example)

See `render.yaml` for a ready-to-deploy service.

1) Create a Web Service, rootDir `backend`, attach a Disk mounted at `/data`.
2) Set env vars:
   - `ARTIFACTS_DIR=/data/artifacts`
   - `BACKEND_BASE_URL=https://<your-backend>`
   - `FRONTEND_URL=https://<your-frontend>`
   - `ALLOWED_ORIGINS=https://<your-frontend>`
   - Optional: `OPENAI_API_KEY`, Stripe vars
3) Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

